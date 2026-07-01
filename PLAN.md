# Plan Migrasi & Refactor: hanif-finance (Cross-Platform)

## Goal
Memindahkan script CLI `hanif-finance` yang sebelumnya hardcoded untuk environment Linux/Kali agar 100% kompatibel dan bisa dijalankan di **Windows** maupun **Linux**, dengan packaging standard (`pyproject.toml`) sehingga mudah diinstall secara global via `pip install -e .` atau `uv tool install`.

## Architecture & Tech Stack
- **Language**: Python 3.10+ (Standard library hanya: `sqlite3`, `json`, `argparse`, `os`, `pathlib`, `sys`, `datetime`).
- **Database**: SQLite3 (`hermes_data.db`).
- **Path Dynamic Resolution**: 
  - Linux: `~/Documents/ObsidianVault/hanif/09 - Hermes/hermes_data.db`
  - Windows: `C:\Users\<user>\Documents\ObsidianVault\hanif\09 - Hermes\hermes_data.db`
  - Override via Env Var: `HANIF_FINANCE_DB_PATH` atau `OBSIDIAN_VAULT_DIR`.
- **Packaging**: `pyproject.toml` dengan `[project.scripts]` entry point `hanif-finance = "hanif_finance.cli:main"`.

## Task Breakdown

### Task 1: Inisialisasi Struktur Project & Repository
- **Target**: Setup struktur folder standard Python CLI project.
- **Files**:
  - `README.md`: Panduan instalasi dan penggunaan untuk orang awam (Windows & Linux).
  - `AGENTS.md`: Panduan dan konteks untuk AI Agent yang akan mengelola atau memodifikasi repo ini di masa depan.
  - `.gitignore`: Mengabaikan file database lokal, venv, dan build artifacts.
  - `pyproject.toml`: Konfigurasi metadata project dan entry point CLI `hanif-finance`.

### Task 2: Refactor Script CLI ke Modular Package (`hanif_finance`)
- **Target**: Memindahkan `/home/brooky/.hermes/skills/productivity/hanif-finance-cli/scripts/finance.py` ke dalam package struktur project dengan resolusi path dinamis.
- **Files**:
  - `hanif_finance/__init__.py`: Versioning.
  - `hanif_finance/db.py`: Modul koneksi database, inisialisasi tabel, dan resolusi path cross-platform (menggunakan `pathlib.Path.home()` dan cek environment variables).
  - `hanif_finance/cli.py`: Modul `argparse` dan eksekusi perintah (balance, list, dump, add, edit, delete).

### Task 3: Verifikasi & Test Lokal
- **Target**: Memastikan CLI berfungsi dengan baik tanpa merusak database SQLite yang sudah ada di Obsidian Vault Hanif.
- **Commands**:
  - `python3 -m hanif_finance.cli balance`
  - `python3 -m hanif_finance.cli list --limit 5`

### Task 4: Push ke GitHub
- **Target**: Menghubungkan repo lokal ke `https://github.com/hanifsetyananda/hanif-finance`.
- **Commands**:
  - `gh repo create hanifsetyananda/hanif-finance --public --source=. --remote=origin --push` (atau via git remote add manual bila repo sudah ada).

## Pitfalls & Edge Cases
- **Symlink Dependency**: Jangan gunakan symlink (`ln -s`) dalam dokumentasi karena gagal di Windows tanpa Administrator right. Gunakan entry point `pyproject.toml` (otomatis menghasilkan `.exe` wrapper di Windows Script folder saat diinstall via pip/uv).
- **SQLite Wal Mode**: Pastikan koneksi menutup dengan bersih (`conn.close()`) agar file `.wal` dan `.shm` tidak mengunci database saat diakses dari Obsidian di Windows.
