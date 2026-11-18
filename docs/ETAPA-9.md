# Etapa 9: documentação, dependências e conferência da entrega

Concluída em 17/11/2026, exclusivamente na APS 3. A pasta da APS 2 e os registros
do banco real foram preservados. Não foram realizados commit, push ou deploy.

## Alterações e requisitos do PDF

O README foi reescrito para apresentar a APS 3: objetivo, ambiente suportado,
instalação, execução, estrutura, responsabilidades, banco, campos, relacionamentos,
integridade, rotas, erros, exemplos JSON, três relatórios, testes e empacotamento.
Isso atende ao conteúdo documental das seções 10 e 13 do PDF. O caminho do banco
e a ausência de migrações foram documentados, conforme seção 3.

requirements.txt fixa as dependências diretas e transitivas de execução.
requirements-dev.txt acrescenta httpx2 2.16.2, httpcore2 2.16.2 e truststore 0.10.5.
A troca do httpx pelo transporte httpx2 removeu o aviso de depreciação do TestClient,
com a suíte completa aprovada. Pacotes antigos existentes na venv de trabalho
não foram removidos; a validação de instalação foi feita em outra venv, limpa.

O ambiente de referência é CPython 3.13.15 em Windows x64. O código requer Python
3.12 ou superior pela configuração transacional SQLite; outras versões/sistemas
não foram validados. A lista exata instalada está em
[evidencias/ambiente-etapa9.txt](evidencias/ambiente-etapa9.txt).

O script scripts/preparar_entrega.py gera um ZIP com código, testes, documentação,
evidências e dependências. Inclui manifesto SHA-256 por arquivo e checksum externo
do pacote. Não inclui .git, ambientes virtuais, eventos.db, .env, caches ou tmp.
Os padrões de exclusão de backup, tmp e output também estão no .gitignore.

## Validação em ambiente limpo

1. Criada uma venv nova em tmp/validacao-etapa9-venv, sem reutilizar pacotes globais.
2. Instalado requirements-dev.txt, incluindo os requisitos de execução fixados.
3. Gerado o pacote, verificados seus hashes, ausência de dados locais e integridade
   do ZIP, e extraído em tmp/entrega-etapa9-extraida.
4. Executados os testes a partir dessa pasta, com o Python da venv nova:
   **52 testes aprovados em 47,520 segundos**, sem aviso de depreciação do TestClient.
5. Executado o demonstrador nessa cópia: **12 cenários e 55 requisições HTTP reais
   aprovados**, com reinicialização do processo da API sobre o mesmo banco temporário.
6. Conferidos pip check, git diff --check e correspondência dos arquivos de código
   e dependências com os hashes da cópia efetivamente testada.

Os testes usam bancos temporários. A aplicação não exigiu o arquivo eventos.db
original para criar as tabelas e executar os fluxos. /docs e OpenAPI responderam
200 no demonstrador; não foi realizada demonstração visual pelo Swagger.

As mudanças posteriores à validação da cópia extraída se restringiram às novas
evidências e a este registro documental. O pacote final foi regenerado e seus
arquivos conferidos novamente com o manifesto.

Evidências:

- [Resumo da validação limpa](evidencias/etapa9-validacao.json).
- [Requisições e respostas dos 12 cenários](evidencias/etapa9-cenarios.json).
- [Dependências instaladas](evidencias/ambiente-etapa9.txt).

## Arquivos da entrega

- output/APS-3-Desenvolvimento-backend.zip.
- output/APS-3-Desenvolvimento-backend.sha256.
- output/MANIFESTO.json, também incluído dentro do ZIP.

Para regenerar:

```powershell
.\.venv\Scripts\python.exe scripts\preparar_entrega.py
```

O ZIP pode ser extraído em outra pasta; siga a instalação do README para criar
uma venv nova. O banco é criado no primeiro início da API. O pacote contém o
código atual do workspace, incluindo arquivos novos ainda não commitados.

## Pendências explícitas e publicação

**A demonstração pela interface Swagger exigida pelo PDF continua pendente.**
Os testes por HTTP real não foram apresentados como substituição integral dessa
exigência. O roteiro está em ETAPA-8.md. Não é correto afirmar que todos os itens
do PDF foram concluídos enquanto essa demonstração não for executada e registrada.

O remoto origin deste checkout ainda aponta para
https://github.com/Luizgsch/APS-2-Desenvolvimento-backend.git.
Ele não foi alterado e nenhum conteúdo foi enviado ao repositório da APS 2.
A entrega preparada é local. Se a entrega acadêmica exigir link de repositório,
publique a APS 3 em repositório próprio antes de enviar esse link.
