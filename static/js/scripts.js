/**
 * @file scripts.js
 * @description Gerencia a interatividade da página de login, como a troca entre a seleção de acesso e o formulário.
 */

/**
 * Exibe o formulário de login e oculta os botões de escolha de acesso.
 * Configura o título e o label do formulário com base no tipo de usuário.
 * * @param {string} userType - O tipo de usuário, "Cliente" ou "Funcionario".
 */
function showLoginForm(userType) {
  // Pega os elementos da página que vamos manipular
  const accessChoiceDiv = document.getElementById('botoes-acesso');
  const loginForm = document.getElementById('form-login');
  const formTitle = document.getElementById('form-titulo');
  const formLabel = document.getElementById('form-label-usuario');
  const userTypeInput = document.getElementById('tipo');

  // Esconde a caixa com os botões de escolha
  accessChoiceDiv.style.display = 'none';

  // Exibe o formulário de login
  // Usamos 'flex' para que o alinhamento interno do formulário funcione bem
  loginForm.style.display = 'flex';

  // Configura o formulário de acordo com o tipo de usuário
  userTypeInput.value = userType;
  
  if (userType === 'Cliente') {
    formTitle.textContent = 'Login Cliente';
    formLabel.textContent = 'CPF:';
  } else {
    formTitle.textContent = 'Login Funcionário';
    formLabel.textContent = 'Matrícula:'; // Muda o label para funcionário
  }
}

/**
 * Exibe os botões de escolha de acesso e oculta o formulário de login.
 * Esta função é chamada pelo novo botão "voltar" (a seta).
 */
function showAccessChoice() {
  // Pega os elementos que vamos manipular
  const accessChoiceDiv = document.getElementById('botoes-acesso');
  const loginForm = document.getElementById('form-login');

  // Esconde o formulário de login
  loginForm.style.display = 'none';

  // Exibe novamente a caixa com os botões de escolha
  accessChoiceDiv.style.display = 'block';
}