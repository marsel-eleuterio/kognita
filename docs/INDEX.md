# Índice de Documentação - X-Health Default Prediction

> Guia centralizado para navegação do projeto

---

## Início Rápido

1. Leia o [SUMMARY.md](SUMMARY.md) (5 min)
2. Execute `notebooks/1_EDA.ipynb`
3. Execute `notebooks/2_model_pipeline.ipynb`
4. Execute `notebooks/3_prediction.ipynb`

---

## Estrutura do Projeto

```
exercicio_DSteam_shared4/
│
├── notebooks/                         # Notebooks Jupyter
│   ├── 1_EDA.ipynb                   # Análise exploratória + viés de maturação
│   ├── 2_model_pipeline.ipynb        # Modelagem + tuning + SHAP
│   └── 3_prediction.ipynb            # Função de predição
│
├── models/                            # Artefatos do modelo
│   ├── model_xgboost_*.pkl           # Pipeline treinado
│   └── model_metadata.json           # Metadados e métricas
│
├── scripts/                           # Scripts auxiliares
├── docs/                              # Documentação (você está aqui)
├── _data/                             # Dataset original
├── README.md                          # Enunciado do exercício
└── requirements.txt                   # Dependências
```

---

## Documentos

| Documento | Descrição | Tempo |
|-----------|-----------|-------|
| [SUMMARY.md](SUMMARY.md) | Resumo executivo | 5 min |
| [PROJECT_README.md](PROJECT_README.md) | Documentação técnica completa | 15 min |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de versões (v1→v2→v3) | 5 min |
| [INDEX.md](INDEX.md) | Este índice | 2 min |
| [README.md](../README.md) | Enunciado original (Kognita) | 5 min |

---

## Notebooks

| # | Notebook | Descrição | Tempo | Cells |
|---|----------|-----------|-------|-------|
| 1 | `notebooks/1_EDA.ipynb` | Análise exploratória + viés de maturação + clusters | 30-60 min | 57 |
| 2 | `notebooks/2_model_pipeline.ipynb` | Modelagem + CV + tuning + SHAP + threshold | 45-90 min | 73 |
| 3 | `notebooks/3_prediction.ipynb` | Função de predição | 15-30 min | 16 |

---

## Navegação por Perfil

### Stakeholder (não-técnico)
1. [SUMMARY.md](SUMMARY.md) — visão geral e resultados
2. [PROJECT_README.md](PROJECT_README.md) — seções "Sobre" e "Resultados"

### Cientista de Dados
1. [SUMMARY.md](SUMMARY.md) — visão rápida
2. `notebooks/1_EDA.ipynb` — análise exploratória
3. `notebooks/2_model_pipeline.ipynb` — pipeline completo
4. [CHANGELOG.md](CHANGELOG.md) — decisões técnicas

### Desenvolvedor
1. `notebooks/3_prediction.ipynb` — API de predição
2. [PROJECT_README.md](PROJECT_README.md) — instalação e uso

---

## Busca por Tópico

| Tópico | Onde |
|--------|-----|
| Valores negativos e anomalias | `1_EDA.ipynb` (seção 6.1) |
| Testes estatísticos (Mann-Whitney) | `1_EDA.ipynb` (seção 6.2) |
| Análise de clusters | `1_EDA.ipynb` (seção 9.1) |
| Viés de maturação | `1_EDA.ipynb` (seção 10) |
| Feature engineering (7 features) | `2_model_pipeline.ipynb` (seção 3) |
| Pré-processamento | `2_model_pipeline.ipynb` (seção 5) |
| Hyperparameter tuning | `2_model_pipeline.ipynb` (seção 9.1) |
| SHAP analysis | `2_model_pipeline.ipynb` (seção 12.1) |
| Otimização de threshold | `2_model_pipeline.ipynb` (seção 11) |
| Feature importance | `2_model_pipeline.ipynb` (seção 12) |
| Função de predição | `3_prediction.ipynb` (seção 3) |
| Instalação | [PROJECT_README.md](PROJECT_README.md) |
| Métricas do modelo | [PROJECT_README.md](PROJECT_README.md) / [SUMMARY.md](SUMMARY.md) |

---

## Instalação

```bash
pip install -r requirements.txt
python -c "import pandas, sklearn, xgboost, lightgbm, shap; print('OK')"
```

---

**Versão**: 3.3.0 | **Data**: 2026-02-13
