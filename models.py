from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__= 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(40))
    password = db.Column(db.String(100))
    created_date = db.Column(db.DateTime, default = datetime.datetime.now)
    preguntas = db.relationship('Pregunta')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = self.__create_password(password)

    def __create_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def toJSON(self):
        return {'User':{ 'username': self.username,
            'email': self.email}}

class Pregunta(db.Model):
    __tablename__= 'pregunta'
    id = db.Column(db.Integer, primary_key=True)
    texto_pregunta = db.Column(db.String(100))
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    respuestas = db.relationship('Respuesta')
    votos = db.relationship('Votos')

    def __init__(self, texto_pregunta, users_id):
        self.texto_pregunta = texto_pregunta
        self.users_id = users_id
        

class Respuesta(db.Model):
    __tablename__ = 'respuesta'
    id = db.Column(db.Integer, primary_key=True)
    texto_respuesta = db.Column(db.String(100))
    preguntas_id = db.Column(db.Integer, db.ForeignKey('pregunta.id'))
    votos = db.relationship('Votos')

    def __init__(self, texto_respuesta, preguntas_id):
        self.texto_respuesta = texto_respuesta
        self.preguntas_id = preguntas_id

class Votos(db.Model):
    __tablename__= 'voto'
    id = db.Column(db.Integer, primary_key=True)
    preguntas_id = db.Column(db.Integer, db.ForeignKey('pregunta.id'))
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    respuestas_id = db.Column(db.Integer, db.ForeignKey('respuesta.id'))

    def __init__(self, preguntas_id, users_id, respuestas_id):        
        self.preguntas_id = preguntas_id
        self.users_id = users_id
        self.respuestas_id = respuestas_id
        



