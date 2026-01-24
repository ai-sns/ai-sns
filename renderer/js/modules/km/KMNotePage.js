/**
 * KM Page - Note Editor (kmtype=1)
 */

const KMNotePage = {
    render() {
        return `
            <div class="km-page-layout">
                <div class="km-editor-area">
                    <!-- Toolbar row 1: File operations -->
                    <div class="km-toolbar-row">
                        <div class="toolbar-group">
                            <button class="km-tool-btn" id="saveNoteBtn" title="保存 (Ctrl+S)">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M17 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/>
                                </svg>
                            </button>
                            <button class="km-tool-btn" id="printBtn" title="打印">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/>
                                </svg>
                            </button>
                        </div>
                        <div class="toolbar-group">
                            <button class="km-tool-btn" id="copyBtn" title="复制 (Ctrl+C)">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                                </svg>
                            </button>
                            <button class="km-tool-btn" id="cutBtn" title="剪切 (Ctrl+X)">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M9.64 7.64c.23-.5.36-1.05.36-1.64 0-2.21-1.79-4-4-4S2 3.79 2 6s1.79 4 4 4c.59 0 1.14-.13 1.64-.36L10 12l-2.36 2.36C7.14 14.13 6.59 14 6 14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4c0-.59-.13-1.14-.36-1.64L12 14l7 7h3v-1L9.64 7.64zM6 8c-1.1 0-2-.89-2-2s.9-2 2-2 2 .89 2 2-.9 2-2 2zm0 12c-1.1 0-2-.89-2-2s.9-2 2-2 2 .89 2 2-.9 2-2 2zm6-7.5c-.28 0-.5-.22-.5-.5s.22-.5.5-.5.5.22.5.5-.22.5-.5.5zM19 3l-6 6 2 2 7-7V3z"/>
                                </svg>
                            </button>
                            <button class="km-tool-btn" id="pasteBtn" title="粘贴 (Ctrl+V)">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M19 2h-4.18C14.4.84 13.3 0 12 0c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 18H5V4h2v3h10V4h2v16z"/>
                                </svg>
                            </button>
                        </div>
                        <div class="toolbar-group">
                            <button class="km-tool-btn" id="undoBtn" title="撤销 (Ctrl+Z)">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"/>
                                </svg>
                            </button>
                            <button class="km-tool-btn" id="redoBtn" title="重做 (Ctrl+Y)">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M18.4 10.6C16.55 8.99 14.15 8 11.5 8c-4.65 0-8.58 3.03-9.96 7.22L3.9 16c1.05-3.19 4.05-5.5 7.6-5.5 1.95 0 3.73.72 5.12 1.88L13 16h9V7l-3.6 3.6z"/>
                                </svg>
                            </button>
                        </div>
                        <div class="toolbar-group">
                            <button class="km-tool-btn" id="searchBtn" title="搜索 (Ctrl+F)">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                                </svg>
                            </button>
                            <button class="km-tool-btn" id="dateBtn" title="插入日期">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM9 10H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/>
                                </svg>
                            </button>
                            <button class="km-tool-btn" id="tableBtn" title="插入表格">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM8 20H4v-4h4v4zm0-6H4v-4h4v4zm0-6H4V4h4v4zm6 12h-4v-4h4v4zm0-6h-4v-4h4v4zm0-6h-4V4h4v4zm6 12h-4v-4h4v4zm0-6h-4v-4h4v4zm0-6h-4V4h4v4z"/>
                                </svg>
                            </button>
                            <button class="km-tool-btn" id="imageBtn" title="插入图片">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                                </svg>
                            </button>
                            <button class="km-tool-btn" id="linkBtn" title="插入链接">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
                                </svg>
                            </button>
                        </div>
                        <div class="toolbar-group">
                            <button class="km-tool-btn list-btn" data-action="insertUnorderedList" title="无序列表">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M4 10.5c-.83 0-1.5.67-1.5 1.5s.67 1.5 1.5 1.5 1.5-.67 1.5-1.5-.67-1.5-1.5-1.5zm0-6c-.83 0-1.5.67-1.5 1.5S3.17 7.5 4 7.5 5.5 6.83 5.5 6 4.83 4.5 4 4.5zm0 12c-.83 0-1.5.68-1.5 1.5s.68 1.5 1.5 1.5 1.5-.68 1.5-1.5-.67-1.5-1.5-1.5zM7 19h14v-2H7v2zm0-6h14v-2H7v2zm0-8v2h14V5H7z"/>
                                </svg>
                            </button>
                            <button class="km-tool-btn list-btn" data-action="insertOrderedList" title="有序列表">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M2 17h2v.5H3v1h1v.5H2v1h3v-4H2v1zm1-9h1V4H2v1h1v3zm-1 3h1.8L2 13.1v.9h3v-1H3.2L5 10.9V10H2v1zm5-6v2h14V5H7zm0 14h14v-2H7v2zm0-6h14v-2H7v2z"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <!-- Toolbar row 2: Format controls -->
                    <div class="km-toolbar-row km-format-row">
                        <select class="km-font-select" id="fontSelect">
                            <option value="Microsoft YaHei UI">Microsoft YaHei UI</option>
                            <option value="SimSun">宋体</option>
                            <option value="SimHei">黑体</option>
                            <option value="Arial">Arial</option>
                            <option value="Times New Roman">Times New Roman</option>
                            <option value="Courier New">Courier New</option>
                        </select>
                        <select class="km-size-select" id="sizeSelect">
                            <option value="1">10pt</option>
                            <option value="2">12pt</option>
                            <option value="3" selected>14pt</option>
                            <option value="4">16pt</option>
                            <option value="5">18pt</option>
                            <option value="6">24pt</option>
                            <option value="7">36pt</option>
                        </select>
                        <div class="km-color-picker-wrapper">
                            <input type="color" class="km-color-picker" id="colorPicker" value="#000000" title="字体颜色">
                            <button class="km-color-btn" id="colorBtn" title="字体颜色">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                    <path d="M9.62 12L12 5.67 14.38 12M11 3L5.5 17h2.25l1.12-3h6.25l1.12 3h2.25L13 3h-2z"/>
                                    <rect x="3" y="20" width="18" height="3" id="colorIndicator" fill="#000000"/>
                                </svg>
                            </button>
                        </div>
                        <div class="toolbar-divider"></div>
                        <button class="km-tool-btn" id="emojiBtn" title="表情">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
                            </svg>
                        </button>
                        <button class="km-tool-btn" id="symbolBtn" title="符号">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                            </svg>
                        </button>
                        <div class="toolbar-divider"></div>
                        <button class="km-tool-btn format-btn" data-format="bold" title="粗体 (Ctrl+B)"><strong>B</strong></button>
                        <button class="km-tool-btn format-btn" data-format="italic" title="斜体 (Ctrl+I)"><em>I</em></button>
                        <button class="km-tool-btn format-btn" data-format="underline" title="下划线 (Ctrl+U)"><u>U</u></button>
                        <button class="km-tool-btn format-btn" data-format="strikeThrough" title="删除线"><s>S</s></button>
                        <button class="km-tool-btn format-btn" data-format="superscript" title="上标">X<sup>1</sup></button>
                        <button class="km-tool-btn format-btn" data-format="subscript" title="下标">X<sub>1</sub></button>
                        <div class="toolbar-divider"></div>
                        <button class="km-tool-btn align-btn" data-action="justifyLeft" title="左对齐">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                <path d="M15 15H3v2h12v-2zm0-8H3v2h12V7zM3 13h18v-2H3v2zm0 8h18v-2H3v2zM3 3v2h18V3H3z"/>
                            </svg>
                        </button>
                        <button class="km-tool-btn align-btn" data-action="justifyCenter" title="居中">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                <path d="M7 15v2h10v-2H7zm-4 6h18v-2H3v2zm0-8h18v-2H3v2zm4-6v2h10V7H7zM3 3v2h18V3H3z"/>
                            </svg>
                        </button>
                        <button class="km-tool-btn align-btn" data-action="justifyRight" title="右对齐">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                <path d="M3 21h18v-2H3v2zm6-4h12v-2H9v2zm-6-4h18v-2H3v2zm6-4h12V7H9v2zM3 3v2h18V3H3z"/>
                            </svg>
                        </button>
                        <button class="km-tool-btn align-btn" data-action="justifyFull" title="两端对齐">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                <path d="M3 21h18v-2H3v2zm0-4h18v-2H3v2zm0-4h18v-2H3v2zm0-4h18V7H3v2zM3 3v2h18V3H3z"/>
                            </svg>
                        </button>
                        <div class="toolbar-divider"></div>
                        <button class="km-tool-btn indent-btn" data-action="outdent" title="减少缩进">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                <path d="M11 17h10v-2H11v2zm-8-5l4 4V8l-4 4zm0 9h18v-2H3v2zM3 3v2h18V3H3zm8 6h10V7H11v2zm0 4h10v-2H11v2z"/>
                            </svg>
                        </button>
                        <button class="km-tool-btn indent-btn" data-action="indent" title="增加缩进">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                                <path d="M3 21h18v-2H3v2zM3 8v8l4-4-4-4zm8 9h10v-2H11v2zM3 3v2h18V3H3zm8 6h10V7H11v2zm0 4h10v-2H11v2z"/>
                            </svg>
                        </button>
                    </div>
                    <!-- Editor content -->
                    <div class="km-editor-content" id="noteContent" contenteditable="true">
                        <p></p>
                    </div>
                </div>
            </div>
        `;
    },

    init() {
        this.bindEditorEvents();
        this.bindToolbarEvents();
        this.bindKeyboardShortcuts();
    },

    bindEditorEvents() {
        const noteContent = document.getElementById('noteContent');
        if (!noteContent) return;

        // Auto-save on content change (debounced)
        let autoSaveTimer;
        noteContent.addEventListener('input', () => {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = setTimeout(() => {
                // Optional: implement auto-save here
                // window.kmHandlers.saveNote(true); // true = silent save
            }, 3000);
        });

        // 保存选区状态（用于工具栏操作）
        noteContent.addEventListener('mousedown', () => {
            this.clearSavedSelection();
        });

        // Update toolbar state based on selection
        noteContent.addEventListener('mouseup', () => {
            this.saveSelection();
            this.updateToolbarState();
        });
        noteContent.addEventListener('keyup', () => {
            this.saveSelection();
            this.updateToolbarState();
        });
    },

    // 保存当前选区（使用节点路径保存，更健壮）
    saveSelection() {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);

            // 保存 Range 副本（用于快速恢复）
            this._savedRange = range.cloneRange();

            // 保存光标位置信息（用于 Range 失效后的恢复）
            this._savedRangeInfo = {
                startContainer: range.startContainer,
                startOffset: range.startOffset,
                endContainer: range.endContainer,
                endOffset: range.endOffset,
                collapsed: range.collapsed
            };
        }
    },

    // 清除保存的选区
    clearSavedSelection() {
        this._savedRange = null;
        this._savedRangeInfo = null;
    },

    // 恢复保存的选区
    restoreSavedSelection() {
        if (this._savedRange) {
            try {
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(this._savedRange);
                this._savedRange = null;
                this._savedRangeInfo = null;
                return;
            } catch (e) {
                // Range 可能已失效，尝试使用保存的节点路径恢复
                console.warn('[KMNotePage] Range restore failed, trying fallback:', e);
            }
        }

        // 回退方案：使用保存的节点路径和偏移量恢复
        if (this._savedRangeInfo) {
            try {
                const selection = window.getSelection();
                const range = document.createRange();
                range.setStart(this._savedRangeInfo.startContainer, this._savedRangeInfo.startOffset);
                if (!this._savedRangeInfo.collapsed) {
                    range.setEnd(this._savedRangeInfo.endContainer, this._savedRangeInfo.endOffset);
                } else {
                    range.collapse(true);
                }
                selection.removeAllRanges();
                selection.addRange(range);
                this._savedRangeInfo = null;
            } catch (e) {
                console.error('[KMNotePage] Failed to restore selection:', e);
            }
        }
    },

    bindToolbarEvents() {
        // Save button
        const saveBtn = document.getElementById('saveNoteBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => window.kmHandlers.saveNote());
        }

        // Print button
        const printBtn = document.getElementById('printBtn');
        if (printBtn) {
            printBtn.addEventListener('click', () => window.print());
        }

        // Copy, Cut, Paste buttons
        const copyBtn = document.getElementById('copyBtn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                document.execCommand('copy');
                this.restoreFocus();
            });
        }

        const cutBtn = document.getElementById('cutBtn');
        if (cutBtn) {
            cutBtn.addEventListener('click', () => {
                document.execCommand('cut');
                this.restoreFocus();
            });
        }

        const pasteBtn = document.getElementById('pasteBtn');
        if (pasteBtn) {
            pasteBtn.addEventListener('click', () => {
                document.execCommand('paste');
                this.restoreFocus();
            });
        }

        // Undo/Redo buttons
        const undoBtn = document.getElementById('undoBtn');
        if (undoBtn) {
            undoBtn.addEventListener('click', () => {
                document.execCommand('undo');
                this.restoreFocus();
            });
        }

        const redoBtn = document.getElementById('redoBtn');
        if (redoBtn) {
            redoBtn.addEventListener('click', () => {
                document.execCommand('redo');
                this.restoreFocus();
            });
        }

        // Search button
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            searchBtn.addEventListener('click', () => {
                this.showSearchDialog();
            });
        }

        // Date button
        const dateBtn = document.getElementById('dateBtn');
        if (dateBtn) {
            dateBtn.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            dateBtn.addEventListener('click', () => {
                this.insertDate();
            });
        }

        // Table button
        const tableBtn = document.getElementById('tableBtn');
        if (tableBtn) {
            tableBtn.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            tableBtn.addEventListener('click', () => {
                this.insertTable();
            });
        }

        // Image button
        const imageBtn = document.getElementById('imageBtn');
        if (imageBtn) {
            imageBtn.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            imageBtn.addEventListener('click', () => {
                this.insertImage();
            });
        }

        // Link button
        const linkBtn = document.getElementById('linkBtn');
        if (linkBtn) {
            linkBtn.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            linkBtn.addEventListener('click', () => {
                this.insertLink();
            });
        }

        // Emoji and Symbol buttons
        const emojiBtn = document.getElementById('emojiBtn');
        if (emojiBtn) {
            emojiBtn.addEventListener('click', () => {
                this.showEmojiPicker();
            });
        }

        const symbolBtn = document.getElementById('symbolBtn');
        if (symbolBtn) {
            symbolBtn.addEventListener('click', () => {
                this.showSymbolPicker();
            });
        }

        // Font selector
        const fontSelect = document.getElementById('fontSelect');
        if (fontSelect) {
            fontSelect.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            fontSelect.addEventListener('change', (e) => {
                this.restoreSavedSelection();
                document.execCommand('fontName', false, e.target.value);
                this.saveSelection();
                this.restoreFocus();
            });
        }

        // Size selector
        const sizeSelect = document.getElementById('sizeSelect');
        if (sizeSelect) {
            sizeSelect.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            sizeSelect.addEventListener('change', (e) => {
                this.restoreSavedSelection();
                document.execCommand('fontSize', false, e.target.value);
                this.saveSelection();
                this.restoreFocus();
            });
        }

        // Color picker - 修复版
        const colorPicker = document.getElementById('colorPicker');
        const colorBtn = document.getElementById('colorBtn');
        if (colorPicker && colorBtn) {
            let savedSelection = null;

            // 保存选区
            const saveSelection = () => {
                const selection = window.getSelection();
                if (selection.rangeCount > 0) {
                    savedSelection = selection.getRangeAt(0).cloneRange();
                }
            };

            // 恢复选区
            const restoreSelection = () => {
                if (savedSelection) {
                    const selection = window.getSelection();
                    selection.removeAllRanges();
                    selection.addRange(savedSelection);
                    savedSelection = null;
                }
            };

            // 颜色改变时应用（input事件更实时）
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

            // 颜色选择完成（change事件）
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
                // 使用 setTimeout 确保选区已保存
                setTimeout(() => {
                    colorPicker.click();
                }, 10);
            });
        }

        // Format buttons (bold, italic, underline, strikethrough)
        document.querySelectorAll('.format-btn').forEach(btn => {
            btn.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            btn.addEventListener('click', () => {
                this.restoreSavedSelection();
                const format = btn.dataset.format;
                document.execCommand(format, false, null);
                this.saveSelection();
                this.updateToolbarState();
                this.restoreFocus();
            });
        });

        // Align buttons
        document.querySelectorAll('.align-btn').forEach(btn => {
            btn.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            btn.addEventListener('click', () => {
                this.restoreSavedSelection();
                const action = btn.dataset.action;
                document.execCommand(action, false, null);
                this.saveSelection();
                this.updateToolbarState();
                this.restoreFocus();
            });
        });

        // List buttons
        document.querySelectorAll('.list-btn').forEach(btn => {
            btn.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            btn.addEventListener('click', () => {
                this.restoreSavedSelection();
                const action = btn.dataset.action;
                document.execCommand(action, false, null);
                this.saveSelection();
                this.updateToolbarState();
                this.restoreFocus();
            });
        });

        // Indent buttons
        document.querySelectorAll('.indent-btn').forEach(btn => {
            btn.addEventListener('mousedown', () => {
                this.saveSelection();
            });
            btn.addEventListener('click', () => {
                this.restoreSavedSelection();
                const action = btn.dataset.action;
                document.execCommand(action, false, null);
                this.saveSelection();
                this.restoreFocus();
            });
        });
    },

    bindKeyboardShortcuts() {
        const noteContent = document.getElementById('noteContent');
        if (!noteContent) return;

        noteContent.addEventListener('keydown', (e) => {
            // Ctrl+S: Save
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                window.kmHandlers.saveNote();
                return;
            }

            // Ctrl+B: Bold
            if (e.ctrlKey && e.key === 'b') {
                e.preventDefault();
                document.execCommand('bold');
                this.updateToolbarState();
                return;
            }

            // Ctrl+I: Italic
            if (e.ctrlKey && e.key === 'i') {
                e.preventDefault();
                document.execCommand('italic');
                this.updateToolbarState();
                return;
            }

            // Ctrl+U: Underline
            if (e.ctrlKey && e.key === 'u') {
                e.preventDefault();
                document.execCommand('underline');
                this.updateToolbarState();
                return;
            }

            // Ctrl+C: Copy
            if (e.ctrlKey && e.key === 'c') {
                // Let browser handle it
            }

            // Ctrl+X: Cut
            if (e.ctrlKey && e.key === 'x') {
                // Let browser handle it
            }

            // Ctrl+V: Paste
            if (e.ctrlKey && e.key === 'v') {
                // Let browser handle it
            }

            // Ctrl+F: Search
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                this.showSearchDialog();
                return;
            }

            // Ctrl+Z: Undo (default behavior, but ensure it works)
            if (e.ctrlKey && e.key === 'z') {
                // Let browser handle it
            }

            // Ctrl+Y: Redo
            if (e.ctrlKey && e.key === 'y') {
                e.preventDefault();
                document.execCommand('redo');
            }
        });
    },

    // 新增方法：搜索功能
    showSearchDialog() {
        // 保存搜索状态
        this._searchState = {
            query: '',
            matches: [],
            currentIndex: -1,
            textNodes: []
        };

        window.Modal.show({
            title: '搜索',
            content: `
                <div class="form-group">
                    <label class="form-label">搜索内容</label>
                    <input type="text" id="searchQueryInput" class="form-input" placeholder="请输入要搜索的内容" autofocus>
                </div>
                <div class="form-group" id="searchResultInfo" style="display: none; color: #666; font-size: 12px;">
                    0/0
                </div>
            `,
            confirmText: '搜索',
            onConfirm: (modal) => {
                const input = modal.element.querySelector('#searchQueryInput');
                const resultInfo = modal.element.querySelector('#searchResultInfo');
                const searchQuery = input ? input.value : '';
                if (searchQuery && searchQuery.trim()) {
                    const noteContent = document.getElementById('noteContent');
                    if (!noteContent) return;

                    // 聚焦到编辑器
                    noteContent.focus();

                    // 如果是新的搜索，重新查找所有匹配项
                    if (this._searchState.query !== searchQuery) {
                        this._searchState.query = searchQuery;
                        this._searchState.currentIndex = -1;

                        // 使用 TreeWalker 在编辑器内查找所有文本
                        const walker = document.createTreeWalker(
                            noteContent,
                            NodeFilter.SHOW_TEXT,
                            null,
                            false
                        );

                        this._searchState.textNodes = [];
                        this._searchState.matches = [];
                        let node;

                        // 收集所有文本节点和匹配项
                        while (node = walker.nextNode()) {
                            this._searchState.textNodes.push(node);

                            // 在每个文本节点中查找所有匹配项
                            let searchIndex = 0;
                            let matchIndex;
                            const text = node.textContent.toLowerCase();
                            const query = searchQuery.toLowerCase();

                            while ((matchIndex = text.indexOf(query, searchIndex)) !== -1) {
                                this._searchState.matches.push({
                                    node: node,
                                    startOffset: matchIndex,
                                    endOffset: matchIndex + searchQuery.length
                                });
                                searchIndex = matchIndex + searchQuery.length;
                            }
                        }
                    }

                    // 如果有匹配项，显示下一个
                    if (this._searchState.matches.length > 0) {
                        // 移动到下一个匹配项
                        this._searchState.currentIndex = (this._searchState.currentIndex + 1) % this._searchState.matches.length;

                        // 选中当前匹配项
                        const match = this._searchState.matches[this._searchState.currentIndex];
                        const range = document.createRange();
                        range.setStart(match.node, match.startOffset);
                        range.setEnd(match.node, match.endOffset);

                        const selection = window.getSelection();
                        selection.removeAllRanges();
                        selection.addRange(range);

                        // 滚动到可见区域
                        const rect = range.getBoundingClientRect();
                        if (rect.top < 0 || rect.bottom > window.innerHeight) {
                            match.node.parentNode.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }

                        // 更新搜索结果信息
                        if (resultInfo) {
                            resultInfo.style.display = 'block';
                            resultInfo.textContent = `${this._searchState.currentIndex + 1}/${this._searchState.matches.length}`;
                        }
                    } else {
                        if (resultInfo) {
                            resultInfo.style.display = 'block';
                            resultInfo.textContent = '未找到匹配项';
                        }
                        window.Modal.alert(`未找到 "${searchQuery}"`);
                    }
                }
                return false; // 不关闭对话框，允许继续搜索下一个
            },
            onOpen: (modal) => {
                const input = modal.element.querySelector('#searchQueryInput');
                if (input) {
                    input.focus();
                    input.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            const confirmBtn = modal.element.querySelector('[data-action="confirm"]');
                            if (confirmBtn) confirmBtn.click();
                        }
                    });
                }
            }
        });
    },

    // 新增方法：插入日期
    insertDate() {
        const now = new Date();
        const dateStr = now.toLocaleDateString('zh-CN');
        const timeStr = now.toLocaleTimeString('zh-CN');

        this.restoreSavedSelection();
        document.execCommand('insertText', false, `${dateStr} ${timeStr}`);
        this.saveSelection();
    },

    // 新增方法：插入表格
    insertTable() {
        window.Modal.show({
            title: '插入表格',
            content: `
                <div class="form-group">
                    <label class="form-label">行数</label>
                    <input type="number" id="tableRowsInput" class="form-input" value="3" min="1" max="20">
                </div>
                <div class="form-group">
                    <label class="form-label">列数</label>
                    <input type="number" id="tableColsInput" class="form-input" value="3" min="1" max="20">
                </div>
            `,
            confirmText: '插入',
            onConfirm: (modal) => {
                const rowsInput = modal.element.querySelector('#tableRowsInput');
                const colsInput = modal.element.querySelector('#tableColsInput');
                const rows = rowsInput ? rowsInput.value : '3';
                const cols = colsInput ? colsInput.value : '3';

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
                return true;
            },
            onOpen: (modal) => {
                const rowsInput = modal.element.querySelector('#tableRowsInput');
                if (rowsInput) {
                    rowsInput.focus();
                    rowsInput.select();
                    rowsInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            const colsInput = modal.element.querySelector('#tableColsInput');
                            if (colsInput) colsInput.focus();
                        }
                    });
                }
                const colsInput = modal.element.querySelector('#tableColsInput');
                if (colsInput) {
                    colsInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            const confirmBtn = modal.element.querySelector('[data-action="confirm"]');
                            if (confirmBtn) confirmBtn.click();
                        }
                    });
                }
            }
        });
    },

    // 新增方法：插入图片
    insertImage() {
        // 获取当前知识库ID
        const kbId = window.kmHandlers?.currentKbId || 1;

        window.Modal.show({
            title: '插入图片',
            width: '600px',
            content: `
                <div class="form-group">
                    <label class="form-label">选择方式</label>
                    <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                        <button type="button" id="uploadTabBtn" class="btn btn-primary" style="flex: 1;">
                            上传图片
                        </button>
                        <button type="button" id="urlTabBtn" class="btn btn-secondary" style="flex: 1;">
                            图片URL
                        </button>
                    </div>
                </div>

                <!-- 上传区域 -->
                <div id="uploadArea" class="form-group">
                    <label class="form-label">选择图片</label>
                    <input type="file" id="imageFileInput" class="form-input" accept="image/*" style="display: none;">
                    <div id="dropZone" style="border: 2px dashed #ddd; border-radius: 8px; padding: 40px; text-align: center; cursor: pointer; transition: all 0.3s; background: #fafafa;">
                        <div style="color: #666; font-size: 14px;">
                            <div style="font-size: 32px; margin-bottom: 10px;">📷</div>
                            <div>点击选择或拖拽图片到此处</div>
                            <div style="font-size: 12px; color: #999; margin-top: 5px;">支持 JPG, PNG, GIF, WebP</div>
                        </div>
                    </div>
                    <div id="imagePreviewContainer" style="margin-top: 15px; display: none;">
                        <label class="form-label">预览</label>
                        <img id="imagePreview" style="max-width: 100%; max-height: 300px; border-radius: 8px; border: 1px solid #ddd;">
                        <button type="button" id="removeImageBtn" class="btn btn-secondary" style="margin-top: 10px; width: 100%;">
                            重新选择
                        </button>
                    </div>
                </div>

                <!-- URL 输入区域 -->
                <div id="urlArea" class="form-group" style="display: none;">
                    <label class="form-label">图片URL</label>
                    <input type="text" id="imageUrlInput" class="form-input" placeholder="请输入图片URL（例如：https://example.com/image.png）">
                </div>

                <!-- 样式设置 -->
                <div class="form-group">
                    <label class="form-label">图片样式</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div>
                            <label class="form-label" style="font-size: 12px;">对齐方式</label>
                            <select id="imageAlign" class="form-select" style="width: 100%;">
                                <option value="left">左对齐</option>
                                <option value="center">居中</option>
                                <option value="right">右对齐</option>
                            </select>
                        </div>
                        <div>
                            <label class="form-label" style="font-size: 12px;">宽度</label>
                            <select id="imageWidth" class="form-select" style="width: 100%;">
                                <option value="auto">原始大小</option>
                                <option value="100%">100%</option>
                                <option value="75%">75%</option>
                                <option value="50%">50%</option>
                                <option value="300">300px</option>
                                <option value="500">500px</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div id="uploadProgress" style="display: none; margin-top: 10px;">
                    <div style="text-align: center; color: #666;">
                        <div class="spinner" style="display: inline-block;"></div>
                        <div style="margin-top: 5px;">上传中...</div>
                    </div>
                </div>
            `,
            confirmText: '插入',
            onConfirm: async (modal) => {
                const imageUrlInput = modal.element.querySelector('#imageUrlInput');
                const imagePreview = modal.element.querySelector('#imagePreview');
                const imageAlign = modal.element.querySelector('#imageAlign');
                const imageWidth = modal.element.querySelector('#imageWidth');

                let imageUrl = '';

                // 如果有预览图片，使用预览的src
                if (imagePreview && imagePreview.src && imagePreview.src !== '') {
                    imageUrl = imagePreview.src;
                } else if (imageUrlInput && imageUrlInput.value && imageUrlInput.value.trim()) {
                    // 否则使用输入的URL
                    imageUrl = imageUrlInput.value.trim();
                }

                if (imageUrl) {
                    this.restoreSavedSelection();

                    // 获取样式
                    const align = imageAlign ? imageAlign.value : 'left';
                    const width = imageWidth ? imageWidth.value : 'auto';

                    // 构建样式
                    let style = '';
                    if (width !== 'auto') {
                        style += `width: ${width};`;
                    } else {
                        style += 'max-width: 100%;';
                    }
                    style += 'margin: 10px 0;';
                    style += 'display: block;';
                    if (align === 'center') {
                        style += 'margin-left: auto; margin-right: auto;';
                    } else if (align === 'right') {
                        style += 'margin-left: auto;';
                    }

                    const imgHTML = `<img src="${imageUrl}" style="${style}" alt="插入的图片">`;
                    document.execCommand('insertHTML', false, imgHTML);
                    this.saveSelection();
                }

                return true;
            },
            onOpen: (modal) => {
                const uploadTabBtn = modal.element.querySelector('#uploadTabBtn');
                const urlTabBtn = modal.element.querySelector('#urlTabBtn');
                const uploadArea = modal.element.querySelector('#uploadArea');
                const urlArea = modal.element.querySelector('#urlArea');
                const dropZone = modal.element.querySelector('#dropZone');
                const imageFileInput = modal.element.querySelector('#imageFileInput');
                const imagePreview = modal.element.querySelector('#imagePreview');
                const imagePreviewContainer = modal.element.querySelector('#imagePreviewContainer');
                const removeImageBtn = modal.element.querySelector('#removeImageBtn');
                const uploadProgress = modal.element.querySelector('#uploadProgress');

                let uploadedImageUrl = '';

                // 切换标签页
                const switchToUpload = () => {
                    uploadTabBtn.classList.remove('btn-secondary');
                    uploadTabBtn.classList.add('btn-primary');
                    urlTabBtn.classList.remove('btn-primary');
                    urlTabBtn.classList.add('btn-secondary');
                    uploadArea.style.display = 'block';
                    urlArea.style.display = 'none';
                };

                const switchToUrl = () => {
                    urlTabBtn.classList.remove('btn-secondary');
                    urlTabBtn.classList.add('btn-primary');
                    uploadTabBtn.classList.remove('btn-primary');
                    uploadTabBtn.classList.add('btn-secondary');
                    urlArea.style.display = 'block';
                    uploadArea.style.display = 'none';
                };

                uploadTabBtn.addEventListener('click', switchToUpload);
                urlTabBtn.addEventListener('click', switchToUrl);

                // 点击上传区域触发文件选择
                dropZone.addEventListener('click', () => imageFileInput.click());

                // 文件选择
                imageFileInput.addEventListener('change', async (e) => {
                    if (e.target.files && e.target.files[0]) {
                        await handleImageUpload(e.target.files[0]);
                    }
                });

                // 拖拽上传
                dropZone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    dropZone.style.borderColor = '#2196F3';
                    dropZone.style.background = '#e3f2fd';
                });

                dropZone.addEventListener('dragleave', (e) => {
                    e.preventDefault();
                    dropZone.style.borderColor = '#ddd';
                    dropZone.style.background = '#fafafa';
                });

                dropZone.addEventListener('drop', async (e) => {
                    e.preventDefault();
                    dropZone.style.borderColor = '#ddd';
                    dropZone.style.background = '#fafafa';

                    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                        await handleImageUpload(e.dataTransfer.files[0]);
                    }
                });

                // 上传处理
                const handleImageUpload = async (file) => {
                    if (!file.type.startsWith('image/')) {
                        window.Modal.alert('请选择图片文件');
                        return;
                    }

                    // 显示进度
                    dropZone.style.display = 'none';
                    uploadProgress.style.display = 'block';

                    try {
                        const formData = new FormData();
                        formData.append('file', file);

                        const response = await fetch(`http://localhost:8788/api/km/${kbId}/upload-image`, {
                            method: 'POST',
                            body: formData
                        });

                        const result = await response.json();

                        if (result.success && result.data) {
                            uploadedImageUrl = result.data.url;

                            // 显示预览
                            dropZone.style.display = 'none';
                            uploadProgress.style.display = 'none';
                            imagePreviewContainer.style.display = 'block';
                            imagePreview.src = uploadedImageUrl;

                            // 清空文件输入
                            imageFileInput.value = '';
                        } else {
                            throw new Error('上传失败');
                        }
                    } catch (error) {
                        console.error('Upload error:', error);
                        window.Modal.alert('图片上传失败：' + error.message);
                        dropZone.style.display = 'block';
                        uploadProgress.style.display = 'none';
                    }
                };

                // 移除图片
                removeImageBtn.addEventListener('click', () => {
                    uploadedImageUrl = '';
                    imagePreview.src = '';
                    imagePreviewContainer.style.display = 'none';
                    dropZone.style.display = 'block';
                });

                // URL 输入框聚焦
                const urlInput = modal.element.querySelector('#imageUrlInput');
                if (urlInput) {
                    urlInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            const confirmBtn = modal.element.querySelector('[data-action="confirm"]');
                            if (confirmBtn) confirmBtn.click();
                        }
                    });
                }
            }
        });
    },

    // 新增方法：插入链接
    insertLink() {
        window.Modal.show({
            title: '插入链接',
            content: `
                <div class="form-group">
                    <label class="form-label">链接地址</label>
                    <input type="text" id="linkUrlInput" class="form-input" placeholder="请输入链接地址（例如：https://example.com）" autofocus>
                </div>
                <div class="form-group">
                    <label class="form-label">链接文字（可选）</label>
                    <input type="text" id="linkTextInput" class="form-input" placeholder="留空则使用链接地址">
                </div>
            `,
            confirmText: '插入',
            onConfirm: (modal) => {
                const urlInput = modal.element.querySelector('#linkUrlInput');
                const textInput = modal.element.querySelector('#linkTextInput');
                const url = urlInput ? urlInput.value : '';
                const text = textInput ? textInput.value : '';

                if (url && url.trim()) {
                    this.restoreSavedSelection();
                    const linkText = text || url;
                    const linkHTML = `<a href="${url}" target="_blank" style="color: #1976d2; text-decoration: underline;">${linkText}</a>`;
                    document.execCommand('insertHTML', false, linkHTML);
                    this.saveSelection();
                }
                return true;
            },
            onOpen: (modal) => {
                const urlInput = modal.element.querySelector('#linkUrlInput');
                if (urlInput) {
                    urlInput.focus();
                    urlInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            const textInput = modal.element.querySelector('#linkTextInput');
                            if (textInput) textInput.focus();
                        }
                    });
                }
                const textInput = modal.element.querySelector('#linkTextInput');
                if (textInput) {
                    textInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            const confirmBtn = modal.element.querySelector('[data-action="confirm"]');
                            if (confirmBtn) confirmBtn.click();
                        }
                    });
                }
            }
        });
    },

    // 新增方法：显示表情选择器
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
    },

    // 新增方法：显示符号选择器
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
    },

    destroy() {
        // Clean up modals if they exist
        const emojiModal = document.getElementById('emojiPickerModal');
        const symbolModal = document.getElementById('symbolPickerModal');
        if (emojiModal) emojiModal.remove();
        if (symbolModal) symbolModal.remove();
    },

    restoreFocus() {
        // 保存当前选区
        const selection = window.getSelection();
        const range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;

        // 焦点回到编辑器
        const noteContent = document.getElementById('noteContent');
        if (noteContent) {
            noteContent.focus();

            // 恢复选区
            if (range) {
                try {
                    selection.removeAllRanges();
                    selection.addRange(range);
                } catch (e) {
                    // 如果恢复失败（选区失效），至少确保焦点在编辑器
                    console.warn('[KMNotePage] Failed to restore selection:', e);
                }
            }
        }
    },

    updateToolbarState() {
        // Update format button states
        document.querySelectorAll('.format-btn').forEach(btn => {
            const format = btn.dataset.format;
            const isActive = document.queryCommandState(format);
            btn.classList.toggle('active', isActive);
        });

        // Update align button states
        document.querySelectorAll('.align-btn').forEach(btn => {
            const action = btn.dataset.action;
            const isActive = document.queryCommandState(action);
            btn.classList.toggle('active', isActive);
        });

        // Update list button states
        document.querySelectorAll('.list-btn').forEach(btn => {
            const action = btn.dataset.action;
            const isActive = document.queryCommandState(action);
            btn.classList.toggle('active', isActive);
        });
    }
};

export default KMNotePage;
