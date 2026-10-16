import random

from flask import Flask, jsonify, render_template, request

import dinheiro as d

app = Flask(__name__, static_folder="public/static", static_url_path="/static")


@app.get("/")
def inicio():
    return render_template("index.html", dinheiro=d.DINHEIRO)


@app.get("/api/dinheiro")
def api_dinheiro():
    return jsonify([d.INFO[v] for v in d.VALORES])


@app.get("/api/equivalencias/<int:centavos>")
def api_equivalencias(centavos: int):
    if centavos <= 0 or centavos > 20000 or centavos % 5:
        return jsonify({"erro": "Escolha um valor entre 5 centavos e R$ 200, múltiplo de 5 centavos."}), 400
    return jsonify({
        "valor": centavos,
        "valor_formatado": d.formatar(centavos),
        "simples": d.equivalencias_simples(centavos),
        "total_combinacoes": d.contar_combinacoes(centavos),
        "exemplos": d.listar_combinacoes(centavos, limite=int(request.args.get("limite", 30))),
        "menos_pecas": d.troco_minimo(centavos),
    })


@app.get("/api/desafio")
def api_desafio():
    """Gera um desafio: 'monte X usando só Y'."""
    alvo = random.choice([100, 200, 500, 1000, 2000, 50, 25])
    opcoes = [v for v in d.VALORES if v < alvo and alvo % v == 0]
    peca = random.choice(opcoes)
    return jsonify({
        "alvo": alvo,
        "alvo_formatado": d.formatar(alvo),
        "peca": d.INFO[peca],
        "resposta": alvo // peca,
    })


@app.post("/api/conferir")
def api_conferir():
    dados = request.get_json(silent=True) or {}
    alvo = int(dados.get("alvo", 0))
    pecas = dados.get("pecas", [])
    total = sum(int(p) for p in pecas if int(p) in d.INFO)
    return jsonify({
        "total": total,
        "total_formatado": d.formatar(total),
        "acertou": total == alvo,
        "falta": max(alvo - total, 0),
        "falta_formatado": d.formatar(max(alvo - total, 0)),
        "passou": max(total - alvo, 0),
        "passou_formatado": d.formatar(max(total - alvo, 0)),
    })


if __name__ == "__main__":
    app.run(debug=True)
