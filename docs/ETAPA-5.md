# Etapa 5: CRUD de participantes persistente

Concluída em 17/11/2026, exclusivamente na APS 3. A APS 2 foi preservada.

## Alterações e requisitos atendidos

O serviço de participantes utiliza sessões SQLAlchemy para cadastrar, listar,
consultar, atualizar e excluir registros no SQLite (seção 5.2 do PDF).
POST retorna 201; GET e PUT retornam 200; DELETE retorna 204 sem corpo.
Participante inexistente retorna 404; entrada inválida retorna 422.
Os controllers usam ParticipanteRead, sem expor atributos internos ORM.
PUT continua exigindo todos os campos obrigatórios.

A restrição UNIQUE do banco garante a unicidade do e-mail, sem depender de
consulta prévia sujeita a disputa entre requisições. O serviço trata especificamente
a violação SQLite da coluna participantes.email, executa rollback e lança uma
exceção de negócio. O controller retorna 409 com a mensagem do PDF:
"Já existe um participante cadastrado com este e-mail."
Outras falhas de integridade continuam no tratamento genérico 500, sem serem
apresentadas como duplicidade de e-mail. Manter o próprio e-mail no PUT é permitido.

A configuração NOCASE existente impede duplicidades com diferenças de caixa
ASCII; não foi acrescentada normalização Unicode. Pydantic valida e-mail, campos
obrigatórios e textos vazios. Isso atende às seções 4.2, 7 e 8.

A exclusão confirma a remoção no banco antes de limpar inscrições em memória.
A cascata remove inscrições persistentes relacionadas, preservando eventos e
outros participantes. Sessões são fechadas e erros provocam rollback.
Controllers tratam HTTP; schemas validam; services operam o ORM (seção 9).

As funções transitórias de inscrição foram adaptadas para consultar participantes
pela sessão. A consulta dos inscritos usa ParticipanteRead e reflete mudanças
no cadastro. O registro das inscrições continua em memória até a etapa 6.

## Testes e resultados

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

32 testes aprovados: 23 anteriores e 9 novos, com subcasos. Os testes HTTP
compartilham preparação de banco temporário em tests/api_support.py.

Cobertura nova: CRUD, lista vazia, validações, atualização completa, 404, 422,
schemas de resposta, OpenAPI, e-mails duplicados em POST e PUT (incluindo caixa
ASCII), manutenção do próprio e-mail e recuperação após conflito.
Também foram verificadas persistência em nova inicialização da aplicação e
leitura por outro processo Python, cascata sem apagar eventos ou outros participantes,
compatibilidade com inscrições transitórias e atualização dos dados dos inscritos.

O teste anterior de eventos passou a conferir participantes preservados no banco,
em vez da antiga lista. Falhas de commit em POST, PUT e DELETE retornaram 500
sem gravação parcial ou limpeza indevida das inscrições em memória. Falha de leitura
e erro de integridade não relacionado ao e-mail também foram tratados sem expor
detalhes técnicos. As sessões não retiveram conexões após as requisições.

Onze verificações HTTP reais passaram com três processos Uvicorn sucessivos sobre
o mesmo banco temporário: criação e atualização no primeiro; leitura, rejeição
de duplicidade e exclusão no segundo; confirmação da exclusão no terceiro.
/docs e OpenAPI retornaram 200. Não houve verificação visual do Swagger.

Evidências locais: tmp/check_stage5_live.py, tmp/stage5-live-results.json e
tmp/stage5-live-0.log a tmp/stage5-live-2.log. Nenhum dado de teste foi inserido
no banco real e os processos de teste foram encerrados.

pip check e git diff --check passaram. Continua o aviso de depreciação do transporte
httpx pelo Starlette, registrado na etapa 4; os testes passaram.

## Pendências

Etapa 6: inscrições persistentes e controle completo de vagas. Duplicidade de
inscrição e evento sem vagas mantêm HTTP 400 até essa etapa.
Etapas 7 a 9: relatórios, revisão dos 12 cenários e entrega final.

A etapa 6 não foi iniciada.
