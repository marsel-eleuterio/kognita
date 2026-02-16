# Changelog - X-Health Default Prediction

---

## [3.4.0] - 2026-02-16

### Mudanças Principais

#### Filtros de Qualidade de Dados (baseados no EDA)

Aplicadas duas decisoes de limpeza de dados fundamentadas na analise exploratoria:

**1. Remocao de registros com valor_total_pedido negativo**
- 144 registros (0.12%) removidos do pipeline de modelagem
- Motivo: possivel inconsistencia nos dados (estornos, ajustes ou erros de cadastro)
- Valores negativos distorcem features derivadas (`taxa_cobertura_divida`, `razao_vencido_pedido`)
- Predicao: rejeita valores negativos com mensagem de erro

**2. Exclusao de 6 variaveis com >=99% de zeros**
- Alto indice de zeros indica possivel filtro pre-venda (clientes sem registros nessas dimensoes)
- Variaveis removidas:
  - `participacao_falencia_valor` (100.00% zeros)
  - `falencia_concordata_qtd` (99.95% zeros)
  - `acao_judicial_valor` (99.53% zeros)
  - `dividas_vencidas_qtd` (99.39% zeros)
  - `dividas_vencidas_valor` (99.33% zeros)
  - `quant_acao_judicial` (99.18% zeros)

**Impacto nas features derivadas:**
- `flag_risco_juridico` simplificada: agora usa apenas `quant_protestos` (96.27% zeros, abaixo do threshold)
- Demais features derivadas nao afetadas

**Arquivos alterados:**
- `notebooks/2_model_pipeline.ipynb`: Cells 5 (remocao negativos), 8 (exclusao variaveis + flag simplificada), 72 (conclusoes)
- `notebooks/3_prediction.ipynb`: Cells 1 (docs), 2 (engineer_features), 4 (validacao negativos), 6-7 (exemplos), 15 (script export)
- `scripts/predict.py`: Docstring, engineer_features, validacao de negativos
- `docs/`: SUMMARY.md, PROJECT_README.md, CHANGELOG.md, INDEX.md atualizados

**Nota**: Modelo precisa ser retreinado para refletir as novas features.

---

## [3.3.0] - 2026-02-13

### Mudanças Principais

#### Feature Engineering Reformulado (7 features derivadas)

Features antigas (5) foram substituidas por 7 features com fundamentacao de negocio:

| Feature Antiga | Feature Nova | Mudanca |
|---|---|---|
| `ratio_vencido_quitado` | `razao_inadimplencia` | Denominador agora e `total_exposto` (vencido + por_vencer + quitado) |
| `ratio_pedido_historico` | `taxa_cobertura_divida` | Formula invertida: quitado/pedido (capacidade historica) |
| `exposicao_total` | `total_exposto` | Inclui `valor_quitado` (antes era so vencido + por_vencer) |
| `tem_protestos` + `tem_acao_judicial` | `flag_risco_juridico` | Unificada: 1 se tem protesto OU acao judicial |
| *(nova)* | `ticket_medio_protestos` | valor_protestos / quant_protestos (gravidade) |
| *(nova)* | `razao_vencido_pedido` | vencido / pedido (alavancagem) |
| *(nova)* | `qtd_parcelas` | Conta barras '/' em forma_pagamento + 1 (proxy fluxo de caixa) |

**Impacto**: Atualizado em 3 locais (pipeline cell 8, predictions cell 2, script embutido cell 15) + model_metadata.json.

**Nota**: Modelo precisa ser retreinado para refletir as novas features.

#### EDA Aprofundado (1_EDA.ipynb: 50 -> 57 cells)

Novas analises adicionadas ao notebook de EDA:

1. **Secao 6.1 - Auditoria de Valores Negativos e Anomalias**
   - Tabela de negativos, zeros e positivos por variavel
   - Taxa de default para registros negativos vs positivos
   - Grafico de composicao (stacked bar)

2. **Secao 6.2 - Analise Estatistica Avancada**
   - Testes Mann-Whitney U (default=0 vs default=1) com effect size
   - Metricas de assimetria (skewness) e curtose (kurtosis)
   - KDE plots sobrepostos por status de default
   - Violin plots das top 6 variaveis discriminativas
   - Analise de esparsidade (zeros vs nao-zeros) e impacto no default

3. **Secao 9.1 - Analise de Clusters (K-Means)**
   - Metodo do cotovelo + Silhouette Score
   - K-Means com RobustScaler + VarianceThreshold
   - PCA 2D para visualizacao dos clusters
   - Taxa de default por cluster
   - Heatmap dos centroides com interpretacao automatica

#### Documentacao Atualizada
- Markdowns de conclusao dos 3 notebooks atualizados
- model_metadata.json: derived_features e numeric_features atualizados
- docs/: INDEX.md, CHANGELOG.md, PROJECT_README.md, SUMMARY.md atualizados

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

| Aspecto | v1.0 | v2.0 | v3.0 | v3.1 | v3.2 | v3.3 | v3.4 |
|---------|------|------|------|------|------|------|------|
| Validação | Out-of-time | StratifiedKFold CV | StratifiedKFold CV | StratifiedKFold CV | StratifiedKFold CV | StratifiedKFold CV | StratifiedKFold CV |
| Scaling | StandardScaler | StandardScaler | RobustScaler | RobustScaler | RobustScaler | RobustScaler | RobustScaler |
| Encoding | OneHotEncoder | OneHotEncoder | Target + OneHot | Target + OneHot | Target + OneHot | Target + OneHot | Target + OneHot |
| Tuning | Nenhum | Nenhum | Moderado | Agressivo | Balanceado | Balanceado | Balanceado |
| Features derivadas | Nenhuma | Nenhuma | 5 (ratios, flags) | 5 | 5 | 7 (reformuladas) | 7 (flag simplificada) |
| Qualidade de dados | Nenhum | Nenhum | Nenhum | Nenhum | Nenhum | Nenhum | **Negativos + 99% zeros** |
| EDA | Básico | + Viés maturação | + Viés maturação | + Viés maturação | + Viés maturação | + Negativos, Clusters, Testes | + Negativos, Clusters, Testes |
| SHAP | Nenhum | Nenhum | Implementado | Implementado | Implementado | Implementado | Implementado |
| Threshold | 0.5 fixo | Otimizado | Otimizado | Otimizado | Otimizado | Otimizado | Otimizado |
| Pipeline | Preprocessor + Model | Preprocessor + Model | Preprocessor + Model | Preprocessor + Model | Preprocessor + Model | Preprocessor + Model | Preprocessor + Model |
| Balanceamento | Nenhum | Nenhum | class_weight | class_weight | class_weight | class_weight | class_weight |

---

**Versão atual**: 3.4.0 | **Data**: 2026-02-16
