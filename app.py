# app.py - a minimal flask api using flask_restful

from flask import Flask, render_template, make_response
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'

db = SQLAlchemy(app)

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)
    email = db.Column(db.String(120), nullable = False)
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()
        

@app.before_first_request
def create_tables():
    print('Tworzenie bazy danych.')
    db.create_all()
    print(db.engine.table_names())


users = [
    'osiakm',
    'admin'
]

parser = reqparse.RequestParser().add_argument(
    'username', help='This field cannot be blank', required=True
).add_argument(
    'password', help='This field cannot be blank', required=True
)

class Index(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('index.html'), 200, headers)


class Login(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('login.html'), 200, headers)

    def post(self):
        headers = {'Content-Type': 'text/html'}
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}
        
        if data['password'] == current_user.password:
            return make_response(render_template('index.html', user=current_user.username), 200, headers)
        else:
            return {'message': 'Wrong credentials'}

class Register(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('register.html'), 200, headers)

    def post(self):
        headers = {'Content-Type': 'text/html'}
        data = parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'. format(data['username'])}

        new_user = UserModel(
            username = data['username'],
            password = data['password'],
            email = data['email']
        )
        print(data)
        try:
            new_user.save_to_db()
            return {'message': 'User {} was created'.format( data['username'])}, 200
        except:
            return {'message': 'Something went wrong'}, 500


class CheckLogin(Resource):
    def get(self, username):
        headers = {'Content-Type': 'text/html'}
        if username in users:
            status = 404
            message = "User exists."
        else:
            status = 200
            message = "There is no user with this username."
        return make_response(message, status, headers)


api.add_resource(Index, '/')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(CheckLogin, '/user/<username>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')