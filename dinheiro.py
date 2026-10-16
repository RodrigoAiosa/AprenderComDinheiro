"""Lógica do dinheiro brasileiro: valores em centavos para evitar erros de arredondamento."""

from functools import lru_cache

# (valor em centavos, tipo, rótulo)
DINHEIRO = [
    (20000, "nota", "R$ 200"),
    (10000, "nota", "R$ 100"),
    (5000, "nota", "R$ 50"),
    (2000, "nota", "R$ 20"),
    (1000, "nota", "R$ 10"),
    (500, "nota", "R$ 5"),
    (200, "nota", "R$ 2"),
    (100, "moeda", "R$ 1"),
    (50, "moeda", "50 centavos"),
    (25, "moeda", "25 centavos"),
    (10, "moeda", "10 centavos"),
    (5, "moeda", "5 centavos"),
]

VALORES = [v for v, _, _ in DINHEIRO]
INFO = {v: {"valor": v, "tipo": t, "rotulo": r} for v, t, r in DINHEIRO}


def formatar(centavos: int) -> str:
    reais, cent = divmod(centavos, 100)
    return f"R$ {reais},{cent:02d}"


def equivalencias_simples(alvo: int) -> list[dict]:
    """Quantas unidades de UM só tipo de dinheiro formam o valor (ex.: R$ 2 = 4 × 50 centavos)."""
    resultado = []
    for v in VALORES:
        if v < alvo and alvo % v == 0:
            resultado.append({"quantidade": alvo // v, **INFO[v]})
    return resultado


@lru_cache(maxsize=None)
def _contar(alvo: int, idx: int) -> int:
    if alvo == 0:
        return 1
    if idx >= len(VALORES):
        return 0
    v = VALORES[idx]
    return sum(_contar(alvo - k * v, idx + 1) for k in range(alvo // v + 1))


def contar_combinacoes(alvo: int, incluir_proprio: bool = False) -> int:
    """Número total de formas de montar o valor com notas e moedas menores."""
    total = _contar(alvo, 0)
    if not incluir_proprio and alvo in INFO:
        total -= 1  # tira a forma "usar a própria nota/moeda"
    return total


def listar_combinacoes(alvo: int, limite: int = 60, max_pecas: int = 12) -> list[list[dict]]:
    """Lista combinações (das com menos peças para as com mais), sem usar a própria nota/moeda."""
    valores = [v for v in VALORES if v < alvo or alvo not in INFO and v <= alvo]
    achadas: list[list[tuple[int, int]]] = []

    def busca(resto, idx, atual, pecas):
        if resto == 0:
            achadas.append(list(atual))
            return
        if idx >= len(valores) or pecas >= max_pecas:
            return
        v = valores[idx]
        for k in range(min(resto // v, max_pecas - pecas), -1, -1):
            if k:
                atual.append((v, k))
            busca(resto - k * v, idx + 1, atual, pecas + k)
            if k:
                atual.pop()

    busca(alvo, 0, [], 0)
    achadas.sort(key=lambda c: sum(k for _, k in c))
    return [[{"quantidade": k, **INFO[v]} for v, k in c] for c in achadas[:limite]]


def troco_minimo(alvo: int) -> list[dict]:
    """Menor número de peças para formar o valor (sistema brasileiro é 'guloso')."""
    resto, partes = alvo, []
    for v in VALORES:
        k, resto = divmod(resto, v)
        if k:
            partes.append({"quantidade": k, **INFO[v]})
    return partes
