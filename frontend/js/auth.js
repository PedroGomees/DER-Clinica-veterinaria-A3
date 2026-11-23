// Funções de login/logout. Usadas por todas as páginas protegidas.

function getToken() {
  return localStorage.getItem("token");
}

function getVeterinarioLogado() {
  const bruto = localStorage.getItem("veterinario");
  return bruto ? JSON.parse(bruto) : null;
}

function salvarSessao(token, veterinario) {
  localStorage.setItem("token", token);
  localStorage.setItem("veterinario", JSON.stringify(veterinario));
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("veterinario");
  location.href = "login.html";
}

// Chame no topo de cada página protegida. Se não houver sessão,
// manda para o login antes mesmo de tentar carregar dados.
function exigirLogin() {
  if (!getToken()) {
    location.href = "login.html";
    throw new Error("redirecionando para o login");
  }
}
