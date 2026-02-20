/**
 * SNS Avatar Configuration Dialog
 */

export class SNSAvatarDialog {
    constructor() {
        this.dialog = null;
        this.selectedAvatar3D = null;
        this.uploadedAvatar = null;
        this.existingConfig = null;
        this.existingAvatar3DName = null;
        this.existingAgentId = null;
    }

    _isDialogAlive() {
        return !!(this.dialog && typeof document !== 'undefined' && document.body && document.body.contains(this.dialog));
    }

    _q(selector) {
        return this.dialog ? this.dialog.querySelector(selector) : null;
    }

    _qa(selector) {
        return this.dialog ? Array.from(this.dialog.querySelectorAll(selector)) : [];
    }

    resolve(urlOrPath) {
        try {
            if (typeof window !== 'undefined' && typeof window.resolveAgentServerUrl === 'function') {
                return window.resolveAgentServerUrl(urlOrPath);
            }
        } catch (e) {
        }
        return urlOrPath;
    }

    async show() {
        const existing = document.getElementById('snsAvatarDialog');
        if (existing) {
            try {
                existing.remove();
            } catch (e) {
            }
        }

        // Create dialog HTML
        const dialogHTML = `
            <div class="modal-overlay" id="snsAvatarDialog">
                <div class="modal-dialog" style="max-width: 800px;">
                    <div class="modal-header">
                        <h3>用户配置</h3>
                        <button class="modal-close" onclick="document.getElementById('snsAvatarDialog').remove()">&times;</button>
                    </div>
                    <div class="modal-tabs">
                        <button class="modal-tab active" data-tab="avatar">头像配置</button>
                        <button class="modal-tab" data-tab="userinfo">用户信息</button>
                    </div>
                    <div class="modal-body">
                        <!-- Avatar Config Tab -->
                        <div class="tab-content active" id="avatarTab">
                            <div class="avatar-config-container">
                                <!-- Upload Avatar Section -->
                                <div class="avatar-section">
                                    <h4>上传头像</h4>
                                    <div class="avatar-upload-area">
                                        <input type="file" id="avatarFileInput" accept="image/*" style="display: none;">
                                        <div class="avatar-preview" id="avatarPreview">
                                            <img id="avatarPreviewImg" src="" alt="头像预览" style="display: none; max-width: 150px; max-height: 150px;">
                                            <div id="avatarPlaceholder" class="avatar-placeholder">
                                                <span>点击上传头像</span>
                                            </div>
                                        </div>
                                        <button class="btn btn-primary" id="uploadAvatarBtn">选择图片</button>
                                    </div>
                                </div>

                                <!-- 3D Avatar Selection Section -->
                                <div class="avatar-section">
                                    <h4>选择3D头像</h4>
                                    <div class="avatar3d-grid" id="avatar3dGrid">
                                        <div class="loading">加载中...</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- User Info Tab -->
                        <div class="tab-content" id="userinfoTab" style="display: none;">
                            <div class="user-info-form">
                                <div class="form-group">
                                    <label for="userNickname">昵称</label>
                                    <input type="text" id="userNickname" class="form-control" placeholder="请输入昵称">
                                </div>
                                <div class="form-group">
                                    <label for="userSign">签名</label>
                                    <input type="text" id="userSign" class="form-control" placeholder="请输入签名">
                                </div>
                                <div class="form-group">
                                    <label for="userSnsUrl">SNS URL</label>
                                    <input type="text" id="userSnsUrl" class="form-control" placeholder="请输入SNS URL">
                                </div>
                                <div class="form-group">
                                    <label for="userAgentId">Agent</label>
                                    <select id="userAgentId" class="form-control">
                                        <option value="">请选择Agent</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="document.getElementById('snsAvatarDialog').remove()">取消</button>
                        <button class="btn btn-primary" id="saveAvatarBtn">保存</button>
                    </div>
                </div>
            </div>
        `;

        // Add to DOM
        document.body.insertAdjacentHTML('beforeend', dialogHTML);
        this.dialog = document.getElementById('snsAvatarDialog');

        if (!this._isDialogAlive()) return;

        await this.loadExistingConfig();

        if (!this._isDialogAlive()) return;

        // Load 3D avatars
        await this.load3DAvatars();

        if (!this._isDialogAlive()) return;

        // Load user info
        await this.loadUserInfo();

        if (!this._isDialogAlive()) return;

        // Load agent list
        await this.loadAgentList();

        if (!this._isDialogAlive()) return;

        // Setup event listeners
        this.setupEventListeners();
    }

    setAvatarPreview(avatarSrc) {
        const img = this._q('#avatarPreviewImg');
        const placeholder = this._q('#avatarPlaceholder');
        if (!img || !placeholder || !avatarSrc) return;

        img.src = avatarSrc;
        img.style.display = 'block';
        placeholder.style.display = 'none';
    }

    async loadExistingConfig() {
        try {
            const response = await fetch(this.resolve('/api/sns/config'));
            const result = await response.json();

            const config = result && typeof result === 'object' && 'data' in result ? result.data : result;
            if (!config || typeof config !== 'object') return;

            this.existingConfig = config;
            if (config.avatar) {
                this.setAvatarPreview(config.avatar);
            }
            if (config.avatar3d) {
                const rawName = String(config.avatar3d || '');
                this.existingAvatar3DName = rawName.toLowerCase().endsWith('.glb') ? rawName.slice(0, -4) : rawName;
            }
        } catch (error) {
            console.error('Error loading existing config:', error);
        }
    }

    async load3DAvatars() {
        try {
            const response = await fetch(this.resolve('/api/sns/avatars3d'));
            const avatars = await response.json();

            const grid = this._q('#avatar3dGrid');
            if (!grid) return;
            grid.innerHTML = '';

            avatars.forEach(avatar => {
                const item = document.createElement('div');
                item.className = 'avatar3d-item';
                item.dataset.name = avatar.name;
                item.dataset.modelUrl = avatar.model_url;
                const previewUrl = this.resolve(avatar.preview_url);
                item.innerHTML = `
                    <img src="${previewUrl}" alt="${avatar.name}">
                    <div class="avatar3d-name">${avatar.name}</div>
                `;
                item.addEventListener('click', () => this.select3DAvatar(item, avatar));
                grid.appendChild(item);
            });

            if (this.existingAvatar3DName) {
                const existingAvatar = avatars.find(a => a.name === this.existingAvatar3DName);
                const existingItem = grid.querySelector(`.avatar3d-item[data-name="${CSS.escape(this.existingAvatar3DName)}"]`);
                if (existingAvatar && existingItem) {
                    this.select3DAvatar(existingItem, existingAvatar);
                }
            }
        } catch (error) {
            console.error('Error loading 3D avatars:', error);
            const grid = this._q('#avatar3dGrid');
            if (grid) grid.innerHTML = '<div class="error">加载失败</div>';
        }
    }

    select3DAvatar(element, avatar) {
        // Remove previous selection
        if (this.dialog) {
            this.dialog.querySelectorAll('.avatar3d-item').forEach(item => {
                item.classList.remove('selected');
            });
        }

        // Select current
        element.classList.add('selected');
        this.selectedAvatar3D = avatar;
    }

    setupEventListeners() {
        // Tab switching
        const modalTabs = this._qa('.modal-tab');
        modalTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const targetTab = e.target.dataset.tab;

                // Update tab buttons
                modalTabs.forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');

                // Update tab content
                const tabContents = this._qa('.tab-content');
                tabContents.forEach(content => {
                    content.style.display = 'none';
                    content.classList.remove('active');
                });

                const targetContent = this._q(`#${targetTab}Tab`);
                if (targetContent) {
                    targetContent.style.display = 'block';
                    targetContent.classList.add('active');
                }
            });
        });

        // Upload button
        const uploadBtn = this._q('#uploadAvatarBtn');
        const fileInput = this._q('#avatarFileInput');
        if (uploadBtn && fileInput) {
            uploadBtn.addEventListener('click', () => {
                fileInput.click();
            });
        }

        // File input change
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.previewAvatar(file);
                }
            });
        }

        // Save button
        const saveBtn = this._q('#saveAvatarBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveConfiguration();
            });
        }
    }

    previewAvatar(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = this._q('#avatarPreviewImg');
            const placeholder = this._q('#avatarPlaceholder');
            if (!img || !placeholder) return;
            img.src = e.target.result;
            img.style.display = 'block';
            placeholder.style.display = 'none';
            this.uploadedAvatar = file;
        };
        reader.readAsDataURL(file);
    }

    async saveConfiguration() {
        try {
            const activeTabEl = this._q('.modal-tab.active');
            const activeTab = activeTabEl ? activeTabEl.dataset.tab : 'avatar';

            if (activeTab === 'avatar') {
                // Save avatar configuration
                const updates = {};

                // Upload avatar if selected
                if (this.uploadedAvatar) {
                    const formData = new FormData();
                    formData.append('file', this.uploadedAvatar);

                    const uploadResponse = await fetch(this.resolve('/api/sns/config/upload-avatar'), {
                        method: 'POST',
                        body: formData
                    });

                    const uploadResult = await uploadResponse.json();
                    if (uploadResult.success) {
                        updates.avatar = uploadResult.avatar_data;
                    }
                }

                // Set 3D avatar if selected
                if (this.selectedAvatar3D) {
                    const name = String(this.selectedAvatar3D.name || '');
                    updates.avatar3d = name.toLowerCase().endsWith('.glb') ? name : `${name}.glb`;
                }

                // Update configuration
                if (Object.keys(updates).length > 0) {
                    const response = await fetch(this.resolve('/api/sns/config'), {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(updates)
                    });

                    const result = await response.json();
                    if (result.success) {
                        alert('配置保存成功！');
                        this.dialog.remove();
                    } else {
                        alert('保存失败：' + result.message);
                    }
                } else {
                    alert('请选择头像或3D头像');
                }
            } else if (activeTab === 'userinfo') {
                // Save user info
                const nicknameEl = this._q('#userNickname');
                const signEl = this._q('#userSign');
                const snsUrlEl = this._q('#userSnsUrl');
                const agentIdEl = this._q('#userAgentId');
                const nickname = nicknameEl ? nicknameEl.value : '';
                const sign = signEl ? signEl.value : '';
                const snsUrl = snsUrlEl ? snsUrlEl.value : '';
                const agentId = agentIdEl ? agentIdEl.value : '';

                const response = await fetch(this.resolve('/api/sns/user-info'), {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        nickname,
                        sign,
                        sns_url: snsUrl,
                        agent_id: agentId || null
                    })
                });

                const result = await response.json();
                if (result.success) {
                    alert('用户信息保存成功！');
                    this.dialog.remove();
                } else {
                    alert('保存失败：' + result.message);
                }
            }
        } catch (error) {
            console.error('Error saving configuration:', error);
            alert('保存失败：' + error.message);
        }
    }

    async loadUserInfo() {
        try {
            const response = await fetch(this.resolve('/api/sns/user-info'));
            const result = await response.json();

            if (result.success && result.data) {
                const nicknameEl = this._q('#userNickname');
                const signEl = this._q('#userSign');
                const snsUrlEl = this._q('#userSnsUrl');
                if (nicknameEl) nicknameEl.value = result.data.nickname || '';
                if (signEl) signEl.value = result.data.sign || '';
                if (snsUrlEl) snsUrlEl.value = result.data.sns_url || '';
                this.existingAgentId = result.data.agent_id || '';
                const agentEl = this._q('#userAgentId');
                if (agentEl) agentEl.value = this.existingAgentId;
            }
        } catch (error) {
            console.error('Error loading user info:', error);
        }
    }

    async loadAgentList() {
        try {
            const response = await fetch(this.resolve('/api/agent/list'));
            const result = await response.json();

            if (result.success && result.data) {
                const select = this._q('#userAgentId');
                if (!select) return;
                result.data.forEach(agent => {
                    const option = document.createElement('option');
                    option.value = agent.id;
                    option.textContent = agent.name;
                    select.appendChild(option);
                });

                if (this.existingAgentId) {
                    select.value = this.existingAgentId;
                }
            }
        } catch (error) {
            console.error('Error loading agent list:', error);
        }
    }
}
