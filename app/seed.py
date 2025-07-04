from app import create_app, db
from app.models import (Usuario, Cliente, Agencia, Conta, Endereco, 
                    ContaCorrente, ContaPoupanca, ContaInvestimento)
from werkzeug.security import generate_password_hash
from datetime import date
from decimal import Decimal

app = create_app()

def seed_data():
    with app.app_context():
        print("Limpando dados antigos...")
        db.session.query(ContaInvestimento).delete()
        db.session.query(ContaCorrente).delete()
        db.session.query(ContaPoupanca).delete()
        db.session.query(Conta).delete()
        db.session.query(Cliente).delete()
        db.session.query(Agencia).delete()
        db.session.query(Endereco).delete()
        db.session.query(Usuario).delete()
        db.session.commit()
        
        print("Criando agência de teste...")
        endereco_agencia = Endereco(cep='01001-000', local='Praça da Sé', numero_casa=1, bairro='Sé', estado='SP')
        db.session.add(endereco_agencia)
        db.session.commit()
        agencia_central = Agencia(nome='Agência Central Imperial', codigo_agencia='0001', id_endereco=endereco_agencia.id_endereco)
        db.session.add(agencia_central)
        db.session.commit()

        print("\nCriando cliente com Conta Corrente...")
        usuario_1 = Usuario(nome='Nathanael (Vader)', CPF='111111', data_nascimento=date(1990, 1, 1), telefone='(11) 91111-1111', email='nathanaelmagno000@gmail.com', tipo_usuario='Cliente', senha_hash=generate_password_hash('senha123'))
        db.session.add(usuario_1)
        db.session.commit()
        cliente_1 = Cliente(id_usuario=usuario_1.id_usuario, score_credito=750.00)
        db.session.add(cliente_1)
        db.session.commit()
        conta_1 = ContaCorrente(numero_conta='12345-6', saldo=10000.00, status='Ativa', id_agencia=agencia_central.id_agencia, id_cliente=cliente_1.id_cliente, limite_cheque_especial=Decimal('500.00'), taxa_manutencao=Decimal('15.00'))
        db.session.add(conta_1)

        print("\nCriando cliente com Conta Poupança...")
        usuario_2 = Usuario(nome='Isabela (Leia)', CPF='222222', data_nascimento=date(1992, 2, 2), telefone='(11) 94444-4444', email='Isabelamb046@gmail.com', tipo_usuario='Cliente', senha_hash=generate_password_hash('senha456'))
        db.session.add(usuario_2)
        db.session.commit()
        cliente_2 = Cliente(id_usuario=usuario_2.id_usuario, score_credito=820.00)
        db.session.add(cliente_2)
        db.session.commit()
        conta_2 = ContaPoupanca(numero_conta='11223-3', saldo=7500.00, status='Ativa', id_agencia=agencia_central.id_agencia, id_cliente=cliente_2.id_cliente, taxa_rendimento=Decimal('0.05'))
        db.session.add(conta_2)

        print("\nCriando cliente com Conta de Investimento...")
        usuario_3 = Usuario(nome='Han Solo', CPF='55555555555', data_nascimento=date(1980, 7, 13), telefone='(11) 95555-5555', email='nathanaelvictor000@gmail.com', tipo_usuario='Cliente', senha_hash=generate_password_hash('senha789'))
        db.session.add(usuario_3)
        db.session.commit()

        cliente_3 = Cliente(id_usuario=usuario_3.id_usuario, score_credito=900.00)
        db.session.add(cliente_3)
        db.session.commit()

        conta_3 = ContaInvestimento(
            numero_conta='98765-4',
            saldo=50000.00,
            status='Ativa',
            id_agencia=agencia_central.id_agencia,
            id_cliente=cliente_3.id_cliente,
            perfil_risco='Alto',
            valor_minimo_deposito=Decimal('1000.00'),
            taxa_rendimento_base=Decimal('0.12')
        )
        db.session.add(conta_3)
        print(" -> Usuário 'Han Solo' e Conta de Investimento '98765-4' criados.")

        db.session.commit()
        print("\nBanco de dados populado com sucesso!")

if __name__ == '__main__':
    seed_data()
