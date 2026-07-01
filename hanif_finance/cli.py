import sys
import json
import argparse
from datetime import datetime
from .db import get_db

def print_balances():
    conn = get_db()
    cursor = conn.cursor()
    print("=== CURRENT BALANCES ===")
    cursor.execute("SELECT name, balance FROM finance_accounts")
    rows = cursor.fetchall()
    if not rows:
        print("No accounts found. Add an account first.")
    else:
        for row in rows:
            print(f"{row[0]}: Rp {row[1]:,.0f}")
    conn.close()

def add_transaction(account, tx_type, amount, category, desc):
    if tx_type not in ("in", "out"):
        print(f"Error: --type must be 'in' or 'out' (got '{tx_type}')", file=sys.stderr)
        sys.exit(1)

    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get account id
    cursor.execute("SELECT id, balance FROM finance_accounts WHERE name COLLATE NOCASE = ?", (account,))
    res = cursor.fetchone()
    if not res:
        # Auto-create account if it doesn't exist
        cursor.execute("INSERT INTO finance_accounts (name, balance, last_updated) VALUES (?, 0, ?)", (account, today))
        conn.commit()
        acc_id = cursor.lastrowid
        balance = 0
        print(f"Created new account: '{account}'")
    else:
        acc_id, balance = res

    amount_in = amount if tx_type == "in" else 0
    amount_out = amount if tx_type == "out" else 0

    new_balance = balance + amount_in - amount_out

    cursor.execute("UPDATE finance_accounts SET balance = ?, last_updated = ? WHERE id = ?", (new_balance, today, acc_id))
    cursor.execute(
        "INSERT INTO finance_transactions (date, description, category, account_id, amount_in, amount_out, balance_after) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (today, desc, category, acc_id, amount_in, amount_out, new_balance)
    )
    
    conn.commit()
    conn.close()
    print(f"Logged: {desc} | {tx_type.upper()} Rp {amount:,.0f} to {account}")
    print_balances()

def list_transactions(limit=10, account=None):
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT t.id, t.date, a.name, t.amount_in, t.amount_out, t.category, t.description, t.balance_after 
        FROM finance_transactions t
        JOIN finance_accounts a ON t.account_id = a.id
    '''
    params = []
    
    if account:
        query += " WHERE a.name COLLATE NOCASE = ?"
        params.append(account)
        
    query += " ORDER BY t.id DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    if not rows:
        print("No transactions found.")
        conn.close()
        return

    print(f"\n{'ID':<5} | {'Date':<10} | {'Account':<12} | {'Jenis':<8} | {'Total':<14} | {'Category':<15} | {'Description'}")
    print("-" * 105)
    
    for row in reversed(rows):
        t_id, date_str, acc_name, amt_in, amt_out, cat, desc, bal_after = row
        short_date = date_str.split(" ")[0] if " " in date_str else date_str
        
        if amt_in > 0:
            jenis = "MASUK"
            total_val = f"+Rp {amt_in:,.0f}"
        else:
            jenis = "KELUAR"
            total_val = f"-Rp {amt_out:,.0f}"
            
        print(f"{t_id:<5} | {short_date:<10} | {acc_name:<12} | {jenis:<8} | {total_val:<14} | {cat:<15} | {desc}")
        
    print("")
    print_balances()

def dump_transactions(limit=100):
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT t.id, t.date, a.name, t.amount_in, t.amount_out, t.category, t.description, t.balance_after 
        FROM finance_transactions t
        JOIN finance_accounts a ON t.account_id = a.id
        ORDER BY t.id DESC LIMIT ?
    '''
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "date": row[1],
            "account": row[2],
            "amount_in": row[3],
            "amount_out": row[4],
            "category": row[5],
            "description": row[6],
            "balance_after": row[7]
        })
    print(json.dumps(result, indent=2))

def edit_transaction(tx_id, amount=None, desc=None, category=None):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT account_id, amount_in, amount_out, description, category FROM finance_transactions WHERE id = ?", (tx_id,))
    tx = cursor.fetchone()
    if not tx:
        print(f"Transaction ID {tx_id} not found.")
        conn.close()
        return
        
    acc_id, old_in, old_out, old_desc, old_cat = tx
    
    new_desc = desc if desc is not None else old_desc
    new_cat = category if category is not None else old_cat
    
    if amount is not None:
        if old_in > 0:
            new_in = amount
            new_out = 0
            diff = new_in - old_in
        else:
            new_in = 0
            new_out = amount
            diff = -(new_out - old_out)
            
        cursor.execute("UPDATE finance_accounts SET balance = balance + ? WHERE id = ?", (diff, acc_id))
        cursor.execute("UPDATE finance_transactions SET amount_in = ?, amount_out = ?, description = ?, category = ? WHERE id = ?",
                       (new_in, new_out, new_desc, new_cat, tx_id))
    else:
        cursor.execute("UPDATE finance_transactions SET description = ?, category = ? WHERE id = ?",
                       (new_desc, new_cat, tx_id))
                       
    conn.commit()
    conn.close()
    print(f"Updated transaction ID {tx_id}.")
    print_balances()

def delete_transaction(tx_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT account_id, amount_in, amount_out, description FROM finance_transactions WHERE id = ?", (tx_id,))
    tx = cursor.fetchone()
    if not tx:
        print(f"Transaction ID {tx_id} not found.")
        conn.close()
        return
        
    acc_id, old_in, old_out, old_desc = tx
    revert_diff = old_out - old_in
    
    cursor.execute("UPDATE finance_accounts SET balance = balance + ? WHERE id = ?", (revert_diff, acc_id))
    cursor.execute("DELETE FROM finance_transactions WHERE id = ?", (tx_id,))
    
    conn.commit()
    conn.close()
    print(f"Deleted transaction ID {tx_id} ('{old_desc}'). Reverted Rp {abs(revert_diff):,.0f} to account balance.")
    print_balances()

def main():
    parser = argparse.ArgumentParser(description="Hanif Finance CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    subparsers.add_parser("balance", help="Check current account balances")
    
    list_p = subparsers.add_parser("list", help="List recent transactions")
    list_p.add_argument("--limit", type=int, default=10, help="Number of transactions to show")
    list_p.add_argument("--account", type=str, help="Filter by account name")
    
    dump_p = subparsers.add_parser("dump", help="Dump transactions as JSON (machine-readable)")
    dump_p.add_argument("--limit", type=int, default=100, help="Number of transactions to show")
    
    add_p = subparsers.add_parser("add", help="Add a new transaction")
    add_p.add_argument("--account", type=str, required=True, help="Account name (e.g. 'Cash', 'BCA')")
    add_p.add_argument("--type", type=str, required=True, choices=["in", "out"], help="Transaction type: 'in' or 'out'")
    add_p.add_argument("--amount", type=float, required=True, help="Amount in Rupiah")
    add_p.add_argument("--category", type=str, required=True, help="Category (e.g. 'Makanan', 'Gaji')")
    add_p.add_argument("--desc", type=str, required=True, help="Description")
    
    edit_p = subparsers.add_parser("edit", help="Edit an existing transaction")
    edit_p.add_argument("--id", type=int, required=True, help="Transaction ID")
    edit_p.add_argument("--amount", type=float, help="New amount")
    edit_p.add_argument("--desc", type=str, help="New description")
    edit_p.add_argument("--category", type=str, help="New category")
    
    del_p = subparsers.add_parser("delete", help="Delete a transaction")
    del_p.add_argument("--id", type=int, required=True, help="Transaction ID")
    
    args = parser.parse_args()
    
    if args.command == "balance" or not args.command:
        print_balances()
    elif args.command == "list":
        list_transactions(limit=args.limit, account=args.account)
    elif args.command == "dump":
        dump_transactions(limit=args.limit)
    elif args.command == "add":
        add_transaction(args.account, args.type, args.amount, args.category, args.desc)
    elif args.command == "edit":
        edit_transaction(args.id, amount=args.amount, desc=args.desc, category=args.category)
    elif args.command == "delete":
        delete_transaction(args.id)

if __name__ == "__main__":
    main()
