# Etapa 7: três relatórios obrigatórios

Concluída em 17/11/2026, exclusivamente na APS 3. A APS 2 permanece preservada.

## Alterações e requisitos atendidos

Criados controller/relatorio_controller.py, service/relatorio_service.py e
schema/relatorio_schema.py; o router foi registrado no FastAPI.

As rotas implementam os campos das seções 6.1 a 6.3 do PDF:

- GET /relatorios/eventos/ocupacao: evento_id, titulo, capacidade,
  total_inscritos, vagas_disponiveis e percentual_ocupacao.
- GET /relatorios/eventos/categorias: categoria, total_eventos,
  capacidade_total e total_inscricoes.
- GET /relatorios/participantes/cursos: curso, total_participantes e total_inscricoes.

Cada rota executa uma consulta SQLAlchemy, com agregações realizadas no SQLite,
retornando JSON validado pelo schema de resposta. Não há valores de resultado
fixos nem cache. Dados vazios retornam lista vazia com HTTP 200 (seção 6.4).
Controllers tratam HTTP, services realizam consultas e schemas definem respostas
(seção 9). As sessões e o tratamento genérico de falhas existentes são reutilizados.

## Contagens e ordenação

Ocupação e categorias usam uma subconsulta com uma linha por evento inscrito.
O LEFT JOIN preserva eventos sem inscrições. Essa agregação anterior ao join
impede multiplicar capacidade pelo número de inscrições. Não se usa SUM DISTINCT
da capacidade, que descartaria indevidamente eventos com capacidades iguais.

A ocupação é arredondada para duas casas decimais. NULLIF e COALESCE protegem
contra divisão por zero; o modelo normalmente já impede capacidade não positiva.
Vagas disponíveis correspondem à capacidade menos o total de inscrições.

Cursos usam COUNT DISTINCT do ID do participante e COUNT do ID da inscrição,
preservando participantes sem inscrições via LEFT JOIN. Um participante inscrito
em vários eventos conta uma vez como participante e várias vezes como inscrição.

Eventos são ordenados por ID; categorias e cursos, pelo texto cadastrado.
Não foi adicionada normalização de categorias ou cursos.

## Testes e resultados

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

49 testes aprovados: 41 anteriores e 8 novos. Cobertura dos relatórios:

- Banco vazio e eventos vazios, parcialmente ocupados e lotados.
- Percentual de 1/3 arredondado para 33.33 e ocupação total de 100.0.
- Categorias com eventos de capacidade igual e múltiplas inscrições.
- Cursos com participantes sem inscrição e participante inscrito em vários eventos.
- Atualização após inscrição, mudança de capacidade, categoria, título e curso.
- Atualização após exclusão de participante e de evento, considerando cascata.
- Resultados preservados após reiniciar a aplicação.
- Uma única consulta SELECT por relatório, sem consultas adicionais por registro.
- Rotas presentes no OpenAPI, /docs acessível, falhas de consulta com resposta
  genérica 500 e nenhuma conexão retida.

O teste HTTP real usou três processos Uvicorn sucessivos e o mesmo banco temporário.
Confirmou dados vazios, evento sem inscrição, agregações, reinicialização e
atualização após PUT e DELETE. As respostas observadas incluem:

```json
{
  "ocupacao": [
    {"evento_id": 1, "titulo": "Workshop", "capacidade": 3, "total_inscritos": 1, "vagas_disponiveis": 2, "percentual_ocupacao": 33.33},
    {"evento_id": 2, "titulo": "Workshop", "capacidade": 3, "total_inscritos": 0, "vagas_disponiveis": 3, "percentual_ocupacao": 0.0}
  ],
  "categorias": [
    {"categoria": "Workshop", "total_eventos": 2, "capacidade_total": 6, "total_inscricoes": 1}
  ],
  "cursos": [
    {"curso": "Computacao", "total_participantes": 1, "total_inscricoes": 1}
  ]
}
```

Esse objeto reúne as respostas das três rotas para documentação; cada rota retorna
sua própria lista. Após mudar capacidade para 4, categoria para Palestra e curso
para Direito, a ocupação passou a 25.0 e os agrupamentos refletiram as alterações.
As exclusões posteriores zeraram as inscrições e removeram grupos sem registros.

Evidências locais: tmp/check_stage7_live.py, tmp/stage7-live-results.json e
tmp/stage7-live-0.log a tmp/stage7-live-2.log. Nenhum dado de teste foi escrito
no banco real. Os processos de teste foram encerrados. Não houve teste visual
do Swagger. pip check e git diff --check passaram.

O aviso conhecido de depreciação do transporte httpx permanece para a etapa 9.

## Pendências

Etapa 8: revisão de integridade e demonstração consolidada dos 12 cenários do PDF.
Etapa 9: README completo, revisão de dependências e conferência final da entrega.
A etapa 8 não foi iniciada.

## Referência técnica

[SQLAlchemy: agregações e subconsultas](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html)
