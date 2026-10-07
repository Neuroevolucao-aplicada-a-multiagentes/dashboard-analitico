# Diretrizes para Agentes de IA (AGENTS.md)

Este documento define as diretrizes e regras arquiteturais que todos os agentes e desenvolvedores devem seguir ao trabalhar no repositório `dashboard-analitico`.

## 1. Princípio Arquitetural de Desacoplamento
* O repositório `dashboard-analitico` consome **apenas dados persistidos** (banco de dados Supabase e arquivos locais/artefatos CSV/JSON/Parquet).
* **NUNCA importe código fonte** dos repositórios irmãos (`neuroevolucao-armazem-fases`, `godot-3d`).
* A integração entre repositórios é feita estritamente através do **Data Contract** (contrato de dados).

## 2. Acesso ao Supabase
* Todas as consultas analíticas ao banco de dados devem utilizar o schema `core` (`core.experiment`, `core.run`, `core.generation`, `core.checkpoint`).
* **Regra de Desempenho Crítica**: **NUNCA** crie consultas que extraiam a tabela `core.individual` inteira ou sem paginação/filtros específicos, prevenindo sobrecarga de memória e lentidão de rede.
* Métricas estendidas de evolução em `core.generation` são persistidas no campo JSONB `metrics` e devem ser descompactadas em colunas planas no DataFrame de análise.

## 3. Fachada Unificada (Data Manager)
* A camada analítica (`app/analysis/`) e as páginas do Streamlit (`app/pages/`) nunca devem chamar diretamente o Supabase ou carregar CSVs diretamente com caminhos rígidos.
* O acesso deve ser intermediado pela fachada unificada (`app/data/data_manager.py`), que garante paridade estrita de colunas e tipos de dados independentemente da origem (`local` ou `supabase`).

## 4. Testes e CI/CD
* Todos os testes devem rodar de forma isolada, determinística e rápida.
* Chamadas de rede para o Supabase devem ser **obrigatoriamente mockadas** com `unittest.mock` / `pytest-mock` para não depender de conexões externas no CI/CD.
