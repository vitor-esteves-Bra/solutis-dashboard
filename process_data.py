#!/usr/bin/env python3
import pandas as pd, json, re
from datetime import datetime, timezone, timedelta

EXCEL     = "data/Fluxo_de_recebimento.xlsx"
TEMPLATE  = "template.html"
OUTPUT    = "index.html"

print(f"Lendo {EXCEL}...")
df = pd.read_excel(EXCEL, sheet_name="CT A RECEBER")
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

# Colunas de risco (M e N)
df["VL_RISCO"]    = pd.to_numeric(df["Risco"], errors="coerce").fillna(0)
df["NIVEL_RISCO"] = df["NIVEL RISCO"].fillna("").astype(str).str.strip().str.lower()

cols = ["MES","PREV_PAG_DT","Excecutivo","Grupo Cliente","CLIENTE",
        "BU","Vertical","DirOP","STATUS","VL_FAT","PMR_DIAS",
        "VL_RISCO","NIVEL_RISCO"]
raw_json = json.dumps(df[cols].to_dict("records"), ensure_ascii=True)
print(f"{len(df)} registros processados")

now_brt    = datetime.now(timezone.utc) - timedelta(hours=3)
excel_date = now_brt.strftime("%d/%m/%Y %H:%M")

with open(TEMPLATE, encoding="utf-8") as f:
    html = f.read()

# Substituir placeholder do badge
html = html.replace("EXCEL_DATE_PLACEHOLDER", excel_date)

# Substituir RAW
html = re.sub(
    r"var RAW\s*=\s*\[.*?\];",
    lambda m, rj=raw_json: f"var RAW = {rj};",
    html, flags=re.DOTALL
)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"index.html gerado — {len(html)//1024} KB — {excel_date}")
assert excel_date in html
assert "EXCEL_DATE_PLACEHOLDER" not in html
print("OK")
