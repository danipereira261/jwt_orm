from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=False, help="Field price is required")

    def get(self, name):
        return {'name': name}
    
    def post(self, name):
        data = Item.parser.parse_args()
        print(data)
        return {'name': name, 'price': data['price']}

api.add_resource(Item, '/item/<string:name>')
app.run(port=50001,host='0.0.0.0',debug=True)