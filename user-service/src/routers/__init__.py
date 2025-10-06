from protos import user_pb2_grpc, user_pb2

from src.services import UserService

class User(user_pb2_grpc.UserServicer):
    def __init__(self):
        self.service = UserService()

    async def GetUserById(self, request, context):
        data = await self.service.get_by_id(request.id, context)
        return user_pb2.GetUserByIdResponse(username=data.username)
    
    async def CreateUser(self, request, context):
        data = {'username': request.username}
        new_user = await self.service.create(data, context)
        return user_pb2.CreateUserResponse(
            id=new_user.id
        )
    
    async def AuthUser(self, request, context):
        user = await self.service.get_or_create(request.username, context)
        return user_pb2.AuthUserResponse(
            id=user.id
        )
    
    async def DeleteUser(self, request, context):
        result = await self.service.delete(request.user_id, context)
        return user_pb2.DeleteUserResponse(
            status=result
        )
