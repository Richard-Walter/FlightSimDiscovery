from flightsimdiscovery import create_app
from flightsimdiscovery import db

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
