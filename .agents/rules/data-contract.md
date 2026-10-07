# Regras do Contrato de Dados (Data Contract)

Este documento especifica o contrato de dados formal para a camada analítica do projeto de Neuroevolução para Ambientes Logísticos.

## 1. Contrato Canônico de Métricas de Treinamento (`RunMetrics`)

Independentemente da fonte de dados (arquivo CSV via `sample_loader` ou banco de dados via `supabase_loader`), a camada analítica deve receber um DataFrame padronizado com as seguintes colunas e tipos garantidos:

### Colunas Inteiras Obrigatórias (Dtype: `int` / `int64`, default: `0`)
* `geracao`: Número sequencial da geração (1-indexado).
* `coletas`: Total acumulado ou por geração de tarefas de coleta realizadas.
* `entregas`: Total acumulado ou por geração de tarefas de entrega concluídas.
* `colisoes`: Quantidade de colisões registradas na geração.
* `mortos`: Quantidade de agentes que atingiram condição de término/morte.

### Colunas Ponto Flutuante Obrigatórias (Dtype: `float` / `float64`, default: `0.0`)
* `fit_medio`: Fitness médio da população na geração.
* `fit_melhor`: Melhor fitness registrado na geração.
* `fit_pior`: Pior fitness registrado na geração.
* `fit_std`: Desvio padrão do fitness da população.
* `taxa_coleta`: Taxa de sucesso de coleta.
* `taxa_entrega`: Taxa de sucesso de entrega.
* `melhor_tempo`: Melhor tempo de conclusão de tarefa.
* `tempo_medio_entrega`: Tempo médio gasto para efetuar entregas.
* `distancia_media_entrega`: Distância média percorrida para entregas.
* `taxa_mutacao_atual`: Taxa de mutação aplicada na geração.
* `forca_mutacao_atual`: Força/magnitude da mutação aplicada.
* `tempo_real_geracao_seg`: Tempo real de processamento da geração em segundos.

### Ordenação Garantida
* O DataFrame resultante deve sempre ser ordenado de forma estritamente ascendente por `geracao` (`df.sort_values(by="geracao")`), com índice reiniciado (`reset_index(drop=True)`).

---

## 2. Mapeamento da Origem Supabase (`core.generation`)

Ao carregar os dados de `core.generation` do Supabase:
1. **Descompactação de JSONB**: O campo `metrics` (JSONB) contém as métricas estendidas e deve ser expandido para colunas no DataFrame.
2. **Resolução de Aliases**:
   * `generation_number` -> mapeado para `geracao`.
   * `best_fitness` -> utilizado como fallback para `fit_melhor`.
   * `average_fitness` -> utilizado como fallback para `fit_medio`.
   * `worst_fitness` -> utilizado como fallback para `fit_pior`.
   * `median_fitness` -> preservado como `fit_mediana` se disponível.
3. **Imputação de Nulos**:
   * Valores ausentes ou nulos em colunas inteiras são preenchidos com `0`.
   * Valores ausentes ou nulos em colunas float são preenchidos com `0.0`.

---

## 3. Restrição de Segurança de Dados
* **Proibição de Extração Massiva**: É estritamente proibido criar endpoints ou loaders que realizem `SELECT * FROM core.individual` sem filtros refinados ou paginação estrita, para evitar saturação de tráfego de rede e consumo excessivo de memória RAM.
