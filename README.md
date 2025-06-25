# 💰 BANCO MALVADER

Sistema bancário educacional desenvolvido para a disciplina **Laboratório de Banco de Dados** – Universidade Católica de Brasília.

## 📌 Objetivo

Criar uma aplicação bancária com interface gráfica e persistência em banco de dados MySQL, aplicando conceitos avançados de Programação Orientada a Objetos (POO), modelagem relacional e programação SQL. O projeto foca em segurança, desempenho, usabilidade e integridade dos dados.

## 🛠️ Tecnologias Utilizadas

- **Back-end**: Python + Flask
- **Banco de Dados**: MySQL 8.x
- **ORM/Conexão**: SQLAlchemy / PyMySQL
- **Front-end**: HTML, CSS, Jinja2
- **E-mails OTP**: Google Gmail API
- **Segurança**: OTP (One-Time Password), hash seguro de senhas (Werkzeug), validações no banco de dados.

## 🧱 Estrutura do Projeto

| Arquivo/Pasta | Descrição |
| :--- | :--- |
| `app.py` | Controlador principal com as rotas Flask. |
| `config.py` | Configurações da aplicação e do banco de dados. |
| `models.py` | Modelos de dados (tabelas) usando SQLAlchemy. |
| `requirements.txt` | Lista de todas as dependências Python para instalação. |
| **`templates/`** | **Pasta com todos os arquivos HTML (vistas).** |
| **`templates/components/`** | **Componentes reutilizáveis incluídos nas páginas.**|
| **`static/`**| **Pasta com arquivos estáticos (CSS, JS, imagens).** |

---

## 🔐 Funcionalidades Principais

### 🧑‍💼 Funcionário
- Login com senha + OTP
- Abertura/encerramento de contas (CP, CC, CI)
- Cadastro e gerenciamento de clientes e funcionários
- Geração de relatórios financeiros (PDF/Excel)
- Controle hierárquico de permissões
- Consulta e alteração de dados com registro em auditoria

### 👤 Cliente
- Login com senha + OTP
- Consultar saldo, limite e extratos
- Realizar depósitos, saques e transferências
- Encerramento de sessão com log

## 🗃️ Banco de Dados

Estrutura relacional com:
- 12+ tabelas (cliente, conta, transação, funcionário, etc.)
- Gatilhos (validação de senha, saldo, limites)
- Procedures (gerar OTP, calcular score de crédito)
- Views (resumo de contas, movimentações recentes)
- Índices e constraints para garantir desempenho e integridade

## 🚀 Configuração e Execução
- Siga os passos abaixo para rodar o projeto. É necessário ter o Python e o MySQL instalados na máquina.

> ⚠️ **Atenção: Configuração da API do Google**
> Para que a funcionalidade de envio de e-mails com OTP (One-Time Password) funcione, é **obrigatório** configurar as credenciais da API do Gmail no seu Google Cloud Platform e autorizar o uso para este projeto. O envio de e-mails não funcionará sem essa autorização prévia.

### Passo 1: Instalação das Dependências
Abra o terminal na pasta raiz do projeto e instale todas as bibliotecas listadas no arquivo `requirements.txt` com o seguinte comando:
```bash
pip install -r requirements.txt
```

### Passo 2: Configuração do Banco de Dados
Para a aplicação funcionar, ela precisa se conectar a um banco de dados MySQL.

#### Crie o Banco de Dados:
Abra o MySQL Workbench e execute o seguinte comando para criar o banco de dados vazio que será usado pela aplicação:
```bash
CREATE DATABASE banco_db;
```

#### Ajuste a Senha de Conexão:
Abra o arquivo config.py no seu editor de código. Localize a linha SQLALCHEMY_DATABASE_URI e altere a senha para a mesma que você usa no seu MySQL Workbench.

Exemplo no arquivo config.py:
Altere "sua_senha_aqui" para a sua senha do usuário 'root' do MySQL
```bash
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:sua_senha_aqui@localhost/banco_db" 
)
```

#### Crie os Scripts de Migração:
Volte para o terminal (na pasta do projeto) e rode o comando abaixo. Ele irá detectar os modelos de tabelas no seu código e gerar os scripts para criar a estrutura do banco de dados.
```bash
flask db migrate -m "Criação inicial das tabelas"
```

#### Crie as Tabelas:
Agora, execute o comando a seguir para aplicar os scripts gerados no passo anterior e criar de fato todas as tabelas no seu banco de dados.
```bash
flask db upgrade
```

#### Popule o Banco (Seed):
Para ter dados iniciais para teste (como um usuário admin e um cliente), rode o comando a seguir. Ele irá inserir esses dados nas tabelas que acabaram de ser criadas.
```bash
python seed.py
```

### Passo 3: Executar a Aplicação
Com tudo configurado, inicie o servidor Flask com o comando:
```bash
flask run
```

A aplicação estará disponível no seu navegador no endereço http://127.0.0.1:5000.

## 👩🏻‍💻 Desenvolvedores

- Isabela Martins Bandeira
- Natália Ematné Kruchak
- Nathanael Victor Paiva Magno
