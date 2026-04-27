import json
from collections import deque
from .llm import LLMClient
from .tools import TOOL_DEFINITIONS, TOOL_MAP
from .config import MAX_HISTORY_TURNS, MAX_ITERATIONS, MAX_TOOL_OUTPUT

SYSTEM_PROMPT = """Kamu adalah ReClaw, agen coding efisien & aman. Tugas: edit script, jalankan command, bantu coding.
ATURAN:
1. Gunakan tools. Jangan tulis kode di chat jika bisa langsung write_file/edit_file.
2. Berpikir singkat. Jangan ulangi konten file dalam reasoning.
3. Untuk edit kecil, gunakan edit_file (old_string->new_string). Untuk file baru, gunakan write_file.
4. run_shell hanya untuk command aman. Jika command berbahaya, tanya user.
5. Jika output tool terlalu panjang, lanjutkan pekerjaan tanpa meminta user untuk menampilkannya ulang.
6. Bahasa: gunakan bahasa yang sama dengan user (default Indonesia)."""

class ReClawAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.history = deque(maxlen=MAX_HISTORY_TURNS * 2)
        self.system_message = {"role": "system", "content": SYSTEM_PROMPT}

    def _truncate_tool_result(self, result: str) -> str:
        if len(result) > MAX_TOOL_OUTPUT:
            half = MAX_TOOL_OUTPUT // 2
            return result[:half] + f"\n... [truncated {len(result)} chars] ...\n" + result[-half:]
        return result

    def run(self, user_input: str):
        """Jalankan satu turn interaksi. Yield dict untuk status atau string untuk konten."""
        messages = [self.system_message]
        messages.extend(list(self.history))
        messages.append({"role": "user", "content": user_input})

        iteration = 0
        
        while iteration < MAX_ITERATIONS:
            iteration += 1
            
            # We use streaming for the assistant's response
            stream = self.llm.chat(messages, tools=TOOL_DEFINITIONS, tool_choice="auto", stream=True)
            
            full_content = ""
            tool_calls = []
            
            # Process the stream
            for chunk in stream:
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    
                    # Handle content streaming
                    if delta.content:
                        full_content += delta.content
                        yield {"type": "content", "delta": delta.content}
                    
                    # Handle tool calls streaming
                    if delta.tool_calls:
                        for tc_delta in delta.tool_calls:
                            if len(tool_calls) <= tc_delta.index:
                                tool_calls.append({
                                    "id": tc_delta.id,
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""}
                                })
                            
                            if tc_delta.id:
                                tool_calls[tc_delta.index]["id"] = tc_delta.id
                            if tc_delta.function:
                                if tc_delta.function.name:
                                    tool_calls[tc_delta.index]["function"]["name"] += tc_delta.function.name
                                if tc_delta.function.arguments:
                                    tool_calls[tc_delta.index]["function"]["arguments"] += tc_delta.function.arguments

            # If no tool calls, we are done with this turn
            if not tool_calls:
                self.history.append({"role": "user", "content": user_input})
                self.history.append({"role": "assistant", "content": full_content})
                return

            # Prepare assistant message with tool calls for history
            assistant_msg = {
                "role": "assistant",
                "content": full_content,
                "tool_calls": tool_calls
            }
            messages.append(assistant_msg)

            # Execute tools
            for tc in tool_calls:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except Exception:
                    args = {}

                yield {"type": "tool_start", "name": name, "args": args}
                
                if name in TOOL_MAP:
                    try:
                        result = TOOL_MAP[name](**args)
                    except Exception as e:
                        result = f"Error executing tool: {str(e)}"
                else:
                    result = f"Error: Tool '{name}' tidak dikenal."

                result_str = self._truncate_tool_result(str(result))
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result_str
                }
                messages.append(tool_msg)
                yield {"type": "tool_end", "name": name, "result": result_str}
