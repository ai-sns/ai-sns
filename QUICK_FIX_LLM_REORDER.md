# Quick Fix: LLM Reorder Issue

## 问题
LLM Online管理对话框中，拖动第一个项目时会被挤到最后。

## 快速修复步骤

### 1. 运行数据库修复脚本
```bash
python fix_positions.py
```

这会自动修复数据库中所有项目的position值。

### 2. 重启应用
关闭并重新启动应用程序。

### 3. 测试
1. 打开Web标签页
2. 点击"LLM Online"的"Manage"按钮
3. 拖动第一个项目到其他位置
4. 验证：项目正确移动，没有跑到最后

## 技术说明

**修复内容**：
- 修改了`WebSidebar.js`的`loadData()`方法
- 添加了position规范化逻辑
- 确保LLM的position在0-999，Tool的position在1000-1999

**为什么需要运行脚本**：
- 数据库中可能已经存在错误的position值
- 脚本会一次性修复所有现有数据
- 之后新的代码会自动保持position值正确

## 验证修复

运行检查脚本查看position值：
```bash
python check_positions.py
```

应该看到：
- LLM项目：position = 0, 1, 2, 3, ...
- Tool项目：position = 1000, 1001, 1002, 1003, ...

## 文件修改
- ✅ `renderer/js/modules/web/WebSidebar.js` - 添加规范化逻辑
- ✅ `fix_positions.py` - 数据库修复脚本（新建）
- ✅ `check_positions.py` - 检查工具（新建）
