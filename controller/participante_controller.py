from fastapi import APIRouter, HTTPException, Response, status
from model.participante import Participante
from service.participante_service import criar_participante, retornar_participantes, pesquisar_participante, atualizar_participante, excluir_participante

router = APIRouter(prefix="/participantes", tags=["Participantes"])

@router.post("", status_code=status.HTTP_201_CREATED)
def cadastrar_participante(recebido: Participante):
    return criar_participante(recebido)

@router.get("")
def listar_participantes():
    return retornar_participantes()

@router.get("/{id}")
def consultar_participante(id: int):
    item = pesquisar_participante(id)
    if item is None:
        raise HTTPException(404, "Participante não encontrado.")
    return item

@router.put("/{id}")
def alterar_participante(id: int, recebido: Participante):
    item = atualizar_participante(id, recebido)
    if item is None:
        raise HTTPException(404, "Participante não encontrado.")
    return item

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_participante(id: int):
    if excluir_participante(id) is None:
        raise HTTPException(404, "Participante não encontrado.")
    return Response(status_code=204)
