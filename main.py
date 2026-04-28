import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Pastikan env key tersedia
if not os.getenv("RECLAW_API_KEY"):
    print("[PERINGATAN] RECLAW_API_KEY belum di-set. Export dulu:")
    print("  export RECLAW_API_KEY='nvapi-...'")
    print("Atau buat file .env di folder ini.")
    sys.exit(1)

from reclaw.agent import ReClawAgent
from reclaw.ui import ui

async def run_app():
    ui.print_welcome()
    agent = ReClawAgent()
    
    try:
        while True:
            ui.set_status("Idle")
            user_text = await ui.get_input_async()

            if user_text.strip().lower() in ("exit", "quit", "keluar"):
                print("\nSampai jumpa!")
                break

            if not user_text.strip():
                continue

            ui.print_user_message(user_text)
            
            try:
                ui.set_status("Thinking...")
                full_response = ""
                
                for event in agent.run(user_text):
                    if event["type"] == "content":
                        ui.set_status("Streaming...")
                        full_response += event["delta"]
                        await ui.stream_content(event["delta"])
                    elif event["type"] == "tool_start":
                        ui.set_status("Executing Tool...")
                        ui.show_tool_start(event["name"], event["args"])
                    elif event["type"] == "tool_end":
                        ui.show_tool_end(event["name"], event["result"])
                    elif event["type"] == "error":
                        ui.set_status("Error")
                        ui.print_error(event["content"])
                
                if full_response:
                    ui.finalize_content(full_response)
                
            except Exception as e:
                ui.set_status("Error")
                ui.print_error(str(e))
    except KeyboardInterrupt:
        print("\nSampai jumpa!")

if __name__ == "__main__":
    try:
        asyncio.run(run_app())
    except KeyboardInterrupt:
        pass
