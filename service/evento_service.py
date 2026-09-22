from service.dados import lista_eventos, lista_inscricoes

def criar_evento(recebido):
    dados = recebido.model_dump()
    dados["id"] = max((item["id"] for item in lista_eventos), default=0) + 1
    lista_eventos.append(dados)
    return dados

def retornar_eventos():
    return lista_eventos

def pesquisar_evento(id):
    return next((item for item in lista_eventos if item["id"] == id), None)

def atualizar_evento(id, recebido):
    for indice, item in enumerate(lista_eventos):
        if item["id"] == id:
            dados = recebido.model_dump()
            dados["id"] = id
            lista_eventos[indice] = dados
            return dados
    return None

def excluir_evento(id):
    for indice, item in enumerate(lista_eventos):
        if item["id"] == id:
            excluido = lista_eventos.pop(indice)
            lista_inscricoes[:] = [i for i in lista_inscricoes if i["evento_id"] != id]
            return excluido
    return None
