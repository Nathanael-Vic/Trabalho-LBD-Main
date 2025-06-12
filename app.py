# app.py (VERSÃO CORRIGIDA E ORGANIZADA)

# ================== IMPORTAÇÕES ==================
# Flask e extensões
from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from models import db, Usuario, Cliente, Funcionario
from flask_migrate import Migrate

# Segurança e utilidades
from werkzeug.security import check_password_hash
from functools import wraps
from datetime import datetime, timedelta, timezone
import random
import os.path
import base64
from email.mime.text import MIMEText

# Bibliotecas do Google para e-mail
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ================== FUNÇÃO DE ENVIO DE EMAIL ==================
# Escopo de permissão: Apenas para enviar e-mails, nada mais.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def enviar_email_otp(destinatario, nome_usuario, otp):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        corpo_email = f"Olá, {nome_usuario}.\n\nSeu código de acesso para o Banco Malvader é: {otp}\n\nEste código expira em 10 minutos."
        message = MIMEText(corpo_email)
        message['To'] = destinatario
        message['Subject'] = "Seu Código de Acesso - Banco Malvader"
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        service.users().messages().send(userId="me", body=create_message).execute()
        print(f"E-mail com OTP enviado para {destinatario}.")
    except HttpError as error:
        print(f'Ocorreu um erro ao enviar o e-mail: {error}')

# ================== FÁBRICA DE APLICAÇÃO ==================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)

    # ================== DECORADOR DE AUTENTICAÇÃO ==================
    # Definido aqui dentro, então só pode ser usado por rotas aqui dentro.
    def login_required(role=None):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    flash('Você precisa fazer login para acessar esta página.', 'danger')
                    return redirect(url_for('index'))
                if role and session.get('user_type') != role:
                    flash('Você não tem permissão para acessar esta página.', 'danger')
                    return redirect(url_for('index'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    # ================== ROTAS ==================
    # Todas as rotas do app devem ser definidas aqui dentro.
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['POST'])
    def login():
        cpf_recebido = request.form.get('cpf', '').strip()
        senha_recebida = request.form.get('senha', '').strip()
        tipo_recebido = request.form.get('tipo', '').strip()

        usuario = Usuario.query.filter_by(CPF=cpf_recebido, tipo_usuario=tipo_recebido).first()

        if usuario and check_password_hash(usuario.senha_hash, senha_recebida):
            otp = str(random.randint(100000, 999999))
            usuario.otp_ativo = otp
            usuario.otp_expiracao = datetime.now(timezone.utc) + timedelta(minutes=10)
            db.session.commit()
            
            enviar_email_otp(usuario.email, usuario.nome, otp)

            session['id_usuario_para_verificar'] = usuario.id_usuario
            flash('Um código de verificação foi enviado para o seu e-mail.', 'info')
            return redirect(url_for('verify_otp'))
        else:
            flash('CPF, senha ou tipo de usuário inválidos.', 'danger')
            return redirect(url_for('index'))

    @app.route('/verify_otp', methods=['GET', 'POST'])
    def verify_otp():
        if 'id_usuario_para_verificar' not in session:
            flash('Por favor, faça o login primeiro.', 'info')
            return redirect(url_for('index'))

        user_id = session['id_usuario_para_verificar']
        usuario = Usuario.query.get(user_id)

        if not usuario:
             flash('Usuário não encontrado. Tente novamente.', 'danger')
             session.pop('id_usuario_para_verificar', None)
             return redirect(url_for('index'))

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
                    return redirect(url_for('dashboard_cliente'))
                else:
                    return redirect(url_for('dashboard_funcionario'))
            else:
                flash('Código OTP inválido ou expirado. Por favor, faça o login novamente para gerar um novo código.', 'danger')
                session.pop('id_usuario_para_verificar', None)
                return redirect(url_for('index'))
        
        return render_template('verify_otp.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Você foi desconectado.', 'info')
        return redirect(url_for('index'))

    @app.route('/dashboard_cliente')
    @login_required(role='Cliente')
    def dashboard_cliente():
        cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
        saldo_atual = cliente.contas[0].saldo if cliente.contas else 0.0
        
        return render_template('dashboard_cliente.html',
                               nome_usuario=cliente.usuario.nome,
                               score_credito=cliente.score_credito,
                               saldo=saldo_atual)

    @app.route('/dashboard_funcionario')
    @login_required(role='Funcionario')
    def dashboard_funcionario():
        funcionario = Funcionario.query.filter_by(id_usuario=session['user_id']).first_or_404()
        return render_template('dashboard_funcionario.html',
                               nome_usuario=funcionario.usuario.nome,
                               cargo=funcionario.cargo)

    # ================== ROTAS DE DEPÓSITO E SAQUE (MOVIDAS PARA O LUGAR CORRETO) ==================
    @app.route('/deposito', methods=['GET', 'POST'])
    @login_required(role='Cliente')
    def deposito():
        # Lógica corrigida para buscar o saldo e enviar para o template
        cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
        saldo_atual = cliente.contas[0].saldo if cliente.contas else 0.0
        
        # Ação do formulário (implementaremos depois)
        if request.method == 'POST':
            # Aqui virá a lógica para gerar o boleto
            pass

        return render_template('deposito.html', 
                               nome_usuario=cliente.usuario.nome, 
                               saldo=saldo_atual)

    @app.route('/saque', methods=['GET', 'POST'])
    @login_required(role='Cliente')
    def saque():
        cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
        saldo_atual = cliente.contas[0].saldo if cliente.contas else 0.0
        
        # Ação do formulário (implementaremos depois)
        if request.method == 'POST':
            # Aqui virá a lógica para efetuar o saque
            pass
            
        return render_template('saque.html', 
                               nome_usuario=cliente.usuario.nome, 
                               saldo=saldo_atual)

    # A função create_app deve retornar a instância do app no final
    return app

# ================== EXECUÇÃO ==================
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)