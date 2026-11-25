// Desenha a barra lateral (igual em toda página protegida) e monta o
// layout ".app" com a área de conteúdo. Chame renderNav("animais") no
// topo da página, passando o identificador do link que deve ficar ativo.

const LINKS_NAV = [
  { id: "inicio", rotulo: "Início", href: "index.html" },
  { id: "tutores", rotulo: "Tutores", href: "tutores.html" },
  { id: "animais", rotulo: "Animais", href: "animais.html" },
  { id: "cadastros", rotulo: "Espécies e raças", href: "cadastros.html" },
  { id: "integracoes", rotulo: "Integração governo", href: "integracoes.html" },
];

function renderNav(ativo) {
  exigirLogin();
  const veterinario = getVeterinarioLogado();

  document.body.innerHTML = `
    <div class="app">
      <aside class="barra-lateral">
        <div class="marca"><span>🐾</span> Clínica Vet</div>
        <nav>
          ${LINKS_NAV.map(
            (l) => `<a href="${l.href}" class="${l.id === ativo ? "ativo" : ""}">${l.rotulo}</a>`
          ).join("")}
        </nav>
        <div class="rodape-usuario">
          <span class="nome">${veterinario ? veterinario.nome_completo : ""}</span>
          <button id="botao-sair" type="button">Sair</button>
        </div>
      </aside>
      <main class="conteudo" id="conteudo"></main>
    </div>
  `;

  document.getElementById("botao-sair").addEventListener("click", logout);
  return document.getElementById("conteudo");
}

function escaparHtml(texto) {
  const div = document.createElement("div");
  div.textContent = texto ?? "";
  return div.innerHTML;
}

// A API manda as datas "cruas" (ex.: "2026-11-24" ou "2026-11-24 14:30:00"),
// sem indicar fuso horário nenhum (ver api-clinica/app/json_provider.py).
// Por isso NÃO usamos `new Date(texto)` direto: o construtor do JavaScript
// tenta adivinhar o fuso e cada navegador adivinha diferente, deslocando a
// hora (e às vezes até o dia). Em vez disso, lemos os números na mão e
// montamos a data já no fuso local, sem nenhuma conversão.
function _partesDaData(valor) {
  const m = /^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2}))?/.exec(valor || "");
  if (!m) return null;
  const [, ano, mes, dia, hora, minuto] = m;
  return new Date(Number(ano), Number(mes) - 1, Number(dia), Number(hora || 0), Number(minuto || 0));
}

function formatarData(valor) {
  if (!valor) return "—";
  const d = _partesDaData(valor);
  if (!d) return valor;
  return d.toLocaleDateString("pt-BR");
}

function formatarDataHora(valor) {
  if (!valor) return "—";
  const d = _partesDaData(valor);
  if (!d) return valor;
  return d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function mostrarAviso(container, mensagem, tipo = "erro") {
  container.innerHTML = `<div class="aviso aviso-${tipo}">${escaparHtml(mensagem)}</div>`;
}
