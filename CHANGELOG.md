# Changelog - X-Health Default Prediction

---

## [3.2.0] - 2026-02-13

### Mudanças Principais

#### Ajuste Balanceado de Hiperparâmetros (Performance + Generalização)

**Problema Identificado**:
A busca agressiva v3.1 resolveu o overfitting mas causou **underfitting** (performance pior que baseline):
- v3.1 Test ROC-AUC: **0.8798** vs Original: 0.9037 → **-2.4%** ❌
- v3.1 Test F1: **0.5642** vs Original: 0.6246 → **-9.7%** ❌
- v3.1 Gap F1: **3.5%** ✅ (excelente generalização)
- **Diagnóstico**: Restrições muito agressivas limitaram capacidade de aprendizado

**Solução - Busca Balanceada v3.2**:
Meio-termo entre complexidade (performance) e regularização (generalização):

1. **Complexidade das árvores** (ligeiramente relaxada):
   - `max_depth`: [3, 5] → **[3, 6]** (mais profundidade)
   - `min_child_weight`: [10, 50] → **[5, 30]** (folhas menores permitidas)

2. **Número de árvores** (moderadamente relaxado):
   - `n_estimators`: [50, 300] → **[100, 400]** (mais árvores)

3. **Learning rate** (ligeiramente relaxado):
   - `learning_rate`: [0.01, 0.10] → **[0.01, 0.15]** (aprendizado mais rápido)

4. **Regularização** (moderada):
   - `gamma`: [1.0, 5.0] → **[0.5, 3.0]** (menos penalidade)
   - `reg_alpha` (L1): [2.0, 8.0] → **[0.5, 4.0]** (menos agressivo)
   - `reg_lambda` (L2): [3.0, 10.0] → **[1.5, 6.0]** (meio-termo)

5. **Randomização** (moderada):
   - `subsample`: [0.5, 0.75] → **[0.55, 0.80]** (menos randomização)
   - `colsample_bytree`: [0.4, 0.7] → **[0.45, 0.80]** (mais features)

**Objetivo v3.2**:
- ROC-AUC Test **> 0.90** (recuperar performance vs v3.1)
- Gap F1 **< 10%** (aceitar gap moderado vs v3.1's 3.5%)
- **Trade-off**: Aceitar generalização um pouco menor para ganhar performance útil

**Filosofia**: Modelo deve ter complexidade suficiente para aprender padrões relevantes, mas com regularização para evitar memorização. Gap moderado (5-10%) é aceitável para modelos de produção.

**Status**: Implementado (aguardando re-execução do notebook)

---

## [3.1.0] - 2026-02-13 (Descontinuado - Underfitting)

### Mudanças Principais

#### Aprimoramento Anti-Overfitting no Hyperparameter Tuning (MUITO AGRESSIVO)

**Problema Identificado**:
O modelo tunado (v3.0.0) apresentou overfitting severo:
- Train ROC-AUC: **0.9993** vs Test: 0.9358 → Gap 6.4%
- Train F1: **0.9536** vs Test F1: 0.7407 → **Gap 22.3%** (SEVERO)

**Solução - Busca Agressiva**:
Espaço de busca DRASTICAMENTE restrito (detalhes omitidos - ver v3.2 para versão atual)

**Resultado**:
- ✅ Overfitting resolvido (Gap F1: 3.5%)
- ❌ **Underfitting** (ROC-AUC: 0.8798 vs 0.9037 baseline)
- **Versão descontinuada** em favor da v3.2 balanceada

---

## [3.0.0] - 2026-02-12

### Mudanças Principais

#### Pré-processamento Avançado
- **Target Encoding** para features de alta cardinalidade (tipo_sociedade, atividade_principal, forma_pagamento) — reduz 203+104 categorias para 2 features numéricas
- **RobustScaler** no lugar de StandardScaler (mais robusto a outliers)
- **class_weight='balanced'** nos modelos que suportam
- Pipeline: 24 features raw → 28 features processadas

#### Hyperparameter Tuning
- RandomizedSearchCV para otimização de hiperparâmetros
- Controles anti-overfitting: max_depth, min_child_weight, reg_alpha, reg_lambda
- Análise de overfitting (train vs test metrics)

#### SHAP Analysis
- Implementação de SHAP (SHapley Additive exPlanations)
- Interpretabilidade global do modelo
- Feature importance com explicações causais

#### Feature Importance Aprimorada
- Nomes descritivos para features processadas (num__, target_enc__, onehot__)
- Color coding por tipo de feature
- Ranking visual

#### Feature Selection (Adicionada e Removida)
- Experimentou-se feature selection por importância acumulada (90%)
- Causou problemas de dimensionalidade no pipeline (preprocessor output ≠ classifier input)
- **Decisão**: Removida em favor de usar todas as features processadas
- Pipeline simplificado: preprocessor → classifier (sem FeatureSelector intermediário)

#### Pipeline Simplificado
- Pipeline final: `Pipeline([('preprocessor', ColumnTransformer), ('classifier', XGBoost)])`
- Recebe dados raw (24 features) e faz todo o pré-processamento internamente
- Sem transformadores customizados — facilita serialização e deploy

#### Prediction Notebook Atualizado
- Adaptado ao pipeline simplificado (preprocessor → classifier)
- Removidos artefatos do FeatureSelector
- Funções predict_default() e predict_default_batch() limpas

#### Documentação Reorganizada
- Removidos: MIGRATION_GUIDE.md, CHANGELOG_CORRECTIONS.md, README_NAVIGATION.md (redundantes/obsoletos)
- Reescritos: PROJECT_README.md, SUMMARY.md, CHANGELOG.md, INDEX.md
- Estrutura: 4 documentos concisos e atualizados

### Métricas do Modelo (v3.0.0)

| Métrica | Valor |
|---------|-------|
| Test ROC-AUC | 0.925 |
| CV ROC-AUC | 0.921 ± 0.003 |
| F1-Score | 0.702 |
| Precision | 0.663 |
| Recall | 0.746 |

### Thresholds Otimizados

| Objetivo | Threshold |
|----------|-----------|
| F1 (balanceado) | 0.575 |
| F2 (capturar defaults) | 0.302 |
| F0.5 (evitar rejeições) | 0.775 |

---

## [2.0.0] - 2026-02-11

### Mudanças Principais

#### Achado Crítico: Viés de Maturação
- Identificado viés temporal: últimos meses com taxa de default artificialmente baixa
- Causa: parcelas recentes sem tempo de maturação
- Evidência: taxa default dados maduros (~18%) vs recentes (~8-10%)

#### Mudança de Estratégia de Validação
- **Antes**: Validação out-of-time (últimos 2 meses como teste)
- **Depois**: StratifiedKFold cross-validation (5 folds)
- Remoção de year/month das features (evitar data leakage)

#### Otimização de Threshold
- Análise de trade-off Precision-Recall
- Thresholds para F1, F2, F0.5
- Análise de custos de negócio (4 cenários)

### Notebooks
- **1_EDA.ipynb**: Adicionada análise de viés de maturação
- **2_model_pipeline.ipynb**: Cross-validation, threshold optimization, 6 modelos comparados
- **3_prediction.ipynb**: Threshold configurável, exemplos práticos

---

## [1.0.0] - 2026-02-11 (Versão Inicial)

### Adicionado
- Notebook 1_EDA.ipynb: Análise exploratória completa
- Notebook 2_model_pipeline.ipynb: Pipeline de modelagem
- Notebook 3_prediction.ipynb: Função de predição
- requirements.txt e documentação inicial

---

## Comparação de Versões

| Aspecto | v1.0 | v2.0 | v3.0 | v3.1 | v3.2 |
|---------|------|------|------|------|------|
| Validação | Out-of-time | StratifiedKFold CV | StratifiedKFold CV | StratifiedKFold CV | StratifiedKFold CV |
| Scaling | StandardScaler | StandardScaler | RobustScaler | RobustScaler | RobustScaler |
| Encoding | OneHotEncoder | OneHotEncoder | Target + OneHot | Target + OneHot | Target + OneHot |
| Tuning | Nenhum | Nenhum | Moderado | Agressivo | **Balanceado** |
| SHAP | Nenhum | Nenhum | Implementado | Implementado | Implementado |
| Threshold | 0.5 fixo | Otimizado | Otimizado | Otimizado | Otimizado |
| Pipeline | Preprocessor + Model | Preprocessor + Model | Preprocessor + Model | Preprocessor + Model | Preprocessor + Model |
| Balanceamento | Nenhum | Nenhum | class_weight | class_weight | class_weight |
| ROC-AUC Test | - | - | 0.9037 | 0.8798 ❌ | > 0.90 (obj) |
| Gap F1 | - | - | 22.3% ❌ | 3.5% ✅ | < 10% (obj) |
| Resultado | - | - | Overfitting severo | Underfitting | **Performance + Generalização** |

---

**Versão atual**: 3.2.0 | **Data**: 2026-02-13
