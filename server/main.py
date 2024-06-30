import os
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, jsonify
from flask_cors import CORS
from project_blueprint import create_project_blueprint
from trade_blueprint import create_trade_blueprint

# Initialize Firebase app
cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def create_app(*args, **kwargs):
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Register blueprints with the Firestore client
    app.register_blueprint(create_project_blueprint(db))
    app.register_blueprint(create_trade_blueprint(db))

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return jsonify({'status': 'API is working'})

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
