# seed.py

# Importa as ferramentas necessárias do seu app
# 'app' nos dá o contexto da aplicação, e 'db' a conexão com o banco.
from app import create_app, db
from models import Usuario, Cliente, Funcionario
from werkzeug.security import generate_password_hash
from datetime import date

# Criamos uma instância do app para poder usar seu contexto
app = create_app()

# Função para criar e salvar os dados
def seed_data():
    # O 'with app.app_context()' é MUITO IMPORTANTE. Ele diz ao SQLAlchemy:
    # "Execute as operações a seguir usando a configuração e conexão do banco de dados
    # definidas no nosso app Flask". Sem isso, daria erro.
    with app.app_context():
        # Limpa as tabelas para evitar duplicatas se rodarmos o script de novo
        print("Limpando dados antigos...")
        db.session.query(Funcionario).delete()
        db.session.query(Cliente).delete()
        db.session.query(Usuario).delete()
        db.session.commit()
        
        # --- 1. Criação do Usuário CLIENTE ---
        print("Criando usuário cliente de teste...")
        
        # Primeiro, o registro na tabela 'usuario'
        usuario_cliente = Usuario(
            nome='Darth Vader',
            CPF='11111111111',
            data_nascimento=date(1977, 5, 25),
            telefone='(11) 91111-1111',
            email='nathanaelmagno000@gmail.com',
            tipo_usuario='Cliente',
            # NUNCA salve senhas em texto! Usamos a função para gerar um hash seguro.
            senha_hash=generate_password_hash('senha123', method='pbkdf2:sha256')
        )
        
        # Adiciona o usuário à "área de preparação" do SQLAlchemy
        db.session.add(usuario_cliente)
        
        # Salva o usuário no banco. Isso é necessário para que ele receba um 'id_usuario'.
        db.session.commit()

        # Agora que o usuário existe, criamos o registro 'cliente' correspondente
        novo_cliente = Cliente(
            id_usuario=usuario_cliente.id_usuario,
            score_credito=750.00
        )
        db.session.add(novo_cliente)
        print(" -> Usuário 'Darth Vader' (Cliente) criado.")

        # --- 2. Criação do Usuário FUNCIONÁRIO ---
        print("Criando usuário funcionário de teste...")

        # O registro na tabela 'usuario'
        usuario_funcionario = Usuario(
            nome='Sheev Palpatine',
            CPF='22222222222',
            data_nascimento=date(1953, 1, 1),
            telefone='(11) 92222-2222',
            email='palpatine@imperio.com',
            tipo_usuario='Funcionario',
            senha_hash=generate_password_hash('ordem66', method='pbkdf2:sha256')
        )
        db.session.add(usuario_funcionario)
        db.session.commit()

        # O registro 'funcionario' correspondente
        novo_funcionario = Funcionario(
            id_usuario=usuario_funcionario.id_usuario,
            codigo_funcionario='EMP001',
            cargo='Gerente',
            id_supervisor=None # O gerente principal não tem supervisor
        )
        db.session.add(novo_funcionario)
        print(" -> Usuário 'Sheev Palpatine' (Funcionário) criado.")

        # Finalmente, salva todas as adições (cliente e funcionario) no banco
        db.session.commit()
        print("\nBanco de dados populado com sucesso!")


# Esta linha permite que a gente execute o script diretamente pelo terminal com 'python seed.py'
if __name__ == '__main__':
    seed_data()