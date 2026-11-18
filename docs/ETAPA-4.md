# Etapa 4: CRUD de eventos persistente

Concluída em 17/11/2026, exclusivamente na APS 3. A APS 2 não foi alterada.

## Alterações

O serviço de eventos substituiu a lista em memória por consultas e operações
SQLAlchemy ORM, usando a sessão recebida pelo controller. Listagens têm ordem por ID.
Criação e atualização executam flush, validam a resposta e confirmam a transação.
As respostas usam EventoRead, sem expor atributos internos ou relacionamentos ORM.

As rotas agora têm os seguintes resultados:

- POST /eventos: 201 com o evento criado.
- GET /eventos: 200 com a lista, incluindo lista vazia.
- GET /eventos/{id}: 200 com o evento ou 404.
- PUT /eventos/{id}: 200 com o evento atualizado ou 404.
- DELETE /eventos/{id}: 204 sem corpo ou 404.

O caminho antigo POST /eventos/ continua funcionando por redirecionamento 307
para /eventos. Clientes que não seguem redirecionamentos devem usar /eventos.
Foram preservadas as validações dos schemas; PUT exige atualização completa.

A atualização impede reduzir capacidade abaixo do número de participantes
inscritos, retornando 409. Durante esta transição, considera tanto registros ORM
quanto inscrições em memória, unindo os IDs dos participantes para evitar duplicação.
Essa verificação pertence à atualização de eventos; a migração da criação de
inscrições e seu controle completo de vagas continuam reservados à etapa 6.

Excluir um evento confirma a remoção no banco antes de limpar inscrições em
memória. As inscrições persistentes são removidas pela cascata já configurada,
preservando os participantes.

A dependência get_db desfaz transações em caso de erro e sempre fecha a sessão.
Um handler SQLAlchemyError retorna HTTP 500 com mensagem genérica, sem SQL,
caminhos ou detalhes técnicos na resposta. Os services não contêm lógica HTTP.

## Compatibilidade durante a transição

As funções de inscrição receberam a sessão para consultar o evento no banco,
e passaram a ler a capacidade do objeto ORM. Essa adaptação foi necessária
para preservar as inscrições existentes depois de remover o CRUD de eventos
das listas. Não foi implementada persistência de participantes nem de inscrições.
Duplicidade de inscrição e falta de vagas ainda mantêm HTTP 400 até a etapa 6.

## Requisitos do PDF atendidos

- Seção 5.1: cadastrar, listar, consultar, atualizar e excluir eventos via SQLite
  usando SQLAlchemy ORM.
- Seções 3 e 11: eventos permanecem disponíveis após reiniciar a aplicação.
- Seções 7 e 8: validação de entrada, proteção da capacidade na atualização,
  exclusão sem inscrições órfãs e tratamento genérico de falhas de persistência.
- Seção 9: controllers tratam HTTP, schemas validam e services consultam o ORM.

## Testes e resultados

Foram aprovados 23 testes automatizados: 14 anteriores e 9 novos testes da API.
Os testes novos cobrem CRUD, lista vazia, 404, 422, atualização completa,
compatibilidade de barra final, documentação OpenAPI, reinicialização da aplicação,
leitura em outro processo Python, inscrições transitórias, capacidade e cascata.

Falhas de commit foram simuladas em POST, PUT e DELETE. Todas retornaram 500
com mensagem genérica, sem alterações parciais; a lista de inscrições foi preservada
quando a exclusão falhou. Falha de consulta também foi simulada, com recuperação
na requisição seguinte e nenhuma conexão retida.

Adicionalmente, um teste HTTP real iniciou três processos Uvicorn sucessivos
usando o mesmo banco temporário. No primeiro, criou e atualizou um evento;
no segundo, confirmou os dados e excluiu o evento; no terceiro, confirmou 404
e lista vazia. As dez verificações HTTP passaram, incluindo /docs e OpenAPI.
Não houve validação visual do Swagger.

Evidências locais: tmp/check_stage4_live.py, tmp/stage4-live-results.json e
tmp/stage4-live-0.log a tmp/stage4-live-2.log. Nenhum dado de teste foi escrito
no eventos.db real. Os processos de teste foram encerrados ao final.

pip check e git diff --check passaram. Foi adicionado requirements-dev.txt com
httpx para TestClient. A versão atual do Starlette emite aviso de depreciação
do transporte httpx em favor de httpx2; isso não impediu os testes. A revisão
final das dependências permanece na etapa 9.

## Pendências

Etapa 5: participantes persistentes. Etapa 6: inscrições persistentes e controle
completo de vagas. Etapas 7 a 9: relatórios, revisão dos 12 cenários e entrega final.
Os antigos scripts pontuais da etapa 1 registram o contrato daquela etapa e não
substituem a suíte atual: os status de POST e DELETE de eventos foram atualizados.

A etapa 5 não foi iniciada.

## Referências técnicas

- [SQLAlchemy: transações e rollback](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#framing-out-a-begin-commit-rollback-block)
- [FastAPI: tratamento de erros](https://fastapi.tiangolo.com/tutorial/handling-errors/)
