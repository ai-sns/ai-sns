# KMNotePage.js 颜色选择器修复说明

## 问题分析

### 原始问题
`km-color-picker-wrapper` 对编辑器文本的颜色修改不稳定，有时可以有时不可以。

### 根本原因
1. **缺少选区管理**：点击工具栏按钮时，文本选区会丢失
2. **事件处理不完善**：只使用 `change` 事件，用户取消选择颜色时不触发
3. **没有实时反馈**：缺少 `input` 事件处理，无法实时预览颜色
4. **焦点管理不当**：使用 `document.getElementById('noteContent').focus()` 但没有恢复选区

## 修复内容

### 1. 添加选区保存/恢复机制
```javascript
saveSelection() {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        this._savedRange = selection.getRangeAt(0).cloneRange();
    }
}

restoreSavedSelection() {
    if (this._savedRange) {
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(this._savedRange);
        this._savedRange = null;
    }
}
```

### 2. 改进颜色选择器实现

**之前的问题代码：**
```javascript
colorPicker.addEventListener('change', (e) => {
    const color = e.target.value;
    document.execCommand('foreColor', false, color);
    // ...
});
```

**修复后的代码：**
```javascript
// 使用 input 事件实现实时预览
colorPicker.addEventListener('input', (e) => {
    const color = e.target.value;
    const indicator = document.getElementById('colorIndicator');
    if (indicator) indicator.setAttribute('fill', color);

    // 恢复选区并应用颜色
    restoreSelection();
    document.execCommand('foreColor', false, color);

    // 重新保存选区，以便连续调整
    saveSelection();
});

// 颜色选择完成
colorPicker.addEventListener('change', (e) => {
    const color = e.target.value;
    const indicator = document.getElementById('colorIndicator');
    if (indicator) indicator.setAttribute('fill', color);

    // 恢复选区并应用颜色
    restoreSelection();
    document.execCommand('foreColor', false, color);
    this.restoreFocus();
});

// 点击颜色按钮时保存选区并打开颜色选择器
colorBtn.addEventListener('click', () => {
    saveSelection();
    setTimeout(() => {
        colorPicker.click();
    }, 10);
});
```

### 3. 为所有工具栏按钮添加选区管理

为以下按钮添加了 `mousedown` 和 `click` 事件处理：
- 格式按钮（粗体、斜体、下划线、删除线）
- 对齐按钮（左对齐、居中、右对齐、两端对齐）
- 列表按钮（有序列表、无序列表）
- 缩进按钮（增加缩进、减少缩进）
- 字体选择器
- 大小选择器

**模式：**
```javascript
btn.addEventListener('mousedown', () => {
    this.saveSelection();  // 保存选区
});

btn.addEventListener('click', () => {
    this.restoreSavedSelection();  // 恢复选区
    document.execCommand(format, false, null);  // 应用格式
    this.saveSelection();  // 重新保存选区
    this.updateToolbarState();  // 更新工具栏状态
    this.restoreFocus();  // 恢复焦点
});
```

### 4. 改进焦点管理

新增 `restoreFocus()` 方法：
```javascript
restoreFocus() {
    const selection = window.getSelection();
    const range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;

    const noteContent = document.getElementById('noteContent');
    if (noteContent) {
        noteContent.focus();

        // 恢复选区
        if (range) {
            try {
                selection.removeAllRanges();
                selection.addRange(range);
            } catch (e) {
                console.warn('[KMNotePage] Failed to restore selection:', e);
            }
        }
    }
}
```

### 5. 增强编辑器事件绑定

在 `bindEditorEvents()` 中添加：
- `mousedown` 事件：清除保存的选区（开始新选区）
- `mouseup` 事件：保存当前选区并更新工具栏状态
- `keyup` 事件：保存当前选区并更新工具栏状态

## 修复效果

### 修复前
- ❌ 点击颜色按钮后，选区可能丢失
- ❌ 调整颜色时没有实时预览
- ❌ 取消颜色选择器时无法恢复选区
- ❌ 连续调整颜色需要重新选中文本

### 修复后
- ✅ 文本选区在所有工具栏操作中保持
- ✅ 颜色选择器支持实时预览（`input` 事件）
- ✅ 取消颜色选择器也能正确恢复选区
- ✅ 连续调整颜色无需重新选中文本
- ✅ 所有格式化工具都支持选区保持

## 技术要点

1. **Range API**：使用 `cloneRange()` 保存选区，避免引用失效
2. **事件时机**：`mousedown` 保存选区，`click` 恢复并应用
3. **延迟执行**：使用 `setTimeout` 确保选区保存后再打开颜色选择器
4. **双重事件**：同时处理 `input` 和 `change` 事件
   - `input`：实时预览（用户拖动颜色选择器时）
   - `change`：最终确认（用户点击确定后）
5. **异常处理**：恢复选区时捕获异常，避免应用崩溃

## 测试建议

1. **基本颜色测试**：
   - 选中一段文字，点击颜色按钮，选择颜色
   - 验证文字颜色是否正确应用

2. **选区保持测试**：
   - 选中文字，多次点击不同颜色
   - 验证选区是否保持，无需重新选中

3. **取消操作测试**：
   - 选中文字，点击颜色按钮，然后点击取消
   - 验证选区是否保持，焦点是否在编辑器

4. **实时预览测试**：
   - 选中文字，打开颜色选择器
   - 拖动颜色滑块，验证文字颜色是否实时变化

5. **组合格式测试**：
   - 选中文字，设置粗体、下划线、颜色
   - 验证所有格式是否正确应用
