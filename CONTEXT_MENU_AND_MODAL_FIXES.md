# Context Menu and Modal Fixes

## 修复内容

### 1. Add对话框关闭后恢复BrowserView ✅

**问题**：
- Add按钮打开的对话框关闭后，BrowserView没有重新显示
- Manage按钮的对话框可以正常恢复BrowserView

**根本原因**：
- Modal组件的`onConfirm`是async函数
- 但`bindEvents`中没有使用await，导致close()在async完成前就被调用
- onClose回调在close()中被调用，但时序不对

**解决方案**：
修改Modal组件的`bindEvents`方法，使用async/await：

```javascript
// 修改前
this.element.addEventListener('click', (e) => {
    if (action === 'confirm') {
        if (this.onConfirm) {
            const result = this.onConfirm(this);  // 没有await
            if (result !== false) {
                this.close();  // 立即调用，不等待async完成
            }
        }
    }
});

// 修改后
this.element.addEventListener('click', async (e) => {
    if (action === 'confirm') {
        if (this.onConfirm) {
            const result = await this.onConfirm(this);  // 等待async完成
            if (result !== false) {
                this.close();  // 在async完成后调用
            }
        }
    }
});
```

**效果**：
- Add对话框关闭后，onClose回调正确触发
- BrowserView正确恢复显示
- 与Manage对话框行为一致

### 2. 优化右键菜单 ✅

**问题**：
- 右键菜单显示图标+文字，占用空间大
- 用户希望只显示图标，文字作为tooltip

**解决方案**：

#### HTML结构修改
```html
<!-- 修改前 -->
<div class="web-context-menu-item" data-action="open-browser">
    <svg>...</svg>
    <span>Open in Default Browser</span>
</div>

<!-- 修改后 -->
<div class="web-context-menu-item" data-action="open-browser" title="Open in Default Browser">
    <svg>...</svg>
</div>
```

#### CSS样式修改
```css
/* 修改前 - 横向布局，有文字 */
.web-context-menu {
    min-width: 200px;
}
.web-context-menu-item {
    display: flex;
    gap: 0.75rem;
    padding: 0.625rem 0.875rem;
}

/* 修改后 - 紧凑布局，只有图标 */
.web-context-menu {
    display: flex;
    gap: 0.25rem;
}
.web-context-menu-item {
    width: 36px;
    height: 36px;
    justify-content: center;
}
```

**效果**：
- 菜单更紧凑，只显示图标
- 鼠标悬停显示tooltip说明
- 图标尺寸从14px增加到18px，更清晰
- 菜单项从垂直排列改为水平排列

## 视觉对比

### 右键菜单

**修改前**：
```
┌─────────────────────────────┐
│ 🔗 Open in Default Browser  │
│ 📋 Copy URL                  │
└─────────────────────────────┘
```

**修改后**：
```
┌──────────┐
│ 🔗  📋   │  (鼠标悬停显示tooltip)
└──────────┘
```

## 文件修改

### 1. renderer/js/shared/components/Modal.js
- `bindEvents()` 方法：添加async/await处理onConfirm

### 2. renderer/js/modules/web/webHandlers.js
- `showContextMenu()` 方法：
  - 移除`<span>`文字
  - 添加`title`属性作为tooltip
  - 增大图标尺寸（14px → 18px）

### 3. renderer/css/web.css
- `.web-context-menu`：
  - 移除`min-width`
  - 添加`display: flex`和`gap`
- `.web-context-menu-item`：
  - 改为固定尺寸（36x36px）
  - 居中对齐图标
  - 移除文字相关样式

## 测试步骤

### 测试1：Add对话框BrowserView恢复
1. 打开Web标签页
2. 点击任意网站图标，在BrowserView中打开
3. 点击"Add"按钮（LLM或Tool）
4. 填写表单并点击"Add"确认
5. **预期**：对话框关闭，BrowserView重新显示
6. 点击"Add"按钮，然后点击"取消"
7. **预期**：对话框关闭，BrowserView重新显示
8. 点击"Add"按钮，然后按ESC键
9. **预期**：对话框关闭，BrowserView重新显示

### 测试2：右键菜单优化
1. 在Web标签页的sidebar中
2. 右键点击任意LLM或Tool图标
3. **预期**：
   - 显示紧凑的横向菜单
   - 只显示两个图标（外部浏览器、复制URL）
   - 鼠标悬停在图标上显示tooltip
4. 点击第一个图标（外部浏览器）
5. **预期**：在默认浏览器中打开URL
6. 右键点击另一个图标，点击第二个图标（复制URL）
7. **预期**：URL复制到剪贴板

### 测试3：Tooltip显示
1. 右键点击图标打开菜单
2. 鼠标悬停在第一个图标上
3. **预期**：显示"Open in Default Browser"
4. 鼠标悬停在第二个图标上
5. **预期**：显示"Copy URL"

## 用户体验改进

### Add对话框
- ✅ 关闭行为与Manage对话框一致
- ✅ 无论如何关闭（确认、取消、ESC），都正确恢复BrowserView
- ✅ 用户体验更流畅

### 右键菜单
- ✅ 更紧凑，不占用太多空间
- ✅ 图标更大更清晰（18px vs 14px）
- ✅ Tooltip提供必要的说明
- ✅ 现代化的UI设计

## 状态
✅ **完成** - Add对话框BrowserView恢复和右键菜单优化都已完成
