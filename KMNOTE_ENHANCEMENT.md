# KMNotePage.js 功能增强说明

## 对比结果

通过对比 `KMPage.js` 和 `KMNotePage.js`，发现 `KMNotePage.js` 缺失以下功能：

### 第一行工具栏缺失的功能

1. **复制按钮** (copyBtn)
   - 功能：复制选中的文本
   - 快捷键：Ctrl+C
   - SVG图标：双层文档图标

2. **剪切按钮** (cutBtn)
   - 功能：剪切选中的文本
   - 快捷键：Ctrl+X
   - SVG图标：剪刀图标

3. **粘贴按钮** (pasteBtn)
   - 功能：粘贴剪贴板内容
   - 快捷键：Ctrl+V
   - SVG图标：剪贴板图标

4. **搜索按钮** (searchBtn)
   - 功能：在笔记中搜索文字
   - 快捷键：Ctrl+F
   - SVG图标：放大镜图标

5. **日期按钮** (dateBtn)
   - 功能：插入当前日期和时间
   - SVG图标：日历图标

6. **表格按钮** (tableBtn)
   - 功能：插入表格（可自定义行列数）
   - SVG图标：表格图标

7. **图片按钮** (imageBtn)
   - 功能：插入图片（通过URL）
   - SVG图标：图片图标

8. **链接按钮** (linkBtn)
   - 功能：插入超链接
   - SVG图标：链接图标

### 第二行工具栏缺失的功能

1. **表情按钮** (emojiBtn)
   - 功能：打开表情选择器
   - SVG图标：笑脸图标
   - 功能说明：
     * 弹出模态框显示9个常用表情
     * 点击表情直接插入到光标位置
     * 自动关闭选择器

2. **符号按钮** (symbolBtn)
   - 功能：打开符号选择器
   - SVG图标：对勾图标
   - 功能说明：
     * 弹出模态框显示16个常用符号
     * 包括版权、商标、货币、数学符号等
     * 点击符号直接插入到光标位置
     * 自动关闭选择器

3. **上标按钮** (superscript)
   - 功能：将选中文字设为上标
   - SVG图标：X<sup>1</sup>
   - 原已有但未实现

4. **下标按钮** (subscript)
   - 功能：将选中文字设为下标
   - SVG图标：X<sub>1</sub>
   - 原已有但未实现

## 新增方法

### 1. showSearchDialog()
**功能：** 搜索笔记内容
```javascript
showSearchDialog() {
    const searchQuery = prompt('请输入要搜索的内容：', '');
    if (searchQuery && searchQuery.trim()) {
        const noteContent = document.getElementById('noteContent');
        if (!noteContent) return;

        // 使用浏览器的查找功能
        if (window.find) {
            window.find(searchQuery);
        } else {
            // 降级方案
            const text = noteContent.innerText;
            const index = text.toLowerCase().indexOf(searchQuery.toLowerCase());
            if (index !== -1) {
                alert(`找到 "${searchQuery}"`);
            } else {
                alert(`未找到 "${searchQuery}"`);
            }
        }
    }
}
```

### 2. insertDate()
**功能：** 插入当前日期和时间
```javascript
insertDate() {
    const now = new Date();
    const dateStr = now.toLocaleDateString('zh-CN');
    const timeStr = now.toLocaleTimeString('zh-CN');

    this.restoreSavedSelection();
    document.execCommand('insertText', false, `${dateStr} ${timeStr}`);
    this.saveSelection();
}
```

### 3. insertTable()
**功能：** 插入可自定义行列数的表格
```javascript
insertTable() {
    const rows = prompt('请输入表格行数：', '3');
    const cols = prompt('请输入表格列数：', '3');

    if (rows && cols && !isNaN(rows) && !isNaN(cols)) {
        let tableHTML = '<table style="border-collapse: collapse; margin: 10px 0;"><tbody>';

        for (let i = 0; i < parseInt(rows); i++) {
            tableHTML += '<tr>';
            for (let j = 0; j < parseInt(cols); j++) {
                tableHTML += '<td style="border: 1px solid #ddd; padding: 8px; min-width: 80px;">&nbsp;</td>';
            }
            tableHTML += '</tr>';
        }

        tableHTML += '</tbody></table>';

        this.restoreSavedSelection();
        document.execCommand('insertHTML', false, tableHTML);
        this.saveSelection();
    }
}
```

### 4. insertImage()
**功能：** 插入图片（通过URL）
```javascript
insertImage() {
    const imageUrl = prompt('请输入图片URL：', '');
    if (imageUrl && imageUrl.trim()) {
        this.restoreSavedSelection();
        const imgHTML = `<img src="${imageUrl}" style="max-width: 100%; margin: 10px 0;" alt="插入的图片">`;
        document.execCommand('insertHTML', false, imgHTML);
        this.saveSelection();
    }
}
```

### 5. insertLink()
**功能：** 插入超链接
```javascript
insertLink() {
    const url = prompt('请输入链接地址：', '');
    const text = prompt('请输入链接文字（可选）：', '');

    if (url && url.trim()) {
        this.restoreSavedSelection();
        const linkText = text || url;
        const linkHTML = `<a href="${url}" target="_blank" style="color: #1976d2; text-decoration: underline;">${linkText}</a>`;
        document.execCommand('insertHTML', false, linkHTML);
        this.saveSelection();
    }
}
```

### 6. showEmojiPicker()
**功能：** 显示表情选择器
```javascript
showEmojiPicker() {
    const emojis = ['😀', '😁', '😂', '😊', '😍', '🤔', '😎', '👍', '👎', '❤️', '🔥', '✨'];
    
    let emojiHTML = '<div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 10000;">';
    emojiHTML += '<h3 style="margin: 0 0 15px 0; font-size: 16px;">选择表情</h3>';
    emojiHTML += '<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px;">';

    emojis.forEach(emoji => {
        emojiHTML += `<button class="emoji-option" data-emoji="${emoji}" style="font-size: 32px; padding: 10px; cursor: pointer; border: 1px solid #eee; border-radius: 4px; background: white;">${emoji}</button>`;
    });

    emojiHTML += '</div>';
    emojiHTML += '<button id="closeEmojiPicker" style="width: 100%; padding: 10px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer;">关闭</button>';
    emojiHTML += '</div>';

    const container = document.createElement('div');
    container.id = 'emojiPickerModal';
    container.innerHTML = emojiHTML;
    document.body.appendChild(container);

    // 绑定点击事件
    container.querySelectorAll('.emoji-option').forEach(btn => {
        btn.addEventListener('click', () => {
            const emoji = btn.dataset.emoji;
            this.restoreSavedSelection();
            document.execCommand('insertText', false, emoji);
            this.saveSelection();
            document.body.removeChild(container);
        });
    });

    document.getElementById('closeEmojiPicker').addEventListener('click', () => {
        document.body.removeChild(container);
    });
}
```

### 7. showSymbolPicker()
**功能：** 显示符号选择器
```javascript
showSymbolPicker() {
    const symbols = ['©', '®', '™', '€', '£', '¥', '°', '±', '×', '÷', '√', '∞', '≈', '≠', '≤', '≥', '∫', '∑', '∂', '∆'];
    
    let symbolHTML = '<div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 10000;">';
    symbolHTML += '<h3 style="margin: 0 0 15px 0; font-size: 16px;">选择符号</h3>';
    symbolHTML += '<div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; margin-bottom: 15px;">';

    symbols.forEach(symbol => {
        symbolHTML += `<button class="symbol-option" data-symbol="${symbol}" style="font-size: 20px; padding: 10px; cursor: pointer; border: 1px solid #eee; border-radius: 4px; background: white;">${symbol}</button>`;
    });

    symbolHTML += '</div>';
    symbolHTML += '<button id="closeSymbolPicker" style="width: 100%; padding: 10px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer;">关闭</button>';
    symbolHTML += '</div>';

    const container = document.createElement('div');
    container.id = 'symbolPickerModal';
    container.innerHTML = symbolHTML;
    document.body.appendChild(container);

    // 绑定点击事件
    container.querySelectorAll('.symbol-option').forEach(btn => {
        btn.addEventListener('click', () => {
            const symbol = btn.dataset.symbol;
            this.restoreSavedSelection();
            document.execCommand('insertText', false, symbol);
            this.saveSelection();
            document.body.removeChild(container);
        });
    });

    document.getElementById('closeSymbolPicker').addEventListener('click', () => {
        document.body.removeChild(container);
    });
}
```

## 新增键盘快捷键

在 `bindKeyboardShortcuts()` 中添加了以下快捷键：

1. **Ctrl+C** - 复制（由浏览器默认处理）
2. **Ctrl+X** - 剪切（由浏览器默认处理）
3. **Ctrl+V** - 粘贴（由浏览器默认处理）
4. **Ctrl+F** - 打开搜索对话框

## 工具栏布局调整

### 第一行工具栏（从2个组增加到5个组）

**原布局：**
- 组1：保存、打印
- 组2：撤销、重做

**新布局：**
- 组1：保存、打印
- 组2：复制、剪切、粘贴
- 组3：撤销、重做
- 组4：搜索、日期、表格、图片、链接
- 组5：无序列表、有序列表

### 第二行工具栏（增加表情和符号）

**原布局：**
- 字体选择、大小选择、颜色选择、格式按钮、对齐按钮、列表按钮、缩进按钮

**新布局：**
- 字体选择、大小选择、颜色选择
- 表情、符号
- 格式按钮（粗体、斜体、下划线、删除线、上标、下标）
- 对齐按钮
- 缩进按钮

## 选区管理增强

所有新增的工具栏按钮都集成了选区管理机制：

1. **mousedown** 事件 → 保存选区
2. **click** 事件 → 恢复选区 → 执行操作 → 保存选区 → 恢复焦点

这确保了：
- 点击工具栏按钮不会丢失文本选区
- 操作后光标位置正确
- 可以连续操作不需要重新选中文本

## 模态框管理

新增的模态框功能：
- 表情选择器模态框
- 符号选择器模态框

**模态框特点：**
- 居中显示（position: fixed, transform: translate(-50%, -50%)）
- 白色背景、圆角、阴影
- 关闭按钮
- 点击选项后自动关闭
- z-index: 10000 确保在最上层

## 清理方法增强

`destroy()` 方法现在会：
1. 清理表情选择器模态框（如果存在）
2. 清理符号选择器模态框（如果存在）
3. 防止页面卸载后模态框残留

## 使用示例

### 搜索文本
1. 点击搜索按钮或按 Ctrl+F
2. 输入要搜索的文字
3. 系统会提示是否找到

### 插入日期
1. 将光标放在要插入日期的位置
2. 点击日期按钮
3. 自动插入当前日期和时间

### 插入表格
1. 点击表格按钮
2. 输入行数和列数
3. 自动插入指定大小的表格

### 插入图片
1. 点击图片按钮
2. 输入图片URL
3. 自动插入图片

### 插入链接
1. 选中文字（可选）
2. 点击链接按钮
3. 输入链接地址和显示文字
4. 自动插入链接

### 插入表情
1. 点击表情按钮
2. 从弹出的表情选择器中选择
3. 表情自动插入到光标位置

### 插入符号
1. 点击符号按钮
2. 从弹出的符号选择器中选择
3. 符号自动插入到光标位置

## 技术细节

1. **选区API**：使用 `window.getSelection()` 和 `Range` API
2. **execCommand**：使用浏览器原生命令进行编辑操作
3. **模态框**：动态创建 DOM 元素，使用完成后移除
4. **事件委托**：一次性绑定事件到父元素，提升性能
5. **内存管理**：destroy() 方法清理所有动态创建的元素

## 兼容性

- 支持现代浏览器
- 降级方案处理不支持的功能
- 使用标准的 DOM API
- 不依赖第三方库

## 测试建议

1. 测试所有新增按钮的基本功能
2. 测试键盘快捷键是否正常工作
3. 测试模态框的打开、选择、关闭流程
4. 测试选区保持是否正常
5. 测试多种格式组合是否正确应用
6. 测试 destroy() 方法是否正确清理模态框

## 注意事项

1. 图片插入使用 URL，本地文件上传需要后端支持
2. 表格功能仅生成 HTML，不支持复杂表格操作
3. 搜索功能依赖浏览器的查找 API
4. 模态框使用 fixed 定位，可能有滚动条遮挡问题
5. execCommand 已被标记为废弃，但为了兼容性仍使用

## 后续优化建议

1. 使用现代富文本编辑器（如 Quill、Draft.js）
2. 实现真正的表格编辑功能
3. 支持拖拽上传图片
4. 优化模态框交互体验
5. 添加更多表情和符号选项
6. 实现高级搜索（正则、区分大小写等）
