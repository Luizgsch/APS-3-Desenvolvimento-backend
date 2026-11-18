import sqlite3

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from model import Participante
from schema.participante_schema import ParticipanteCreate, ParticipanteRead, ParticipanteUpdate
from service.erros import EmailDuplicadoError

def _salvar(db: Session, participante: Participante) -> ParticipanteRead:
    try:
        db.flush()
        resultado = ParticipanteRead.model_validate(participante)
        db.commit()
        return resultado
    except IntegrityError as erro:
        db.rollback()
        # Só a violação específica de e-mail é um conflito conhecido de negócio.
        if (
            isinstance(erro.orig, sqlite3.IntegrityError)
            and getattr(erro.orig, "sqlite_errorcode", None) == sqlite3.SQLITE_CONSTRAINT_UNIQUE
            and str(erro.orig) == "UNIQUE constraint failed: participantes.email"
        ):
            raise EmailDuplicadoError() from erro
        raise

def criar_participante(db: Session, recebido: ParticipanteCreate) -> ParticipanteRead:
    participante = Participante(**recebido.model_dump())
    db.add(participante)
    return _salvar(db, participante)

def retornar_participantes(db: Session) -> list[Participante]:
    return list(db.scalars(select(Participante).order_by(Participante.id)))

def pesquisar_participante(db: Session, id: int) -> Participante | None:
    return db.get(Participante, id)

def atualizar_participante(db: Session, id: int, recebido: ParticipanteUpdate) -> ParticipanteRead | None:
    participante = pesquisar_participante(db, id)
    if participante is None:
        return None
    for campo, valor in recebido.model_dump().items():
        setattr(participante, campo, valor)
    return _salvar(db, participante)


def excluir_participante(db: Session, id: int) -> bool:
    participante = pesquisar_participante(db, id)
    if participante is None:
        return False
    db.delete(participante)
    db.commit()
    return True
