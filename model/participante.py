from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from model.inscricao import Inscricao


class Participante(Base):
    __tablename__ = "participantes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String(collation="NOCASE"), nullable=False, unique=True)
    curso: Mapped[str] = mapped_column(String, nullable=False)

    inscricoes: Mapped[list[Inscricao]] = relationship(
        back_populates="participante", cascade="all, delete-orphan", passive_deletes=True
    )
