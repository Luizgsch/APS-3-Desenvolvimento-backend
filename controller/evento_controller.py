from fastapi import APIRouter, HTTPException, Response, status

from model.evento import Evento
from service.evento_service import (
    atualizar_evento,
    criar_evento,
    excluir_evento,
    pesquisar_evento,
    retornar_eventos,
)

router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_eventos(evento_recebido: Evento):
    return criar_evento(evento_recebido)


@router.get("")
def ver_eventos():
    return retornar_eventos()


@router.get("/{id}")
def listar_evento(id: int):
    evento = pesquisar_evento(id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    return evento


@router.put("/{id}")
def trocar_evento(id: int, evento_recebido: Evento):
    evento = atualizar_evento(id, evento_recebido)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    return evento


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_evento(id: int):
    if excluir_evento(id) is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
