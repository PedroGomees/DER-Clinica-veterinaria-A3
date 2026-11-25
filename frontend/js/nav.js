// Desenha a barra lateral (igual em toda página protegida) e monta o
// layout ".app" com a área de conteúdo. Chame renderNav("animais") no
// topo da página, passando o identificador do link que deve ficar ativo.

// Ícones em SVG, desenhados na mão (sem depender de nenhuma biblioteca
// de ícones nem de internet). Todos seguem o mesmo estilo: contorno,
// 24x24, cor herdada do texto (currentColor).
const ICONES = {
  logo: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <ellipse cx="12" cy="15.3" rx="4.3" ry="3.4"/>
    <circle cx="6.9" cy="9.3" r="1.8"/><circle cx="11" cy="6.6" r="1.8"/>
    <circle cx="15.3" cy="6.8" r="1.8"/><circle cx="18.8" cy="10" r="1.8"/>
  </svg>`,
  inicio: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M4 11.2 12 4l8 7.2"/><path d="M6 9.8V20h12V9.8"/><path d="M9.8 20v-5.3h4.4V20"/>
  </svg>`,
  tutores: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="8.2" r="3.4"/><path d="M5 20c0-3.9 3.1-6.6 7-6.6s7 2.7 7 6.6"/>
  </svg>`,
  animais: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <ellipse cx="12" cy="15.5" rx="4.2" ry="3.3"/>
    <circle cx="7.1" cy="9.3" r="1.6"/><circle cx="11" cy="6.8" r="1.6"/>
    <circle cx="15" cy="6.8" r="1.6"/><circle cx="18.3" cy="9.6" r="1.6"/>
  </svg>`,
  cadastros: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M11.5 3H19a1 1 0 0 1 1 1v7.5a1 1 0 0 1-.3.7l-8 8a1 1 0 0 1-1.4 0l-6.2-6.2a1 1 0 0 1 0-1.4l8-8a1 1 0 0 1 .4-.3z"/>
    <circle cx="16" cy="8" r="1.3" fill="currentColor" stroke="none"/>
  </svg>`,
  integracoes: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 3.3 18.5 6v5.3c0 4.4-2.8 7.8-6.5 9.4-3.7-1.6-6.5-5-6.5-9.4V6L12 3.3z"/>
    <path d="M9.2 12.1l1.9 1.9 3.7-3.7"/>
  </svg>`,
  sair: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M9 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h3"/><path d="M14.5 8 18.5 12l-4 4"/><path d="M18.5 12H9.5"/>
  </svg>`,
  menu: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/>
  </svg>`,
  imprimir: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M7 8.5V4h10v4.5"/><rect x="4.5" y="8.5" width="15" height="7" rx="1.3"/><path d="M7 14.5h10V20H7z"/>
  </svg>`,
  sino: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 10a6 6 0 0 1 12 0c0 4.2 1.3 5.6 1.8 6.2H4.2C4.7 15.6 6 14.2 6 10z"/><path d="M10 19a2.2 2.2 0 0 0 4 0"/>
  </svg>`,
  busca: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="10.5" cy="10.5" r="6.3"/><path d="M19.8 19.8 15 15"/>
  </svg>`,
};

const LINKS_NAV = [
  { id: "inicio", rotulo: "Início", href: "index.html", icone: "inicio" },
  { id: "tutores", rotulo: "Tutores", href: "tutores.html", icone: "tutores" },
  { id: "animais", rotulo: "Animais", href: "animais.html", icone: "animais" },
  { id: "cadastros", rotulo: "Espécies e raças", href: "cadastros.html", icone: "cadastros" },
  { id: "integracoes", rotulo: "Integração governo", href: "integracoes.html", icone: "integracoes" },
];

function iniciais(nome) {
  const partes = (nome || "").trim().split(/\s+/);
  const primeira = partes[0]?.[0] || "";
  const ultima = partes.length > 1 ? partes[partes.length - 1][0] : "";
  return (primeira + ultima).toUpperCase() || "V";
}

function renderNav(ativo) {
  exigirLogin();
  const veterinario = getVeterinarioLogado();

  document.body.innerHTML = `
    <button class="botao-menu-movel" id="botao-menu-movel" type="button" aria-label="Abrir menu">${ICONES.menu}</button>
    <div class="fundo-menu-movel" id="fundo-menu-movel"></div>
    <div class="app">
      <aside class="barra-lateral" id="barra-lateral">
        <div class="marca"><span class="logo-marca">${ICONES.logo}</span> Clínica Vet</div>
        <button class="botao-busca-global" id="botao-busca-global" type="button">
          ${ICONES.busca}<span class="rotulo-busca">Buscar</span><span class="atalho-busca">Ctrl K</span>
        </button>
        <nav>
          ${LINKS_NAV.map(
            (l) => `<a href="${l.href}" class="${l.id === ativo ? "ativo" : ""}">${ICONES[l.icone]}<span>${l.rotulo}</span></a>`
          ).join("")}
        </nav>
        <div class="rodape-usuario">
          <div class="avatar">${iniciais(veterinario?.nome_completo)}</div>
          <div class="info"><span class="nome">${escaparHtml(veterinario ? veterinario.nome_completo : "")}</span></div>
          <button id="botao-sair" type="button" title="Sair">${ICONES.sair}</button>
        </div>
      </aside>
      <main class="conteudo" id="conteudo"></main>
    </div>

    <div class="fundo-modal" id="fundo-busca-global" hidden>
      <div class="modal modal-busca">
        <input type="search" id="input-busca-global" placeholder="Buscar tutor ou animal..." autocomplete="off">
        <div class="resultados-busca-global" id="resultados-busca-global"></div>
      </div>
    </div>
  `;

  document.getElementById("botao-sair").addEventListener("click", logout);

  // Menu móvel: some da tela por padrão (CSS) e abre/fecha por cima do
  // conteúdo, em vez de espremer os links numa barra horizontal.
  const barraLateral = document.getElementById("barra-lateral");
  const fundoMenuMovel = document.getElementById("fundo-menu-movel");
  function alternarMenuMovel() {
    barraLateral.classList.toggle("aberta");
    fundoMenuMovel.classList.toggle("aberto");
  }
  document.getElementById("botao-menu-movel").addEventListener("click", alternarMenuMovel);
  fundoMenuMovel.addEventListener("click", alternarMenuMovel);
  barraLateral.querySelectorAll("nav a").forEach((a) => a.addEventListener("click", alternarMenuMovel));

  configurarBuscaGlobal(barraLateral, fundoMenuMovel);

  return document.getElementById("conteudo");
}

// Busca global (Ctrl+K): procura tutores e animais ao mesmo tempo e leva
// direto para a tela de cada um. Não precisa de rota nova na API: usa os
// mesmos GET /tutores/?q= e GET /animais/?q= que as telas de lista já usam.
function configurarBuscaGlobal(barraLateral, fundoMenuMovel) {
  const fundo = document.getElementById("fundo-busca-global");
  const input = document.getElementById("input-busca-global");
  const resultados = document.getElementById("resultados-busca-global");
  const MENSAGEM_INICIAL = '<p class="mensagem-busca">Digite para buscar tutores e animais...</p>';

  function abrir() {
    barraLateral.classList.remove("aberta");
    fundoMenuMovel.classList.remove("aberto");
    fundo.hidden = false;
    input.value = "";
    resultados.innerHTML = MENSAGEM_INICIAL;
    setTimeout(() => input.focus(), 20);
  }
  function fechar() { fundo.hidden = true; }

  document.getElementById("botao-busca-global").addEventListener("click", abrir);
  fundo.addEventListener("click", (ev) => { if (ev.target === fundo) fechar(); });

  document.addEventListener("keydown", (ev) => {
    if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "k") {
      ev.preventDefault();
      fundo.hidden ? abrir() : fechar();
    } else if (ev.key === "Escape" && !fundo.hidden) {
      fechar();
    }
  });

  function itemResultado(icone, href, titulo, subtitulo) {
    return `<a class="resultado-busca" href="${href}">${ICONES[icone]}
      <span class="texto-resultado"><strong>${escaparHtml(titulo)}</strong><span>${escaparHtml(subtitulo)}</span></span>
    </a>`;
  }

  async function buscar(termo) {
    resultados.innerHTML = '<p class="mensagem-busca">Buscando...</p>';
    try {
      const [tutores, animais] = await Promise.all([
        api.get(`/tutores/?q=${encodeURIComponent(termo)}`),
        api.get(`/animais/?q=${encodeURIComponent(termo)}`),
      ]);
      if (tutores.length === 0 && animais.length === 0) {
        resultados.innerHTML = '<p class="mensagem-busca">Nada encontrado.</p>';
        return;
      }
      resultados.innerHTML =
        (tutores.length
          ? '<div class="grupo-resultado-busca">Tutores</div>' +
            tutores.slice(0, 6).map((t) => itemResultado("tutores", `animais.html?id_tutor=${t.id_tutor}`, t.nome_completo, t.cpf)).join("")
          : "") +
        (animais.length
          ? '<div class="grupo-resultado-busca">Animais</div>' +
            animais.slice(0, 6).map((a) => itemResultado("animais", `animal.html?id=${a.id_animal}`, a.nome, `tutor: ${a.nome_tutor}`)).join("")
          : "");
    } catch (erro) {
      resultados.innerHTML = `<p class="mensagem-busca">${escaparHtml(erro.message)}</p>`;
    }
  }

  let temporizador;
  input.addEventListener("input", () => {
    clearTimeout(temporizador);
    const termo = input.value.trim();
    if (!termo) { resultados.innerHTML = MENSAGEM_INICIAL; return; }
    temporizador = setTimeout(() => buscar(termo), 300);
  });
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
