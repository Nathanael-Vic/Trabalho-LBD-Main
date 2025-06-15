# seed.py

from app import create_app, db
from models import Usuario, Cliente, Funcionario, Agencia, Conta, Endereco
from werkzeug.security import generate_password_hash
from datetime import date

app = create_app()

def seed_data():
    with app.app_context():
        print("Limpando dados antigos...")
        # A ordem de limpeza é importante por causa das chaves estrangeiras
        db.session.query(Conta).delete()
        db.session.query(Funcionario).delete()
        db.session.query(Cliente).delete()
        db.session.query(Agencia).delete()
        db.session.query(Endereco).delete()
        db.session.query(Usuario).delete()
        db.session.commit()
        
        # --- 1. Criação de Endereço e Agência ---
        print("Criando agência de teste...")
        endereco_agencia = Endereco(
            cep='01001-000',
            local='Praça da Sé',
            numero_casa=1,
            bairro='Sé',
            estado='SP',
            complemento='Lado da Catedral'
        )
        db.session.add(endereco_agencia)
        db.session.commit()

        agencia_central = Agencia(
            nome='Agência Central Imperial',
            codigo_agencia='0001',
            id_endereco=endereco_agencia.id_endereco
        )
        db.session.add(agencia_central)
        db.session.commit()
        print(" -> Agência '0001' criada.")

        # --- 2. Criação do PRIMEIRO Usuário CLIENTE (Darth Vader) ---
        print("\nCriando o primeiro usuário cliente...")
        usuario_cliente_1 = Usuario(
            nome='Darth Vader',
            CPF='11111111111',
            data_nascimento=date(1977, 5, 25),
            telefone='(11) 91111-1111',
            email='nathanaelmagno000@gmail.com', # Mesmo e-mail
            tipo_usuario='Cliente',
            senha_hash=generate_password_hash('senha123', method='pbkdf2:sha256')
        )
        db.session.add(usuario_cliente_1)
        db.session.commit()

        cliente_1 = Cliente(
            id_usuario=usuario_cliente_1.id_usuario,
            score_credito=750.00
        )
        db.session.add(cliente_1)
        db.session.commit()

        conta_1 = Conta(
            numero_conta='12345-6',
            saldo=10000.00,
            tipo_conta='Corrente',
            status='Ativa',
            id_agencia=agencia_central.id_agencia,
            id_cliente=cliente_1.id_cliente
        )
        db.session.add(conta_1)
        print(" -> Usuário 'Darth Vader' e conta '12345-6' criados.")

        # --- 3. Criação do SEGUNDO Usuário CLIENTE (Luke Skywalker) ---
        print("\nCriando o segundo usuário cliente...")
        usuario_cliente_2 = Usuario(
            nome='Luke Skywalker',
            CPF='33333333333', # CPF diferente
            data_nascimento=date(1977, 5, 25),
            telefone='(11) 93333-3333',
            email='nathanaelvictor000@gmail.com', # Mesmo e-mail, como solicitado
            tipo_usuario='Cliente',
            senha_hash=generate_password_hash('senha456', method='pbkdf2:sha256') # Senha diferente
        )
        db.session.add(usuario_cliente_2)
        db.session.commit()

        cliente_2 = Cliente(
            id_usuario=usuario_cliente_2.id_usuario,
            score_credito=850.00
        )
        db.session.add(cliente_2)
        db.session.commit()

        conta_2 = Conta(
            numero_conta='78910-1', # Número de conta diferente
            saldo=5000.00,
            tipo_conta='Poupanca',
            status='Ativa',
            id_agencia=agencia_central.id_agencia,
            id_cliente=cliente_2.id_cliente
        )
        db.session.add(conta_2)
        print(" -> Usuário 'Luke Skywalker' e conta '78910-1' criados.")

        # --- 4. Criação do Usuário FUNCIONÁRIO (Comentado) ---
        # print("\nCriando usuário funcionário de teste...")
        # usuario_funcionario = Usuario(
        #     nome='Sheev Palpatine',
        #     CPF='22222222222',
        #     data_nascimento=date(1953, 1, 1),
        #     telefone='(11) 92222-2222',
        #     email='palpatine@imperio.com',
        #     tipo_usuario='Funcionario',
        #     senha_hash=generate_password_hash('ordem66', method='pbkdf2:sha256')
        # )
        # db.session.add(usuario_funcionario)
        # db.session.commit()
        #
        # novo_funcionario = Funcionario(
        #     id_usuario=usuario_funcionario.id_usuario,
        #     codigo_funcionario='EMP001',
        #     cargo='Gerente',
        #     id_supervisor=None
        # )
        # db.session.add(novo_funcionario)
        # print(" -> Usuário 'Sheev Palpatine' (Funcionário) criado.")

        # Finalmente, salva todas as adições no banco
        db.session.commit()
        print("\nBanco de dados populado com sucesso!")

if __name__ == '__main__':
    seed_data()
