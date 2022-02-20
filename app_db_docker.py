from datetime import timedelta
from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_jwt import JWT, jwt_required, current_identity
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config["JWT_EXPIRATION_DELTA"] = timedelta(seconds=3600)
app.config["JWT_SECRET_KEY"] = "jajhjahudhadnenvhdvjdjdfhdfjjhjhajajhahajajajhajhnchs"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@localhost/aulla_orm"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))    
    password = db.Column(db.String(80))

    def json(self):
        return f"{self.id} - {self.username}"    

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

class User(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help="Username cannot be empty")
    parser.add_argument('password', type=str, required=True, help="Password cannot be empty")

    def post(self):
        data = User.parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": "Esse usuário já existe"}, 400

        user = UserModel(username=data["username"], password=data["password"])
        user.save_to_db()

        return {"message": "Usuário criado"}, 201    

def authenticate(username, password):
    user = UserModel.find_by_username(username)
    if user and user.password == password:
        return user

def identity(payload):
    user_id = payload['identity']
    return UserModel.find_by_id(user_id)

jwt = JWT(app, authenticate, identity)

class ItemModel(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float(2))

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
       db.session.delete(self)
       db.session.commit()

    def json(self):
        return{"id": self.id, "name": self.name, "price": self.price}             

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=False, help="Field price is required")

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': "Item não encontrado!"}, 404
    
    @jwt_required()
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message": "Já existe um item com esse nome!"}, 400

        data = Item.parser.parse_args()
        item = ItemModel(name=name, price=data["price"])

        item.save_to_db()
        return item.json(), 201

    @jwt_required()
    def put(self, name):
        item = ItemModel.find_by_name(name)
        data = Item.parser.parse_args()

        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name=name, price=data["price"])

        item.save_to_db()

        return item.json()

    @jwt_required()
    def delete(self, name):
        item = ItemModel.find_by_name(name)

        if item:
            item.delete_from_db()

        return {"message": "Item deletado"}, 200    


api.add_resource(Item, '/item/<string:name>')
api.add_resource(User, '/register')
db.init_app(app)
app.run(port=50001,host='0.0.0.0',debug=True)