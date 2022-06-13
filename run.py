from main import app,csrf,db,socketio
from config import DevelopmentConfig as config

if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    socketio.run(app) 

