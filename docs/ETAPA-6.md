# Etapa 6: inscrições persistentes e controle de vagas

Concluída em 17/11/2026, exclusivamente na APS 3. A APS 2 foi preservada.

## Alterações

O serviço de inscrições agora utiliza SQLAlchemy ORM e sessões por requisição.
A criação verifica evento, participante, duplicidade e disponibilidade, nessa ordem.
POST /eventos/{evento_id}/inscricoes/{participante_id} retorna 201 com id,
evento_id, participante_id e data_inscricao. ID e data são gerados no momento da
inserção; a data segue a configuração existente de data local do servidor.

Evento ou participante inexistente retorna 404. Inscrição duplicada retorna 409
com "Participante já está inscrito neste evento." Evento lotado retorna 409 com
"Não existem vagas disponíveis para este evento." IDs não positivos ou de formato
inválido são rejeitados com 422. A restrição UNIQUE do banco permanece como proteção
adicional; somente a violação específica do par evento/participante é traduzida
como duplicidade. Demais falhas de integridade recebem o tratamento genérico 500.

GET /eventos/{evento_id}/inscricoes utiliza um join pelo relacionamento ORM
Participante.inscricoes, sem consultas individuais para cada inscrito. Retorna
ParticipanteRead na ordem do ID da inscrição, lista vazia para evento sem inscritos
ou 404 para evento inexistente.

O armazenamento em listas e o arquivo service/dados.py foram removidos.
Os serviços de eventos e participantes deixaram de manter compatibilidade com
inscrições em memória. A cascata no banco remove inscrições relacionadas quando
um evento ou participante é excluído. Excluir um participante libera suas vagas.
Dados mantidos apenas na memória de execuções anteriores não foram migrados.

## Controle transacional de vagas

A inscrição e o PUT de evento executam primeiro um UPDATE SQLAlchemy que mantém
a capacidade atual. Ele obtém o bloqueio de escrita SQLite antes de consultar
o evento e contar inscrições. O bloqueio permanece até commit ou rollback,
serializando inscrições e alterações de capacidade, inclusive entre processos
que utilizem este mesmo fluxo e arquivo SQLite.

A capacidade não pode ser reduzida abaixo da quantidade persistida de inscritos.
O aumento permite novas inscrições. A proteção depende dos serviços: alterações
arbitrárias feitas diretamente no banco, fora da aplicação, não são cobertas por
essa regra de lotação. Não foi introduzido trigger ou contador redundante.

SQLite permite apenas uma transação de escrita por vez, portanto o bloqueio
também pode fazer operações de eventos diferentes aguardarem. Bloqueio prolongado
pode superar o timeout padrão do driver e retornar erro genérico 500; não é
interpretado como falta de vagas. Falhas provocam rollback e fechamento da sessão.

## Requisitos do PDF atendidos

- Seções 3 e 4.3: inscrição persistente com ID, data e referências válidas.
- Seção 5.3: inscrição, verificações prévias e consulta dos participantes por
  relacionamentos SQLAlchemy.
- Seções 7 e 8: unicidade, vagas consistentes, proteção na atualização, cascata
  sem órfãos e códigos 404/409/422 com mensagens sem detalhes internos.
- Seção 9: controllers tratam HTTP; services tratam consultas e regras.
- Seção 11: inscrição, duplicidade, evento inexistente, lotação e persistência
  após reinicialização demonstrados. Os cenários dos relatórios ainda não se aplicam.

## Testes e resultados

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

41 testes aprovados: 32 existentes, adaptados à remoção das listas, e 9 novos
de inscrições, com subcasos. Os testes usam bancos temporários.

Os testes novos verificam campos e data, relacionamentos, lista vazia, duplicidade
antes da lotação, 404/422, recuperação após falhas, reinicialização, aumento e redução
de capacidade e liberação de vaga após excluir participante. Falhas de flush,
commit, integridade e leitura foram simuladas; não deixaram inscrições parciais
nem expuseram detalhes técnicos.

Três testes concorrentes com sessões distintas passaram:

1. Quatro participantes disputando uma vaga: um 201 e três 409, com uma inscrição.
2. Três requisições para o mesmo participante: um 201 e dois 409, sem duplicação.
3. Inscrição disputando com redução de capacidade: somente a operação compatível
   foi aceita; a quantidade de inscritos permaneceu menor ou igual à capacidade.

A primeira execução identificou um join ORM orientado incorretamente na consulta
dos inscritos. Foi corrigido para Participante.inscricoes e toda a suíte passou.

Vinte verificações HTTP reais passaram em três processos Uvicorn sucessivos,
usando o mesmo banco temporário. Confirmaram inscrição após reiniciar, persistência
dos conflitos, liberação de vaga após excluir participante, nova inscrição,
exclusão em cascata do evento e preservação do participante. /docs e OpenAPI
retornaram 200; não houve teste visual do Swagger.

Evidências locais: tmp/check_stage6_live.py, tmp/stage6-live-results.json e
tmp/stage6-live-0.log a tmp/stage6-live-2.log. Processos encerrados após os testes;
nenhum dado de teste foi inserido no banco real.

pip check e git diff --check passaram. O aviso conhecido do transporte httpx
no Starlette permanece para revisão das dependências na etapa 9.

## Pendências

Etapa 7: três relatórios dinâmicos obrigatórios. Etapa 8: revisão de integridade
e demonstração consolidada dos 12 cenários. Etapa 9: revisão final do README,
dependências e entrega. A etapa 7 não foi iniciada.

## Referências técnicas

- [SQLite: transações e bloqueios de escrita](https://www.sqlite.org/lang_transaction.html)
- [SQLAlchemy: UPDATE com entidades ORM](https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html)
