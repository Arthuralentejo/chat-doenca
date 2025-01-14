from flask_restplus import Resource, Namespace, fields
from flask import request
from loguru import logger
from datetime import datetime
from base import Response, Services
from domain.message import Message

api = Namespace('User',description='User related operations')

userModel = api.model('UserModel', {
    'name': fields.String,
    'password': fields.String
})

services = Services()

@api.route('/')
class UserController(Resource):
    @api.expect(userModel)
    def post(self):
        try:                       
            name = request.json.get('name')
            password = request.json.get('password')
            
            if name is None or len(name) == 0:
                return Response.create_error_response(400, 'Empty name')
                       
            if password is None or len(password) == 0:
                return Response.create_error_response(400, 'Empty password')
            
            id = self.user_service.create(name, password)
            return Response.create_response(201, 'User created', {'id': id})
                        
        except Exception as e:
            logger.error(f'Error creating user: {e}')
            return Response.create_response(500, str(e))

@api.route('/<id>')
class UserIdController(Resource):        
    def get(self, id):
        try:
            user_id = services.auth(request)
            
            if user_id is None or len(user_id) == 0:
                return Response.create_error_response(401, 'Unauthorized')
            
            user = services.user_service.get(id)
            if user is None:
                return Response.create_error_response(404, 'User not found')
            
            return Response.create_response(200, 'User loaded', { 'user': user.ToJson()} )
        
        except Exception as e:
            logger.error(f'Error getting user: {e}')
            return Response.create_response(500, str(e))
        
