import sqlite3
import os

def migrate_cnpj_db(db_path):
    """
    Connects to the cnpj.db database and applies necessary schema modifications.
    """
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        sql_commands = """
        CREATE TABLE IF NOT EXISTS cnpj_search (
            cnpj TEXT PRIMARY KEY NOT NULL
        );

        INSERT OR IGNORE INTO cnpj_search (cnpj)
        SELECT DISTINCT cnpj FROM socios WHERE cnpj IS NOT NULL;

        CREATE INDEX IF NOT EXISTS idx_socios_cnpj ON socios (cnpj);
        CREATE INDEX IF NOT EXISTS idx_estabelecimento_cnpj ON estabelecimento (cnpj);
        CREATE INDEX IF NOT EXISTS idx_empresas_cnpj_basico ON empresas (cnpj_basico);
        """
        cursor.executescript(sql_commands)
        conn.commit()
        print(f"Database {db_path} migrated successfully.")

    except sqlite3.Error as e:
        print(f"Error migrating database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Assuming cnpj.db is in the same directory as this script, or specify its full path
    # You might need to adjust this path based on where your cnpj.db file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(current_dir, os.pardir, 'db', 'cnpj.db') # Corrected path based on user feedback
    
    # If cnpj.db is in the project root, you might use:
    # project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
    # db_file = os.path.join(project_root, 'cnpj.db')

    migrate_cnpj_db(db_file)
