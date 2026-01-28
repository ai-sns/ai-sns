#!/bin/bash

echo "================================"
echo "Web Sidebar 快速测试脚本"
echo "================================"
echo ""

# 检查后端服务器是否运行
echo "1. 检查后端服务器..."
if curl -s http://localhost:8788/health > /dev/null 2>&1; then
    echo "   ✅ 后端服务器正在运行"
else
    echo "   ❌ 后端服务器未运行"
    echo "   请先启动: python api_server.py"
    exit 1
fi

echo ""
echo "2. 测试 GET /api/system/web-mng..."
response=$(curl -s http://localhost:8788/api/system/web-mng)
if echo "$response" | grep -q "success"; then
    echo "   ✅ GET 请求成功"
    echo "   响应: $response" | head -c 100
    echo "..."
else
    echo "   ❌ GET 请求失败"
    echo "   响应: $response"
fi

echo ""
echo "3. 测试 PUT /api/system/web-mng/reorder..."
response=$(curl -s -X PUT http://localhost:8788/api/system/web-mng/reorder \
    -H "Content-Type: application/json" \
    -d '[{"id":1,"position":0},{"id":2,"position":1}]')

if echo "$response" | grep -q "success"; then
    echo "   ✅ PUT 请求成功"
    echo "   响应: $response"
else
    echo "   ❌ PUT 请求失败"
    echo "   响应: $response"
fi

echo ""
echo "4. 测试空数组..."
response=$(curl -s -X PUT http://localhost:8788/api/system/web-mng/reorder \
    -H "Content-Type: application/json" \
    -d '[]')

if echo "$response" | grep -q "success"; then
    echo "   ✅ 空数组测试成功"
else
    echo "   ❌ 空数组测试失败"
    echo "   响应: $response"
fi

echo ""
echo "5. 测试无效数据（应该返回 422）..."
response=$(curl -s -w "\n%{http_code}" -X PUT http://localhost:8788/api/system/web-mng/reorder \
    -H "Content-Type: application/json" \
    -d '[{"id":1}]')

http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "422" ]; then
    echo "   ✅ 正确拒绝了无效数据 (422)"
else
    echo "   ⚠️  返回了 $http_code，期望 422"
fi

echo ""
echo "================================"
echo "测试完成！"
echo "================================"
echo ""
echo "下一步:"
echo "1. 打开浏览器访问应用"
echo "2. 进入 Web 页面"
echo "3. 测试拖拽排序功能"
echo "4. 查看浏览器控制台和后端日志"
echo ""
echo "如果仍有问题，请查看:"
echo "- DEBUG_REORDER_422.md"
echo "- test_reorder_frontend.html"
echo "- test_reorder_api.py"
