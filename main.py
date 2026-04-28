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
from reclaw.ui import print_welcome, ui

async def background_maintenance():
    """Task to keep the UI refreshed and repaired."""
    while True:
        ui.update_display()
        if ui.live:
            ui.live.refresh()
        await asyncio.sleep(1.0)

async def run_app():
    print_welcome()
    await asyncio.sleep(1.0)
    
    agent = ReClawAgent()
    ui.start()
    
    # Start background maintenance
    maintenance_task = asyncio.create_task(background_maintenance())
    
    try:
        while True:
            ui.set_status("Idle")
            user_text = await ui.get_input_async()

            if user_text.strip().lower() in ("exit", "quit", "keluar"):
                break

            if not user_text.strip():
                continue

            ui.add_user_message(user_text)
            
            try:
                ui.set_status("Thinking...")
                for event in agent.run(user_text):
                    if event["type"] == "content":
                        ui.set_status("Streaming...")
                        await ui.stream_content(event["delta"])
                    elif event["type"] == "tool_start":
                        ui.set_status("Executing Tool...")
                        ui.set_tool(event["name"])
                    elif event["type"] == "tool_end":
                        ui.set_tool(None)
                    elif event["type"] == "error":
                        ui.set_status("Error")
                        await ui.stream_content(f"\n\n[bold red]![/bold red] {event['content']}\n")
                
                ui.finalize_content()
            except Exception as e:
                ui.set_status("Error")
                await ui.stream_content(f"\n\n[bold red]SYSTEM ERROR:[/bold red] {str(e)}\n")
                ui.finalize_content()
    finally:
        maintenance_task.cancel()
        ui.stop()
        print("\nSampai jumpa!")

if __name__ == "__main__":
    try:
        asyncio.run(run_app())
    except KeyboardInterrupt:
        pass
