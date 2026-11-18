# APS 3 - API de Eventos Acadêmicos

[Repositório no GitHub](https://github.com/Luizgsch/APS-3-Desenvolvimento-backend)

Continuação da APS 2: API RESTful com FastAPI, persistência SQLite/SQLAlchemy ORM
e três relatórios dinâmicos. Eventos, participantes e inscrições permanecem no
banco após reiniciar a aplicação. Este projeto fica na pasta da APS 3; não é
necessário copiar ou alterar a APS 2 para executar.

## Requisitos e instalação

Ambiente de referência: **CPython 3.13.15, Windows x64**. O código requer Python
3.12 ou superior por usar `sqlite3.Connection.autocommit`; outras versões e
sistemas não foram validados. SQLite já acompanha o Python. Dependências diretas
e transitivas estão fixadas em `requirements.txt`; testes usam `requirements-dev.txt`.

Extraia o ZIP ou baixe o código e abra um terminal na raiz, onde fica `main.py`:

```powershell
git clone https://github.com/Luizgsch/APS-3-Desenvolvimento-backend.git
cd APS-3-Desenvolvimento-backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Não copie um ambiente virtual de outra pasta. Se já houver `.venv`, use um
ambiente novo ou preserve o existente antes de recriá-lo. Os comandos usam o
executável diretamente, sem exigir ativação nem mudança na política do PowerShell.

## Execução

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- OpenAPI: http://127.0.0.1:8000/openapi.json

Use Ctrl+C para encerrar. No Swagger, expanda a operação, clique em **Try it out**,
preencha os campos e clique em **Execute**. Guarde os IDs retornados para consultar,
alterar, excluir ou inscrever participantes.

## Estrutura e responsabilidades

```text
main.py                       aplicação, lifespan, routers e handler de falhas
database.py                   engine, Base, fábrica e dependência de sessões
controller/                   rotas e códigos HTTP
model/                        Evento, Participante e Inscricao do SQLAlchemy
schema/                       entradas e respostas Pydantic
service/                      regras, transações, CRUD e agregações
tests/                        testes com bancos temporários
scripts/validar_cenarios.py    12 cenários por HTTP com reinicialização real
scripts/preparar_entrega.py    pacote ZIP e manifesto de arquivos
docs/                         registros das etapas e evidências
requirements.txt              dependências de execução fixadas
requirements-dev.txt          dependências de testes fixadas
```

O `lifespan` importa os modelos e cria as tabelas por `Base.metadata.create_all()`.
Os controllers recebem uma sessão por requisição usando `Depends(get_db)`.
Os serviços confirmam operações com commit; exceções provocam rollback e a sessão
sempre é fechada. O pool é liberado no encerramento. Não há armazenamento em listas.

## Banco, entidades e integridade

`eventos.db` é criado automaticamente **na raiz deste projeto**, com caminho
absoluto derivado de `database.py`, independentemente do diretório do terminal.
O banco e seus arquivos auxiliares não fazem parte do ZIP nem do Git.

| Tabela | Campos |
|---|---|
| eventos | id, titulo, descricao, data, horario, local, capacidade, categoria |
| participantes | id, nome, email, curso |
| inscricoes | id, evento_id, participante_id, data_inscricao |

Evento e Participante possuem relações de um para muitos com Inscricao. As duas
chaves estrangeiras são obrigatórias e verificadas em cada conexão SQLite.
Excluir um evento ou participante remove suas inscrições em cascata, preservando
a outra entidade. Excluir um participante libera suas vagas.

O banco impede e-mails repetidos, inscrições repetidas para o mesmo par e
capacidade não positiva. E-mails usam NOCASE do SQLite, cuja comparação sem
distinção de caixa é limitada a ASCII. Não há normalização adicional de categorias
ou cursos. Pydantic valida e-mail, datas, horários, capacidade positiva e campos
obrigatórios; textos são aparados e não podem ficar vazios.

IDs são gerados na inserção. `data_inscricao` usa a data local do servidor,
gerada pelo ORM. PUT exige todos os campos de cadastro e mantém o ID original.
O cliente não escolhe ID nem data da inscrição.

Inscrições verificam evento, participante, duplicidade e vagas, nessa ordem.
O PUT de evento rejeita capacidade menor que a quantidade de inscritos.
Um bloqueio de escrita SQLite obtido antes da leitura serializa inscrições e
alterações de capacidade na mesma transação, protegendo a última vaga. Bloqueios
prolongados podem causar erro de acesso 500. A regra de vagas depende dos serviços;
escritas arbitrárias feitas fora da API não são cobertas por essa regra.

`create_all()` cria tabelas ausentes, mas não migra estruturas antigas. Alembic
não é utilizado. Não remova `eventos.db` se precisar preservar registros. Para
backup simples, encerre a aplicação antes de copiar o banco e guarde a cópia
fora do pacote de código.

## Rotas e respostas

| Método | Rota | Sucesso |
|---|---|---|
| GET | / | 200, mensagem de funcionamento |
| POST | /eventos | 201, evento criado |
| GET | /eventos | 200, lista ordenada por ID |
| GET | /eventos/{id} | 200, evento |
| PUT | /eventos/{id} | 200, evento atualizado |
| DELETE | /eventos/{id} | 204, sem corpo |
| POST | /participantes | 201, participante criado |
| GET | /participantes | 200, lista ordenada por ID |
| GET | /participantes/{id} | 200, participante |
| PUT | /participantes/{id} | 200, participante atualizado |
| DELETE | /participantes/{id} | 204, sem corpo |
| POST | /eventos/{evento_id}/inscricoes/{participante_id} | 201, inscrição com ID e data |
| GET | /eventos/{evento_id}/inscricoes | 200, participantes na ordem das inscrições |
| GET | /relatorios/eventos/ocupacao | 200, ocupação por evento |
| GET | /relatorios/eventos/categorias | 200, totais por categoria |
| GET | /relatorios/participantes/cursos | 200, totais por curso |

Listagens sem registros retornam `[]`. Use os caminhos sem barra final;
`/eventos/` continua funcionando por redirecionamento HTTP 307.

Erros usam `{"detail": ...}`: 404 para entidade inexistente; 409 para e-mail
repetido, inscrição duplicada, falta de vagas ou redução indevida de capacidade;
422 para entrada inválida; 500 para falhas de persistência, sem SQL ou caminhos
internos na resposta. Manter o próprio e-mail em uma atualização é permitido.

## Exemplo de uso

No Swagger, envie `POST /eventos`:

```json
{
  "titulo": "Workshop de Python",
  "descricao": "Introdução ao desenvolvimento com Python",
  "data": "2026-12-01",
  "horario": "19:00",
  "local": "Auditório",
  "capacidade": 2,
  "categoria": "Workshop"
}
```

Depois envie `POST /participantes`:

```json
{"nome": "Participante de exemplo", "email": "participante@example.com", "curso": "Computacao"}
```

Use os IDs retornados em `POST /eventos/{evento_id}/inscricoes/{participante_id}`,
sem corpo JSON. Exemplo de resposta (ID e data dependem da execução):

```json
{"evento_id": 1, "participante_id": 1, "id": 1, "data_inscricao": "2026-11-17"}
```

Consulte `GET /eventos/1/inscricoes` usando o ID real. Repetir a inscrição retorna
409 com `{"detail": "Participante já está inscrito neste evento."}`.

## Relatórios dinâmicos

As três rotas retornam JSON calculado no SQLite via SQLAlchemy, uma consulta por
relatório, sem listas de resultados fixas e sem cache dos totais.

- **Ocupação:** evento_id, titulo, capacidade, total_inscritos, vagas_disponiveis
  e percentual_ocupacao. Inclui eventos sem inscrições; ordena por ID. Percentual
  igual a `inscritos * 100 / capacidade`, arredondado para duas casas e protegido
  contra divisão por zero.
- **Categorias:** categoria, total_eventos, capacidade_total e total_inscricoes.
  Agrega inscrições antes do join para somar cada capacidade uma vez, inclusive
  quando dois eventos têm capacidade igual. Inclui categorias sem inscrições.
- **Cursos:** curso, total_participantes e total_inscricoes. Conta participantes
  distintos, mesmo com várias inscrições, e inclui participantes sem inscrições.
  Categorias e cursos são ordenados pelo texto cadastrado.

No exemplo anterior, com um evento de capacidade 2 e uma inscrição, a ocupação é:

```json
[{"evento_id": 1, "titulo": "Workshop de Python", "capacidade": 2, "total_inscritos": 1, "vagas_disponiveis": 1, "percentual_ocupacao": 50.0}]
```

Nesse mesmo exemplo, categorias e cursos retornam, respectivamente:

```json
[{"categoria": "Workshop", "total_eventos": 1, "capacidade_total": 2, "total_inscricoes": 1}]
```

```json
[{"curso": "Computacao", "total_participantes": 1, "total_inscricoes": 1}]
```

Alterar capacidade/categoria/curso, criar inscrição ou excluir registros atualiza
as próximas consultas. Se não houver registros da entidade principal, retorna `[]`.

## Testes e evidências

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -X utf8 scripts\validar_cenarios.py
```

A suíte possui 52 testes: infraestrutura, modelos, schemas, CRUD, falhas de
persistência, concorrência e relatórios. Usa bancos temporários, preservando o banco
real. O transporte de testes é httpx2, compatível com o TestClient instalado.

O demonstrador executa os 12 cenários por HTTP real, em dois processos Uvicorn
sucessivos sobre o mesmo banco temporário. Registra 55 requisições e respostas JSON
em [docs/evidencias/etapa8.json](docs/evidencias/etapa8.json). Uma nova execução
substitui essa evidência. A auditoria direta do arquivo SQLite existe somente
nos testes; a aplicação usa ORM.

Veja a matriz e o roteiro Swagger em [docs/ETAPA-8.md](docs/ETAPA-8.md).
**Pendente de demonstração:** os testes automatizados e `/docs` por HTTP passaram,
mas os 12 cenários não foram executados pela interface Swagger. O PDF exige essa
demonstração; o navegador automatizado estava indisponível. Não há capturas de
Swagger apresentadas como evidência concluída.

## Pacote de entrega

```powershell
.\.venv\Scripts\python.exe scripts\preparar_entrega.py
```

Gera ZIP, manifesto com SHA-256 por arquivo e checksum do pacote em `output/`.
Inclui código, documentação, evidências, testes e dependências. Exclui ambientes
virtuais, Git, banco real, caches, temporários e `.env`. Extraia em outra pasta,
crie uma nova `.venv` e siga a instalação. O manifesto permite conferir os arquivos.

O repositório desta entrega é
[Luizgsch/APS-3-Desenvolvimento-backend](https://github.com/Luizgsch/APS-3-Desenvolvimento-backend).
A APS 2 permanece em seu repositório separado. Os registros em docs/ETAPA-1.md
a docs/ETAPA-9.md descrevem as verificações locais anteriores à publicação.

O GitHub hospeda o código e este README. Uma URL de API em execução depende de
um serviço de hospedagem Python com armazenamento persistente para eventos.db;
GitHub Pages não executa esta API FastAPI.
