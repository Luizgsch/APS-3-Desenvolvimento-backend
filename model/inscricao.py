from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from model.evento import Evento
    from model.participante import Participante


class Inscricao(Base):
    __tablename__ = "inscricoes"
    __table_args__ = (
        UniqueConstraint("evento_id", "participante_id", name="uq_inscricoes_evento_participante"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(
        ForeignKey("eventos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    participante_id: Mapped[int] = mapped_column(
        ForeignKey("participantes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data_inscricao: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    evento: Mapped[Evento] = relationship(back_populates="inscricoes")
    participante: Mapped[Participante] = relationship(back_populates="inscricoes")
