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

# --- TOOL DEFINITIONS (OpenAI format) ---
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Baca konten file teks. Gunakan limit untuk file besar. Returns konten atau error.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relatif/absolut file"},
                    "limit": {"type": "integer", "description": "Maksimal baris yang dibaca (default 30)", "default": 30}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Tulis atau timpa file dengan konten baru. Hati-hati akan overwrite.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path file target"},
                    "content": {"type": "string", "description": "Konten lengkap file"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit parsial file: cari old_string dan ganti dengan new_string. Lebih hemat token dari write_file utuh.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_string": {"type": "string", "description": "Teks yang akan dicari dan diganti (harus exact match, termasuk whitespace)"},
                    "new_string": {"type": "string", "description": "Teks pengganti"}
                },
                "required": ["path", "old_string", "new_string"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Jalankan perintah shell. Hanya untuk command aman. Output terbatas 800 chars.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command shell"},
                    "timeout": {"type": "integer", "description": "Timeout detik", "default": 30}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List file dan folder di direktori. Defaults ke direktori kerja.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path direktori", "default": "."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Cari teks di semua file dalam direktori (recursive) menggunakan glob pattern sederhana.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Teks yang dicari"},
                    "path": {"type": "string", "description": "Direktori mulai", "default": "."},
                    "file_pattern": {"type": "string", "description": "Glob pattern file, misal *.py", "default": "*"}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Hapus file. Gunakan dengan hati-hati.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path file yang akan dihapus"}
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
                    "path": {"type": "string", "description": "Path direktori baru"}
                },
                "required": ["path"]
            }
        }
    }
]

# --- TOOL IMPLEMENTATIONS ---

def tool_read_file(path: str, limit: int = MAX_FILE_PREVIEW):
    safe, msg = is_safe_path(path)
    if not safe:
        return f"Error (safety): {msg}"
    if not os.path.exists(path):
        return f"Error: File tidak ditemukan: {path}"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        total = len(lines)
        if limit and total > limit:
            head = lines[:limit]
            content = "".join(head)
            return f"[Baris 1-{limit} dari {total}]\n{content}"
        return "".join(lines)
    except Exception as e:
        return f"Error membaca file: {e}"

def tool_write_file(path: str, content: str):
    safe, msg = is_safe_path(path)
    if not safe:
        return f"Error (safety): {msg}"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Sukses menulis file: {path} ({len(content)} chars)"
    except Exception as e:
        return f"Error menulis file: {e}"

def tool_edit_file(path: str, old_string: str, new_string: str):
    safe, msg = is_safe_path(path)
    if not safe:
        return f"Error (safety): {msg}"
    if not os.path.exists(path):
        return f"Error: File tidak ditemukan: {path}"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if old_string not in content:
            return f"Error: old_string tidak ditemukan di {path}. Pastikan exact match termasuk whitespace."
        content = content.replace(old_string, new_string, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Sukses edit file: {path}"
    except Exception as e:
        return f"Error edit file: {e}"

def tool_run_shell(command: str, timeout: int = 30):
    safe, msg = is_safe_command(command)
    if not safe:
        return f"BLOCKED (safety): {msg}. Gunakan command alternatif atau jalankan manual."
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=os.getcwd()
        )
        output = f"[exit {result.returncode}]\n{result.stdout}"
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return _truncate(output)
    except subprocess.TimeoutExpired:
        return f"Error: Command timeout ({timeout}s)."
    except Exception as e:
        return f"Error shell: {e}"

def tool_list_directory(path: str = "."):
    safe, msg = is_safe_path(path)
    if not safe:
        return f"Error (safety): {msg}"
    try:
        entries = os.listdir(path)
        lines = []
        for e in sorted(entries):
            full = os.path.join(path, e)
            kind = "DIR" if os.path.isdir(full) else "FILE"
            size = ""
            if kind == "FILE":
                size = f" ({os.path.getsize(full)}b)"
            lines.append(f"[{kind}] {e}{size}")
        return "\n".join(lines) if lines else "(direktori kosong)"
    except Exception as e:
        return f"Error list direktori: {e}"

def tool_search_files(pattern: str, path: str = ".", file_pattern: str = "*"):
    safe, msg = is_safe_path(path)
    if not safe:
        return f"Error (safety): {msg}"
    try:
        matches = []
        search_path = os.path.join(path, "**", file_pattern)
        for filepath in glob.glob(search_path, recursive=True):
            if os.path.isfile(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if pattern in line:
                                matches.append(f"{filepath}:{i}: {line.strip()}")
                                if len(matches) >= 20:
                                    break
                        if len(matches) >= 20:
                            break
                except Exception:
                    continue
        if not matches:
            return f"Tidak ditemukan: '{pattern}'"
        return _truncate("\n".join(matches), limit=MAX_TOOL_OUTPUT)
    except Exception as e:
        return f"Error search: {e}"

def tool_delete_file(path: str):
    safe, msg = is_safe_path(path)
    if not safe:
        return f"Error (safety): {msg}"
    try:
        if os.path.exists(path):
            os.remove(path)
            return f"Sukses menghapus file: {path}"
        return f"Error: File tidak ditemukan: {path}"
    except Exception as e:
        return f"Error menghapus file: {e}"

def tool_create_directory(path: str):
    safe, msg = is_safe_path(path)
    if not safe:
        return f"Error (safety): {msg}"
    try:
        os.makedirs(path, exist_ok=True)
        return f"Sukses membuat direktori: {path}"
    except Exception as e:
        return f"Error membuat direktori: {e}"

# Mapping name -> function
TOOL_MAP = {
    "read_file": tool_read_file,
    "write_file": tool_write_file,
    "edit_file": tool_edit_file,
    "run_shell": tool_run_shell,
    "list_directory": tool_list_directory,
    "search_files": tool_search_files,
    "delete_file": tool_delete_file,
    "create_directory": tool_create_directory,
}
