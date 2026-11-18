# Etapa 2: configuração do SQLite e SQLAlchemy

Concluída em 16/11/2026, exclusivamente na APS 3. A APS 2 permanece preservada.

## Alterações

- Instalado SQLAlchemy 2.0.58 na `.venv` e registrado em `requirements.txt`.
- Configurados engine SQLite, URL absoluta e base declarativa em `database.py`.
- Banco localizado em `eventos.db`, na raiz da APS 3, e ignorado pelo Git.
- Habilitada a verificação de chaves estrangeiras em cada nova conexão.
- Configurado controle transacional com `autocommit=False` no driver SQLite.
  Essa configuração requer Python 3.12 ou superior; o ambiente utiliza Python 3.13.15.
- Disponibilizada a dependência `get_db()`, com uma sessão por uso, rollback
  em caso de exceção e fechamento garantido. Não há commit automático:
  os serviços controlarão a confirmação das operações.
- Adicionada `criar_tabelas()`, baseada em `Base.metadata.create_all()`.
- Integrada a inicialização ao lifespan do FastAPI; o engine libera seu pool
  no encerramento.
- Documentada a configuração no README e adicionados testes de infraestrutura.

A criação das tabelas depende dos modelos registrados na metadata. Como a etapa 3
ainda não foi autorizada, não existem tabelas de Evento, Participante ou Inscrição.
O arquivo SQLite é criado na inicialização, mas as rotas continuam usando listas
em memória. Os modelos existentes ainda são Pydantic e não foram alterados.

## Requisitos do PDF

Atendidos nesta etapa: configuração organizada da conexão, fábrica de sessões,
disponibilização de sessões para uso posterior nas rotas e serviços e liberação
das sessões (seção 3.1). Preparado o mecanismo de criação de tabelas a partir dos
modelos (seção 3.2), cuja aplicação às entidades depende da etapa 3.
Também foram registrados a nova dependência (seção 10) e o caminho do banco no
README (seções 3.1 e 13).

O PRAGMA usado na configuração não substitui as operações ORM da aplicação.
Ele apenas ativa a verificação de chaves estrangeiras do SQLite.

## Testes e resultados

Comando dos testes de infraestrutura:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Cinco testes aprovados:

1. Caminho absoluto do banco, limitado à raiz da APS 3.
2. Criação idempotente de tabelas de teste, sem apagar registros, com dados
   mantidos após descarte do pool e reconexão ao arquivo temporário.
3. Chaves estrangeiras ativadas em novas conexões e rejeição de referência inválida.
4. Fechamento de sessão sem confirmação implícita de escrita e sem conexão retida.
5. Rollback e fechamento após exceção, sem gravação parcial ou conexão retida.

As tabelas auxiliares desses testes existem apenas em bancos temporários.
Não são entidades nem tabelas da aplicação.

Também foram aprovadas as 25 verificações HTTP da etapa 1, incluindo CRUD atual,
inscrições, erros esperados, `/docs` e `/openapi.json`. A API iniciou em cerca de
1,79 s sem recarga e 1,78 s com `--reload`. O teste da documentação foi HTTP,
sem nova verificação visual no navegador.

Verificação direta confirmou o arquivo `eventos.db`, ausência de tabelas de domínio,
`PRAGMA foreign_keys=1` e nenhuma conexão emprestada ao final. A criação também
foi executada após mudar a pasta de trabalho para `tmp`, mantendo o banco na raiz.
`pip check` e `git diff --check` passaram.

## Pendências

Etapa 3: definir e importar os modelos ORM, relacionamentos e schemas Pydantic;
então comprovar a criação das tabelas reais. Etapas 4 a 6: integrar as sessões aos
serviços e rotas, migrar o CRUD e implementar integridade e tratamento de falhas
de persistência. Etapas 7 a 9: relatórios, testes completos e revisão da entrega.

Não foi demonstrada persistência dos eventos pelas rotas nesta etapa.
A etapa 3 aguarda solicitação explícita do usuário.

## Referências técnicas

- [SQLAlchemy: suporte SQLite e chaves estrangeiras](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support)
- [SQLAlchemy: ciclo de vida das sessões](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [FastAPI: lifespan](https://fastapi.tiangolo.com/advanced/events/)
