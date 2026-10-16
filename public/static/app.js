// ---------- utilidades ----------
const BICHOS = { 20000: "🐺", 10000: "🐟", 5000: "🐆", 2000: "🐒", 1000: "🦜", 500: "🪶", 200: "🐢" };
const INFO = {};
window.DINHEIRO.forEach(([valor, tipo, rotulo]) => (INFO[valor] = { valor, tipo, rotulo }));
const VALORES = Object.keys(INFO).map(Number).sort((a, b) => b - a);

const fmt = (c) => "R$ " + Math.floor(c / 100) + "," + String(c % 100).padStart(2, "0");
const nomeCurto = (v) => (v >= 100 ? "R$ " + v / 100 : v + "¢");

function peca(valor, onClick) {
  const info = INFO[valor];
  const el = document.createElement("button");
  el.className = "dinheiro";
  el.title = info.rotulo;
  el.setAttribute("aria-label", info.rotulo);
  if (info.tipo === "nota") {
    el.innerHTML = `<div class="nota n${valor / 100}"><span>R$ ${valor / 100}</span><span class="bicho">${BICHOS[valor]}</span></div>`;
  } else {
    const txt = valor >= 100 ? "1<br>real" : valor + "<br>cent";
    el.innerHTML = `<div class="moeda m${valor}">${txt}</div>`;
  }
  if (onClick) el.addEventListener("click", () => onClick(valor, el));
  return el;
}

function grupoPecas(lista, maxMostrar = 20) {
  const box = document.createElement("div");
  box.className = "pecas pequeno";
  lista.forEach(({ valor, quantidade }, i) => {
    if (i > 0) box.insertAdjacentHTML("beforeend", '<span class="mais">+</span>');
    const n = Math.min(quantidade, maxMostrar);
    for (let k = 0; k < n; k++) box.appendChild(peca(valor));
    if (quantidade > maxMostrar) box.insertAdjacentHTML("beforeend", `<span class="mais">… (${quantidade})</span>`);
  });
  return box;
}

function frase(lista) {
  return lista
    .map(({ quantidade, tipo, rotulo }) => {
      const nome = tipo === "nota" ? (quantidade > 1 ? "notas de " : "nota de ") : quantidade > 1 ? "moedas de " : "moeda de ";
      return `${quantidade} ${nome}${rotulo.replace(" centavos", " centavos")}`;
    })
    .join(" + ");
}

function falar(texto) {
  try {
    const u = new SpeechSynthesisUtterance(texto);
    u.lang = "pt-BR";
    speechSynthesis.cancel();
    speechSynthesis.speak(u);
  } catch (e) {}
}

// ---------- abas ----------
document.querySelectorAll(".aba").forEach((b) =>
  b.addEventListener("click", () => {
    document.querySelectorAll(".aba").forEach((x) => x.classList.toggle("ativa", x === b));
    document.querySelectorAll(".painel").forEach((p) => p.classList.toggle("ativo", p.id === b.dataset.aba));
    if (b.dataset.aba === "desafio" && !desafioAtual) novoDesafio();
  })
);

// ---------- EXPLORAR ----------
const vitrineExplorar = document.getElementById("vitrine-explorar");
const resExplorar = document.getElementById("resultado-explorar");
VALORES.filter((v) => v > 5).forEach((v) => vitrineExplorar.appendChild(peca(v, explorar)));

async function explorar(valor) {
  resExplorar.innerHTML = '<p class="dica">Contando... 🧮</p>';
  const r = await fetch(`/api/equivalencias/${valor}?limite=25`).then((x) => x.json());
  resExplorar.innerHTML = "";

  const g1 = document.createElement("div");
  g1.className = "grupo";
  g1.innerHTML = `<h3>${INFO[valor].rotulo} é igual a…</h3>`;
  r.simples.forEach((s) => {
    const linha = document.createElement("div");
    linha.className = "linha";
    linha.appendChild(grupoPecas([{ valor, quantidade: 1 }]));
    linha.insertAdjacentHTML("beforeend", '<span class="igual">=</span>');
    linha.appendChild(grupoPecas([s]));
    linha.insertAdjacentHTML("beforeend", `<span class="frase">${frase([s])}</span>`);
    linha.addEventListener("click", () => falar(`${INFO[valor].rotulo} é igual a ${frase([s])}`));
    g1.appendChild(linha);
  });
  resExplorar.appendChild(g1);

  const g2 = document.createElement("div");
  g2.className = "grupo";
  g2.innerHTML = `<h3>Misturando notas e moedas</h3>
    <p>Existem <strong>${r.total_combinacoes.toLocaleString("pt-BR")}</strong> jeitos diferentes de formar ${r.valor_formatado}! Veja alguns:</p>`;
  r.exemplos
    .filter((c) => c.length > 1)
    .slice(0, 12)
    .forEach((c) => {
      const linha = document.createElement("div");
      linha.className = "linha";
      linha.appendChild(grupoPecas(c, 10));
      linha.insertAdjacentHTML("beforeend", `<span class="frase">${frase(c)}</span>`);
      linha.addEventListener("click", () => falar(frase(c)));
      g2.appendChild(linha);
    });
  resExplorar.appendChild(g2);
  resExplorar.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---------- MONTAR ----------
const selAlvo = document.getElementById("select-alvo");
[25, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 150, 375, 1275].sort((a, b) => a - b).forEach((v) => {
  selAlvo.insertAdjacentHTML("beforeend", `<option value="${v}">${fmt(v)}</option>`);
});
selAlvo.value = 200;
let alvo = 200;
let cofrinho = [];
const bandeja = document.getElementById("bandeja");
const vitrineMontar = document.getElementById("vitrine-montar");
VALORES.forEach((v) => vitrineMontar.appendChild(peca(v, (val) => { cofrinho.push(val); atualizarMontar(); })));

function atualizarMontar() {
  document.getElementById("alvo-montar").textContent = fmt(alvo);
  bandeja.innerHTML = "";
  cofrinho.forEach((v, i) =>
    bandeja.appendChild(peca(v, () => { cofrinho.splice(i, 1); atualizarMontar(); }))
  );
  const total = cofrinho.reduce((a, b) => a + b, 0);
  document.getElementById("total-montar").textContent = fmt(total);
  const barra = document.getElementById("barra-preenchida");
  barra.style.width = Math.min(100, (total / alvo) * 100) + "%";
  barra.style.background = total > alvo ? "var(--vermelho)" : "var(--verde)";
  const msg = document.getElementById("msg-montar");
  msg.className = "msg";
  if (total === 0) msg.textContent = "Toque nas notas e moedas para colocar no cofrinho!";
  else if (total < alvo) msg.textContent = `Faltam ${fmt(alvo - total)} 🤔`;
  else if (total > alvo) { msg.textContent = `Passou ${fmt(total - alvo)}! Toque numa peça do cofrinho para tirar.`; msg.classList.add("erro"); }
  else {
    msg.textContent = `🎉 Parabéns! Você montou ${fmt(alvo)} com ${cofrinho.length} peça${cofrinho.length > 1 ? "s" : ""}!`;
    msg.classList.add("ok", "festa");
    falar("Parabéns! Você conseguiu!");
  }
}
selAlvo.addEventListener("change", () => { alvo = Number(selAlvo.value); cofrinho = []; atualizarMontar(); });
document.getElementById("limpar").addEventListener("click", () => { cofrinho = []; atualizarMontar(); });
atualizarMontar();

// ---------- DESAFIO ----------
let desafioAtual = null;
let acertos = 0;
async function novoDesafio() {
  desafioAtual = await fetch("/api/desafio").then((x) => x.json());
  const { alvo, alvo_formatado, peca: p, resposta } = desafioAtual;
  const perg = document.getElementById("pergunta");
  perg.innerHTML = "";
  perg.insertAdjacentHTML("beforeend", "<span>Quantas</span>");
  perg.appendChild(grupoPecas([{ valor: p.valor, quantidade: 1 }]));
  perg.insertAdjacentHTML("beforeend", `<span>${p.tipo === "nota" ? "notas" : "moedas"} de ${p.rotulo} formam</span>`);
  perg.appendChild(grupoPecas([{ valor: alvo, quantidade: 1 }]));
  perg.insertAdjacentHTML("beforeend", "<span>?</span>");

  const set = new Set([resposta]);
  while (set.size < 4) {
    const d = resposta + Math.floor(Math.random() * 7) - 3;
    if (d > 0) set.add(d);
  }
  const opcoes = document.getElementById("opcoes");
  opcoes.innerHTML = "";
  [...set].sort((a, b) => a - b).forEach((n) => {
    const b = document.createElement("button");
    b.textContent = n;
    b.addEventListener("click", () => responder(n, b));
    opcoes.appendChild(b);
  });
  document.getElementById("msg-desafio").textContent = "";
  document.getElementById("proximo").hidden = true;
}

function responder(n, botao) {
  const { resposta, alvo_formatado, peca: p } = desafioAtual;
  const msg = document.getElementById("msg-desafio");
  document.querySelectorAll("#opcoes button").forEach((b) => (b.disabled = true));
  const nome = `${p.tipo === "nota" ? "notas" : "moedas"} de ${p.rotulo}`;
  if (n === resposta) {
    botao.classList.add("certa");
    acertos++;
    document.getElementById("acertos").textContent = acertos;
    msg.className = "msg ok festa";
    msg.textContent = `🎉 Isso! ${resposta} ${nome} formam ${alvo_formatado}!`;
  } else {
    botao.classList.add("errada");
    document.querySelectorAll("#opcoes button").forEach((b) => Number(b.textContent) === resposta && b.classList.add("certa"));
    msg.className = "msg erro";
    msg.textContent = `Quase! São ${resposta} ${nome} para formar ${alvo_formatado}.`;
  }
  falar(msg.textContent.replace(/[🎉]/g, ""));
  document.getElementById("proximo").hidden = false;
}
document.getElementById("proximo").addEventListener("click", novoDesafio);
