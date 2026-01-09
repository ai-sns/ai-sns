@echo off
REM 测试流式聊天 API (Windows)

echo 正在测试流式聊天 API...
echo URL: http://localhost:8788/api/chat/stream
echo.

curl -N -X POST http://localhost:8788/api/chat/stream ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -d "{\"messages\": [{\"role\": \"user\", \"content\": \"你好，请用一句话介绍自己\"}]}"

echo.
echo 测试完成
pause
