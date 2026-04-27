# ReClaw

**ReClaw** adalah AI Agentic Coding Assistant yang ringan, hemat token, dan aman. Terinspirasi dari OpenClaw, ReClaw dirancang untuk membantu developer mengedit script, menjalankan command shell, dan menavigasi proyek secara interaktif langsung dari terminal.

## Fitur Utama

- **Hemat Token**: Riwayat percakapan dibatasi hanya 6 turn terakhir. Output tool dipotong otomatis agar tidak boros.
- **Edit Parsial**: Gunakan `edit_file` (old_string → new_string) untuk mengubah kode tanpa menulis ulang seluruh file.
- **Aman**: Command shell berbahaya seperti `rm -rf /`, `sudo`, `curl | sh`, dll diblokir otomatis.
- **Model Canggih**: Menggunakan `moonshotai/kimi-k2-instruct` via NVIDIA API.
- **CLI Interaktif**: Antarmuka terminal yang bersih dan berwarna menggunakan Rich.

## Tools yang Tersedia

| Tool | Fungsi |
|------|--------|
| `read_file` | Baca isi file (default 30 baris) |
| `write_file` | Buat/timpa file baru |
| `edit_file` | Edit parsial file (hemat token) |
| `run_shell` | Jalankan command shell (dengan filter keamanan) |
| `list_directory` | Lihat isi direktori |
| `search_files` | Cari teks di file-file proyek |

## Instalasi

1. **Clone / Download** folder ReClaw.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Atur API Key**:
   ```bash
   export RECLAW_API_KEY="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"
   ```
   Atau salin `.env.example` ke `.env` dan paste key di situ.

## Cara Menjalankan

```bash
python main.py
```

## Contoh Penggunaan

```
Anda > buatkan file hello.py yang mencetak "Halo dari ReClaw"
```

ReClaw akan langsung membuat file tanpa perlu kamu copy-paste kode.

```
Anda > tambahkan fungsi tambah(a,b) di hello.py
```

ReClaw akan membaca file, lalu menggunakan `edit_file` untuk menambahkan fungsi.

```
Anda > jalankan file hello.py
```

ReClaw akan mengeksekusi `python hello.py` dan menampilkan outputnya.

## Keamanan

- Akses ke path sistem seperti `/etc`, `/bin`, dll diblokir.
- Shell command yang mengandung pola berbahaya akan ditolak.
- ReClaw berjalan di direktori kerja saat ini (cwd) dan tidak bisa menyentuh file di luar tanpa izin.

## Catatan

- **Hemat Token**: Jika bekerja dengan file besar, ReClaw hanya membaca 30 baris pertama secara default. Kamu bisa meminta membaca bagian tertentu.
- **Bahasa**: ReClaw secara otomatis merespons dalam bahasa Indonesia karena system prompt diatur demikian.

---

Selamat ngoding! 🚀
