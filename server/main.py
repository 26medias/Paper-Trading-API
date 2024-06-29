import os
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
from flask_cors import CORS
from project_blueprint import project_bp
from trade_blueprint import trade_bp

# Initialize Firebase app
cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def create_app(*args, **kwargs):
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    app.register_blueprint(project_bp)
    app.register_blueprint(trade_bp)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return jsonify({'status': 'API is working'})

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
