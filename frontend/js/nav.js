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

function formatarData(valor) {
  if (!valor) return "—";
  // aceita "2026-11-23" ou "2026-11-23T10:30:00" / "...GMT"
  const d = new Date(valor);
  if (Number.isNaN(d.getTime())) return valor;
  return d.toLocaleDateString("pt-BR");
}

function formatarDataHora(valor) {
  if (!valor) return "—";
  const d = new Date(valor);
  if (Number.isNaN(d.getTime())) return valor;
  return d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function mostrarAviso(container, mensagem, tipo = "erro") {
  container.innerHTML = `<div class="aviso aviso-${tipo}">${escaparHtml(mensagem)}</div>`;
}
