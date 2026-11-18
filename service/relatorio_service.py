from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from model import Evento, Inscricao, Participante


def _inscricoes_por_evento():
    """Uma linha por evento impede multiplicar a capacidade nos joins."""
    return (
        select(Inscricao.evento_id, func.count(Inscricao.id).label("total"))
        .group_by(Inscricao.evento_id)
        .subquery()
    )


def ocupacao_eventos(db: Session):
    inscricoes = _inscricoes_por_evento()
    total = func.coalesce(inscricoes.c.total, 0)
    consulta = (
        select(
            Evento.id.label("evento_id"), Evento.titulo, Evento.capacidade,
            total.label("total_inscritos"),
            (Evento.capacidade - total).label("vagas_disponiveis"),
            func.coalesce(
                func.round(total * 100.0 / func.nullif(Evento.capacidade, 0), 2), 0.0
            ).label("percentual_ocupacao"),
        )
        .outerjoin(inscricoes, inscricoes.c.evento_id == Evento.id)
        .order_by(Evento.id)
    )
    return db.execute(consulta).mappings().all()


def eventos_por_categoria(db: Session):
    inscricoes = _inscricoes_por_evento()
    consulta = (
        select(
            Evento.categoria,
            func.count(Evento.id).label("total_eventos"),
            func.sum(Evento.capacidade).label("capacidade_total"),
            func.sum(func.coalesce(inscricoes.c.total, 0)).label("total_inscricoes"),
        )
        .outerjoin(inscricoes, inscricoes.c.evento_id == Evento.id)
        .group_by(Evento.categoria)
        .order_by(Evento.categoria)
    )
    return db.execute(consulta).mappings().all()


def participantes_por_curso(db: Session):
    consulta = (
        select(
            Participante.curso,
            func.count(distinct(Participante.id)).label("total_participantes"),
            func.count(Inscricao.id).label("total_inscricoes"),
        )
        .outerjoin(Participante.inscricoes)
        .group_by(Participante.curso)
        .order_by(Participante.curso)
    )
    return db.execute(consulta).mappings().all()
