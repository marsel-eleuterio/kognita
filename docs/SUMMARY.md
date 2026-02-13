# Resumo Executivo - X-Health Default Prediction

> **Versão**: 3.3.0 | **Data**: 2026-02-13 | **Status**: Produção

---

## Visão Geral

Modelo de machine learning para predição de default (calote) em transações B2B da X-Health.

**Destaques**:
- Identificação de viés de maturação nos dados (achado crítico)
- StratifiedKFold CV ao invés de validação out-of-time
- 7 features derivadas com fundamentação de negócio
- Hyperparameter tuning com controles anti-overfitting
- SHAP analysis para interpretabilidade
- Otimização de threshold para diferentes cenários de negócio

---

## Estrutura do Projeto

```
exercicio_DSteam_shared4/
├── notebooks/                    # Notebooks Jupyter
│   ├── 1_EDA.ipynb              # Análise exploratória + clusters + viés de maturação
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

## Feature Engineering (7 features derivadas)

| Feature | Fórmula | Lógica |
|---------|---------|--------|
| `total_exposto` | vencido + por_vencer + quitado | Volume total de relacionamento |
| `razao_inadimplencia` | vencido / total_exposto | Grau de deterioração da carteira |
| `taxa_cobertura_divida` | quitado / pedido | Capacidade histórica de pagamento |
| `razao_vencido_pedido` | vencido / pedido | Alavancagem atual |
| `flag_risco_juridico` | 1 se protestos OU ações judiciais | Sinal binário de alerta |
| `ticket_medio_protestos` | valor_protestos / quant_protestos | Gravidade do problema jurídico |
| `qtd_parcelas` | contagem de '/' em forma_pagamento + 1 | Proxy de fluxo de caixa |

---

## Pipeline de Modelagem

### Pré-processamento (ColumnTransformer)

| Tipo | Transformação | Features |
|------|--------------|----------|
| Numérico | SimpleImputer + RobustScaler | 22 features (15 brutas + 7 derivadas) |
| Alta cardinalidade | SimpleImputer + TargetEncoder | atividade_principal, forma_pagamento |
| Baixa cardinalidade | SimpleImputer + OneHotEncoder | tipo_sociedade, opcao_tributaria, month |

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

### Notebook 1: EDA (57 cells)
- Análise univariada/bivariada completa
- Auditoria de valores negativos e anomalias (seção 6.1)
- Testes estatísticos Mann-Whitney U com effect size, KDE e violin plots (seção 6.2)
- Análise de esparsidade (zeros vs não-zeros) e impacto no default
- Matriz de correlação
- Análise de clusters K-Means com PCA e perfis de risco (seção 9.1)
- Análise temporal detalhada
- Identificação de viés de maturação e picos anomalos

### Notebook 2: Pipeline (73 cells)
- Feature engineering (7 features derivadas com fundamentação de negócio)
- ColumnTransformer (Target Encoding + RobustScaler + OneHotEncoder)
- 6 modelos com StratifiedKFold CV
- Hyperparameter tuning (RandomizedSearchCV)
- Feature importance com nomes descritivos
- SHAP analysis
- Otimização de threshold (4 cenários de custo)

### Notebook 3: Predição (16 cells)
- Funções `predict_default()` e `predict_default_batch()`
- Feature engineering automático (7 features derivadas)
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

**Versão**: 3.3.0 | **Data**: 2026-02-13
