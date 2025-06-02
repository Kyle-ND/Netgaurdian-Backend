import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))



from flask import Flask
from Routes.auth import auth_bp
from Routes.users import users_bp
from Routes.incidents import incidents_bp
from Routes.alerts import alerts_bp
from Routes.chatbot import chatbot_bp
from flask_cors import CORS
from Routes.scan import scan_bp  # added 


def create_app():
    app = Flask(__name__)
    CORS(app)

    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(incidents_bp, url_prefix='/incidents')
    app.register_blueprint(alerts_bp, url_prefix='/alerts')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(scan_bp, url_prefix="/scan")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)