from elda.db.session import engine
from elda.db.models import Base


def init_db():
    """Create all tables (safe — won't drop existing ones)."""
    try:
        # Add new columns to existing tables gracefully via ALTER TABLE if needed
        import sqlalchemy as sa
        with engine.connect() as conn:
            inspector = sa.inspect(engine)
            existing = [c['name'] for c in inspector.get_columns('interactions')] if 'interactions' in inspector.get_table_names() else []

            # Add missing columns to interactions table without dropping data
            if 'sender' not in existing:
                conn.execute(sa.text("ALTER TABLE interactions ADD COLUMN sender TEXT DEFAULT 'Patient'"))
            if 'emotion' not in existing:
                conn.execute(sa.text("ALTER TABLE interactions ADD COLUMN emotion TEXT DEFAULT 'Neutral'"))
            conn.commit()
    except Exception as e:
        print(f"[DB] Migration note: {e}")

    Base.metadata.create_all(bind=engine)
    print("[DB] Tables created / verified.")


if __name__ == "__main__":
    init_db()
