"""Gerador de folhas de atividades para imprimir (área do professor).

Cada folha é gerada a partir de um número (semente). O mesmo número sempre gera
a mesma folha, então o professor pode reimprimir ou compartilhar a folha exata.
"""

import random

import dinheiro as d

TIPOS = {
    "quantas": {
        "titulo": "Quantas cabem?",
        "instrucao": "Escreva quantas moedas ou notas são necessárias para formar o valor.",
    },
    "somar": {
        "titulo": "Quanto dinheiro tem aqui?",
        "instrucao": "Conte as notas e moedas e escreva o valor total.",
    },
    "ligar": {
        "titulo": "Ligue os valores iguais",
        "instrucao": "Ligue cada nota ou moeda da esquerda ao grupo da direita que vale a mesma coisa.",
    },
    "completar": {
        "titulo": "Quanto falta?",
        "instrucao": "Veja quanto dinheiro já tem e escreva quanto falta para chegar ao valor pedido.",
    },
    "recortar": {
        "titulo": "Dinheirinho para recortar",
        "instrucao": "Recorte as notas e moedas e use para brincar de loja, troco e contagem.",
    },
}

NIVEIS = {
    1: {"nome": "Fácil (até R$ 2)", "pecas": [200, 100, 50], "max": 200},
    2: {"nome": "Médio (até R$ 10)", "pecas": [1000, 500, 200, 100, 50, 25], "max": 1000},
    3: {"nome": "Difícil (até R$ 50)", "pecas": [5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5], "max": 5000},
}


def _nome(valor: int, qtd: int) -> str:
    info = d.INFO[valor]
    if info["tipo"] == "nota":
        base = "notas" if qtd != 1 else "nota"
    else:
        base = "moedas" if qtd != 1 else "moeda"
    return f"{base} de {info['rotulo']}"


def _expandir(grupo):
    """[(valor, qtd), ...] -> [valor, valor, ...] em ordem decrescente."""
    return [v for v, k in sorted(grupo, reverse=True) for _ in range(k)]


def _pares_quantas(nivel):
    cfg = NIVEIS[nivel]
    pares = []
    for alvo in d.VALORES:
        if alvo > cfg["max"]:
            continue
        for p in cfg["pecas"]:
            if p < alvo and alvo % p == 0 and alvo // p <= 20:
                pares.append((alvo, p))
    return pares


def _quantas(rng, nivel, qtd):
    pares = _pares_quantas(nivel)
    rng.shuffle(pares)
    itens = []
    for alvo, p in (pares * 3)[:qtd]:
        n = alvo // p
        itens.append({
            "alvo": alvo,
            "peca": p,
            "texto": f"Quantas {_nome(p, 2)} formam",
            "resposta": f"{n} {_nome(p, n)}",
        })
    return itens


def _somar(rng, nivel, qtd):
    pecas = NIVEIS[nivel]["pecas"]
    maximo = {1: 4, 2: 6, 3: 7}[nivel]
    itens = []
    for _ in range(qtd):
        n = rng.randint(2, maximo)
        grupo = sorted((rng.choice(pecas) for _ in range(n)), reverse=True)
        itens.append({"pecas": grupo, "resposta": d.formatar(sum(grupo))})
    return itens


def _completar(rng, nivel, qtd):
    pecas = NIVEIS[nivel]["pecas"]
    alvos = [v for v in d.VALORES if v <= NIVEIS[nivel]["max"] and v >= 100] or [100]
    itens = []
    while len(itens) < qtd:
        alvo = rng.choice(alvos)
        menores = [p for p in pecas if p < alvo]
        if not menores:
            continue
        grupo, total = [], 0
        for _ in range(rng.randint(1, 5)):
            p = rng.choice(menores)
            if total + p < alvo:
                grupo.append(p)
                total += p
        if not grupo:
            continue
        itens.append({
            "alvo": alvo,
            "pecas": sorted(grupo, reverse=True),
            "resposta": d.formatar(alvo - total),
        })
    return itens


def _grupo_equivalente(rng, alvo, pecas):
    """Um jeito de formar `alvo` com peças menores, com no máximo 8 peças."""
    menores = [p for p in pecas if p < alvo]
    opcoes = [[(p, alvo // p)] for p in menores if alvo % p == 0 and alvo // p <= 8]
    for combo in d.listar_combinacoes(alvo, limite=40, max_pecas=8):
        if all(c["valor"] in menores for c in combo) and len(combo) > 1:
            opcoes.append([(c["valor"], c["quantidade"]) for c in combo])
    return _expandir(rng.choice(opcoes)) if opcoes else None


def _ligar(rng, nivel, qtd):
    pecas = NIVEIS[nivel]["pecas"]
    candidatos = [v for v in d.VALORES if v <= NIVEIS[nivel]["max"] and any(p < v for p in pecas)]
    rng.shuffle(candidatos)
    esquerda = []
    for alvo in candidatos:
        grupo = _grupo_equivalente(rng, alvo, pecas)
        if grupo:
            esquerda.append({"alvo": alvo, "grupo": grupo})
        if len(esquerda) == min(qtd, 6):
            break
    direita = list(range(len(esquerda)))
    rng.shuffle(direita)
    letras = "ABCDEF"
    return {
        "esquerda": [{"numero": i + 1, "alvo": e["alvo"]} for i, e in enumerate(esquerda)],
        "direita": [{"letra": letras[j], "grupo": esquerda[i]["grupo"]} for j, i in enumerate(direita)],
        "gabarito": [
            {"numero": i + 1, "letra": letras[direita.index(i)], "resposta": d.formatar(e["alvo"])}
            for i, e in enumerate(esquerda)
        ],
    }


def _recortar(rng, nivel, qtd):
    pecas = NIVEIS[nivel]["pecas"]
    # quantidade de cada peça pensada para caber numa folha A4
    notas = [p for p in pecas if p >= 200]
    moedas = [p for p in pecas if p < 200]
    por_nota = 4 if len(notas) <= 3 else 3
    por_moeda = 8 if len(moedas) <= 3 else 5
    return {"notas": [p for p in notas for _ in range(por_nota)], "moedas": [p for p in moedas for _ in range(por_moeda)]}


GERADORES = {
    "quantas": _quantas,
    "somar": _somar,
    "completar": _completar,
    "ligar": _ligar,
    "recortar": _recortar,
}


def gerar_folha(tipo="quantas", nivel=1, quantidade=8, semente=None):
    tipo = tipo if tipo in TIPOS else "quantas"
    nivel = nivel if nivel in NIVEIS else 1
    quantidade = max(2, min(int(quantidade), 12))
    if semente is None:
        semente = random.randint(1000, 9999)
    rng = random.Random(f"{tipo}-{nivel}-{quantidade}-{semente}")
    return {
        "tipo": tipo,
        "nivel": nivel,
        "nivel_nome": NIVEIS[nivel]["nome"],
        "quantidade": quantidade,
        "semente": semente,
        "titulo": TIPOS[tipo]["titulo"],
        "instrucao": TIPOS[tipo]["instrucao"],
        "itens": GERADORES[tipo](rng, nivel, quantidade),
    }
