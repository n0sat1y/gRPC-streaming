from protos import user_pb2_grpc, user_pb2
from google.protobuf.json_format import MessageToDict

from src.services import UserService

class User(user_pb2_grpc.UserServicer):
    def __init__(self):
        self.service = UserService()

    async def GetUserById(self, request, context):
        data = await self.service.get_by_id(request.id, context)
        return user_pb2.GetUserByIdResponse(id=data.id, username=data.username)
    
    async def GetUserWithPassword(self, request, context):
        data = await self.service.get_by_username(request.username, context)
        return user_pb2.GetUserWithPasswordResponse(
            user_id=data.id,
            password=data.password
        )
    
    async def GetMultipleUsers(self, request, context):
        users, missed = await self.service.get_multiple(request.ids, context)
        status = 'Success'
        users_response = [user_pb2.UserData(id=x.id, username=x.username) for x in users]
        if missed:
            status = 'Missed'
            missed = [user_pb2.OptionalUserId(id=x) for x in missed]
        return user_pb2.GetMultipleUsersResponse(
            status=status,
            users=users_response,
            missed=missed
        )
    
    async def CreateUser(self, request, context):
        data = {
            'username': request.username,
            'password': request.password
        }
        new_user = await self.service.create(data, context)
        return user_pb2.CreateUserResponse(
            id=new_user.id
        )
    
    async def DeleteUser(self, request, context):
        result = await self.service.delete(request.user_id, context)
        return user_pb2.DeleteUserResponse(
            status=result
        )
    
