# dashboard-analitico

Dashboard analítico em Python para análise acadêmica dos resultados de treinamento e das execuções da simulação multiagente em ambiente logístico 3D.

## Papel deste repositório na arquitetura

Este repositório é a camada analítica do TCC **"Neuroevolução aplicada à simulação de multiagentes em ambientes logísticos"**.

Relação com outros repositórios:

- **neuroevolucao-armazem-fases**: treinamento evolutivo de agentes e persistência de resultados no Supabase.
- **godot-3d**: execução dos agentes no simulador 3D e geração de telemetria de execução.
- **dashboard-analitico** (este): leitura de dados persistidos, análise de métricas e visualização interativa.

> Princípio: este dashboard depende de **contratos de dados** e resultados persistidos, sem dependência direta de código interno dos outros repositórios.

## Status atual

Implementação inicial de scaffolding:

- Estrutura de pastas da aplicação (`app/`, `tests/`, `docs/`, `data/samples/`).
- Entry point mínimo com Streamlit.
- Placeholders para carregamento de dados (Supabase e local).
- Placeholders para módulos de análise e visualização.
- Teste básico de importação dos módulos principais.

A definição formal do **contrato de dados analítico** ainda está em andamento.

## Estrutura inicial

```text
app/
  main.py
  pages/
  data/
  analysis/
  visualizations/
tests/
data/samples/
docs/
```

## Configuração do ambiente

### 1) Criar e ativar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependências

```bash
pip install -r requirements.txt
```

### 3) Configurar variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Variáveis utilizadas:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `LOCAL_RESULTS_PATH` (opcional, padrão: `data/samples`)

> Não versione segredos. O arquivo `.env` está ignorado no Git.

## Executar aplicação Streamlit

```bash
streamlit run app/main.py
```

## Testes

```bash
pytest -q
```
