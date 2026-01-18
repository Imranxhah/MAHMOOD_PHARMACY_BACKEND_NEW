import sqlite3
import sys

def check_constraints():
    with open('debug_output.txt', 'w') as f:
        try:
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            
            f.write("--- Tables in DB ---\n")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            f.write(f"Found {len(tables)} tables.\n")

            f.write("\n--- Searching for FKs to 'orders_order' ---\n")
            for table in tables:
                table_name = table[0]
                # Get foreign keys for each table
                cursor.execute(f"PRAGMA foreign_key_list({table_name});")
                fks = cursor.fetchall()
                for fk in fks:
                    # fk format: (id, seq, table, from, to, on_update, on_delete, match)
                    target_table = fk[2]
                    if target_table == 'orders_order':
                        f.write(f"[FOUND] Table '{table_name}' -> 'orders_order'. On Delete: {fk[6]}\n")

            f.write("\n--- Searching for FKs to 'orders_orderitem' ---\n")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA foreign_key_list({table_name});")
                fks = cursor.fetchall()
                for fk in fks:
                    target_table = fk[2]
                    if target_table == 'orders_orderitem':
                        f.write(f"[FOUND] Table '{table_name}' -> 'orders_orderitem'. On Delete: {fk[6]}\n")

            conn.close()
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    check_constraints()
