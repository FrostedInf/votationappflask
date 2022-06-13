from flask import Flask,json,jsonify
from flask import render_template
from flask import make_response
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import flash
from flask import g
from models import db
from models import User, Pregunta, Respuesta, Votos
import os
from werkzeug.utils import secure_filename
from flask_wtf import CSRFProtect
from werkzeug.datastructures import CombinedMultiDict
from flask_wtf.file import FileField
from config import DevelopmentConfig
import forms
from flask_socketio import SocketIO, emit

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
socketio = SocketIO(app, cors_allowed_origins="*" ) 

csrf = CSRFProtect(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.before_request
def before_ver():
        g.conectado = False
        if 'username' in session:
            g.conectado = True
        if 'username' not in session and request.endpoint in ['perfil','resultados','crudRespuestas']:
            flash('Antes de entrar a la pagina logueate')
            return redirect(url_for('login'))

@app.after_request
def after_ver(response):
    return response

#User Controllers
@app.route('/')
def index():
    title = "Inicio"
    return render_template('index.html', title = title, conectado = g.conectado)

@app.route('/contact')
def contactView():
    return render_template('contact.html', conectado = g.conectado)

@app.route('/registro', methods = ['GET', 'POST'])
def register():
    form = forms.UserFormRegister(request.form)
    if request.method == 'POST' and form.validate():
        user = User( form.username.data,
        form.email.data,
        form.password.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Usuario registrado con exito')
        return redirect(url_for('login'))

    return render_template('registro.html' ,form = form)

@app.route('/login', methods = ['GET', 'POST'] )
def login():
    login_form = forms.LoginForm(request.form)
    if request.method == 'POST' and login_form.validate():
        username = login_form.username.data
        password = login_form.password.data
        user = User.query.filter_by(username = username).first()
        if user is not None and user.verify_password(password):
            flash('Bienvenido {}'.format(username))
            session['username'] = login_form.username.data
            session['password'] = login_form.password.data
            return redirect(url_for('index'))
        else:
            flash('usuario no encontrado')
    return render_template('login.html', form = login_form)

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    if 'username' in session:
        session.pop('username')
    return redirect(url_for('login'))

@app.route("/perfil", methods = ['GET', 'POST'])
def perfil():
    userSesion = session['username']
    user = User.query.filter_by(username=userSesion).first()
    preguntas = Pregunta.query.join(User).filter(Pregunta.users_id == user.id).add_columns(Pregunta.texto_pregunta, User.username,Pregunta.id).all()
    print(userSesion)
    form = forms.EncuestaForm(request.form)

    if request.method == 'POST' and form.validate():
        userSesion=session['username']
        user=User.query.filter_by(username=userSesion).first()
        pregunta = Pregunta( form.textoPregunta.data, user.id )
        db.session.add(pregunta)
        db.session.commit()
        flash('pregunta guardad')
        return redirect(url_for('perfil'))

    return render_template('perfil.html', conectado = g.conectado, formPregunta=form, user=user, preguntas = preguntas)    

@app.route("/respuestas/<int:idPregunta>", methods = ['GET', 'POST'])
def crudRespuestas(idPregunta):
    userSesion = session['username']
    user = User.query.filter_by(username=userSesion).first()
    identificador = idPregunta
    respuestas = Respuesta.query.join(Pregunta).filter(Respuesta.preguntas_id == idPregunta).add_columns(Pregunta.texto_pregunta, Respuesta.texto_respuesta).all()
    print(userSesion)
    form = forms.RespuestaForm(request.form)

    if request.method == 'POST' and form.validate():        
        respuesta = Respuesta( form.textoRespuesta.data, identificador)
        db.session.add(respuesta)
        db.session.commit()
        flash('Respuesta guardada')
        return redirect(url_for('crudRespuestas',idPregunta = identificador))

    return render_template('respuestas.html', conectado = g.conectado, formRespuesta=form, user=user, respuestas = respuestas)

@app.route("/resultados/<int:idPregunta>", methods = ['GET', 'POST'])
def resultados(idPregunta):
    userSesion = session['username']
    user = User.query.filter_by(username=userSesion).first()
    identificador = idPregunta    
    
    pregunta = Pregunta.query.filter_by( id = idPregunta).first()
    usuario_pregunta = User.query.filter_by(id=pregunta.users_id).first()
    respuestas = Respuesta.query.join(Pregunta).filter(Respuesta.preguntas_id == idPregunta).add_columns(Respuesta.id,Respuesta.texto_respuesta).all()
    encuestado = True if user.id != pregunta.users_id else False
    votohecho = Votos.query.filter_by(users_id = user.id, preguntas_id = pregunta.id).first()
    respuestaSeleccionada = None
    if votohecho:
        respuestaSeleccionada = Respuesta.query.filter_by(id = votohecho.respuestas_id).first()
    print(votohecho)
    print(respuestaSeleccionada)

    if request.method == 'POST' and votohecho is None:        
        votos = Votos( identificador , user.id, request.form['opciones'])
        db.session.add(votos)
        db.session.commit()
        print("opciones es igual a" + request.form['opciones'])
        flash('Voto guardado')
        return redirect(url_for('resultados',idPregunta = identificador))

    if request.method == 'POST' and votohecho is not None:        
        votohecho.respuestas_id = request.form['opciones']
        db.session.commit()
        print("opciones es igual a" + request.form['opciones'])
        flash('Voto actualizado')
        return redirect(url_for('resultados',idPregunta = identificador))
    
    return render_template('resultados.html', 
        conectado = g.conectado, 
        user=user, 
        respuestas = respuestas, 
        esEncuestado=encuestado, 
        pregunta=pregunta, 
        preguntaUsuario = usuario_pregunta,
        votohecho = votohecho,
        respuestaSeleccionada = respuestaSeleccionada
        )
    
@socketio.on('votos')
def handleVote(idpregunta):
    identificador = idpregunta    
    print('El id de tu pregunta es ' + str(identificador))
    listaRespuestas = []
    listaRespuestaVoto = []
    listaVotos = []
    listaEtiquetas = []
    
    pregunta = Pregunta.query.filter_by( id = idpregunta).first()
    respuestas = Respuesta.query.join(Pregunta).filter(Respuesta.preguntas_id == idpregunta).add_columns(Respuesta.id,Respuesta.texto_respuesta).all()
    votos = Votos.query.filter_by(preguntas_id = idpregunta).all()
    
    for respuesta in respuestas:
        listaRespuestas.append(respuesta.id)
    
    for respuesta in respuestas:
        listaEtiquetas.append(respuesta.texto_respuesta)
    

    for respuestavoto in votos:
        listaRespuestaVoto.append(respuestavoto.respuestas_id)
    
    
    for voto in listaRespuestas:
        listaVotos.append(listaRespuestaVoto.count(voto)) 

    print(listaEtiquetas, sep='\n')
    print(listaVotos, sep='\n')

    emit('resultados_votos',{'etiquetas' : listaEtiquetas, 'datos' : listaVotos}, broadcast=True)
