# Etapa 8: testes e revisão de integridade

Validação realizada em 17/11/2026, exclusivamente na APS 3. A APS 2 não foi alterada.

## Resultado e limite da validação

Os 12 cenários funcionais da seção 11 do PDF passaram em uma demonstração HTTP
real com banco temporário e dois processos Uvicorn sucessivos. Foram registradas
55 requisições com método, rota, JSON enviado, status esperado, status observado
e JSON recebido em [evidencias/etapa8.json](evidencias/etapa8.json).

A execução pela interface Swagger continua pendente. O PDF exige testes usando
Swagger; a automação disponível informou que o host de navegador está indisponível.
Portanto, esta revisão não declara concluída essa parte do requisito. /docs e
/openapi.json responderam 200, mas isso não comprova uso do botão “Try it out”.

## Alterações desta etapa

- Adicionado scripts/validar_cenarios.py, um demonstrador reproduzível por HTTP
  real. Cria banco temporário, inicia e encerra a API, reinicia o processo sobre
  o mesmo arquivo e salva evidências JSON. Compara o hash do banco real antes
  e depois para verificar sua preservação.
- Adicionados três testes de integridade, com subcasos, sem mudar as regras da API.
- Registrada inspeção somente de leitura do banco real em
  [evidencias/integridade-etapa8.json](evidencias/integridade-etapa8.json).
- Acrescentadas instruções pontuais de teste ao README. A revisão final do README
  e das dependências continua na etapa 9.

## Matriz dos 12 cenários

| Nº do PDF | Cenário | Evidência observada |
|---|---|---|
| 1 | Cadastro e consulta de eventos | POST 201 e GET 200; campos e quantidade conferidos |
| 2 | Cadastro e consulta de participantes | POST 201 e GET 200; três participantes conferidos |
| 3 | Atualização e exclusão | PUT 200, DELETE 204 e GET posterior 404, para ambas as entidades |
| 4 | Inscrição | POST 201 com ID e data; participante consultado no evento |
| 5 | Inscrição duplicada | 409 com a mensagem prevista |
| 6 | Evento inexistente | 404; participante inexistente também conferido |
| 7 | Falta de vagas | Duas inscrições aceitas e terceira rejeitada com 409 |
| 8 | Persistência após reinicialização | Novo PID; eventos, participantes, inscritos, ID e data preservados |
| 9 | Ocupação | Evento cheio em 100.0%; evento vazio em 0.0% |
| 10 | Categorias | Dois eventos de mesma capacidade somados corretamente: capacidade 4 e duas inscrições |
| 11 | Cursos | Dois participantes em Computacao e duas inscrições; Direito com um participante e zero inscrições |
| 12 | Relatórios após mudanças | Nova inscrição, mudança de categoria/capacidade/curso e exclusões refletidas nas três rotas |

Os JSONs enviados e recebidos de cada linha estão na chave `cenarios`, identificados
pelo número do PDF. As assertivas do script verificam conteúdo, além do HTTP.
O campo `resultado` só recebe `aprovado` depois da execução bem-sucedida do cenário.

## Revisão adicional de integridade

A suíte completa aprovou 52 testes, incluindo os 49 anteriores e três novos:

1. Duas requisições simultâneas com o mesmo e-mail criaram um participante:
   um HTTP 201 e um HTTP 409, sem conexão retida.
2. Atualização direta das chaves estrangeiras de uma inscrição para IDs inexistentes
   foi rejeitada pelo SQLite. O rollback preservou as referências originais.
3. Uma consulta prévia simulada deixou de detectar inscrição duplicada. A restrição
   UNIQUE real rejeitou o INSERT; o serviço retornou 409 e manteve uma inscrição.

Os testes existentes também verificam disputa pela última vaga, inscrição versus
redução de capacidade, falhas de flush/commit/leitura, rollback, fechamento de
sessões, cascatas carregadas e não carregadas, validações Pydantic e agregações
sem duplicação. Nenhuma mudança funcional foi necessária nesta revisão.

No banco temporário da demonstração, após as cascatas: integrity_check retornou
`ok`, foreign_key_check retornou lista vazia e restaram zero inscrições.
No banco real, inspecionado com SQLite em `mode=ro`, integrity_check retornou `ok`,
foreign_key_check retornou lista vazia e a consulta encontrou zero inscrições órfãs.
O demonstrador confirmou que o hash do banco real permaneceu igual.

As consultas SQLite diretas do demonstrador servem apenas para auditar o arquivo
e as PRAGMAs de integridade. Os CRUDs e relatórios da aplicação continuam via ORM.

Na primeira execução do demonstrador, os cenários passaram, mas a limpeza do arquivo
temporário encontrou uma conexão de auditoria ainda aberta. O script foi corrigido
para fechar explicitamente essas conexões; a segunda execução terminou com código 0.
Os processos da API são encerrados em bloco finally, inclusive em caso de falha.

`pip check` e `git diff --check` passaram. Permanece o aviso conhecido de depreciação
do transporte httpx no TestClient do Starlette, sem falha nos testes. A revisão de
dependências fica para a etapa 9.

## Como repetir a validação

Na raiz da APS 3:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -X utf8 scripts\validar_cenarios.py
```

O demonstrador substitui seu arquivo de evidências pela execução mais recente.
Não remove nem preenche o banco real. Os dados de demonstração usam example.com.

## Roteiro para a demonstração pelo Swagger

Para usar um banco de demonstração separado, inicie o servidor auxiliar abaixo.
Use um nome de arquivo novo se esse arquivo já existir; não apague dados pessoais.

```powershell
New-Item -ItemType Directory -Force tmp | Out-Null
.\.venv\Scripts\python.exe scripts\validar_cenarios.py --serve .\tmp\swagger-etapa8.db 8001
```

Abra http://127.0.0.1:8001/docs. Expanda cada operação, selecione “Try it out”,
preencha os parâmetros e execute na ordem da matriz. Os corpos de entrada estão
no arquivo de evidências; substitua os IDs pelos retornados pelo seu banco.
Registre as respostas para os 12 cenários. Para o cenário 8, encerre o servidor
com Ctrl+C e repita o mesmo comando, mantendo o mesmo arquivo SQLite.

Na preparação, cadastre dois eventos Workshop de capacidade 2, três participantes
(dois de Computacao e um de Direito) e inscreva os dois primeiros no primeiro evento.
Isso reproduz os totais da matriz. No cenário 12, inscreva o primeiro participante
também no segundo evento; os participantes de Computacao continuam sendo dois,
mas suas inscrições passam a três. Mude a capacidade do primeiro evento para 4,
sua categoria para Palestra e o curso do primeiro participante para Direito.
Verifique os três relatórios antes e depois de excluir participante e eventos.

Este roteiro foi preparado, mas não foi executado pela interface nesta sessão.

## Pendências

- Executar e registrar a demonstração visual no Swagger, exigida pelo PDF.
- Etapa 9: documentação final, dependências reproduzíveis e conferência da entrega.

A etapa 9 não foi iniciada.
