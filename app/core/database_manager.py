import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Import model

Base = declarative_base()


class DatabaseManager:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@db:5432/haussteuerung"
        )
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        Base.metadata.create_all(bind=self.engine)  # optional: Tabellen erstellen

    @contextmanager
    def session_scope(self):
        """Contextmanager für eine saubere DB-Session"""
        session: Session = self.SessionLocal()
        try:
            yield session
            session.commit()  # commit nach erfolgreicher Verarbeitung
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
