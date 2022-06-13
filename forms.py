from wtforms import Form
from wtforms import StringField, PasswordField, IntegerField, FloatField, FileField
from wtforms import validators
from models import User
from wtforms.fields.html5 import EmailField

class LoginForm(Form):
    username =  StringField('username', [validators.DataRequired(),validators.Length(max=50, message='El campo no puede tener más de %(max)d caracteres')])
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.Length(min=8, max=15 , message='El campo debe tener de %(min)d  a %(max)d caracteres'),
        ])

class UserFormRegister(Form):
    username =  StringField('username', [
        validators.DataRequired(message = 'El username es requerido'),
        validators.Length(max=50, message='El campo no puede tener más de %(max)d caracteres'),
        validators.Regexp('^[^\s]+(\s+[^\s]+)*$', message = 'no se permiten espacios para el nombre del usuarios')
        ])
    email = EmailField('email',
        [
        validators.DataRequired('El email es requerido'),
        validators.Email('Ingrese email valido'),
        validators.Length(max=40, message='El campo no puede tener más de %(max)d caracteres')
        ])
    password = PasswordField('password', [
        validators.DataRequired(message = 'El password es requerido'), 
        validators.Length(min=8, max=15, message='El campo debe tener de %(min)d  a %(max)d caracteres'),
        validators.Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,15})', message= 'min. 8 a max. 15 caracteres, al menos una letra mayuscula y una minuscula,al menos un caracter especial ')
        ])

    def validate_username(form, field):
        username = field.data
        user = User.query.filter_by(username = username).first()
        if user is not None:
            raise validators.ValidationError('El usuario ya se encuentra registrado')

class EncuestaForm(Form):
    textoPregunta =  StringField('Pregunta', [
        validators.DataRequired(),
        validators.Length(max = 90,min = 8,message='El campo debe tener de %(min)d  a %(max)d caracteres'),
        validators.Regexp('^[^\s]+(\s+[^\s]+)*$', message = 'no se permiten espacios al inicio y final de la pregunta')
        ])

class RespuestaForm(Form):
    textoRespuesta =  StringField('Respuesta', [
    validators.DataRequired(),
    validators.Length(max = 90, min=8 , message='El campo debe tener de %(min)d  a %(max)d caracteres'),
    validators.Regexp('^[^\s]+(\s+[^\s]+)*$', message = 'no se permiten espacios al inicio y final de la respuesta')
    ])