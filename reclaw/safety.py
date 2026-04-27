import os
from .config import DANGEROUS_PATTERNS

# Direktori yang sebaiknya dihindari (relatif terhadap root sistem)
SENSITIVE_PATHS = ["/etc", "/usr/bin", "/bin", "/sbin", "/sys", "/dev", "C:\\Windows"]

def is_safe_path(path: str):
    """Cek apakah path aman untuk diakses oleh agent."""
    abs_path = os.path.abspath(path)
    # Cek path sistem sensitif
    for sp in SENSITIVE_PATHS:
        if abs_path.startswith(os.path.abspath(sp)):
            return False, f"Akses ke sistem path '{sp}' diblokir demi keamanan."
    return True, "ok"

def is_safe_command(command: str):
    """Cek apakah shell command mengandung pola berbahaya."""
    lowered = command.lower().strip()
    for pattern in DANGEROUS_PATTERNS:
        # Simple substring check (case insensitive)
        if pattern.lower() in lowered:
            return False, f"Command mengandung pola berbahaya '{pattern}'"
    return True, "ok"
