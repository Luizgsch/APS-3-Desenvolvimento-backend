"""Conexão SQLite e ciclo de vida das sessões da aplicação."""

from collections.abc import Generator
from pathlib import Path
import sqlite3

from sqlalchemy import URL, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_PATH = Path(__file__).resolve().parent / "eventos.db"
DATABASE_URL = URL.create("sqlite+pysqlite", database=str(DATABASE_PATH))

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "autocommit": False},
)


@event.listens_for(engine, "connect")
def habilitar_chaves_estrangeiras(
    connection: sqlite3.Connection, connection_record: object
) -> None:
    """Ativa a verificação de referências em cada conexão SQLite."""
    anterior = connection.autocommit
    connection.autocommit = True
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()
    finally:
        connection.autocommit = anterior


class Base(DeclarativeBase):
    """Base compartilhada pelos modelos ORM da aplicação."""


SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessão por requisição; o serviço controla o commit."""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def criar_tabelas() -> None:
    """Cria, sem apagar dados, as tabelas registradas na metadata da Base."""
    import model  # Registra as entidades antes de executar create_all.

    Base.metadata.create_all(bind=engine)
