# Hanif Finance CLI 💰

Asisten CLI sederhana dan super cepat untuk mencatat pemasukan, pengeluaran, serta memantau saldo keuangan pribadi langsung ke dalam database SQLite di Obsidian Vault. Dirancang agar **100% kompatibel di Windows, Linux, dan macOS** tanpa dependensi pihak ketiga.

## ✨ Fitur Utama
- **Cross-Platform**: Berjalan lancar di Windows (PowerShell/CMD), Linux, dan macOS.
- **Zero Dependencies**: Hanya menggunakan Python Standard Library (tidak butuh `pip install library_lain`).
- **Obsidian Integrated**: Otomatis menyimpan dan membaca data dari SQLite di dalam Obsidian Vault (`09 - Hermes/hermes_data.db`).
- **Human & Machine Friendly**: Menampilkan tabel rapi untuk manusia, dan format JSON untuk integrasi dengan AI (Hermes Agent).

---

## 🚀 Panduan Instalasi (Untuk Orang Awam)

### 1. Prasyarat
Pastikan komputer kamu sudah terinstall **Python 3.10** atau lebih baru.
- Cek dengan membuka Terminal (Linux/macOS) atau Command Prompt/PowerShell (Windows) lalu ketik:
  ```bash
  python --version
  ```

### 2. Cara Install
Download atau clone repository ini, lalu buka terminal di dalam folder project ini dan jalankan perintah berikut:

#### Di Windows (Command Prompt / PowerShell):
```cmd
pip install -e .
```
*(Atau jika menggunakan `uv`: `uv tool install .`)*

#### Di Linux / macOS:
```bash
pip install -e .
```

Setelah selesai, perintah `hanif-finance` sekarang bisa langsung diketik dari folder mana saja di komputer kamu!

---

## 📖 Cara Penggunaan

### 🔍 Melihat Saldo & Riwayat Transaksi

#### 1. Cek Saldo Semua Akun
Menampilkan saldo terkini untuk akun seperti Cash, BCA, DANA, dll.
```bash
hanif-finance balance
```

#### 2. Lihat Riwayat Transaksi Terakhir
Menampilkan 10 transaksi terakhir dalam bentuk tabel rapi:
```bash
hanif-finance list --limit 10
```
*(Bisa juga difilter per akun, misal: `hanif-finance list --account "Cash"`)*

---

### 📝 Mencatat Transaksi Baru

#### 1. Pengeluaran (Uang Keluar)
Gunakan `--type out`. Semua parameter wajib diisi:
```bash
hanif-finance add --account "Cash" --type out --amount 15000 --category "Makanan" --desc "Beli nasi goreng"
```

#### 2. Pemasukan (Uang Masuk)
Gunakan `--type in`:
```bash
hanif-finance add --account "BCA" --type in --amount 5000000 --category "Gaji" --desc "Bayaran project website"
```

> **💡 Tips Tanggal Lampau:** CLI ini mencatat waktu secara otomatis (real-time). Jika kamu ingin mencatat transaksi untuk hari sebelumnya, cukup ketik tanggalnya di dalam keterangan (`--desc`), contoh: `--desc "18 Juni: Beli kopi"`.

---

### ✏️ Mengedit & Menghapus Transaksi

#### 1. Edit Transaksi
Jika salah ketik nominal atau deskripsi (saldo akun akan otomatis disesuaikan):
```bash
hanif-finance edit --id 12 --amount 20000 --desc "Beli nasgor + sate"
```

#### 2. Hapus Transaksi
Menghapus transaksi berdasarkan ID (nominal akan otomatis dikembalikan ke saldo akun):
```bash
hanif-finance delete --id 12
```

---

## ⚙️ Konfigurasi Lanjutan & Open Source (Opsional)

### Dimana datanya disimpan?
CLI ini sangat fleksibel dan otomatis menyesuaikan lokasinya:
1. **Untuk Pengguna Umum / Open Source**: Jika kamu install di laptop biasa, aplikasi otomatis menyimpan datanya secara aman di folder home kamu:
   - **Windows**: `C:\Users\<NamaKamu>\.hanif-finance\data.db`
   - **Linux / macOS**: `~/.hanif-finance/data.db`
2. **Untuk Pengguna Obsidian**: Jika sistem mendeteksi folder Obsidian Vault Hanif (`~/Documents/ObsidianVault/...`), data otomatis tersambung ke sana.
3. **Custom Location**: Kamu bisa menentukan sendiri lokasi file `.db` dengan mengisi Environment Variable `HANIF_FINANCE_DB_PATH` di sistem operasi kamu.

---

## 📦 Cara Install dari File Executable (.exe / Binary) — Tanpa Python
Jika kamu mendownload file standalone binary (`hanif-finance.exe` untuk Windows atau `hanif-finance` untuk Linux) dari GitHub Releases, kamu tidak perlu menginstall Python. Agar perintah `hanif-finance` bisa diketik langsung dari folder mana pun di terminalmu, ikuti langkah pemasangan ke **Global PATH** di bawah ini:

### 🪟 Windows (.exe)
1. Buat folder baru di komputermu, misalnya di `C:\Program Files\HanifFinance\` atau `C:\Tools\`.
2. Pindahkan file `hanif-finance.exe` yang sudah didownload ke dalam folder tersebut.
3. Daftarkan folder tersebut ke System PATH Windows:
   - Buka **Start Menu** → ketik `Environment Variables` → pilih **Edit the system environment variables**.
   - Klik tombol **Environment Variables...** di pojok kanan bawah.
   - Di bagian *User variables* atau *System variables*, cari dan klik dua kali pada baris **Path**.
   - Klik tombol **New**, lalu masukkan jalur folder tadi (contoh: `C:\Program Files\HanifFinance`).
   - Klik **OK** pada semua jendela yang terbuka untuk menyimpan.
4. Buka ulang Command Prompt atau PowerShell, lalu ketik `hanif-finance balance`. Selesai!

### 🐧 Linux / macOS
1. Pindahkan file binary `hanif-finance` yang sudah didownload ke dalam folder global path (biasanya `/usr/local/bin` atau `~/.local/bin`):
   ```bash
   sudo mv hanif-finance /usr/local/bin/hanif-finance
   ```
2. Berikan izin eksekusi (executable permission) pada file tersebut:
   ```bash
   sudo chmod +x /usr/local/bin/hanif-finance
   ```
3. Buka terminal baru dan ketik `hanif-finance balance`. Selesai!

---

## 🛠️ Build Sendiri Menjadi Executable (.exe / Binary)
Jika kamu seorang developer dan ingin mengkompilasi sendiri kode source ini menjadi satu file executable mandiri:

1. Install dependency builder (PyInstaller):
   ```bash
   pip install -e .[build]
   # atau jika pakai pip biasa:
   pip install pyinstaller
   ```
2. Jalankan script build yang sudah disediakan:
   ```bash
   python build_exe.py
   ```
3. File binary siap pakai akan muncul di dalam folder `dist/`. Kamu bisa mendistribusikan file tersebut atau memasangnya ke PATH menggunakan panduan di atas.
