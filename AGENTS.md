# AGENTS.md — Hanif Finance CLI (Cross-Platform)

## Project Context
`hanif-finance` adalah CLI tool berbasis Python standard library yang digunakan untuk mencatat dan memantau transaksi keuangan pribadi Hanif ke dalam database SQLite (`hermes_data.db`). Database ini berada di dalam Obsidian Vault Hanif (`09 - Hermes/hermes_data.db`) dan menjadi single source of truth untuk monitoring keuangan baik oleh manusia maupun AI Agent (Hermes).

Project ini di-refactor agar **100% Cross-Platform (Windows & Linux)** sehingga dapat berjalan lancar ketika Hanif berpindah device kerja ke Windows tanpa ketergantungan pada symlink bash (`ln -sf`).

## Architecture & Conventions
- **Zero Third-Party Dependencies**: Gunakan HANYA standard library Python (`sqlite3`, `json`, `argparse`, `os`, `pathlib`, `sys`, `datetime`). Jangan tambahkan ORM (SQLAlchemy, Peewee) atau CLI library eksternal (Click, Typer, Rich).
- **Dynamic Path Resolution**:
  - Secara default, path database dicari di `~/Documents/ObsidianVault/hanif/09 - Hermes/hermes_data.db` (menggunakan `pathlib.Path.home()`).
  - Harus mendukung override via Environment Variable:
    1. `HANIF_FINANCE_DB_PATH`: Langsung menunjuk ke file `.db`.
    2. `OBSIDIAN_VAULT_DIR`: Menunjuk ke root folder vault, lalu append `/09 - Hermes/hermes_data.db`.
- **Packaging**: Gunakan `pyproject.toml` dengan entry point `hanif-finance = "hanif_finance.cli:main"`. Ketika diinstall via `pip install -e .` atau `uv tool install`, Windows akan otomatis membuat wrapper executable (`hanif-finance.exe`) di folder Scripts/bin.

## Database Schema (`hermes_data.db`)
- Tabel `finance_accounts`: `(id, name, balance, last_updated)`
- Tabel `finance_transactions`: `(id, date, description, category, account_id, amount_in, amount_out, balance_after)`
- **WARNING**: Jangan ubah nama kolom atau struktur tabel tanpa migrasi, karena Hermes Agent secara otomatis melakukan query ke SQLite ini saat sesi Daily Standup.

## Rules for AI Agents Working in this Repo
1. **No Redundant Scripts**: Jangan pernah membuat script Python sekali pakai (`execute_code`) untuk mencatat atau membaca transaksi. Selalu gunakan CLI ini (`hanif-finance ...` atau `python -m hanif_finance.cli ...`).
2. **Output Formats**:
   - `list` & `balance`: Harus human-readable (tabel sederhana, tanpa jam/detik pada tanggal, total info di bagian **bawah**).
   - `dump`: Harus machine-readable (JSON array mentah dengan timestamp lengkap dan `balance_after`) untuk diparsing oleh AI.
3. **No Backdating Flag**: CLI ini sengaja tidak memiliki flag `--date`. Transaksi selalu dicatat pada waktu real-time (`now()`). Jika mencatat transaksi masa lalu, tulis tanggal eksplisit di awal parameter `--desc` (contoh: `--desc "18 Juni: Beli nasgor"`).
4. **Account Names**: Gunakan Exact Name String case-insensitive saat query (contoh: `"Cash"`, `"BCA"`). Jangan gunakan ID integer untuk filter akun.
