#!/usr/bin/env python3
"""
process_data.py — Lê data/Fluxo_de_recebimento.xlsx e gera index.html.
"""
import pandas as pd
import json, re, os
from datetime import datetime, timezone, timedelta

EXCEL_PATH    = "data/Fluxo_de_recebimento.xlsx"
TEMPLATE_PATH = "template.html"
OUTPUT_PATH   = "index.html"

print(f"[1/4] Lendo {EXCEL_PATH}...")
df = pd.read_excel(EXCEL_PATH, sheet_name="CT A RECEBER")

df["PREV . PAG"]  = pd.to_datetime(df["PREV . PAG"],  errors="coerce")
df["MES SERVICO"] = pd.to_datetime(df["MÊS SERVIÇO"], errors="coerce")
df = df[df["PREV . PAG"].notna()].copy()

df["PREV_PAG_DT"] = df["PREV . PAG"].dt.strftime("%Y-%m-%d")
df["MES"]         = df["PREV . PAG"].dt.strftime("%Y-%m")
df["VL_FAT"]      = df["VL. FATURADO"].fillna(0)
df["PMR_DIAS"]    = (df["PREV . PAG"] - df["MES SERVICO"]).dt.days.fillna(-1).astype(int)

for c in ["Grupo Cliente","CLIENTE","Excecutivo","BU","Vertical","Diretor de Operações","STATUS"]:
    df[c] = df[c].fillna("").astype(str).str.strip()
df["DirOP"] = df["Diretor de Operações"]

cols = ["MES","PREV_PAG_DT","Excecutivo","Grupo Cliente","CLIENTE",
        "BU","Vertical","DirOP","STATUS","VL_FAT","PMR_DIAS"]
raw = df[cols].to_dict("records")
print(f"[2/4] {len(raw)} registros processados")

raw_json = json.dumps(raw, ensure_ascii=True)

now_brt    = datetime.now(timezone.utc) - timedelta(hours=3)
excel_date = now_brt.strftime("%d/%m/%Y %H:%M")
print(f"[2b] Data BRT: {excel_date}")

print(f"[3/4] Lendo {TEMPLATE_PATH}...")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Substituir marcador de data — string simples, sem regex
html = html.replace("EXCEL_DATE_PLACEHOLDER", excel_date)

# Substituir RAW — lambda evita bad escape
html = re.sub(
    r"var RAW\s*=\s*\[.*?\];",
    lambda m, rj=raw_json: f"var RAW = {rj};",
    html,
    flags=re.DOTALL
)

print(f"[4/4] Gravando {OUTPUT_PATH}...")
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

# Verificar resultado
with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
    check = f.read()
date_ok  = excel_date in check
badge_ok = 'badge-excel' in check
placeholder_left = "EXCEL_DATE_PLACEHOLDER" in check
print(f"Data no HTML: {date_ok} | badge presente: {badge_ok} | placeholder restante: {placeholder_left}")
if placeholder_left:
    raise Exception("ERRO: EXCEL_DATE_PLACEHOLDER ainda presente no HTML!")

print(f"Concluido — {len(check)//1024} KB")
