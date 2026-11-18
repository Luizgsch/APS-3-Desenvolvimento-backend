from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from model.inscricao import Inscricao


class Evento(Base):
    __tablename__ = "eventos"
    __table_args__ = (CheckConstraint("capacidade > 0", name="ck_eventos_capacidade_positiva"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    horario: Mapped[time] = mapped_column(Time, nullable=False)
    local: Mapped[str] = mapped_column(String, nullable=False)
    capacidade: Mapped[int] = mapped_column(nullable=False)
    categoria: Mapped[str] = mapped_column(String, nullable=False)

    inscricoes: Mapped[list[Inscricao]] = relationship(
        back_populates="evento", cascade="all, delete-orphan", passive_deletes=True
    )
