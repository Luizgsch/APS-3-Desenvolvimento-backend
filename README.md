# API de Eventos Acadêmicos

API RESTful desenvolvida em Python utilizando FastAPI para gerenciamento
de eventos acadêmicos, participantes e inscrições.

## Tecnologias utilizadas

- Python
- FastAPI
- Pydantic
- Uvicorn

## Funcionalidades

A API permite:

- cadastrar eventos;
- listar eventos;
- consultar evento por ID;
- atualizar eventos;
- excluir eventos;
- cadastrar participantes;
- listar participantes;
- consultar participante por ID;
- atualizar participantes;
- excluir participantes;
- inscrever participantes em eventos;
- listar participantes inscritos em um evento;
- validar dados de entrada;
- impedir inscrições duplicadas;
- controlar a capacidade dos eventos;
- tratar erros com códigos HTTP adequados.

## Instalação

Clone ou baixe o projeto.

Crie um ambiente virtual:

python -m venv .venv

Ative o ambiente virtual no Windows:

.\.venv\Scripts\Activate.ps1

Instale as dependências:

pip install -r requirements.txt

## Execução

Execute o projeto com:

python -m uvicorn main:app --reload

A API ficará disponível em:

http://127.0.0.1:8000

A documentação Swagger ficará disponível em:

http://127.0.0.1:8000/docs

## Rotas

### Eventos

POST /eventos  
GET /eventos  
GET /eventos/{id}  
PUT /eventos/{id}  
DELETE /eventos/{id}

### Participantes

POST /participantes  
GET /participantes  
GET /participantes/{id}  
PUT /participantes/{id}  
DELETE /participantes/{id}

### Inscrições

POST /eventos/{evento_id}/inscricoes/{participante_id}

GET /eventos/{evento_id}/inscricoes

## Exemplo de cadastro de evento

POST /eventos

{
    "titulo": "Workshop de Python",
    "descricao": "Introdução ao desenvolvimento com Python",
    "data": "2026-10-20",
    "horario": "19:00",
    "local": "Auditório",
    "capacidade": 30,
    "categoria": "Workshop"
}

## Exemplo de cadastro de participante

POST /participantes

{
    "nome": "Luiz",
    "email": "luiz@exemplo.com",
    "curso": "Engenharia de Software"
}

## Armazenamento

Os dados são armazenados em memória utilizando listas Python.

Ao encerrar a aplicação, os dados cadastrados são perdidos.