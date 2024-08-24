from flask_restful import reqparse, fields, marshal_with, abort, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from flask import jsonify

from utils import calculate_max_children_depth, calculate_max_parents_depth

db = SQLAlchemy()


class UserModel(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    parent1_id: Mapped[int] = mapped_column(nullable=True, default=None)
    parent2_id: Mapped[int] = mapped_column(nullable=True)


user_parser_create = reqparse.RequestParser()
user_parser_create.add_argument('first_name', type=str,
                                required=True, help='First name is required')
user_parser_create.add_argument('last_name', type=str,
                                required=True, help='Last name is required')
user_parser_create.add_argument('parent1_id', type=int)
user_parser_create.add_argument('parent2_id', type=int)

user_parser_update = reqparse.RequestParser()
user_parser_update.add_argument('first_name', type=str)
user_parser_update.add_argument('last_name', type=str)
user_parser_update.add_argument('parent1_id', type=int)
user_parser_update.add_argument('parent2_id', type=int)


def abort_if_user_does_not_exists(user_id, message="User not found"):
    user = UserModel.query.filter_by(id=user_id).first()
    if not user:
        abort(404, message=message)


def abort_if_not_correct_parent(user_id, parent_id):
    print(user_id, parent_id)
    if user_id == parent_id:
        abort(400, message="User can't be his own parent")


userFields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'parent1_id': fields.Raw,
    'parent2_id': fields.Raw
}


class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        """
        Returns users list
        ---
        tags:
          - Users
        responses:
          200:
            description: Users list
            schema:
                id: Users
                type: array
                items:
                    type: object
                    $ref: '#/definitions/User'
        """
        users = UserModel.query.all()
        return users

    @marshal_with(userFields)
    def post(self):
        """
        Create user
        ---
        tags: 
            - Users
        parameters:
            - in: body
              schema:
                type: object
                properties:
                    first_name:
                        type: string
                        required: true
                    last_name: 
                        type: string
                        required: true
                    parent1_id:
                        type: integer
                    parent2_id:
                        type: integer

        """
        args = user_parser_create.parse_args()
        user = UserModel(first_name=args["first_name"], last_name=args['last_name'],
                         parent1_id=args['parent1_id'], parent2_id=args['parent2_id'])

        if 'parent1_id' in args and args['parent1_id'] != None:
            parent = UserModel.query.filter_by(id=args['parent1_id']).first()
            if not parent:
                abort(400, message="Parent 1 not found")

        if 'parent2_id' in args and args['parent2_id'] != None:
            parent = UserModel.query.filter_by(id=args['parent2_id']).first()
            if not parent:
                abort(400, message="Parent 2 not found")

        db.session.add(user)
        db.session.commit()
        return user, 201

    # Deleting whole table of users. Only used for testing purposes
    def delete(self):
        num_rows_deleted = db.session.query(UserModel).delete()
        db.session.commit()
        return num_rows_deleted


class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        """
        Returns user by id
        ---
        tags:
          - Users
        parameters:
          - in: path
            name: id
            required: true
            description: User id
            type: int
        responses:
          200:
            description: User data
            schema:
              id: User
              properties:
                id:
                  type: integer
                first_name:
                    type: string
                last_name:
                    type: string
                parent1_id:
                  type: integer
                parent2_id:
                  type: integer
        """
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        return user

    def delete(self, id):
        """
        Delete user
        ---
        tags:
            - Users
        parameters:
          - in: path
            name: id
            required: true
            description: User id
            type: int
        responses:
            204:
                schema:
                    properties:
                        message:
                            type: string
                            default: "User deleted"

        """
        abort_if_user_does_not_exists(id)

        user = UserModel.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 204

    @marshal_with(userFields)
    def patch(self, id):
        """
        Update user
        ---
        tags: 
            - Users
        parameters:
            - in: body
              schema:
                type: object
                properties:
                    first_name:
                        type: string
                    last_name: 
                        type: string
                    parent1_id:
                        type: integer
                    parent2_id:
                        type: integer

        """
        abort_if_user_does_not_exists(id)

        user = UserModel.query.filter_by(id=id).first()
        args = user_parser_update.parse_args()
        print(args)
        if args['first_name'] != None:
            user.first_name = args['first_name']

        if args['last_name'] != None:
            user.last_name = args['last_name']

        if args['parent1_id'] != None:
            abort_if_user_does_not_exists(
                args['parent1_id'], "Parent 1 does not exist")
            abort_if_not_correct_parent(id, args['parent1_id'])
            user.parent1_id = args['parent1_id']

        if args['parent2_id'] != None:
            abort_if_not_correct_parent(id, args['parent2_id'])
            abort_if_user_does_not_exists(
                args['parent2_id'], "Parent 2 does not exist")
            user.parent2_id = args['parent2_id']

        db.session.commit()
        return user


def get_parents(user_id):
    user = db.session.query(UserModel).filter_by(id=user_id).first()

    if not user:
        return None

    parent_node = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'parents': []
    }

    if user.parent1_id:
        parent1_tree = get_parents(user.parent1_id)
        if parent1_tree:
            parent_node['parents'].append(parent1_tree)

    if user.parent2_id:
        parent2_tree = get_parents(user.parent2_id)
        if parent2_tree:
            parent_node['parents'].append(parent2_tree)

    return parent_node


def get_children(user_id):
    user = db.session.query(UserModel).filter_by(id=user_id).first()

    if not user:
        return None

    child_node = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'children': []
    }

    children = db.session.query(UserModel).filter(
        (UserModel.parent1_id == user.id) |
        (UserModel.parent2_id == user.id)
    ).all()

    for child in children:
        child_node['children'].append(get_children(child.id))

    return child_node


def get_tree(user_id):
    user = db.session.query(UserModel).filter_by(id=user_id).first()

    if not user:
        return None

    tree_node = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'parents': [],
        'children': []
    }

    if user.parent1_id or user.parent2_id:
        parents = get_parents(user.id)
        if parents:
            tree_node['parents'] = parents['parents']

    children = get_children(user.id)
    if children:
        tree_node['children'] = children['children']

    return tree_node


class Tree(Resource):
    def get(self, id):
        """
        Returns genealogy tree of user
        ---
        tags:
          - Tree
        parameters:
          - in: path
            name: id
            required: true
            description: User id
            type: int
        definitions:
            Single_tree_node:
                type: object
                properties:
                    id:
                        type: integer
                    first_name:
                        type: string
                    last_name:
                        type: string
                    parent1_id:
                        type: integer
                    parent2_id:
                        type: integer
        responses:
          200:
            description: Genealogy tree of user
            schema:
              id: Tree_node
              properties:
                id:
                  type: integer
                first_name:
                    type: string
                last_name:
                    type: string
                parent1_id:
                  type: integer
                parent2_id:
                  type: integer
                children:
                    type: array
                    items:
                        type: object
                        $ref: '#/definitions/Single_tree_node'
                parents:
                    type: array
                    items:
                        type: object
                        $ref: '#/definitions/Single_tree_node'
                max_children_depth:
                    type: integer
                max_parents_depth:
                    type: integer
                max_node_depth:
                    type: integer
        """
        abort_if_user_does_not_exists(id)
        user = UserModel.query.filter_by(id=id).first()

        tree = get_tree(user.id)
        max_children_depth = calculate_max_children_depth(tree)
        max_parents_depth = calculate_max_parents_depth(tree)
        max_node_depth = max_children_depth + max_parents_depth
        result = {"max_children_depth": max_children_depth,
                  "max_parents_depth": max_parents_depth,
                  "max_node_depth": max_node_depth,
                  "tree": tree}
        return jsonify(result)
