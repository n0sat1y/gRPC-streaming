import grpc

from protos import user_pb2_grpc, user_pb2
from src.services import UserService
from src.routers.kafka import broker
from src.exceptions.user import (
    UserNotFoundError, UserAlreadyExistsError
)

class User(user_pb2_grpc.UserServicer):
    def __init__(self):
        self.service = UserService()
        self.broker = broker

    async def GetUserById(self, request, context):
        try:
            data = await self.service.get_by_id(request.id)
            return user_pb2.UserData(
                id=data.id, 
                username=data.username,
                created_at=data.created_at
            )
        except UserNotFoundError as e:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details=str(e)
            ) 
        except Exception as e:
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details="An error occured during getting user"
            ) 
    
    async def GetUserByUsernameWithPassword(self, request, context):
        try:
            data = await self.service.get_by_username(request.username)
            return user_pb2.GetUserWithPasswordResponse(
                user_id=data.id,
                password=data.password
            )
        except UserNotFoundError as e:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details=str(e)
            ) 
        except Exception as e:
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details="An error occured during getting user"
            ) 
    
    async def CreateUser(self, request, context):
        try:
            data = {
                'username': request.username,
                'password': request.password
            }
            new_user = await self.service.create(data, self.broker)
            return user_pb2.UserId(
                id=new_user.id
            )
        except UserAlreadyExistsError as e:
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                details=str(e)
            ) 
        except Exception as e:
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details="An error occured during creating user"
            ) 
    
    async def DeleteUser(self, request, context):
        try:
            result = await self.service.delete(request.id, self.broker)
            return user_pb2.DeleteUserResponse(
                status=result
            )
        except UserNotFoundError as e:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details=str(e)
            ) 
        except Exception as e:
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details="An error occured during deleting user"
            ) 
