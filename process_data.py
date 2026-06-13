#!/usr/bin/env python3
"""
process_data.py — Lê data/Fluxo_de_recebimento.xlsx e gera index.html.
Executado automaticamente pelo GitHub Actions a cada push do Excel.
"""
import pandas as pd
import json, re, sys
from datetime import datetime

EXCEL_PATH    = "data/Fluxo_de_recebimento.xlsx"
TEMPLATE_PATH = "template.html"
OUTPUT_PATH   = "index.html"

print(f"[1/4] Lendo {EXCEL_PATH}...")
df = pd.read_excel(EXCEL_PATH, sheet_name="CT A RECEBER")

df["PREV . PAG"]  = pd.to_datetime(df["PREV . PAG"],  errors="coerce")
df["MES SERVICO"] = pd.to_datetime(df["MÊS SERVIÇO"], errors="coerce")
df["DATA PAG"]    = pd.to_datetime(df["DATA PAG."],    errors="coerce")
df["EMISSAO"]     = pd.to_datetime(df["EMISSÃO"],      errors="coerce")

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

ultima_atualizacao = datetime.now().strftime("%d/%m/%Y às %H:%M")

print(f"[3/4] Lendo {TEMPLATE_PATH}...")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# CORREÇÃO: usar lambda para evitar que o Python interprete
# sequências de escape (\u, \n, etc.) presentes no JSON/HTML como
# escape de regex — causava "re.error: bad escape \u"
replacement = raw_json

html = re.sub(
    r"var RAW\s*=\s*\[.*?\];",
    lambda m: f"var RAW = {replacement};",
    html,
    flags=re.DOTALL
)

print(f"[4/4] Gravando {OUTPUT_PATH}...")
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Concluido — {len(html)//1024} KB")
