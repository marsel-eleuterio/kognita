# X-Health Default Prediction Model
## Projeto de Machine Learning para Predição de Calote em Transações B2B

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.0-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Contexto de Negócio](#contexto-de-negócio)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Uso](#uso)
- [Notebooks](#notebooks)
- [Dataset](#dataset)
- [Metodologia](#metodologia)
- [Resultados](#resultados)
- [Reprodutibilidade](#reprodutibilidade)
- [Próximos Passos](#próximos-passos)

---

## Sobre o Projeto

Este projeto desenvolve um modelo de machine learning para **predição de default (calote)** em transações B2B da empresa X-Health, que comercializa dispositivos eletrônicos de saúde.

### Objetivo Principal
Criar um algoritmo capaz de inferir a **probabilidade de default** para um dado pedido, permitindo que o time financeiro tome decisões mais informadas e minimize perdas.

---

## Contexto de Negócio

- **Empresa**: X-Health (comércio B2B de dispositivos eletrônicos de saúde)
- **Modelo de Negócio**: Vendas à crédito (pagamento futuro à vista ou parcelado)
- **Problema**: Alto índice de não-pagamentos (defaults/calotes)
- **Solução Proposta**: Modelo probabilístico de predição de risco de crédito

---

## Estrutura do Projeto

```
exercicio_DSteam_shared4/
│
├── notebooks/                              # Notebooks Jupyter
│   ├── 1_EDA.ipynb                        # Análise Exploratória de Dados
│   ├── 2_model_pipeline.ipynb             # Pipeline de Modelagem
│   └── 3_prediction.ipynb                 # Função de Predição
│
├── models/                                 # Artefatos do modelo
│   ├── model_xgboost_*.pkl                # Pipeline treinado (preprocessor + classifier)
│   └── model_metadata.json                # Metadados, métricas e thresholds
│
├── scripts/                                # Scripts auxiliares
│   └── *.py                               # Scripts de manipulação de notebooks
│
├── docs/                                   # Documentação
│   ├── PROJECT_README.md                  # Este arquivo
│   ├── SUMMARY.md                         # Resumo executivo
│   ├── CHANGELOG.md                       # Histórico de versões
│   └── INDEX.md                           # Índice de navegação
│
├── _data/
│   └── dataset_2021-5-26-10-14.csv        # Dataset original
│
├── README.md                               # Enunciado original do exercício
└── requirements.txt                        # Dependências Python
```

---

## Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip ou conda

### Usando pip

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Verificar Instalação

```bash
python -c "import pandas, sklearn, xgboost, lightgbm, shap; print('OK')"
```

---

## Uso

### Execução dos Notebooks

Execute os notebooks na seguinte ordem:

1. **Análise Exploratória** — `notebooks/1_EDA.ipynb`
   - Explorar dados, identificar padrões
   - Observar análise de viés de maturação (seção crítica)

2. **Pipeline de Modelagem** — `notebooks/2_model_pipeline.ipynb`
   - Pré-processamento, feature engineering, treinamento
   - Hyperparameter tuning, SHAP analysis
   - **Output**: `models/model_*.pkl` e `models/model_metadata.json`

3. **Função de Predição** — `notebooks/3_prediction.ipynb`
   - Carregar pipeline treinado
   - Fazer predições em novos dados

### Função de Predição

```python
# Exemplo de uso (no notebook 3)
input_dict = {
    "ioi_3months": 3,
    "valor_vencido": 125000,
    "valor_total_pedido": 35000
}

result = predict_default(input_dict)
# Output: {"default": 0, "probability": 0.23, "threshold_used": 0.575}
```

---

## Notebooks

### 1. Análise Exploratória (1_EDA.ipynb) — 57 cells

- Carregamento e limpeza de dados
- Análise de valores faltantes e distribuição do target (~16-17% default)
- Análise univariada e bivariada
- **Auditoria de valores negativos e anomalias numéricas** (seção 6.1)
- **Testes estatísticos Mann-Whitney U** com effect size, KDE plots e violin plots (seção 6.2)
- **Análise de esparsidade** (zeros vs não-zeros) e impacto no default
- Matriz de correlação
- **Análise de clusters K-Means** com PCA, Silhouette Score e perfis de risco (seção 9.1)
- **Análise temporal detalhada** com séries temporais
- **ACHADO CRÍTICO: Viés de Maturação** — últimos meses têm taxa de default artificialmente baixa (parcelas ainda não venceram)
- Decisão: NÃO usar validação out-of-time

### 2. Pipeline de Modelagem (2_model_pipeline.ipynb) — 73 cells

- **Preparação de dados**: Remoção de variável year para evitar data leakage; month mantido como categórica (sazonalidade)
- **Feature engineering**: 7 features derivadas (razao_inadimplencia, taxa_cobertura_divida, total_exposto, razao_vencido_pedido, flag_risco_juridico, ticket_medio_protestos, qtd_parcelas)
- **Divisão treino/teste**: Estratificada 80/20
- **Pré-processamento** (ColumnTransformer):
  - Numéricos: SimpleImputer(median) + RobustScaler
  - Alta cardinalidade (tipo_sociedade, atividade_principal, forma_pagamento): SimpleImputer + TargetEncoder
  - Baixa cardinalidade (opcao_tributaria): SimpleImputer + OneHotEncoder
  - **24 features raw → 28 features após encoding**
- **Comparação de 6 modelos** com StratifiedKFold CV (5 folds):
  Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost, LightGBM
- **Hyperparameter tuning** com RandomizedSearchCV e controles anti-overfitting
- **Análise detalhada**: ROC curve, Precision-Recall, Confusion Matrix
- **Análise de custos de negócio** (4 cenários de threshold)
- **Feature Importance** com nomes descritivos e color coding
- **SHAP Analysis** (SHapley Additive exPlanations) para interpretabilidade
- **Pipeline final**: `Pipeline([('preprocessor', ColumnTransformer), ('classifier', XGBoost)])`

### 3. Função de Predição (3_prediction.ipynb) — 16 cells

- Carregamento do pipeline completo (preprocessor → classifier)
- Funções `predict_default()` e `predict_default_batch()`
- Exemplos práticos (bom pagador, alto risco)
- Comparação de thresholds
- Predições em batch
- Validação com dados reais

---

## Dataset

- **Fonte**: X-Health
- **Localização**: `_data/dataset_2021-5-26-10-14.csv`
- **Formato**: CSV (separador `\t`, encoding `utf-8`)
- **Missing Values**: Indicados como "missing"

### Variáveis

#### Internas (Histórico do Cliente)
| Variável | Descrição |
|----------|-----------|
| `default_3months` | Quantidade de defaults nos últimos 3 meses |
| `ioi_Xmonths` | Intervalo médio entre pedidos (dias) nos últimos X meses |
| `valor_por_vencer` | Total em pagamentos a vencer (R$) |
| `valor_vencido` | Total em pagamentos vencidos (R$) |
| `valor_quitado` | Total pago no histórico (R$) |

#### Externas (Bureau de Crédito)
| Variável | Descrição |
|----------|-----------|
| `quant_protestos` | Quantidade de protestos de títulos |
| `valor_protestos` | Valor total dos protestos (R$) |
| `quant_acao_judicial` | Quantidade de ações judiciais |
| `acao_judicial_valor` | Valor total das ações judiciais (R$) |
| `participacao_falencia_valor` | Valor total de falências (R$) |
| `dividas_vencidas_valor` | Valor total de dívidas vencidas (R$) |
| `dividas_vencidas_qtd` | Quantidade de dívidas vencidas |
| `falencia_concordata_qtd` | Quantidade de concordatas |

#### Categóricas
| Variável | Descrição |
|----------|-----------|
| `tipo_sociedade` | Tipo de sociedade do cliente B2B |
| `opcao_tributaria` | Opção tributária do cliente |
| `atividade_principal` | Atividade principal do cliente |
| `forma_pagamento` | Forma de pagamento combinada |

#### Contexto e Target
| Variável | Descrição |
|----------|-----------|
| `valor_total_pedido` | Valor total do pedido (R$) |
| `default` | 0 = Pago em dia, 1 = Default (calote) |

---

## Metodologia

### 1. Análise Exploratória
- Compreensão dos dados, padrões e anomalias
- **Análise temporal e identificação de viés de maturação**
- Decisão sobre estratégia de validação

### 2. Feature Engineering (7 features derivadas)
- `total_exposto`: volume total de relacionamento financeiro (vencido + por_vencer + quitado)
- `razao_inadimplencia`: grau de deterioração da carteira (vencido / total_exposto)
- `taxa_cobertura_divida`: capacidade histórica de pagamento (quitado / pedido)
- `razao_vencido_pedido`: alavancagem atual (vencido / pedido)
- `flag_risco_juridico`: sinal binário (1 se tem protestos OU ações judiciais)
- `ticket_medio_protestos`: gravidade do problema jurídico (valor / quantidade)
- `qtd_parcelas`: complexidade de pagamento extraída de forma_pagamento (proxy fluxo de caixa)
- **Exclusão de variável year** para evitar data leakage; month mantido como categórica

### 3. Pré-processamento
- **Missing Values**: Imputação por mediana (numérico) ou "missing"/"unknown" (categórico)
- **Scaling**: RobustScaler para variáveis numéricas (robusto a outliers)
- **Encoding**: Target Encoding para alta cardinalidade (reduz 203+104 categorias → 2 features), OneHotEncoder para baixa cardinalidade
- **Split**: Divisão estratificada 80/20

### 4. Modelagem
- **Comparação**: 6 algoritmos com StratifiedKFold CV (5 folds)
- **Seleção**: Melhor modelo baseado em CV ROC-AUC
- **Balanceamento**: `class_weight='balanced'` nos modelos que suportam
- **Hyperparameter Tuning**: RandomizedSearchCV com controles anti-overfitting (max_depth, min_child_weight, reg_alpha, reg_lambda)

### 5. Avaliação e Interpretabilidade
- **Métricas**: CV ROC-AUC (média ± std), Test ROC-AUC, F1, Precision, Recall
- **Curvas**: ROC, Precision-Recall, Confusion Matrix
- **Feature Importance**: Ranking com nomes descritivos
- **SHAP Analysis**: Interpretabilidade global e local das predições

### 6. Otimização de Threshold
- Trade-off Precision vs Recall
- F-Scores: F1, F2 (prioriza Recall), F0.5 (prioriza Precision)
- Análise de custos: 4 cenários de negócio (FN vs FP)

---

## Achado Crítico: Viés de Maturação (Maturity Bias)

### O Problema

Últimos meses do dataset apresentam taxa de default significativamente MENOR que a média histórica.

**Causa**: Parcelas recentes ainda não tiveram tempo suficiente para vencer e se tornarem defaults.

### Evidências

| Maturação dos Dados | Taxa de Default Observada |
|---------------------|---------------------------|
| 12+ meses (maduros) | ~18-20% |
| 6-12 meses | ~16-18% |
| 3-6 meses | ~12-14% |
| 0-3 meses (recentes) | ~8-10% |

### Decisão

- **NÃO usar** validação out-of-time
- **USAR** StratifiedKFold cross-validation (5 folds)
- **Remover** year/month das features

---

## Resultados

### Modelo Selecionado: XGBoost (com hyperparameter tuning)

| Métrica | Valor |
|---------|-------|
| **Test ROC-AUC** | 0.925 |
| **CV ROC-AUC** | 0.921 ± 0.003 |
| **Test F1-Score** | 0.702 |
| **Test Precision** | 0.663 |
| **Test Recall** | 0.746 |

### Features
- **24 features raw** (20 numéricas + 3 alta cardinalidade + 1 baixa cardinalidade)
- **28 features processadas** após Target Encoding e OneHotEncoding

### Thresholds Otimizados

| Objetivo | Threshold | Descrição |
|----------|-----------|-----------|
| **Balanceado (F1)** | 0.575 | Equilibra Precision e Recall |
| **Capturar Defaults (F2)** | 0.302 | Prioriza Recall (minimizar perdas) |
| **Evitar Rejeições (F0.5)** | 0.775 | Prioriza Precision (menos falsos alarmes) |

### Pipeline Salvo
```
Pipeline([
    ('preprocessor', ColumnTransformer),  # encoding + scaling
    ('classifier', XGBoostClassifier)     # modelo otimizado
])
```
O pipeline recebe dados raw (24 features) e faz todo o pré-processamento internamente.

---

## Reprodutibilidade

### Checklist
- requirements.txt com todas as dependências
- Random Seeds fixados (RANDOM_STATE=42)
- Dataset incluído no repositório (`_data/`)
- Pipeline completo serializado (preprocessor + classifier)
- Metadados salvos em JSON (métricas, features, thresholds)

### Como Reproduzir

```bash
pip install -r requirements.txt

# Executar notebooks em ordem:
# 1. notebooks/1_EDA.ipynb
# 2. notebooks/2_model_pipeline.ipynb
# 3. notebooks/3_prediction.ipynb

# Verificar artefatos gerados:
ls models/model_*.pkl models/model_metadata.json
```

---

## Próximos Passos

### Melhorias Técnicas
- [ ] Calibração de probabilidades (Isotonic/Platt scaling)
- [ ] Ensemble methods (stacking, blending)
- [ ] Análise de maturação em produção

### Implantação em Produção
- [ ] API REST (Flask/FastAPI)
- [ ] Containerização (Docker)
- [ ] Monitoring e alertas
- [ ] Feedback loop para retreinamento

### Governança
- [ ] Model Cards (documentação formal)
- [ ] Fairness analysis
- [ ] Model Registry e versionamento

---

## Notas Importantes

1. **Privacidade**: Repositório privado, não compartilhar
2. **Caráter Fictício**: Exercício de seleção, não projeto real da Kognita Lab
3. **Foco**: Capacidade de análise, raciocínio, identificação de problemas, qualidade de código
4. **Decisões Fundamentadas**: Todas baseadas em análise de dados

---

**Versão**: 3.3.0 | **Data**: 2026-02-13 | **Status**: Produção
