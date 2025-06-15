# app.py

# ================== IMPORTAÇÕES ==================
import os
import random
from datetime import datetime, timedelta, timezone
from functools import wraps
from decimal import Decimal

# Flask e extensões
from flask import (Flask, Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from flask_migrate import Migrate
from werkzeug.security import check_password_hash

# Módulos locais
from config import Config
from models import db, Usuario, Cliente, Funcionario, Conta, Transacao
from auth_services import enviar_email_otp

# ================== CONFIGURAÇÃO DO BLUEPRINT ==================
main_bp = Blueprint('main', __name__)


# ================== DECORADOR DE AUTENTICAÇÃO ==================
def login_required(role=None):
    # CORREÇÃO: @wraps deve receber a função 'f' para funcionar corretamente.
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Você precisa fazer login para acessar esta página.', 'danger')
                return redirect(url_for('main.index'))
            if role and session.get('user_type') != role:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ================== ROTAS (usando o Blueprint) ==================

@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/login', methods=['POST'])
def login():
    # CORREÇÃO 2: Remove o token antigo no início de qualquer tentativa de login.
    # Isso garante que não haverá conflitos se o servidor for reiniciado.
    if os.path.exists('token.json'):
        os.remove('token.json')
        print("Token de autorização antigo removido para garantir uma nova sessão.")

    cpf_recebido = request.form.get('cpf', '').strip()
    senha_recebida = request.form.get('senha', '').strip()
    tipo_recebido = request.form.get('tipo', '').strip()
    
    usuario = Usuario.query.filter_by(CPF=cpf_recebido, tipo_usuario=tipo_recebido).first()

    if usuario and check_password_hash(usuario.senha_hash, senha_recebida):
        otp = str(random.randint(100000, 999999))
        if enviar_email_otp(usuario.email, usuario.nome, otp):
            usuario.otp_ativo = otp
            usuario.otp_expiracao = datetime.now(timezone.utc) + timedelta(minutes=10)
            db.session.commit()
            session['id_usuario_para_verificar'] = usuario.id_usuario
            flash('Um código de verificação foi enviado para o seu e-mail.', 'info')
            return redirect(url_for('main.verify_otp'))
        else:
            # Se o envio de e-mail falhar, volta para a index com uma mensagem.
            return redirect(url_for('main.index'))
    else:
        # CORREÇÃO 1: A senha ou usuário estão errados.
        # Pisca a mensagem de erro e redireciona DE VOLTA para a página de login (index).
        # O seu template index.html deve exibir essa mensagem flash.
        flash('CPF, senha ou tipo de usuário inválidos.', 'danger')
        return redirect(url_for('main.index'))


@main_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    # ... (código da rota sem alterações) ...
    if 'id_usuario_para_verificar' not in session:
        flash('Por favor, faça o login primeiro.', 'info')
        return redirect(url_for('main.index'))
    user_id = session['id_usuario_para_verificar']
    usuario = Usuario.query.get(user_id)
    if not usuario:
        flash('Usuário não encontrado. Tente novamente.', 'danger')
        session.pop('id_usuario_para_verificar', None)
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        submitted_otp = request.form.get('otp')
        expiracao = usuario.otp_expiracao
        if expiracao and expiracao.tzinfo is None:
            expiracao = expiracao.replace(tzinfo=timezone.utc)
        if usuario.otp_ativo == submitted_otp and expiracao and datetime.now(timezone.utc) < expiracao:
            usuario.otp_ativo = None
            usuario.otp_expiracao = None
            db.session.commit()
            session.pop('id_usuario_para_verificar', None)
            session['user_id'] = usuario.id_usuario
            session['user_type'] = usuario.tipo_usuario
            flash('Login realizado com sucesso!', 'success')
            if usuario.tipo_usuario == 'Cliente':
                return redirect(url_for('main.dashboard_cliente'))
            else:
                # Futuramente, redirecionar para o dashboard de funcionário
                return redirect(url_for('main.dashboard_cliente'))
        else:
            flash('Código OTP inválido ou expirado.', 'danger')
            session.pop('id_usuario_para_verificar', None)
            return redirect(url_for('main.index'))
    return render_template('verify_otp.html')


@main_bp.route('/logout')
def logout():
    # ... (código da rota sem alterações) ...
    session.clear()
    if os.path.exists('token.json'):
        os.remove('token.json')
        print("Arquivo token.json removido com sucesso.")
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))


@main_bp.route('/dashboard_cliente')
@login_required(role='Cliente')
def dashboard_cliente():
    # ... (código da rota sem alterações) ...
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    saldo_atual = cliente.contas[0].saldo if cliente.contas else 0.0
    return render_template('dashboard_cliente.html',
                           nome_usuario=cliente.usuario.nome,
                           score_credito=cliente.score_credito,
                           saldo=saldo_atual)


@main_bp.route('/transferencia', methods=['GET', 'POST'])
@login_required(role='Cliente')
def transferencia():
    # ... (código da rota sem alterações) ...
    cliente_origem = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta_origem = cliente_origem.contas[0] if cliente_origem.contas else None
    if not conta_origem:
        flash('Nenhuma conta bancária encontrada para realizar a operação.', 'danger')
        return redirect(url_for('main.dashboard_cliente'))
    if request.method == 'POST':
        numero_conta_destino = request.form.get('numero_conta_destino')
        valor_str = request.form.get('valor')
        try:
            valor = Decimal(valor_str.replace(',', '.'))
            if valor <= 0:
                flash('O valor da transferência deve ser positivo.', 'danger')
                return redirect(url_for('main.transferencia'))
        except (ValueError, TypeError):
            flash('Valor inválido para a transferência.', 'danger')
            return redirect(url_for('main.transferencia'))
        conta_destino = Conta.query.filter_by(numero_conta=numero_conta_destino).first()
        if not conta_destino:
            flash('A conta de destino não foi encontrada.', 'danger')
        elif conta_destino.id_conta == conta_origem.id_conta:
            # CORREÇÃO: Corrigido o 'не' para 'não'
            flash('Você não pode transferir para a sua própria conta.', 'warning')
        elif conta_origem.saldo < valor:
            flash('Saldo insuficiente para realizar a transferência.', 'danger')
        else:
            try:
                conta_origem.saldo -= valor
                conta_destino.saldo += valor
                nova_transacao = Transacao(tipo_transacao='Transferencia', valor=valor, descricao=f'Transferência de {conta_origem.numero_conta} para {conta_destino.numero_conta}', id_conta_origem=conta_origem.id_conta, id_conta_destino=conta_destino.id_conta)
                db.session.add(nova_transacao)
                db.session.commit()
                flash(f'Transferência de R$ {valor:.2f} realizada com sucesso!', 'success')
                return redirect(url_for('main.dashboard_cliente'))
            except Exception as e:
                db.session.rollback()
                print(f"Erro na transação: {e}")
                flash('Ocorreu um erro ao processar a transferência. Tente novamente.', 'danger')
    return render_template('transferencia.html', saldo=conta_origem.saldo, nome_usuario=cliente_origem.usuario.nome)


@main_bp.route('/deposito', methods=['GET', 'POST'])
@login_required(role='Cliente')
def deposito():
    # ... (código da rota sem alterações) ...
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0] if cliente.contas else None
    if not conta:
        flash('Nenhuma conta bancária encontrada para realizar a operação.', 'danger')
        return redirect(url_for('main.dashboard_cliente'))
    if request.method == 'POST':
        valor_str = request.form.get('valor')
        try:
            valor = Decimal(valor_str.replace(',', '.'))
            if valor <= 0:
                raise ValueError("O valor do depósito deve ser positivo.")
            conta.saldo += valor
            nova_transacao = Transacao(tipo_transacao='Deposito', valor=valor, descricao=f'Depósito em conta', id_conta_destino=conta.id_conta)
            db.session.add(nova_transacao)
            db.session.commit()
            flash(f'Depósito de R$ {valor:.2f} realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard_cliente'))
        except ValueError as e:
            flash(str(e) or 'Valor de depósito inválido.', 'danger')
        except Exception as e:
            db.session.rollback()
            print(f"Erro no depósito: {e}")
            flash('Ocorreu um erro ao processar o depósito.', 'danger')
    return render_template('deposito.html', nome_usuario=cliente.usuario.nome, saldo=conta.saldo)


@main_bp.route('/saque', methods=['GET', 'POST'])
@login_required(role='Cliente')
def saque():
    # ... (código da rota sem alterações) ...
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0] if cliente.contas else None
    if not conta:
        flash('Nenhuma conta bancária encontrada para realizar a operação.', 'danger')
        return redirect(url_for('main.dashboard_cliente'))
    if request.method == 'POST':
        valor_str = request.form.get('valor')
        try:
            valor = Decimal(valor_str.replace(',', '.'))
            if valor <= 0:
                raise ValueError("O valor do saque deve ser positivo.")
            if conta.saldo < valor:
                raise ValueError("Saldo insuficiente para realizar o saque.")
            conta.saldo -= valor
            nova_transacao = Transacao(tipo_transacao='Saque', valor=valor, descricao=f'Saque da conta', id_conta_origem=conta.id_conta)
            db.session.add(nova_transacao)
            db.session.commit()
            flash(f'Saque de R$ {valor:.2f} realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard_cliente'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            print(f"Erro no saque: {e}")
            flash('Ocorreu um erro ao processar o saque.', 'danger')
    return render_template('saque.html', nome_usuario=cliente.usuario.nome, saldo=conta.saldo)


# ================== FÁBRICA DE APLICAÇÃO E EXECUÇÃO ==================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app, db)
    app.register_blueprint(main_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
