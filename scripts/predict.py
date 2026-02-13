
"""predict.py - Predicao de default (X-Health Credit Risk).

Feature engineering automatico: features derivadas calculadas internamente.
Missing values: categoricas -> 'unknown', numericas -> NaN (imputer usa mediana).
month e tratado como categorica (correlacao com default no EDA).
"""
import pandas as pd, numpy as np, joblib, json
from pathlib import Path

model = joblib.load(list(Path('models/').glob('model_*.pkl'))[0])
with open('models/model_metadata.json') as f: metadata = json.load(f)

ALL_FEATURES = metadata['numeric_features'] + metadata['high_cardinality_features'] + metadata['low_cardinality_features']
CATEGORICAL_FEATURES = metadata['high_cardinality_features'] + metadata['low_cardinality_features']
DERIVED_FEATURES = metadata.get('derived_features', [])
THRESHOLD_F1 = metadata.get('optimal_threshold_f1', 0.5)


def engineer_features(df):
    df = df.copy()
    if all(c in df.columns for c in ['valor_vencido', 'valor_por_vencer', 'valor_quitado']):
        df['total_exposto'] = df['valor_vencido'] + df['valor_por_vencer'] + df['valor_quitado']
    if 'valor_vencido' in df.columns and 'total_exposto' in df.columns:
        df['razao_inadimplencia'] = df['valor_vencido'] / (df['total_exposto'] + 1)
    if 'valor_quitado' in df.columns and 'valor_total_pedido' in df.columns:
        df['taxa_cobertura_divida'] = df['valor_quitado'] / (df['valor_total_pedido'] + 1)
    if 'valor_vencido' in df.columns and 'valor_total_pedido' in df.columns:
        df['razao_vencido_pedido'] = df['valor_vencido'] / (df['valor_total_pedido'] + 1)
    if 'quant_protestos' in df.columns and 'quant_acao_judicial' in df.columns:
        df['flag_risco_juridico'] = ((df['quant_protestos'] > 0) | (df['quant_acao_judicial'] > 0)).astype(int)
    elif 'quant_protestos' in df.columns:
        df['flag_risco_juridico'] = (df['quant_protestos'] > 0).astype(int)
    elif 'quant_acao_judicial' in df.columns:
        df['flag_risco_juridico'] = (df['quant_acao_judicial'] > 0).astype(int)
    if 'valor_protestos' in df.columns and 'quant_protestos' in df.columns:
        df['ticket_medio_protestos'] = df['valor_protestos'] / (df['quant_protestos'] + 1)
    if 'forma_pagamento' in df.columns:
        df['qtd_parcelas'] = df['forma_pagamento'].apply(
            lambda x: str(x).count('/') + 1 if pd.notna(x) and str(x) not in ('nan', 'missing', 'unknown', '') else 1
        )
    return df


def to_categorical(x):
    if pd.isna(x) or x is None or x == 'missing' or x == '':
        return 'unknown'
    try:
        return str(int(float(x)))
    except (ValueError, TypeError):
        return str(x)


def predict_default(input_dict, threshold=None):
    if threshold is None: threshold = THRESHOLD_F1
    df = pd.DataFrame([input_dict])
    for col in df.columns:
        if col in CATEGORICAL_FEATURES:
            df[col] = df[col].apply(to_categorical)
        else:
            df[col] = pd.to_numeric(df[col].replace('missing', np.nan), errors='coerce')
    df = engineer_features(df)
    for f in ALL_FEATURES:
        if f not in df.columns:
            df[f] = 'unknown' if f in CATEGORICAL_FEATURES else np.nan
    prob = float(model.predict_proba(df[ALL_FEATURES])[0, 1])
    return {"default": int(prob >= threshold), "probability": round(prob, 4), "threshold_used": round(threshold, 4)}

if __name__ == '__main__':
    print(predict_default({"ioi_3months": 3, "valor_vencido": 125000, "valor_total_pedido": 35000, "month": 6}))
