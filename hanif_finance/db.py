import os
import sqlite3
from pathlib import Path

def get_db_path() -> Path:
    """Resolve database path dynamically across Windows and Linux."""
    # 1. Check direct environment variable override
    if "HANIF_FINANCE_DB_PATH" in os.environ:
        return Path(os.environ["HANIF_FINANCE_DB_PATH"]).resolve()
        
    # 2. Check vault root override
    if "OBSIDIAN_VAULT_DIR" in os.environ:
        vault_dir = Path(os.environ["OBSIDIAN_VAULT_DIR"]).resolve()
        return vault_dir / "09 - Hermes" / "hermes_data.db"
        
    # 3. Check if running in Hanif's environment (has his specific Obsidian vault structure)
    home_dir = Path.home()
    hanif_vault_db = home_dir / "Documents" / "ObsidianVault" / "hanif" / "09 - Hermes" / "hermes_data.db"
    if hanif_vault_db.parent.exists():
        return hanif_vault_db
        
    # 4. Open-source default: store cleanly in ~/.hanif-finance/data.db (works on Windows/Linux/Mac)
    user_data_db = home_dir / ".hanif-finance" / "data.db"
    return user_data_db

def get_db() -> sqlite3.Connection:
    """Get SQLite database connection and ensure schema exists."""
    db_path = get_db_path()
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Ensure tables exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finance_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0,
            last_updated TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finance_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT,
            category TEXT,
            account_id INTEGER,
            amount_in REAL DEFAULT 0,
            amount_out REAL DEFAULT 0,
            balance_after REAL,
            FOREIGN KEY (account_id) REFERENCES finance_accounts(id)
        )
    ''')
    conn.commit()
    return conn
