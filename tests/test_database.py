"""Testes da infraestrutura, sem introduzir entidades da aplicação."""

from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from sqlalchemy import Column, ForeignKey, Integer, MetaData, Table, create_engine, event, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

import database
import model  # Registra entidades antes de substituir a Base nos testes isolados.


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "test.db"
        self.engine = create_engine(
            database.URL.create("sqlite+pysqlite", database=str(self.path)),
            connect_args={"check_same_thread": False, "autocommit": False},
        )
        event.listen(self.engine, "connect", database.habilitar_chaves_estrangeiras)
        self.factory = sessionmaker(bind=self.engine, autoflush=False)
        self.metadata = MetaData()
        self.parent = Table("test_parent", self.metadata, Column("id", Integer, primary_key=True))
        self.child = Table(
            "test_child", self.metadata,
            Column("id", Integer, primary_key=True),
            Column("parent_id", ForeignKey("test_parent.id"), nullable=False),
        )

    def tearDown(self):
        self.engine.dispose()
        self.directory.cleanup()

    def create_tables(self):
        with patch.object(database, "Base", SimpleNamespace(metadata=self.metadata)), patch.object(database, "engine", self.engine):
            database.criar_tabelas()

    def test_database_path_is_absolute_and_inside_aps3(self):
        self.assertTrue(database.DATABASE_PATH.is_absolute())
        self.assertEqual(database.DATABASE_PATH.parent, Path(database.__file__).resolve().parent)
        self.assertEqual(database.DATABASE_URL.database, str(database.DATABASE_PATH))

    def test_table_creation_is_idempotent_and_preserves_data(self):
        self.create_tables()
        with self.engine.begin() as connection:
            connection.execute(self.parent.insert().values(id=1))
        self.create_tables()
        self.assertEqual(set(inspect(self.engine).get_table_names()), {"test_parent", "test_child"})
        self.engine.dispose()
        with self.engine.connect() as connection:
            self.assertEqual(connection.scalar(select(self.parent.c.id)), 1)

    def test_foreign_keys_are_enabled_on_new_connections(self):
        self.create_tables()
        for _ in range(2):
            self.engine.dispose()
            with self.engine.connect() as connection:
                self.assertEqual(connection.scalar(text("PRAGMA foreign_keys")), 1)
            with self.assertRaises(IntegrityError), self.engine.begin() as connection:
                connection.execute(self.child.insert().values(id=1, parent_id=999))

    def test_session_closes_without_implicitly_committing(self):
        self.create_tables()
        session = self.factory()
        wrapped = Mock(wraps=session)
        with patch.object(database, "SessionLocal", return_value=wrapped):
            dependency = database.get_db()
            next(dependency).execute(self.parent.insert().values(id=1))
            with self.assertRaises(StopIteration):
                next(dependency)
        wrapped.close.assert_called_once()
        self.assertEqual(self.engine.pool.checkedout(), 0)
        with self.factory() as check:
            self.assertIsNone(check.scalar(select(self.parent.c.id)))

    def test_session_rolls_back_and_closes_after_exception(self):
        self.create_tables()
        session = self.factory()
        wrapped = Mock(wraps=session)
        with patch.object(database, "SessionLocal", return_value=wrapped):
            dependency = database.get_db()
            next(dependency).execute(self.parent.insert().values(id=1))
            with self.assertRaisesRegex(RuntimeError, "falha simulada"):
                dependency.throw(RuntimeError("falha simulada"))
        wrapped.rollback.assert_called_once()
        wrapped.close.assert_called_once()
        self.assertEqual(self.engine.pool.checkedout(), 0)
        with self.factory() as check:
            self.assertIsNone(check.scalar(select(self.parent.c.id)))


if __name__ == "__main__":
    unittest.main()
