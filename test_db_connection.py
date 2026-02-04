from sqlalchemy import create_engine, text

try:
    engine = create_engine(
        "postgresql://admin:admin123@localhost:5432/fiverr_db"
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Successfully connected to Postgres!")
except Exception as e:
    print(e)
