# Команда для сериализации proto-файлов

```
python -m grpc_tools.protoc -I ../protobuf --python_out=./protos --grpc_python_out=./protos ../protobuf/user.proto
