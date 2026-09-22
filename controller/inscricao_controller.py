from fastapi import APIRouter, HTTPException, status
from service.inscricao_service import criar_inscricao, retornar_inscritos

router = APIRouter(tags=["Inscrições"])

@router.post("/eventos/{evento_id}/inscricoes/{participante_id}", status_code=status.HTTP_201_CREATED)
def inscrever_participante(evento_id: int, participante_id: int):
    item, erro = criar_inscricao(evento_id, participante_id)
    erros = {
        "evento_nao_encontrado": (404, "Evento não encontrado."),
        "participante_nao_encontrado": (404, "Participante não encontrado."),
        "ja_inscrito": (400, "Participante já está inscrito neste evento."),
        "sem_vagas": (400, "Não existem vagas disponíveis para este evento."),
    }
    if erro:
        codigo, detalhe = erros[erro]
        raise HTTPException(codigo, detalhe)
    return item

@router.get("/eventos/{evento_id}/inscricoes")
def listar_inscritos(evento_id: int):
    itens = retornar_inscritos(evento_id)
    if itens is None:
        raise HTTPException(404, "Evento não encontrado.")
    return itens
