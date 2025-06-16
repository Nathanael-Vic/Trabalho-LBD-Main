# run.py
# Este é o novo ponto de entrada da sua aplicação.
# Para iniciar o servidor, execute no terminal: python run.py

from app import create_app

# Cria a instância da aplicação a partir da nossa fábrica em app/__init__.py
app = create_app()

if __name__ == '__main__':
    # Usar debug=False em produção
    app.run(debug=True, port=5000)
