import sqlite3

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from model import Inscricao, Participante
from schema.inscricao_schema import InscricaoRead
from service.evento_service import pesquisar_evento
from service.participante_service import pesquisar_participante
from service.transacoes import bloquear_evento_para_escrita

def criar_inscricao(db: Session, evento_id: int, participante_id: int):
    bloquear_evento_para_escrita(db, evento_id)
    evento = pesquisar_evento(db, evento_id)
    if evento is None:
        return None, "evento_nao_encontrado"
    if pesquisar_participante(db, participante_id) is None:
        return None, "participante_nao_encontrado"
    if db.scalar(select(Inscricao.id).where(
        Inscricao.evento_id == evento_id, Inscricao.participante_id == participante_id
    )) is not None:
        return None, "ja_inscrito"
    total = db.scalar(select(func.count()).select_from(Inscricao).where(Inscricao.evento_id == evento_id))
    if total >= evento.capacidade:
        return None, "sem_vagas"
    inscricao = Inscricao(evento_id=evento_id, participante_id=participante_id)
    db.add(inscricao)
    try:
        db.flush()
        resultado = InscricaoRead.model_validate(inscricao)
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        if (
            isinstance(erro.orig, sqlite3.IntegrityError)
            and getattr(erro.orig, "sqlite_errorcode", None) == sqlite3.SQLITE_CONSTRAINT_UNIQUE
            and str(erro.orig) == "UNIQUE constraint failed: inscricoes.evento_id, inscricoes.participante_id"
        ):
            return None, "ja_inscrito"
        raise
    return resultado, None

def retornar_inscritos(db: Session, evento_id: int) -> list[Participante] | None:
    if pesquisar_evento(db, evento_id) is None:
        return None
    return list(db.scalars(
        select(Participante)
        .join(Participante.inscricoes)
        .where(Inscricao.evento_id == evento_id)
        .order_by(Inscricao.id)
    ))
