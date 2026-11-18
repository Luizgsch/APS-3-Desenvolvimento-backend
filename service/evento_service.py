from sqlalchemy import func, select
from sqlalchemy.orm import Session

from model import Evento, Inscricao
from schema.evento_schema import EventoCreate, EventoRead, EventoUpdate
from service.erros import CapacidadeInsuficienteError
from service.transacoes import bloquear_evento_para_escrita

def criar_evento(db: Session, recebido: EventoCreate) -> EventoRead:
    evento = Evento(**recebido.model_dump())
    db.add(evento)
    db.flush()
    resultado = EventoRead.model_validate(evento)
    db.commit()
    return resultado

def retornar_eventos(db: Session) -> list[Evento]:
    return list(db.scalars(select(Evento).order_by(Evento.id)))

def pesquisar_evento(db: Session, id: int) -> Evento | None:
    return db.get(Evento, id)

def atualizar_evento(db: Session, id: int, recebido: EventoUpdate) -> EventoRead | None:
    bloquear_evento_para_escrita(db, id)
    evento = pesquisar_evento(db, id)
    if evento is None:
        return None
    total = db.scalar(select(func.count()).select_from(Inscricao).where(Inscricao.evento_id == id))
    if recebido.capacidade < total:
        raise CapacidadeInsuficienteError()
    for campo, valor in recebido.model_dump().items():
        setattr(evento, campo, valor)
    db.flush()
    resultado = EventoRead.model_validate(evento)
    db.commit()
    return resultado

def excluir_evento(db: Session, id: int) -> bool:
    evento = pesquisar_evento(db, id)
    if evento is None:
        return False
    db.delete(evento)
    db.commit()
    return True
