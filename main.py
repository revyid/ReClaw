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
from reclaw.ui import print_welcome, print_response, print_error, get_input

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
            from reclaw.ui import StatusManager
            with StatusManager("Processing..."):
                # We consume the generator here
                # In a real streaming UI we might update the Live display
                # But for now we'll print tool calls as they happen
                chunks = list(agent.run(user_text))
            
            for chunk in chunks:
                print_response(chunk)
        except Exception as e:
            print_error(str(e))

if __name__ == "__main__":
    main()
