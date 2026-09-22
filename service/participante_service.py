from service.dados import lista_participantes, lista_inscricoes

def criar_participante(recebido):
    dados = recebido.model_dump()
    dados["id"] = max((item["id"] for item in lista_participantes), default=0) + 1
    lista_participantes.append(dados)
    return dados

def retornar_participantes():
    return lista_participantes

def pesquisar_participante(id):
    return next((item for item in lista_participantes if item["id"] == id), None)

def atualizar_participante(id, recebido):
    for indice, item in enumerate(lista_participantes):
        if item["id"] == id:
            dados = recebido.model_dump()
            dados["id"] = id
            lista_participantes[indice] = dados
            return dados
    return None

def excluir_participante(id):
    for indice, item in enumerate(lista_participantes):
        if item["id"] == id:
            excluido = lista_participantes.pop(indice)
            lista_inscricoes[:] = [i for i in lista_inscricoes if i["participante_id"] != id]
            return excluido
    return None
