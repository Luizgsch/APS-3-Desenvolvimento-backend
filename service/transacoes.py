from sqlalchemy import update
from sqlalchemy.orm import Session

from model import Evento


def bloquear_evento_para_escrita(db: Session, evento_id: int) -> None:
    """Obtém o bloqueio de escrita SQLite antes de ler capacidade e inscrições.

    O UPDATE preserva a capacidade e mantém o bloqueio até commit ou rollback.
    Inscrições e alterações de capacidade usam a mesma ordem de acesso.
    """
    db.execute(
        update(Evento)
        .where(Evento.id == evento_id)
        .values(capacidade=Evento.capacidade)
        .execution_options(synchronize_session=False)
    )
