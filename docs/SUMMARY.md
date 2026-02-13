# Resumo Executivo - X-Health Default Prediction

> **Versão**: 3.0.0 | **Data**: 2026-02-12 | **Status**: Produção

---

## Visão Geral

Modelo de machine learning para predição de default (calote) em transações B2B da X-Health.

**Destaques**:
- Identificação de viés de maturação nos dados (achado crítico)
- StratifiedKFold CV ao invés de validação out-of-time
- Hyperparameter tuning com controles anti-overfitting
- SHAP analysis para interpretabilidade
- Otimização de threshold para diferentes cenários de negócio

---

## Estrutura do Projeto

```
exercicio_DSteam_shared4/
├── notebooks/                    # Notebooks Jupyter
│   ├── 1_EDA.ipynb              # Análise exploratória + viés de maturação
│   ├── 2_model_pipeline.ipynb   # Modelagem + tuning + SHAP
│   └── 3_prediction.ipynb       # Função de predição
├── models/                       # Pipeline treinado + metadados
├── scripts/                      # Scripts auxiliares
├── docs/                         # Documentação
├── _data/                        # Dataset
├── README.md                     # Enunciado original
└── requirements.txt              # Dependências
```

---

## Achado Crítico: Viés de Maturação

Últimos meses do dataset têm taxa de default artificialmente baixa (parcelas ainda não venceram).

| Maturação | Taxa Default | Status |
|-----------|-------------|--------|
| 12+ meses | ~18-20% | Maduro |
| 6-12 meses | ~16-18% | Intermediário |
| 0-6 meses | ~8-14% | Incompleto |

**Decisão**: StratifiedKFold CV (5 folds) ao invés de out-of-time validation.

---

## Pipeline de Modelagem

### Pré-processamento (ColumnTransformer)

| Tipo | Transformação | Features |
|------|--------------|----------|
| Numérico | SimpleImputer + RobustScaler | 20 features |
| Alta cardinalidade | SimpleImputer + TargetEncoder | tipo_sociedade, atividade_principal, forma_pagamento |
| Baixa cardinalidade | SimpleImputer + OneHotEncoder | opcao_tributaria |

**24 features raw → 28 features processadas**

### Modelos Comparados (6)
Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, **XGBoost** (vencedor), LightGBM

### Melhor Modelo: XGBoost

| Métrica | Valor |
|---------|-------|
| **Test ROC-AUC** | 0.925 |
| **CV ROC-AUC** | 0.921 ± 0.003 |
| **F1-Score** | 0.702 |
| **Precision** | 0.663 |
| **Recall** | 0.746 |

### Thresholds Otimizados

| Objetivo | Threshold | Uso |
|----------|-----------|-----|
| Balanceado (F1) | 0.575 | Equilibra precision e recall |
| Capturar defaults (F2) | 0.302 | Minimizar perdas financeiras |
| Evitar rejeições (F0.5) | 0.775 | Minimizar falsos alarmes |

### Pipeline Final
```
Pipeline([
    ('preprocessor', ColumnTransformer),   # encoding + scaling
    ('classifier', XGBoostClassifier)      # modelo otimizado
])
```

---

## Análises Implementadas

### Notebook 1: EDA (50 cells)
- Análise univariada/bivariada completa
- Análise temporal detalhada
- Identificação de viés de maturação
- Boxplots comparativos (Pago vs Default)

### Notebook 2: Pipeline (73 cells)
- Feature engineering (ratios, flags)
- ColumnTransformer (Target Encoding + RobustScaler + OneHotEncoder)
- 6 modelos com StratifiedKFold CV
- Hyperparameter tuning (RandomizedSearchCV)
- Feature importance com nomes descritivos
- SHAP analysis
- Otimização de threshold (4 cenários de custo)

### Notebook 3: Predição (15 cells)
- Funções `predict_default()` e `predict_default_batch()`
- Exemplos práticos
- Comparação de thresholds
- Validação com dados reais

---

## Como Usar

```bash
# 1. Instalar
pip install -r requirements.txt

# 2. Executar notebooks em ordem
# notebooks/1_EDA.ipynb → notebooks/2_model_pipeline.ipynb → notebooks/3_prediction.ipynb
```

---

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [PROJECT_README.md](PROJECT_README.md) | Documentação técnica completa |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de versões |
| [INDEX.md](INDEX.md) | Índice de navegação |
| [SUMMARY.md](SUMMARY.md) | Este resumo executivo |

---

**Versão**: 3.0.0 | **Data**: 2026-02-12
