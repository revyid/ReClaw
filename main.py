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
from reclaw.ui import print_welcome, print_error, get_input, ui

def main():
    print_welcome()
    agent = ReClawAgent()

    while True:
        user_text = get_input()

        if user_text.strip().lower() in ("exit", "quit", "keluar"):
            print("\nSampai jumpa!")
            break

        if not user_text.strip():
            continue

        ui.add_user_message(user_text)
        
        try:
            with ui:
                ui.set_status("Thinking...")
                for event in agent.run(user_text):
                    if event["type"] == "content":
                        ui.set_status("Streaming...")
                        ui.update_content(event["delta"])
                    elif event["type"] == "tool_start":
                        ui.set_status("Executing Tool...")
                        ui.set_tool(event["name"])
                    elif event["type"] == "tool_end":
                        ui.set_tool(None)
                    elif event["type"] == "error":
                        ui.set_status("Error")
                        # We'll show errors in the chat area for now
                        ui.update_content(f"\n\n[bold red]![/bold red] {event['content']}\n")
                
                ui.finalize_content()
                ui.set_status("Idle")
        except Exception as e:
            print_error(str(e))

if __name__ == "__main__":
    main()
