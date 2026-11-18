# Etapa 3: modelos ORM, relacionamentos e schemas Pydantic

Concluída em 16/11/2026, exclusivamente na APS 3. Nenhum arquivo da APS 2 foi alterado.

## Alterações

Os arquivos de `model/` agora representam entidades SQLAlchemy:

- `Evento`: id, titulo, descricao, data, horario, local, capacidade e categoria.
- `Participante`: id, nome, email e curso.
- `Inscricao`: id, evento_id, participante_id e data_inscricao.

Todos os campos são obrigatórios no banco. Os IDs são gerados pelo SQLite.
A data da inscrição usa `date.today` como valor padrão executado pelo ORM no momento
da inserção, com a data local do servidor. Não é um horário nem um timestamp.

Evento e Participante possuem relacionamentos bidirecionais com Inscricao.
O banco aplica unicidade do e-mail e do par evento/participante, referências válidas
e capacidade maior que zero. O e-mail usa NOCASE do SQLite, cuja comparação sem
distinção de caixa é limitada a ASCII; não há promessa de normalização Unicode.

Excluir um evento ou participante remove somente suas inscrições relacionadas,
preservando a outra entidade. Essa política utiliza `ON DELETE CASCADE` no banco
e `cascade="all, delete-orphan"` com `passive_deletes=True` no ORM.

Os schemas ficam em `schema/`, separados entre criação, atualização completa
por PUT e leitura. A inscrição possui schemas de criação e leitura; a API não
prevê atualização de inscrição. Os schemas de leitura usam `from_attributes=True`
e não incluem coleções recursivas.

As validações mantêm os campos obrigatórios, capacidade positiva, datas, horários
e e-mail válidos. Os textos são aparados, rejeitando campos compostos apenas por
espaços. IDs de inscrição precisam ser positivos.

Os controllers de eventos e participantes passaram a importar os schemas de
entrada. Essa mudança mantém a API executável após converter `model/` para ORM.
Os serviços continuam usando listas; não foi iniciado o CRUD persistente.
Schemas de saída e inscrição serão integrados às rotas nas próximas etapas.

`criar_tabelas()` importa o pacote `model` antes de `create_all()`. A inicialização
cria `eventos`, `participantes` e `inscricoes` em `eventos.db`, sem apagar dados.
`create_all()` não altera tabelas antigas existentes; migrações não foram implementadas.

## Requisitos do PDF

- Seções 3.2 e 4: tabelas derivadas dos modelos, campos mínimos, tipos e relacionamentos.
- Seção 7: validações Pydantic e restrições de integridade no banco, incluindo
  unicidade e exclusões sem inscrições órfãs.
- Seção 9: separação entre representação ORM e validação Pydantic.

A aplicação das regras de vagas e o tratamento HTTP de falhas de persistência
dependem da integração dos serviços nas etapas 4 a 6.

## Testes e resultados

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

14 testes aprovados: 5 de infraestrutura e 9 de modelos/schemas, com subcasos.
Os testes novos verificam:

- Gravação em arquivo temporário e leitura dos relacionamentos após reconexão.
- Geração de ID e data da inscrição; serialização ORM para schemas de leitura.
- Rejeição de e-mails duplicados, inclusive com diferença de caixa ASCII.
- Rejeição de inscrição duplicada e referências inexistentes.
- Rejeição no banco de capacidade não positiva e campo obrigatório nulo.
- Exclusão de cada entidade principal com coleções carregadas, não carregadas
  e por DELETE executado pelo SQLAlchemy, sem inscrições órfãs.
- Exclusão da inscrição removida da coleção ORM, preservando o participante.
- Validações de entrada e manutenção dos campos obrigatórios no PUT.

Uma primeira execução detectou reutilização de e-mail na preparação dos subcasos
de exclusão. O teste foi corrigido para limpar a entidade sobrevivente entre os
subcasos; a restrição de unicidade do modelo funcionou corretamente.

As 25 verificações HTTP locais da etapa 1 passaram, incluindo CRUD em memória,
inscrições, validações, `/docs` e OpenAPI. Não houve teste visual do Swagger.
A inspeção do banco real confirmou as três tabelas com todos os campos, as duas
chaves estrangeiras com CASCADE e a restrição composta de unicidade.
Os testes de escrita ORM usam bancos temporários, sem inserir dados de teste no
banco real. `pip check` e `git diff --check` passaram.

## Pendências

Etapa 4: CRUD de eventos persistente. Etapa 5: participantes persistentes.
Etapa 6: inscrições persistentes e controle de vagas, incluindo HTTP 409 e proteção
contra redução de capacidade abaixo da quantidade de inscritos.
Etapas 7 a 9: relatórios, revisão de integridade e entrega final.

A persistência via rotas e os 12 cenários finais do PDF ainda não estão concluídos.
A etapa 4 aguarda autorização explícita do usuário.

## Referências técnicas

- [SQLAlchemy: cascatas no ORM e no banco](https://docs.sqlalchemy.org/en/20/orm/cascades.html#using-foreign-key-on-delete-cascade-with-orm-relationships)
- [Pydantic: validação a partir de atributos](https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances)
