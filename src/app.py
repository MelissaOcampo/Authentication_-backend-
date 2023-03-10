"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
import json
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Usuario, Personajes, Vehiculos, Planetas, Favoritos
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required,JWTManager
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)


# @app.route("/signup", methods=["POST"]) Se recibe una solicitud POST en la ruta "/signup"
# def signup():
    # body= json.loads(request.data)   # Se convierte la información enviada en la solicitud a un diccionario llamado body usando json.loads y request.data.

    # usuario_signup = Usuario.query.filter_by(email=body["email"]).first() #Se busca en la base de datos si el email enviado en la solicitud ya está registrado usando Usuario.query.filter_by(email=body["email"]).first().

    # if usuario_signup is None: #Si no se encuentra ningún usuario con el email enviado, se crea una nueva instancia de la clase Usuario usando los datos enviados en el cuerpo de la solicitud body.

        # name2 =  Usuario(name=body ["name"], surname=body ["surname"], email=body["email"], password=body["password"]) 
        
        #Se agrega la nueva instancia a la base de datos usando db.session.add(name2) y se guardan los cambios en la base de datos usando db.session.commit().
        # db.session.add(name2)
        # db.session.commit()
        # response_body = {"msg":"el usuario fue creado con exito"}

        # return jsonify(response_body), 200 #Se devuelve una respuesta con un mensaje de éxito y un código de estado HTTP 200 (OK).

@app.route('/signup', methods=['POST'])
def signup():  
    request_body = request.data    
    decoded_object = json.loads(request_body)   
    get_email = Usuario.query.filter_by(email=decoded_object["email"]).first()   
    if get_email is None:        
        new_user = Usuario(name=decoded_object["name"], surname=decoded_object["surname"], email=decoded_object["email"], password=decoded_object["password"])     
        db.session.add(new_user)     
        db.session.commit()      
        return jsonify({"msg":"Usuario creado correctamente."}), 200   
    else:        
        return jsonify({"msg":"El usuario ya existe"}), 400

    response_body = {"msg":"el usuario ya existe en el sistema"}

    return jsonify(response_body), 400 #Si el usuario ya existe en la base de datos, se devuelve una respuesta con un mensaje de error y un código de estado HTTP 400 

@app.route("/login", methods=["POST"]) #Se recibe una solicitud POST en la ruta "/login"
def login():
    #Se extraen los valores de email y password enviados en la solicitud usando request.json.get("email", None) y request.json.get("password", None).
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    #Se busca en la base de datos si el email enviado en la solicitud ya está registrado usando Usuario.query.filter_by(email=email).first().
    user_login = Usuario.query.filter_by(email=email).first()
    print(user_login)
    if email != user_login.email or password != user_login.password:
        return jsonify({"msg": "Bad email or password"}), 401 #Si el email o la contraseña enviados no coinciden con los registrados en la base de datos, se devuelve una respuesta con un mensaje de error y un código de estado HTTP 401 
    access_token = create_access_token(identity=email) 
    return jsonify(access_token=access_token) #Si el email y la contraseña enviados coinciden con los registrados en la base de datos, se crea un identificador de acceso usando create_access_token y se devuelve una respuesta  y un código de estado HTTP 200 (OK).

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/private", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    user_private = Usuario.query.filter_by(email=current_user).first()
    return jsonify(logged_in_as=user_private.serialize()), 200


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Comienzan las rutas
@app.route('/personajes', methods=['GET'])
def get_personajes():
    all_personajes= Personajes.query.all()
    results = list(map(lambda item: item.serialize(),all_personajes))

    return jsonify(results), 200

@app.route('/personajes/<int:personajes_id>', methods=['GET'])
def select_personajes(personajes_id):
    personaje = Personajes.query.filter_by(id=personajes_id).first()
    return jsonify(personajes_id), 200

@app.route('/planetas', methods=['GET'])
def get_planetas():
    all_planetas= Planetas.query.all()
    results = list(map(lambda item: item.serialize(),all_planetas))
    return jsonify(results), 200

@app.route('/planetas/<int:planetas_id>', methods=['GET'])
def select_planetas(planetas_id):
    planetas = Planetas.query.filter_by(id=planetas_id).first()
    return jsonify(planetas_id), 200  

@app.route('/usuario', methods=['GET'])
def get_usuario():
    all_usuario= Usuario.query.all()
    results = list(map(lambda item: item.serialize(),all_usuario))
    return jsonify(results), 200

@app.route('/usuario/<int:usuario_id>/favoritos', methods=['GET'])
def usuario(usuario_id):
    favoritos= Favoritos.query.filter_by(usuario_id = usuario_id).all()
    results = list(map(lambda item: item.serialize(),favoritos))
    return jsonify(results), 200


@app.route('/usuario/<int:usuario_id>/favoritos', methods=['POST'])
def add_planetas_favoritos(usuario_id):
        request_body = request.json
        print(request_body)
        print(request_body["planetas_id"]) 
        new_favoritos= Favoritos(usuario_id = usuario_id,personajes_id= None, vehiculos_id= None, planetas_id= request_body['planetas_id']) 
        favoritos= Favoritos.query.filter_by(usuario_id = usuario_id, planetas_id= request_body['planetas_id']).first()
        print(favoritos)

        if favoritos is None:
            new_favoritos= Favoritos(usuario_id = usuario_id,personajes_id= None, vehiculos_id= None, planetas_id= request_body['planetas_id'] ) 
            db.session.add(new_favoritos)
            db.session. commit()

            return jsonify({'msg':'se agrego favorito'}), 200

        return jsonify({'msg':'se quito favortio'}), 400

@app.route('/usuario/<int:usuario_id>/favoritos/personajes', methods=['POST'])
def add_personajes_favoritos(usuario_id):

    request_body = request.json
    print(request_body)
    print(request_body['personajes_id'])

    new_favoritos_personajes = Favoritos(usuario_id = usuario_id, personajes_id = request_body['personajes_id'], vehiculos_id = None, planetas_id = None)

    favoritos = Favoritos.query.filter_by(usuario_id=usuario_id, personajes_id=request_body['personajes_id']).first()
    print(favoritos)

    if favoritos is None:
        new_favoritos_personajes = Favoritos(usuario_id = usuario_id, personajes_id = request_body['personajes_id'], vehiculos_id = None, planets_id = None)
        db.session.add(new_favoritos_personajes)
        db.session.commit()

        return jsonify({'msg': 'favorito agregado'}), 200    

    return jsonify({'msg': 'favorito existe'}), 400


# Finalizan las rutas

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
