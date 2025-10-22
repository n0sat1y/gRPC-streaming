# Команда для сериализации proto-файлов

```
python -m grpc_tools.protoc -I ../protobuf --python_out=./protos --grpc_python_out=./protos ../protobuf/user.proto
```

# Примеры websocket запросов

## Send Message Event
```
{
  "event_type": "send_message",
  "request_id": "req_12345",
  "payload": {
    "chat_id": 123456,
    "content": "Hello, this is a test message"
  }
}
```
## Delete Message Event
```
{
  "event_type": "delete_message",
  "request_id": "req_67890",
  "payload": {
    "message_id": "msg_abc123def456"
  }
}
```
## Edit Message Event
```
{
  "event_type": "edit_message",
  "request_id": "req_11111",
  "payload": {
    "message_id": "msg_abc123def456",
    "new_content": "This is the edited message content"
  }
}
```
## Read Messages Event
```
{
  "event_type": "mark_as_read",
  "payload": {
    "chat_id": 123456,
    "last_read_message": "msg_xyz789"
  }
}
```
