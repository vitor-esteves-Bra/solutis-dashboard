#!/usr/bin/env python3
"""
process_data.py — Le data/Fluxo_de_recebimento.xlsx e gera index.html.
"""
import pandas as pd
import json, re
from datetime import datetime, timezone, timedelta

EXCEL_PATH    = "data/Fluxo_de_recebimento.xlsx"
TEMPLATE_PATH = "template.html"
OUTPUT_PATH   = "index.html"

print(f"[1/4] Lendo {EXCEL_PATH}...")
df = pd.read_excel(EXCEL_PATH, sheet_name="CT A RECEBER")

df["PREV . PAG"]  = pd.to_datetime(df["PREV . PAG"],  errors="coerce")
df["MES SERVICO"] = pd.to_datetime(df["MES SERVICO"] if "MES SERVICO" in df.columns else df["MES SERVICO"], errors="coerce")
try:
    df["MES SERVICO"] = pd.to_datetime(df["MES SERVICO"], errors="coerce")
except:
    df["MES SERVICO"] = pd.to_datetime(df.get("MES SERVICO", df.get("MÊS SERVIÇO","")), errors="coerce")

df["MES SERVICO"] = pd.to_datetime(df["MÊS SERVIÇO"], errors="coerce")
df = df[df["PREV . PAG"].notna()].copy()

df["PREV_PAG_DT"] = df["PREV . PAG"].dt.strftime("%Y-%m-%d")
df["MES"]         = df["PREV . PAG"].dt.strftime("%Y-%m")
df["VL_FAT"]      = df["VL. FATURADO"].fillna(0)
df["PMR_DIAS"]    = (df["PREV . PAG"] - df["MES SERVICO"]).dt.days.fillna(-1).astype(int)

for c in ["Grupo Cliente","CLIENTE","Excecutivo","BU","Vertical","Diretor de Operacoes","STATUS"]:
    col = c if c in df.columns else c.replace("Operacoes","Operações")
    if col in df.columns:
        df[c] = df[col].fillna("").astype(str).str.strip()
    else:
        df[c] = ""

if "Diretor de Operações" in df.columns:
    df["DirOP"] = df["Diretor de Operações"].fillna("").astype(str).str.strip()
else:
    df["DirOP"] = ""

cols = ["MES","PREV_PAG_DT","Excecutivo","Grupo Cliente","CLIENTE",
        "BU","Vertical","DirOP","STATUS","VL_FAT","PMR_DIAS"]
for c in cols:
    if c not in df.columns:
        df[c] = ""

raw      = df[cols].to_dict("records")
raw_json = json.dumps(raw, ensure_ascii=True)
print(f"[2/4] {len(raw)} registros processados")

now_brt    = datetime.now(timezone.utc) - timedelta(hours=3)
excel_date = now_brt.strftime("%d/%m/%Y %H:%M")
print(f"[2b] Data BRT: {excel_date}")

print(f"[3/4] Lendo {TEMPLATE_PATH}...")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Substituir placeholder do badge diretamente no HTML
badge_html = (
    '''<div class="hbadge" style="display:flex">'''
    '''<svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">'''
    '''<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>'''
    '''<polyline points="14 2 14 8 20 8"/></svg>'''
    f" Base: <strong>{excel_date}</strong></div>"
)
html = html.replace("<!--BADGE_EXCEL_PLACEHOLDER-->", badge_html)

# Substituir RAW
html = re.sub(
    r"var RAW\s*=\s*\[.*?\];",
    lambda m, rj=raw_json: f"var RAW = {rj};",
    html,
    flags=re.DOTALL
)

print(f"[4/4] Gravando {OUTPUT_PATH}...")
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

# Verificacoes
with open(OUTPUT_PATH) as f:
    check = f.read()

assert excel_date in check,               "ERRO: data nao encontrada no HTML!"
assert "BADGE_EXCEL_PLACEHOLDER" not in check, "ERRO: placeholder nao substituido!"
assert "display:flex" in check,           "ERRO: badge nao esta visivel!"
print(f"OK — {len(check)//1024} KB | data={excel_date} | badge=visivel")
