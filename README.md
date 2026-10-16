# 🐷 Aprender com Dinheiro

Simulação de contagem de dinheiro brasileiro para ensinar crianças que, por exemplo,
**a nota de R$ 2 equivale a 4 moedas de 50 centavos** — e todas as outras combinações.

Feito em **Python (Flask)** e publicado no **Vercel**.

## O que a criança pode fazer

| Modo | Como funciona |
|---|---|
| 🔍 **Explorar** | Toca numa nota ou moeda e vê todas as trocas com um só tipo (R$ 2 = 2 × R$ 1 = 4 × 50¢ = 8 × 25¢ = 20 × 10¢ = 40 × 5¢), quantas combinações misturadas existem e vários exemplos. Tocar numa linha lê a frase em voz alta. |
| 🧺 **Montar valor** | Escolhe um valor e vai colocando notas e moedas no cofrinho até acertar. Mostra quanto falta ou quanto passou. |
| ⭐ **Desafio** | Perguntas do tipo "Quantas moedas de 25 centavos formam R$ 1?" com placar de acertos. |
| 🍎 **Para professores** | Em `/atividades`: gera folhas A4 para imprimir (Quantas cabem?, Quanto dinheiro tem aqui?, Quanto falta?, Ligue os valores iguais e Dinheirinho para recortar), em 3 níveis, colorida ou preto e branco, com gabarito. |

Notas: R$ 200, 100, 50, 20, 10, 5, 2 · Moedas: R$ 1, 50¢, 25¢, 10¢, 5¢.

## Rodar no computador

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000

## Estrutura

```
app.py              # rotas Flask (página + API)
dinheiro.py         # lógica: equivalências, contagem de combinações, troco mínimo
atividades.py       # gerador das folhas de atividades para professores
templates/index.html
public/static/      # CSS e JavaScript (servidos pela CDN do Vercel)
requirements.txt
```

## API

- `GET /api/equivalencias/<centavos>` — ex.: `/api/equivalencias/200`
- `GET /api/desafio` — desafio aleatório
- `POST /api/conferir` — `{"alvo": 200, "pecas": [50, 50, 100]}`

## Deploy no Vercel

O Vercel detecta o Flask automaticamente pelo `app.py`. Basta importar o repositório
em vercel.com → *Add New Project* (nome do projeto: `aprendercomdinheiro`).
