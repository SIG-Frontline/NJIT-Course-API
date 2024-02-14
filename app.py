from flask import Flask
from API import api as api_routes
from docs import docs as docs_routes

app = Flask(__name__)

app.register_blueprint(api_routes)
app.register_blueprint(docs_routes)

if __name__ == '__main__':
    app.run(debug=True)
    