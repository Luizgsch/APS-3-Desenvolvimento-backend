from service.dados import lista_inscricoes
from service.evento_service import pesquisar_evento
from service.participante_service import pesquisar_participante

def criar_inscricao(evento_id, participante_id):
    evento = pesquisar_evento(evento_id)
    if evento is None:
        return None, "evento_nao_encontrado"
    if pesquisar_participante(participante_id) is None:
        return None, "participante_nao_encontrado"
    if any(i["evento_id"] == evento_id and i["participante_id"] == participante_id for i in lista_inscricoes):
        return None, "ja_inscrito"
    if sum(i["evento_id"] == evento_id for i in lista_inscricoes) >= evento["capacidade"]:
        return None, "sem_vagas"
    item = {"evento_id": evento_id, "participante_id": participante_id}
    lista_inscricoes.append(item)
    return item, None

def retornar_inscritos(evento_id):
    if pesquisar_evento(evento_id) is None:
        return None
    return [p for i in lista_inscricoes if i["evento_id"] == evento_id if (p := pesquisar_participante(i["participante_id"])) is not None]
