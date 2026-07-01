# AGENTS.md — Hanif Finance CLI (Cross-Platform)

## Project Context
`hanif-finance` adalah CLI tool berbasis Python standard library yang digunakan untuk mencatat dan memantau transaksi keuangan pribadi Hanif ke dalam database SQLite (`hermes_data.db`). Database ini berada di dalam Obsidian Vault Hanif (`09 - Hermes/hermes_data.db`) dan menjadi single source of truth untuk monitoring keuangan baik oleh manusia maupun AI Agent (Hermes).

Project ini di-refactor agar **100% Cross-Platform (Windows & Linux)** sehingga dapat berjalan lancar ketika Hanif berpindah device kerja ke Windows tanpa ketergantungan pada symlink bash (`ln -sf`).

## Available CLI Commands & Usage Syntax
AI Agent WAJIB memanggil aplikasi lewat terminal menggunakan perintah `hanif-finance <subcommand> [args]` atau `python3 -m hanif_finance.cli <subcommand> [args]`.

### 1. Check Balances
Menampilkan saldo saat ini dari setiap akun:
```bash
hanif-finance balance
```

### 2. List Transactions (Human-Readable)
Menampilkan daftar transaksi terbaru dalam format tabel untuk ditampilkan ke user:
```bash
hanif-finance list --limit 10
# Filter berdasarkan akun tertentu (Gunakan Exact Name persis seperti di database, contoh: "Bank BCA"):
hanif-finance list --account "Cash" --limit 5
```

### 3. Dump Transactions (Machine-Readable / JSON)
Menampilkan riwayat transaksi dalam format mentah JSON (termasuk timestamp lengkap & `balance_after`). Gunakan perintah ini jika AI perlu melakukan parsing, agregasi, atau perhitungan background:
```bash
hanif-finance dump --limit 100
```

### 4. Add Transaction
Mencatat transaksi baru. **Semua argument wajib diisi** (tidak mendukung short arguments seperti `-a`, `-t`):
```bash
# Pemasukan (in)
hanif-finance add --account "Bank BCA" --type in --amount 5000000 --category "Gaji" --desc "Bayaran project website"

# Pengeluaran (out)
hanif-finance add --account "Cash" --type out --amount 15000 --category "Makanan" --desc "Beli nasi goreng"
```
*Catatan:* Argument `--type` hanya menerima `in` atau `out` (bukan MASUK/KELUAR). Tidak ada argument `--date`; transaksi otomatis memakai waktu sekarang. Untuk tanggal masa lalu, tulis di dalam deskripsi: `--desc "18 Juni: Beli nasgor"`.

### 5. Edit Transaction
Mengedit transaksi berdasarkan ID (otomatis menyesuaikan kalkulasi saldo akun yang bersangkutan):
```bash
hanif-finance edit --id 12 --amount 20000 --desc "Beli nasgor + sate" --category "Makanan"
```

### 6. Delete Transaction
Menghapus transaksi berdasarkan ID (nominal uang otomatis dikembalikan ke saldo akun):
```bash
hanif-finance delete --id 12
```

### 7. Standalone Executable (.exe / Binary Build)
Untuk mendistribusikan aplikasi tanpa mengharuskan user menginstall Python, compile menjadi file binary standalone menggunakan PyInstaller:
```bash
pip install -e .[build]
python build_exe.py
```
Binary akan dihasilkan di `dist/hanif-finance` (atau `dist/hanif-finance.exe` di Windows).

## Architecture & Conventions
- **Zero Third-Party Dependencies for Core**: Gunakan HANYA standard library Python untuk core runtime (`sqlite3`, `json`, `argparse`, `os`, `pathlib`, `sys`, `datetime`). PyInstaller hanya dijadikan optional dependency untuk proses build release.
- **Dynamic Path Resolution**:
  - Secara otomatis mendeteksi environment:
    1. Override via `HANIF_FINANCE_DB_PATH` atau `OBSIDIAN_VAULT_DIR`.
    2. Jika folder Obsidian Vault Hanif ada (`~/Documents/ObsidianVault/...`), gunakan `hermes_data.db`.
    3. **Fallback Open Source**: Jika tidak di environment Hanif, otomatis buat dan simpan database di `~/.hanif-finance/data.db` (Windows/Linux/Mac).
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
