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

        // 工具栏按钮
        document.querySelectorAll('.km-tool-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                let action = btn.dataset.action;
                if (!action) {
                    // 根据按钮属性推测action
                    if (btn.classList.contains('format-btn')) {
                        action = btn.dataset.format;
                    } else if (btn.dataset.align) {
                        action = btn.dataset.align;
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
                const url = prompt('输入链接地址:');
                if (url) document.execCommand('createLink', false, url);
                break;
            case 'insertImage':
                const imgUrl = prompt('输入图片地址:');
                if (imgUrl) document.execCommand('insertImage', false, imgUrl);
                break;
            default:
                console.log('未知操作:', action);
        }
    },

    saveNote() {
        const noteContent = document.getElementById('noteContent');
        if (!noteContent) return;

        const content = noteContent.innerHTML;
        console.log('保存笔记:', content);

        if (typeof Notification !== 'undefined') {
            Notification.success('笔记已保存');
        }
    },

    showSearchDialog() {
        const searchTerm = prompt('请输入搜索内容:');
        if (searchTerm) {
            const noteContent = document.getElementById('noteContent');
            if (noteContent) {
                const text = noteContent.innerText;
                const index = text.indexOf(searchTerm);
                if (index !== -1) {
                    alert(`找到搜索内容在位置 ${index}`);
                } else {
                    alert('未找到搜索内容');
                }
            }
        }
    },

    insertTable() {
        const rows = prompt('请输入行数:');
        const cols = prompt('请输入列数:');

        if (rows && cols) {
            let tableHtml = '<table border="1" cellpadding="5" cellspacing="0">';
            for (let i = 0; i < parseInt(rows); i++) {
                tableHtml += '<tr>';
                for (let j = 0; j < parseInt(cols); j++) {
                    tableHtml += '<td>&nbsp;</td>';
                }
                tableHtml += '</tr>';
            }
            tableHtml += '</table>';
            document.execCommand('insertHTML', false, tableHtml);
        }
    },

    insertEmoticon() {
        const emoticon = prompt('请输入表情符号:');
        if (emoticon) {
            document.execCommand('insertText', false, emoticon);
        }
    },

    insertSpecialChar() {
        const specialChar = prompt('请输入特殊字符:');
        if (specialChar) {
            document.execCommand('insertText', false, specialChar);
        }
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
