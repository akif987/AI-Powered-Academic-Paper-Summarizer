"""Drop all tables and recreate them."""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connection parameters
host = "localhost"
port = 8081
user = "postgres"
password = "Akifbro@987"
dbname = "paper_summarizer"

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=dbname
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    print("Dropping all tables...")
    cursor.execute("""
        DROP TABLE IF EXISTS query_cache CASCADE;
        DROP TABLE IF EXISTS summaries CASCADE;
        DROP TABLE IF EXISTS embeddings CASCADE;
        DROP TABLE IF EXISTS chunks CASCADE;
        DROP TABLE IF EXISTS papers CASCADE;
        DROP TABLE IF EXISTS alembic_version CASCADE;
    """)
    print("✅ All tables dropped successfully!")
    
    cursor.close()
    conn.close()
    
    print("\nNow run: alembic upgrade head")
    
except Exception as e:
    print(f"❌ Error: {e}")
