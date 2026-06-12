# Solutis · Dashboard de Recebimentos

Dashboard executivo gerado automaticamente a partir do Excel de fluxo de caixa.

## Como atualizar os dados

1. Renomeie seu Excel para: **`Fluxo_de_recebimento.xlsx`**
2. Acesse a pasta [`data/`](./data/) neste repositório
3. Clique em **Add file → Upload files** e substitua o arquivo anterior
4. Confirme o commit — o pipeline roda automaticamente

O dashboard estará atualizado em **~2 minutos**.

## Acesso

🔗 **https://vitor-esteves-bra.github.io/solutis-dashboard/**

Senha: `data_analytics`

## Estrutura do repositório

```
solutis-dashboard/
├── data/
│   └── Fluxo_de_recebimento.xlsx   ← substituir para atualizar os dados
├── .github/
│   └── workflows/
│       └── update-dashboard.yml    ← pipeline automático
├── process_data.py                 ← script Python de processamento
├── template.html                   ← layout, design e lógica do dashboard
└── index.html                      ← dashboard publicado (gerado automaticamente)
```

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Dados | Python · pandas · openpyxl |
| Frontend | HTML · CSS · JavaScript · Chart.js |
| CI/CD | GitHub Actions |
| Hospedagem | GitHub Pages |
