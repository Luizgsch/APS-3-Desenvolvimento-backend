# Etapa 1: preparação e validação da execução

Validação realizada em 16/11/2026, exclusivamente na APS 3.

## Escopo e estado inicial

O PDF da APS 3 foi lido integralmente (13 páginas). Seus requisitos orientam as
etapas seguintes; esta etapa não implementa persistência, modelos ORM ou relatórios.
Não foram encontrados arquivos AGENTS.md adicionais nos caminhos locais consultados.
Foram seguidas as instruções fornecidas pelo usuário na conversa.

O Git já apresentava uma alteração em `controller/evento_controller.py` e o arquivo
`database.py` vazio, não rastreado. Ambos foram preservados. Os hashes dos arquivos
da aplicação, README e requirements foram comparados antes e depois, sem alterações.
A pasta da APS 2 não foi modificada.

## Ambiente corrigido

- Ambiente anterior preservado em `.venv-backup-etapa1/`, dentro da APS 3.
- `.venv/` recriada no caminho atual com CPython 3.13.15.
- Mesmas versões de todas as dependências anteriores reinstaladas e comparadas.
- Instalação de `requirements.txt` e `pip check` concluídas sem conflitos.
- Ativação pelo PowerShell e executáveis `pip.exe` e `uvicorn.exe` validados.
- Configurado o interpretador padrão do workspace em `.vscode/settings.json`.
- Backup e arquivos temporários excluídos apenas do Git local em `.git/info/exclude`.

Versões principais: FastAPI 0.141.1, Pydantic 2.13.5, Uvicorn 0.53.0,
email-validator 2.3.0. SQLite 3.50.4 está disponível na biblioteca padrão.
SQLAlchemy permanece ausente, reservado para a etapa 2.
O requirements ainda não fixa versões; sua consolidação permanece na etapa 9.

## Testes e resultados

Os testes utilizaram um processo Uvicorn isolado e requisições HTTP reais em
`127.0.0.1:8000`. Os processos de teste foram encerrados ao final.

- Inicialização normal: aproximadamente 1,30 s.
- Inicialização com `--reload`, observando o projeto: aproximadamente 1,24 s.
- `/`, `/docs` e `/openapi.json`: HTTP 200 nas duas formas de execução.
- HTML de `/docs` contém a inicialização do Swagger; OpenAPI contém as rotas esperadas.
- Cadastro, listagem, consulta, atualização e exclusão de eventos e participantes: aprovados.
- Inscrição e consulta dos inscritos: aprovadas.
- Exclusão de participante remove sua inscrição da lista em memória: aprovado.
- Evento inexistente: HTTP 404; e-mail inválido: HTTP 422.
- Inscrição duplicada: HTTP 400, comportamento atual registrado; adequação para 409 pendente.
- Dados temporários dos testes removidos; nova execução iniciou com listas vazias.
- `git diff --check`: aprovado.

Esses testes verificam a base atual em memória. Não comprovam os 12 cenários finais
da APS 3, que dependem do banco e dos relatórios.

A tentativa de verificação visual no navegador foi interrompida pela ferramenta:
o host de navegador estava indisponível e o controle nativo não conseguiu confirmar
a URL do Brave. Portanto, a interface Swagger e seus recursos externos não foram
validados visualmente, nem foram executadas operações pelo botão “Try it out”.

Evidências locais e script pontual estão em `tmp/check_stage1.py`,
`tmp/stage1-results.json`, `tmp/uvicorn.log`, `tmp/uvicorn-reload.log`,
`tmp/environment-before.txt`, `tmp/environment-after.txt` e `tmp/source-before.json`.
Esses arquivos são auxiliares locais, não uma suíte final de testes.

## Investigação do travamento

Há dois problemas distintos a considerar:

1. O ambiente copiado continha o caminho antigo
   `D:\Projetos2\api_eventos\.venv` nos scripts de ativação e em `pyvenv.cfg`.
   Essa inconsistência foi corrigida recriando o ambiente. Ela não comprova a causa
   do travamento da interface do VS Code.
2. Os logs do VS Code confirmam períodos sem resposta. Em
   `%APPDATA%\Code\logs\20261116T172222\main.log`, há perda de heartbeat do
   terminal às 17:23:48 e 17:23:58, janela sem resposta às 17:24:38 e amostra
   às 17:24:53. O log também registra espera por atualização do editor.
   A sessão `20261116T165958` registra janelas sem resposta e erros
   `net::ERR_INSUFFICIENT_RESOURCES`. Logs da extensão Python registram erros 193
   ao inspecionar aliases `python*.exe.__target__`; isso não é erro do interpretador
   real usado nos testes. O log da extensão Codex registra encerramento inesperado
   do app-server às 17:25:07.

Esses registros são indícios de problemas no editor, terminal e extensões.
Não permitem atribuir uma causa única nem afirmar falta de RAM.
A API executou sem travamento fora do terminal integrado, inclusive com `--reload`.
Não ocorreu WinError 10013 nestes testes. Nenhuma configuração global, extensão,
política de execução ou proteção do Windows foi alterada.

Se o travamento reaparecer no editor, será necessário correlacionar os novos logs
com o comando exato e capturar um perfil de desempenho durante o episódio.

## Relação com o PDF e pendências

Foi validada a base de execução de Python, FastAPI, Pydantic e Uvicorn (seção 10),
a disponibilidade HTTP da documentação (parte da seção 11) e uma amostra das
funcionalidades existentes que devem ser preservadas (seções 2 e 5).
Nenhum requisito de persistência foi declarado concluído nesta etapa.

Permanecem para as etapas 2 a 9: SQLite com SQLAlchemy, sessões, tabelas, entidades,
schemas separados, CRUD persistente, integridade, controle de vagas, relatórios,
12 cenários finais de teste, README e dependências reproduzíveis.

Para executar na raiz da APS 3, sem depender da ativação do terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

API: http://127.0.0.1:8000

Swagger: http://127.0.0.1:8000/docs

A etapa 2 aguarda solicitação explícita do usuário.
