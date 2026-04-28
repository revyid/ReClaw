import json
import time
import asyncio
from collections import deque
from .llm import LLMClient
from .tools import TOOL_DEFINITIONS, TOOL_MAP
from .config import MAX_HISTORY_TURNS, MAX_ITERATIONS, MAX_TOOL_OUTPUT

# Enhanced System Prompt for Auto-Solver and Proactive Fixing
SYSTEM_PROMPT = """Kamu adalah ReClaw Pro v3.7.
Tugas: Coding assistant agentic, efisien, aman, dan proaktif.

PRINSIP KERJA:
1. AUTO-SOLVER: Jika run_shell menghasilkan error, kamu WAJIB menganalisis log tersebut dan langsung mencoba memperbaikinya (Auto-Fix) menggunakan tool yang sesuai.
2. TRANSPARANSI: Gunakan tools langsung. Jangan banyak bicara sebelum eksekusi.
3. EFISIENSI: Gunakan edit_file untuk perubahan kecil. Jangan ulangi kode yang sudah ada.
4. KONTEKS: Selalu cek isi file atau direktori jika ragu.

Bahasa: Indonesia (default)."""

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
        messages = [self.system_message]
        messages.extend(list(self.history))
        messages.append({"role": "user", "content": user_input})

        iteration = 0
        while iteration < MAX_ITERATIONS:
            iteration += 1
            
            max_retries = 3
            retry_count = 0
            stream = None
            
            while retry_count < max_retries:
                try:
                    stream = self.llm.chat(messages, tools=TOOL_DEFINITIONS, tool_choice="auto", stream=True)
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        yield {"type": "error", "content": f"Connection failed: {str(e)}"}
                        return
                    time.sleep(1)
            
            full_content = ""
            tool_calls = []
            
            try:
                for chunk in stream:
                    if isinstance(chunk, dict) and "error" in chunk:
                        yield {"type": "error", "content": f"API Error: {chunk['error']}"}
                        return
                        
                    if hasattr(chunk, 'choices') and chunk.choices:
                        delta = chunk.choices[0].delta
                        if delta.content:
                            full_content += delta.content
                            yield {"type": "content", "delta": delta.content}
                        
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
            except Exception as e:
                yield {"type": "error", "content": f"Stream interrupted: {str(e)}"}
                return

            if not tool_calls:
                self.history.append({"role": "user", "content": user_input})
                self.history.append({"role": "assistant", "content": full_content})
                return

            assistant_msg = {"role": "assistant", "content": full_content, "tool_calls": tool_calls}
            messages.append(assistant_msg)

            for tc in tool_calls:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except:
                    args = {}

                yield {"type": "tool_start", "name": name, "args": args}
                
                if name in TOOL_MAP:
                    try:
                        result = TOOL_MAP[name](**args)
                    except Exception as e:
                        result = f"Error: {str(e)}"
                else:
                    result = f"Error: Unknown tool '{name}'"

                result_str = self._truncate_tool_result(str(result))
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result_str})
                yield {"type": "tool_end", "name": name, "result": result_str}
