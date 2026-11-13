// Funções que falam com a API da clínica. Use em todas as páginas.
const API_URL = "http://localhost:5000";

async function requisicao(metodo, caminho, corpo) {
  const opcoes = { method: metodo, headers: { "Content-Type": "application/json" } };
  // Quando houver login, enviar o token aqui:
  // const token = localStorage.getItem("token");
  // if (token) opcoes.headers["Authorization"] = `Bearer ${token}`;
  if (corpo !== undefined) opcoes.body = JSON.stringify(corpo);

  const resposta = await fetch(API_URL + caminho, opcoes);
  const dados = await resposta.json();
  if (!resposta.ok) throw new Error(dados.erro || "Erro na requisição");
  return dados;
}

const api = {
  get: (caminho) => requisicao("GET", caminho),
  post: (caminho, corpo) => requisicao("POST", caminho, corpo),
  put: (caminho, corpo) => requisicao("PUT", caminho, corpo),
  delete: (caminho) => requisicao("DELETE", caminho),
};
