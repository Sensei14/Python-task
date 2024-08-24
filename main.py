from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from database import db, User, Users, Tree

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
app.config['SWAGGER'] = {
    'title': 'Users genealogy tree',
}
swagger = Swagger(app)


with app.app_context():
    db.create_all()


api.add_resource(Users, '/users')
api.add_resource(User, '/users/<int:id>')
api.add_resource(Tree, '/tree/<int:id>')


if __name__ == "__main__":
    app.run(debug=True)
