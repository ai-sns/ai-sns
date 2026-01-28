@echo off
echo ================================
echo Web Sidebar 快速测试脚本
echo ================================
echo.

echo 1. 检查后端服务器...
curl -s http://localhost:8788/health >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✓ 后端服务器正在运行
) else (
    echo    ✗ 后端服务器未运行
    echo    请先启动: python api_server.py
    exit /b 1
)

echo.
echo 2. 测试 GET /api/system/web-mng...
curl -s http://localhost:8788/api/system/web-mng > temp_response.txt
findstr /C:"success" temp_response.txt >nul
if %errorlevel% equ 0 (
    echo    ✓ GET 请求成功
) else (
    echo    ✗ GET 请求失败
    type temp_response.txt
)

echo.
echo 3. 测试 PUT /api/system/web-mng/reorder...
curl -s -X PUT http://localhost:8788/api/system/web-mng/reorder -H "Content-Type: application/json" -d "[{\"id\":1,\"position\":0},{\"id\":2,\"position\":1}]" > temp_response.txt
findstr /C:"success" temp_response.txt >nul
if %errorlevel% equ 0 (
    echo    ✓ PUT 请求成功
    type temp_response.txt
) else (
    echo    ✗ PUT 请求失败
    type temp_response.txt
)

echo.
echo 4. 测试空数组...
curl -s -X PUT http://localhost:8788/api/system/web-mng/reorder -H "Content-Type: application/json" -d "[]" > temp_response.txt
findstr /C:"success" temp_response.txt >nul
if %errorlevel% equ 0 (
    echo    ✓ 空数组测试成功
) else (
    echo    ✗ 空数组测试失败
    type temp_response.txt
)

echo.
echo 5. 测试无效数据（应该返回 422）...
curl -s -w "%%{http_code}" -X PUT http://localhost:8788/api/system/web-mng/reorder -H "Content-Type: application/json" -d "[{\"id\":1}]" > temp_response.txt
findstr /C:"422" temp_response.txt >nul
if %errorlevel% equ 0 (
    echo    ✓ 正确拒绝了无效数据 (422)
) else (
    echo    ⚠ 返回了其他状态码
    type temp_response.txt
)

del temp_response.txt >nul 2>&1

echo.
echo ================================
echo 测试完成！
echo ================================
echo.
echo 下一步:
echo 1. 打开浏览器访问应用
echo 2. 进入 Web 页面
echo 3. 测试拖拽排序功能
echo 4. 查看浏览器控制台和后端日志
echo.
echo 如果仍有问题，请查看:
echo - DEBUG_REORDER_422.md
echo - test_reorder_frontend.html
echo - test_reorder_api.py
echo.
pause
