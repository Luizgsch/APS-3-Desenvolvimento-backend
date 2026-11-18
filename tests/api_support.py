from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

import database
import main


class APITestCase(unittest.TestCase):
    """Isola o banco sem alterar dados reais."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "test.db"
        self.engine = create_engine(
            database.URL.create("sqlite+pysqlite", database=str(self.path)),
            connect_args={"check_same_thread": False, "autocommit": False},
        )
        event.listen(self.engine, "connect", database.habilitar_chaves_estrangeiras)
        self.factory = sessionmaker(bind=self.engine, autoflush=False)
        self.patches = [patch.object(database, "engine", self.engine),
                        patch.object(database, "SessionLocal", self.factory),
                        patch.object(main, "engine", self.engine)]
        for item in self.patches:
            item.start()
        self.client = TestClient(main.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        for item in reversed(self.patches):
            item.stop()
        self.engine.dispose()
        self.directory.cleanup()
