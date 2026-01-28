# Add Button BrowserView Fix - Complete

## 问题描述
点击Add按钮（LLM和Tool的Add按钮）时，弹出的对话框会被BrowserView遮挡，用户无法看到或操作对话框。

## 根本原因
与Manage按钮相同的问题：BrowserView是Electron的原生组件，位于Web内容层之上，CSS的z-index无法影响它。因此即使对话框的z-index很高，仍然会被BrowserView遮挡。

## 解决方案

### 1. 增强Modal组件
在`renderer/js/shared/components/Modal.js`中添加`onClose`回调：
- 添加`onClose`选项到构造函数
- 在`close()`方法中调用`onClose`回调
- 确保无论如何关闭对话框（确认、取消、ESC、点击遮罩），都会触发`onClose`

### 2. 修改showAddModal方法
在`renderer/js/modules/web/webHandlers.js`中：
- **打开对话框时**：调用`hideBrowserView()`隐藏BrowserView
- **关闭对话框时**：使用`onClose`回调调用`showBrowserView()`恢复BrowserView
- 适用于两个Add按钮（LLM和Tool）

## 实现细节

### Modal.js 修改
```javascript
// 构造函数中添加
this.onClose = options.onClose || null;

// close方法中添加
if (this.onClose) {
    this.onClose();
}
```

### webHandlers.js 修改
```javascript
showAddModal(type) {
    // 打开时隐藏BrowserView
    if (window.electronAPI && window.electronAPI.hideBrowserView) {
        window.electronAPI.hideBrowserView();
    }

    Modal.show({
        // ... 对话框内容 ...
        onClose: () => {
            // 关闭时恢复BrowserView（无论如何关闭）
            if (window.electronAPI && window.electronAPI.showBrowserView) {
                window.electronAPI.showBrowserView();
            }
        }
    });
}
```

## 关闭场景覆盖

使用`onClose`回调确保在所有关闭场景下都恢复BrowserView：
1. ✅ 点击"Add"按钮确认
2. ✅ 点击"取消"按钮
3. ✅ 点击X关闭按钮
4. ✅ 按ESC键
5. ✅ 点击遮罩层

## 测试步骤

### 测试LLM Add按钮
1. 打开Web标签页
2. 点击任意网站图标，在BrowserView中打开
3. 点击LLM部分的"Add"按钮
4. **预期**：对话框显示在最上层，可见且可操作
5. 填写表单或点击取消
6. **预期**：对话框关闭，BrowserView恢复显示

### 测试Tool Add按钮
1. 打开Web标签页
2. 点击任意网站图标，在BrowserView中打开
3. 点击Tool部分的"Add"按钮
4. **预期**：对话框显示在最上层，可见且可操作
5. 填写表单或点击取消
6. **预期**：对话框关闭，BrowserView恢复显示

### 测试所有关闭方式
对于每个Add按钮，测试：
1. 点击"Add"确认 → BrowserView恢复 ✅
2. 点击"取消" → BrowserView恢复 ✅
3. 点击X按钮 → BrowserView恢复 ✅
4. 按ESC键 → BrowserView恢复 ✅
5. 点击遮罩层 → BrowserView恢复 ✅

## 控制台日志验证

**打开Add对话框时：**
```
[BrowserView] Hidden (not destroyed)
```

**关闭Add对话框时：**
```
[BrowserView] Shown (restored)
```

## 修改的文件

1. `renderer/js/shared/components/Modal.js`
   - 添加`onClose`回调支持
   
2. `renderer/js/modules/web/webHandlers.js`
   - 在`showAddModal()`中添加BrowserView隐藏/显示逻辑

## 与Manage按钮的一致性

现在所有对话框都使用相同的模式：
- **Manage对话框**：打开时隐藏BrowserView，关闭时显示
- **Edit对话框**：继承Manage对话框的BrowserView状态（已隐藏）
- **Add对话框**：打开时隐藏BrowserView，关闭时显示

## 状态
✅ **完成** - 两个Add按钮（LLM和Tool）的BrowserView遮挡问题已解决
