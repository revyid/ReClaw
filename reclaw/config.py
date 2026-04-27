from dotenv import load_dotenv
import os

load_dotenv()

# NVIDIA API Configuration
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_API_KEY = os.getenv("RECLAW_API_KEY", "")
MODEL_NAME = "moonshotai/kimi-k2-instruct"

# Token & Context Management (Hemat Token)
MAX_HISTORY_TURNS = 6       # Hanya simpan 6 turn terakhir
MAX_TOOL_OUTPUT = 800       # Karakter maksimal output tool ke LLM
MAX_FILE_PREVIEW = 30       # Baris maksimal baca file
MAX_ITERATIONS = 15         # Maksimal loop agent per tugas

# Safety
DANGEROUS_PATTERNS = [
    "rm -rf /", "sudo ", "chmod -R 777 /", "mkfs", "dd if=", 
    ":(){ :|:& };:", "> /dev/sda", "curl .*|.*sh", "wget .*|.*sh",
    "del /f /s /q", "rd /s /q", "format ", "diskpart"
]

# UI
AGENT_NAME = "ReClaw"
