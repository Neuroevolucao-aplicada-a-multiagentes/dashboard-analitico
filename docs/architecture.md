# Arquitetura inicial do dashboard analítico

## Fluxo de dados (alto nível)

1. **neuroevolucao-armazem-fases** executa o treinamento e persiste resultados no Supabase.
2. **godot-3d** executa agentes treinados na simulação 3D e persiste telemetria no Supabase e/ou arquivos locais de resultados.
3. **dashboard-analitico** lê os resultados persistidos, calcula métricas analíticas e apresenta visualizações para análise acadêmica.

## Princípio arquitetural

O dashboard depende de **contratos de dados e resultados persistidos**.
Ele **não** deve importar código interno dos repositórios de treinamento ou simulação.

## Status atual

- Estrutura inicial do projeto Python criada.
- Placeholders para carregamento de dados (Supabase e local) criados.
- Placeholders para análise e visualizações criados.
- App Streamlit mínimo criado.

## Funcionalidades planejadas (não implementadas nesta etapa)

- Definição formal dos contratos de dados analíticos.
- Métricas avançadas de treinamento e execução.
- Comparações entre treinamento e comportamento observado na simulação.
- Dashboard interativo completo com múltiplas páginas e filtros.
