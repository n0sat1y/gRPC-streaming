# Команда для сериализации proto-файлов

```
python -m grpc_tools.protoc -I ../protobuf --python_out=./protos --grpc_python_out=./protos ../protobuf/user.proto
```

# Примеры WebSocket запросов

## Send Message Event
```json
{
  "event_type": "send_message",
  "request_id": "req_12345",
  "payload": {
    "chat_id": 123456,
    "content": "Hello, this is a test message",
    "reply_to": null
  }
}
```

## Delete Message Event
```json
{
  "event_type": "delete_message",
  "request_id": "req_67890",
  "payload": {
    "message_id": "msg_abc123def456"
  }
}
```

## Edit Message Event
```json
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
```json
{
  "event_type": "mark_as_read",
  "request_id": "req_22222",
  "payload": {
    "chat_id": 123456,
    "last_read_message": "msg_xyz789"
  }
}
```

## Add Reaction Event
```json
{
  "event_type": "add_reaction",
  "request_id": "req_33333",
  "payload": {
    "message_id": "msg_skdfbs",
    "reaction": "👍"
  }
}
```

## Remove Reaction Event
```json
{
  "event_type": "remove_reaction",
  "request_id": "req_44444",
  "payload": {
    "message_id": "msg_skdfbs",
    "reaction": "👍"
  }
}
```

## Forward Messages Event
```json
{
  "event_type": "forward_messages",
  "request_id": "req_55555",
  "payload": {
    "chat_id": 123456,
    "messages": ["msg_abc123", "msg_def456"],
    "content": "Forwarded messages from previous chat"
  }
}
```

## Error Response
```json
{
  "event_type": "error",
  "payload": {
    "code": "INVALID_REQUEST",
    "details": "Missing required field: request_id"
  }
}
```

## Общие поля

Все события (кроме ошибки) содержат:
- `event_type` (string) - тип события
- `request_id` (string) - уникальный идентификатор запроса
- `payload` (object) - данные события

## Типы событий

| Event Type | Описание |
|------------|----------|
| `send_message` | Отправка сообщения |
| `delete_message` | Удаление сообщения |
| `edit_message` | Редактирование сообщения |
| `mark_as_read` | Отметка сообщений как прочитанных |
| `add_reaction` | Добавление реакции |
| `remove_reaction` | Удаление реакции |
| `forward_messages` | Пересылка сообщений |
| `error` | Ошибка |
