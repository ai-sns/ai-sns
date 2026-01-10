/**
 * KM Handlers - 事件处理
 */

const kmHandlers = {
    init() {
        this.bindEvents();
        this.loadNoteList();
    },

    bindEvents() {
        // 新建笔记按钮
        const newNoteBtn = document.getElementById('newNoteBtn');
        if (newNoteBtn) {
            newNoteBtn.addEventListener('click', () => this.showNewNoteModal());
        }

        // 设置按钮
        const kmSettingBtn = document.getElementById('kmSettingBtn');
        if (kmSettingBtn) {
            kmSettingBtn.addEventListener('click', () => this.showSettingModal());
        }

        // 字体选择器
        const fontSelect = document.getElementById('fontSelect');
        if (fontSelect) {
            fontSelect.addEventListener('change', (e) => {
                document.execCommand('fontName', false, e.target.value);
            });
        }

        // 字号选择器
        const sizeSelect = document.getElementById('sizeSelect');
        if (sizeSelect) {
            sizeSelect.addEventListener('change', (e) => {
                const size = e.target.value;
                // 使用fontSize命令设置字号
                document.execCommand('fontSize', false, '7'); // 先设置为最大值
                const fontElements = document.querySelectorAll('font[size="7"]');
                fontElements.forEach(font => {
                    font.removeAttribute('size');
                    font.style.fontSize = size + 'pt';
                });
            });
        }

        // 工具栏按钮
        document.querySelectorAll('.km-tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                // 先聚焦编辑器
                const noteContent = document.getElementById('noteContent');
                if (noteContent) {
                    noteContent.focus();
                }

                let action = btn.dataset.action;
                if (!action) {
                    // 根据按钮属性推测action
                    if (btn.classList.contains('format-btn')) {
                        action = btn.dataset.format;
                    } else {
                        // 根据title属性判断
                        const title = btn.getAttribute('title');
                        action = this.getTitleAction(title);
                    }
                }
                console.log('KM Editor Action:', action);
                this.executeEditorAction(action);
            });
        });

        // 编辑器链接点击处理
        this.setupLinkClickHandler();

        // 树节点展开/折叠
        document.addEventListener('click', (e) => {
            const expandIcon = e.target.closest('.tree-expand');
            if (expandIcon) {
                const treeNode = expandIcon.closest('.km-tree-node');
                if (treeNode) {
                    treeNode.classList.toggle('expanded');
                }
            }
        });
    },

    setupLinkClickHandler() {
        const noteContent = document.getElementById('noteContent');
        if (!noteContent) return;

        // 鼠标悬停在链接上时显示提示
        noteContent.addEventListener('mouseover', (e) => {
            const link = e.target.closest('a');
            if (link && link.href) {
                // 添加悬停样式
                link.style.textDecoration = 'underline';
                link.style.cursor = 'pointer';

                // 显示提示
                link.title = `按住 Ctrl 键点击打开: ${link.href}`;
            }
        });

        // 鼠标离开链接时移除提示
        noteContent.addEventListener('mouseout', (e) => {
            const link = e.target.closest('a');
            if (link && link.href) {
                link.style.textDecoration = link.dataset.originalDecoration || 'underline';
            }
        });

        // 处理链接点击
        noteContent.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (link && link.href) {
                // 如果按住 Ctrl 键（Windows/Linux）或 Cmd 键（Mac），则打开链接
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    window.open(link.href, '_blank');
                    if (typeof Notification !== 'undefined') {
                        Notification.success('已在新标签页打开链接');
                    }
                }
            }
        });

        // 右键菜单
        noteContent.addEventListener('contextmenu', (e) => {
            const link = e.target.closest('a');
            if (link && link.href) {
                e.preventDefault();
                this.showLinkContextMenu(e, link);
            }
        });
    },

    showLinkContextMenu(event, link) {
        // 创建右键菜单
        const existingMenu = document.querySelector('.link-context-menu');
        if (existingMenu) {
            existingMenu.remove();
        }

        const menu = document.createElement('div');
        menu.className = 'link-context-menu';
        menu.style.cssText = `
            position: fixed;
            left: ${event.clientX}px;
            top: ${event.clientY}px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10001;
            min-width: 180px;
            padding: 6px 0;
        `;

        menu.innerHTML = `
            <div class="context-menu-item" data-action="open">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="margin-right: 8px;">
                    <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
                </svg>
                在新标签页打开
            </div>
            <div class="context-menu-item" data-action="copy">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="margin-right: 8px;">
                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                </svg>
                复制链接地址
            </div>
            <div class="context-menu-item" data-action="edit">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="margin-right: 8px;">
                    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
                编辑链接
            </div>
            <div class="context-menu-item" data-action="remove">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="margin-right: 8px;">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
                删除链接
            </div>
        `;

        document.body.appendChild(menu);

        // 添加菜单项样式
        const style = document.createElement('style');
        style.textContent = `
            .context-menu-item {
                display: flex;
                align-items: center;
                padding: 10px 16px;
                cursor: pointer;
                font-size: 14px;
                color: #333;
                transition: background 0.2s;
            }
            .context-menu-item:hover {
                background: #f5f5f5;
            }
            .context-menu-item svg {
                flex-shrink: 0;
            }
        `;
        document.head.appendChild(style);

        // 点击菜单项
        menu.addEventListener('click', (e) => {
            const item = e.target.closest('.context-menu-item');
            if (!item) return;

            const action = item.dataset.action;

            switch (action) {
                case 'open':
                    window.open(link.href, '_blank');
                    if (typeof Notification !== 'undefined') {
                        Notification.success('已在新标签页打开链接');
                    }
                    break;
                case 'copy':
                    navigator.clipboard.writeText(link.href).then(() => {
                        if (typeof Notification !== 'undefined') {
                            Notification.success('链接地址已复制');
                        }
                    });
                    break;
                case 'edit':
                    this.editLink(link);
                    break;
                case 'remove':
                    const text = document.createTextNode(link.textContent);
                    link.parentNode.replaceChild(text, link);
                    if (typeof Notification !== 'undefined') {
                        Notification.success('链接已删除');
                    }
                    break;
            }

            menu.remove();
        });

        // 点击其他地方关闭菜单
        setTimeout(() => {
            document.addEventListener('click', function closeMenu() {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            });
        }, 0);
    },

    editLink(link) {
        const currentUrl = link.href;
        const currentText = link.textContent;

        if (typeof Modal === 'undefined') {
            const url = prompt('输入新的链接地址:', currentUrl);
            if (url) {
                link.href = url;
            }
            return;
        }

        Modal.show({
            title: '编辑链接',
            content: `
                <div class="form-group">
                    <label>链接文本</label>
                    <input type="text" class="form-input" id="editLinkText" value="${currentText}" placeholder="链接显示文本">
                </div>
                <div class="form-group">
                    <label>链接地址</label>
                    <input type="url" class="form-input" id="editLinkUrl" value="${currentUrl}" placeholder="https://example.com">
                </div>
            `,
            confirmText: '保存',
            onConfirm: () => {
                const newUrl = document.getElementById('editLinkUrl')?.value;
                const newText = document.getElementById('editLinkText')?.value;

                if (newUrl) {
                    link.href = newUrl;
                    if (newText) {
                        link.textContent = newText;
                    }
                    if (typeof Notification !== 'undefined') {
                        Notification.success('链接已更新');
                    }
                }
            }
        });
    },

    getTitleAction(title) {
        const actionMap = {
            '粗体': 'bold',
            '斜体': 'italic',
            '下划线': 'underline',
            '删除线': 'strikethrough',
            '上标': 'superscript',
            '下标': 'subscript',
            '左对齐': 'justifyLeft',
            '居中': 'justifyCenter',
            '右对齐': 'justifyRight',
            '两端对齐': 'justifyFull',
            '无序列表': 'insertUnorderedList',
            '有序列表': 'insertOrderedList',
            '增加缩进': 'indent',
            '减少缩进': 'outdent',
            '保存': 'save',
            '打印': 'print',
            '复制': 'copy',
            '剪切': 'cut',
            '粘贴': 'paste',
            '撤销': 'undo',
            '重做': 'redo',
            '搜索': 'search',
            '日期': 'insertDate',
            '表格': 'insertTable',
            '图片': 'insertImage',
            '链接': 'createLink',
            '表情': 'insertEmoticon',
            '符号': 'insertSpecialChar'
        };
        return actionMap[title] || '';
    },

    executeEditorAction(action) {
        const noteContent = document.getElementById('noteContent');
        if (!noteContent) return;

        switch (action) {
            case 'bold':
                document.execCommand('bold', false, null);
                break;
            case 'italic':
                document.execCommand('italic', false, null);
                break;
            case 'underline':
                document.execCommand('underline', false, null);
                break;
            case 'strikethrough':
                document.execCommand('strikeThrough', false, null);
                break;
            case 'superscript':
                document.execCommand('superscript', false, null);
                break;
            case 'subscript':
                document.execCommand('subscript', false, null);
                break;
            case 'justifyLeft':
                document.execCommand('justifyLeft', false, null);
                break;
            case 'justifyCenter':
                document.execCommand('justifyCenter', false, null);
                break;
            case 'justifyRight':
                document.execCommand('justifyRight', false, null);
                break;
            case 'justifyFull':
                document.execCommand('justifyFull', false, null);
                break;
            case 'insertUnorderedList':
                document.execCommand('insertUnorderedList', false, null);
                break;
            case 'insertOrderedList':
                document.execCommand('insertOrderedList', false, null);
                break;
            case 'indent':
                document.execCommand('indent', false, null);
                break;
            case 'outdent':
                document.execCommand('outdent', false, null);
                break;
            case 'save':
                this.saveNote();
                break;
            case 'print':
                window.print();
                break;
            case 'copy':
                document.execCommand('copy', false, null);
                break;
            case 'cut':
                document.execCommand('cut', false, null);
                break;
            case 'paste':
                document.execCommand('paste', false, null);
                break;
            case 'undo':
                document.execCommand('undo', false, null);
                break;
            case 'redo':
                document.execCommand('redo', false, null);
                break;
            case 'search':
                this.showSearchDialog();
                break;
            case 'insertDate':
                const now = new Date();
                const dateStr = now.toLocaleString('zh-CN');
                document.execCommand('insertText', false, dateStr);
                break;
            case 'insertTable':
                this.insertTable();
                break;
            case 'insertEmoticon':
                this.insertEmoticon();
                break;
            case 'insertSpecialChar':
                this.insertSpecialChar();
                break;
            case 'createLink':
                this.insertLink();
                break;
            case 'insertImage':
                this.insertImage();
                break;
            default:
                console.log('未知操作:', action);
        }
    },

    saveNote() {
        const noteContent = document.getElementById('noteContent');
        if (!noteContent) return;

        const content = noteContent.innerHTML;

        // 获取当前笔记ID（从选中的树节点获取）
        const activeNode = document.querySelector('.km-tree-node .km-tree-item.active');
        const noteId = activeNode ? activeNode.dataset.noteId : 'default';
        const noteTitle = activeNode ? activeNode.querySelector('.tree-text')?.textContent : 'Untitled';

        // 保存到localStorage
        const noteData = {
            id: noteId,
            title: noteTitle,
            content: content,
            lastModified: new Date().toISOString()
        };

        localStorage.setItem(`km_note_${noteId}`, JSON.stringify(noteData));

        // TODO: 如果需要，可以在这里调用后端API保存
        // await window.api.post('/api/km/notes', noteData);

        console.log('笔记已保存:', noteTitle);

        if (typeof Notification !== 'undefined') {
            Notification.success('笔记已保存');
        } else {
            alert('笔记已保存');
        }
    },

    showSearchDialog() {
        if (typeof Modal === 'undefined') {
            const searchTerm = prompt('请输入搜索内容:');
            if (searchTerm) {
                this.searchAndHighlight(searchTerm);
            }
            return;
        }

        Modal.show({
            title: '搜索内容',
            content: `
                <div class="form-group">
                    <label>搜索关键词</label>
                    <input type="text" class="form-input" id="searchInput" placeholder="输入搜索内容" autofocus>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="searchCaseSensitive"> 区分大小写
                    </label>
                </div>
            `,
            confirmText: '搜索',
            cancelText: '取消',
            onConfirm: () => {
                const searchTerm = document.getElementById('searchInput')?.value;
                const caseSensitive = document.getElementById('searchCaseSensitive')?.checked;
                if (searchTerm) {
                    this.searchAndHighlight(searchTerm, caseSensitive);
                }
            }
        });
    },

    searchAndHighlight(searchTerm, caseSensitive = false) {
        const noteContent = document.getElementById('noteContent');
        if (!noteContent) return;

        // 清除之前的高亮
        const html = noteContent.innerHTML.replace(/<mark class="search-highlight">(.*?)<\/mark>/g, '$1');
        noteContent.innerHTML = html;

        if (!searchTerm) return;

        // 搜索并高亮
        const regex = new RegExp(searchTerm, caseSensitive ? 'g' : 'gi');
        const newHtml = noteContent.innerHTML.replace(regex, '<mark class="search-highlight">$&</mark>');
        noteContent.innerHTML = newHtml;

        const matches = noteContent.querySelectorAll('.search-highlight');
        if (matches.length > 0) {
            matches[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            if (typeof Notification !== 'undefined') {
                Notification.success(`找到 ${matches.length} 个匹配项`);
            } else {
                alert(`找到 ${matches.length} 个匹配项`);
            }
        } else {
            if (typeof Notification !== 'undefined') {
                Notification.warning('未找到匹配内容');
            } else {
                alert('未找到匹配内容');
            }
        }
    },

    insertTable() {
        if (typeof Modal === 'undefined') {
            const rows = prompt('请输入行数:');
            const cols = prompt('请输入列数:');
            if (rows && cols) {
                this.createTable(parseInt(rows), parseInt(cols));
            }
            return;
        }

        Modal.show({
            title: '插入表格',
            content: `
                <div class="form-group">
                    <label>行数</label>
                    <input type="number" class="form-input" id="tableRows" value="3" min="1" max="20">
                </div>
                <div class="form-group">
                    <label>列数</label>
                    <input type="number" class="form-input" id="tableCols" value="3" min="1" max="10">
                </div>
            `,
            confirmText: '插入',
            onConfirm: () => {
                const rows = parseInt(document.getElementById('tableRows')?.value);
                const cols = parseInt(document.getElementById('tableCols')?.value);
                if (rows > 0 && cols > 0) {
                    this.createTable(rows, cols);
                }
            }
        });
    },

    createTable(rows, cols) {
        let tableHtml = '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; margin: 10px 0;">';
        for (let i = 0; i < rows; i++) {
            tableHtml += '<tr>';
            for (let j = 0; j < cols; j++) {
                tableHtml += '<td style="border: 1px solid #ddd; padding: 8px;">&nbsp;</td>';
            }
            tableHtml += '</tr>';
        }
        tableHtml += '</table>';
        document.execCommand('insertHTML', false, tableHtml);
    },

    insertEmoticon() {
        const emoticons = ['😀', '😂', '😍', '🤔', '👍', '👎', '❤️', '🎉', '⭐', '✅', '❌', '📝', '💡', '🔥', '👏', '🙏'];

        if (typeof Modal === 'undefined') {
            const emoticon = prompt('请输入表情符号:');
            if (emoticon) {
                document.execCommand('insertText', false, emoticon);
            }
            return;
        }

        Modal.show({
            title: '选择表情',
            content: `
                <div style="display: grid; grid-template-columns: repeat(8, 1fr); gap: 10px; padding: 10px;">
                    ${emoticons.map(emoji => `
                        <button class="emoji-btn" data-emoji="${emoji}" style="font-size: 24px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: white;">
                            ${emoji}
                        </button>
                    `).join('')}
                </div>
            `,
            confirmText: '关闭',
            onConfirm: () => {}
        });

        // 为表情按钮添加点击事件
        setTimeout(() => {
            document.querySelectorAll('.emoji-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const emoji = e.target.dataset.emoji || e.target.textContent.trim();
                    document.execCommand('insertText', false, emoji);
                    if (typeof Modal !== 'undefined') {
                        Modal.hide();
                    }
                });
            });
        }, 100);
    },

    insertSpecialChar() {
        const specialChars = ['©', '®', '™', '€', '£', '¥', '¢', '§', '¶', '†', '‡', '•', '…', '′', '″', '‹', '›', '«', '»', '‰', '°', '±', '×', '÷', '≈', '≠', '≤', '≥', '∞'];

        if (typeof Modal === 'undefined') {
            const char = prompt('请输入特殊字符:');
            if (char) {
                document.execCommand('insertText', false, char);
            }
            return;
        }

        Modal.show({
            title: '选择特殊字符',
            content: `
                <div style="display: grid; grid-template-columns: repeat(10, 1fr); gap: 8px; padding: 10px;">
                    ${specialChars.map(char => `
                        <button class="char-btn" data-char="${char}" style="font-size: 18px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: white;">
                            ${char}
                        </button>
                    `).join('')}
                </div>
            `,
            confirmText: '关闭',
            onConfirm: () => {}
        });

        // 为特殊字符按钮添加点击事件
        setTimeout(() => {
            document.querySelectorAll('.char-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const char = e.target.dataset.char || e.target.textContent.trim();
                    document.execCommand('insertText', false, char);
                    if (typeof Modal !== 'undefined') {
                        Modal.hide();
                    }
                });
            });
        }, 100);
    },

    insertLink() {
        const noteContent = document.getElementById('noteContent');
        if (!noteContent) return;

        // 保存当前选区
        const selection = window.getSelection();
        const range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;
        const selectedText = selection.toString();

        if (typeof Modal === 'undefined') {
            const url = prompt('输入链接地址:');
            if (url) {
                if (range) {
                    const link = document.createElement('a');
                    link.href = url;
                    link.target = '_blank';
                    link.textContent = selectedText || url;
                    range.deleteContents();
                    range.insertNode(link);
                }
            }
            return;
        }

        Modal.show({
            title: '插入链接',
            content: `
                <div class="form-group">
                    <label>链接文本</label>
                    <input type="text" class="form-input" id="linkText" value="${selectedText}" placeholder="链接显示文本">
                </div>
                <div class="form-group">
                    <label>链接地址</label>
                    <input type="url" class="form-input" id="linkUrl" placeholder="https://example.com" autofocus>
                </div>
            `,
            confirmText: '插入',
            onConfirm: () => {
                const url = document.getElementById('linkUrl')?.value;
                let text = document.getElementById('linkText')?.value;

                if (!url) {
                    if (typeof Notification !== 'undefined') {
                        Notification.warning('请输入链接地址');
                    }
                    return false;
                }

                // 如果没有文本，使用URL作为文本
                if (!text) {
                    text = url;
                }

                // 创建链接
                noteContent.focus();
                const link = document.createElement('a');
                link.href = url;
                link.target = '_blank';
                link.textContent = text;
                link.style.color = '#1a73e8';
                link.style.textDecoration = 'underline';

                if (range) {
                    try {
                        range.deleteContents();
                        range.insertNode(link);
                        // 将光标移到链接后面
                        range.setStartAfter(link);
                        range.setEndAfter(link);
                        selection.removeAllRanges();
                        selection.addRange(range);
                    } catch (e) {
                        // 如果出错，使用insertHTML作为后备
                        document.execCommand('insertHTML', false, link.outerHTML + '&nbsp;');
                    }
                } else {
                    document.execCommand('insertHTML', false, link.outerHTML + '&nbsp;');
                }

                if (typeof Notification !== 'undefined') {
                    Notification.success('链接已插入');
                }
            }
        });

        // 自动聚焦URL输入框
        setTimeout(() => {
            const urlInput = document.getElementById('linkUrl');
            if (urlInput) {
                urlInput.focus();
            }
        }, 100);
    },

    insertImage() {
        if (typeof Modal === 'undefined') {
            const imgUrl = prompt('输入图片地址:');
            if (imgUrl) document.execCommand('insertImage', false, imgUrl);
            return;
        }

        Modal.show({
            title: '插入图片',
            content: `
                <div class="form-group">
                    <label>选择插入方式</label>
                    <div style="margin-bottom: 15px;">
                        <input type="radio" id="imageUrl" name="imageType" value="url" checked>
                        <label for="imageUrl" style="margin-right: 20px;">图片链接</label>
                        <input type="radio" id="imageFile" name="imageType" value="file">
                        <label for="imageFile">本地文件</label>
                    </div>
                </div>
                <div class="form-group" id="urlInput">
                    <label>图片地址</label>
                    <input type="url" class="form-input" id="imgUrl" placeholder="https://example.com/image.jpg">
                </div>
                <div class="form-group" id="fileInput" style="display: none;">
                    <label>选择图片文件</label>
                    <input type="file" class="form-input" id="imgFile" accept="image/*">
                </div>
            `,
            confirmText: '插入',
            onConfirm: () => {
                const imageType = document.querySelector('input[name="imageType"]:checked')?.value;
                if (imageType === 'url') {
                    const url = document.getElementById('imgUrl')?.value;
                    if (url) {
                        document.execCommand('insertImage', false, url);
                    }
                } else {
                    const file = document.getElementById('imgFile')?.files[0];
                    if (file) {
                        this.handleImageFile(file);
                    }
                }
            }
        });

        // 切换输入方式
        setTimeout(() => {
            document.querySelectorAll('input[name="imageType"]').forEach(radio => {
                radio.addEventListener('change', (e) => {
                    if (e.target.value === 'url') {
                        document.getElementById('urlInput').style.display = 'block';
                        document.getElementById('fileInput').style.display = 'none';
                    } else {
                        document.getElementById('urlInput').style.display = 'none';
                        document.getElementById('fileInput').style.display = 'block';
                    }
                });
            });
        }, 100);
    },

    handleImageFile(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const base64 = e.target.result;
            document.execCommand('insertImage', false, base64);
            if (typeof Notification !== 'undefined') {
                Notification.success('图片已插入');
            }
        };
        reader.onerror = () => {
            if (typeof Notification !== 'undefined') {
                Notification.error('图片读取失败');
            } else {
                alert('图片读取失败');
            }
        };
        reader.readAsDataURL(file);
    },

    showNewNoteModal() {
        if (typeof Modal === 'undefined') {
            console.error('Modal component not loaded');
            return;
        }

        Modal.show({
            title: '新建笔记',
            content: `
                <div class="form-group">
                    <label>标题</label>
                    <input type="text" class="form-input" id="noteTitle" placeholder="输入笔记标题">
                </div>
            `,
            confirmText: '创建',
            onConfirm: () => {
                const title = document.getElementById('noteTitle')?.value;
                if (!title) {
                    if (typeof Notification !== 'undefined') {
                        Notification.error('请输入笔记标题');
                    }
                    return false;
                }
                if (typeof Notification !== 'undefined') {
                    Notification.success('笔记已创建');
                }
            }
        });
    },

    showSettingModal() {
        if (typeof Modal === 'undefined') {
            console.error('Modal component not loaded');
            return;
        }

        Modal.show({
            title: 'KM 设置',
            content: `
                <div class="form-group">
                    <label>默认字体</label>
                    <select class="form-select">
                        <option>Microsoft YaHei UI</option>
                        <option>宋体</option>
                        <option>黑体</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>默认字号</label>
                    <select class="form-select">
                        <option>12pt</option>
                        <option>14pt</option>
                        <option>16pt</option>
                    </select>
                </div>
            `,
            confirmText: '保存',
            onConfirm: () => {
                if (typeof Notification !== 'undefined') {
                    Notification.success('设置已保存');
                }
            }
        });
    },

    async loadNoteList() {
        const noteTree = document.getElementById('noteTree');
        if (!noteTree) return;

        // 这里可以从API加载笔记列表
        // 示例代码已经在HTML中提供了静态列表
    },

    destroy() {
        // 清理事件监听器
    }
};

export default kmHandlers;
