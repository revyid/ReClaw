import os
import subprocess
import glob
from .config import MAX_FILE_PREVIEW, MAX_TOOL_OUTPUT
from .safety import is_safe_path, is_safe_command

def _truncate(text, limit=MAX_TOOL_OUTPUT):
    """Potong output agar tidak boros token."""
    if len(text) > limit:
        half = limit // 2
        return text[:half] + f"\n... [{len(text)} chars truncated] ...\n" + text[-half:]
    return text

# --- TOOL DEFINITIONS ---
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Baca konten file teks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "limit": {"type": "integer", "default": 30}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_file",
            "description": "Lihat file dengan format yang lebih baik (line numbers).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Tulis atau timpa file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit parsial file (old_string -> new_string).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_string": {"type": "string"},
                    "new_string": {"type": "string"}
                },
                "required": ["path", "old_string", "new_string"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Jalankan perintah shell.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {"type": "integer", "default": 30}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List file dan folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": "."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Hapus file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Buat direktori baru.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    }
]

# --- TOOL IMPLEMENTATIONS ---

def tool_read_file(path: str, limit: int = MAX_FILE_PREVIEW):
    safe, msg = is_safe_path(path)
    if not safe: return f"Error: {msg}"
    if not os.path.exists(path): return f"Error: File not found: {path}"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        if limit and len(lines) > limit:
            return "".join(lines[:limit]) + f"\n... [truncated {len(lines)-limit} lines]"
        return "".join(lines)
    except Exception as e: return f"Error: {e}"

def tool_view_file(path: str):
    safe, msg = is_safe_path(path)
    if not safe: return f"Error: {msg}"
    if not os.path.exists(path): return f"Error: File not found: {path}"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        output = []
        for i, line in enumerate(lines, 1):
            output.append(f"{i:4} | {line.rstrip()}")
        return "\n".join(output[:100]) # Limit to 100 lines for view
    except Exception as e: return f"Error: {e}"

def tool_write_file(path: str, content: str):
    safe, msg = is_safe_path(path)
    if not safe: return f"Error: {msg}"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: Written to {path}"
    except Exception as e: return f"Error: {e}"

def tool_edit_file(path: str, old_string: str, new_string: str):
    safe, msg = is_safe_path(path)
    if not safe: return f"Error: {msg}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if old_string not in content: return "Error: old_string not found."
        new_content = content.replace(old_string, new_string, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return f"Success: Edited {path}"
    except Exception as e: return f"Error: {e}"

def tool_run_shell(command: str, timeout: int = 30):
    safe, msg = is_safe_command(command)
    if not safe: return f"Blocked: {msg}"
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        output = f"[exit {result.returncode}]\n{result.stdout}"
        if result.stderr: output += f"\n[stderr]\n{result.stderr}"
        return _truncate(output)
    except Exception as e: return f"Error: {e}"

def tool_list_directory(path: str = "."):
    safe, msg = is_safe_path(path)
    if not safe: return f"Error: {msg}"
    try:
        entries = os.listdir(path)
        return "\n".join([f"[{'DIR' if os.path.isdir(os.path.join(path, e)) else 'FILE'}] {e}" for e in sorted(entries)])
    except Exception as e: return f"Error: {e}"

def tool_delete_file(path: str):
    safe, msg = is_safe_path(path)
    if not safe: return f"Error: {msg}"
    try:
        if os.path.exists(path):
            os.remove(path)
            return f"Success: Deleted {path}"
        return "Error: File not found."
    except Exception as e: return f"Error: {e}"

def tool_create_directory(path: str):
    safe, msg = is_safe_path(path)
    if not safe: return f"Error: {msg}"
    try:
        os.makedirs(path, exist_ok=True)
        return f"Success: Created directory {path}"
    except Exception as e: return f"Error: {e}"

TOOL_MAP = {
    "read_file": tool_read_file,
    "view_file": tool_view_file,
    "write_file": tool_write_file,
    "edit_file": tool_edit_file,
    "run_shell": tool_run_shell,
    "list_directory": tool_list_directory,
    "delete_file": tool_delete_file,
    "create_directory": tool_create_directory,
}
