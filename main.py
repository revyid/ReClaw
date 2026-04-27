import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Pastikan env key tersedia
if not os.getenv("RECLAW_API_KEY"):
    print("[PERINGATAN] RECLAW_API_KEY belum di-set. Export dulu:")
    print("  export RECLAW_API_KEY='nvapi-...'")
    print("Atau buat file .env di folder ini.")
    sys.exit(1)

from reclaw.agent import ReClawAgent
from reclaw.ui import print_welcome, print_error, get_input, StreamingDisplay

def main():
    print_welcome()
    agent = ReClawAgent()

    while True:
        try:
            user_text = get_input()
        except (EOFError, KeyboardInterrupt):
            print("\nSampai jumpa!")
            break

        if user_text.strip().lower() in ("exit", "quit", "keluar"):
            print("\nReClaw dimatikan.")
            break

        if not user_text.strip():
            continue

        try:
            with StreamingDisplay() as display:
                for event in agent.run(user_text):
                    if event["type"] == "content":
                        display.update_content(event["delta"])
                    elif event["type"] == "tool_start":
                        display.show_tool_start(event["name"], event["args"])
                    elif event["type"] == "tool_end":
                        display.show_tool_end(event["name"], event["result"])
                    elif event["type"] == "error":
                        print_error(event["content"])
        except Exception as e:
            print_error(str(e))

if __name__ == "__main__":
    main()
