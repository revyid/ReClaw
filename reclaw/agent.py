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
        """Jalankan satu turn interaksi. Yield string untuk ditampilkan ke user."""
        # Bangun messages untuk API: system + riwayat lama + user_input baru
        messages = [self.system_message]
        messages.extend(list(self.history))
        messages.append({"role": "user", "content": user_input})

        iteration = 0
        final_answer = None

        while iteration < MAX_ITERATIONS:
            iteration += 1
            msg = self.llm.chat(messages, tools=TOOL_DEFINITIONS, tool_choice="auto")

            # Jika API error dalam bentuk dict
            if isinstance(msg, dict):
                final_answer = f"[Error] {msg['content']}"
                break

            # Jika tidak ada tool call -> jawaban langsung
            if not msg.tool_calls:
                final_answer = msg.content or "(tidak ada respons)"
                break

            # Ada tool calls: tambahkan ke messages untuk iterasi berikutnya
            assistant_msg = {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    }
                    for tc in msg.tool_calls
                ]
            }
            messages.append(assistant_msg)

            # Eksekusi setiap tool
            for tc in msg.tool_calls:
                name = tc.function.name
                import json
                try:
                    args = json.loads(tc.function.arguments)
                except Exception:
                    args = {}

                if name in TOOL_MAP:
                    result = TOOL_MAP[name](**args)
                else:
                    result = f"Error: Tool '{name}' tidak dikenal."

                result = self._truncate_tool_result(str(result))
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                }
                messages.append(tool_msg)
                yield f"[Tool] {name} -> {result[:120]}..."

        # Simpan ringkasan turn ke history setelah selesai
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": final_answer})
        yield final_answer
