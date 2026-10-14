"""Testet die Verbindung zu Supabase.  Aufruf:  python -m scripts.check_db"""

from sqlalchemy import inspect, text

from app.database import engine


def main() -> None:
    with engine.connect() as conn:
        print("Verbunden mit:", conn.execute(text("SELECT version()")).scalar_one())
        print("Datenbank:    ", conn.execute(text("SELECT current_database()")).scalar_one())
    tables = inspect(engine).get_table_names(schema="public")
    print("Tabellen im Schema public:", ", ".join(sorted(tables)) or "(noch keine)")


if __name__ == "__main__":
    main()
