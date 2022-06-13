import os 
from werkzeug.utils import secure_filename 
class Config(object): 
    SECRET_KEY = 'my_secret_key'

class DevelopmentConfig(Config):
    DEBUG = True 
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://voteuser:snakesarecool1237@localhost:3306/appvote'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/img/votes'
    HOST = '0.0.0.0'
    PORT =  5000 
