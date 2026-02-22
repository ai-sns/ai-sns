/**
 * SNS Social Role Configuration Dialog
 */

export class SNSSocialRoleDialog {
    constructor() {
        this.dialog = null;
        this.selectedRole = null;
        this.isEditing = false;
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
        const existing = document.getElementById('snsSocialRoleDialog');
        if (existing) {
            try {
                existing.remove();
            } catch (e) {
            }
        }

        const existingStyles = document.getElementById('snsSocialRoleDialogStyles');
        if (existingStyles) {
            try {
                existingStyles.remove();
            } catch (e) {
            }
        }

        // Create dialog HTML
        const dialogHTML = `
            <div class="modal-overlay" id="snsSocialRoleDialog">
                <div class="modal-dialog" style="max-width: 1200px; width: 90vw;">
                    <div class="modal-header">
                        <h3>Prompt Setting</h3>
                        <button class="modal-close" onclick="(() => { const d=document.getElementById('snsSocialRoleDialog'); if(d) d.remove(); const s=document.getElementById('snsSocialRoleDialogStyles'); if(s) s.remove(); })()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="social-role-container">
                            <div class="role-list-section">
                                <h4>Prompt list</h4>
                                <div class="role-list" id="socialRoleList">
                                    <div class="loading">Loading...</div>
                                </div>
                            </div>
                            <div class="role-detail-section">
                                <div class="role-detail-header">
                                    <h4>Detail</h4>
                                </div>
                                <div class="role-preview" id="rolePreview">
                                    <div class="role-preview-content">
                                        <p class="placeholder">Please select a prompt.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <div class="role-actions" id="roleActions" style="display: none;">
                            <button class="btn btn-secondary" id="editRoleBtn">Edit</button>
                            <button class="btn btn-primary" id="saveRoleBtn" style="display: none;">Save</button>
                            <button class="btn btn-secondary" id="cancelEditBtn" style="display: none;">Cancel</button>
                        </div>
                        <button class="btn btn-secondary" onclick="(() => { const d=document.getElementById('snsSocialRoleDialog'); if(d) d.remove(); const s=document.getElementById('snsSocialRoleDialogStyles'); if(s) s.remove(); })()">Close</button>
                    </div>
                </div>
            </div>
        `;

        // Add styles
        const styles = `
            <style id="snsSocialRoleDialogStyles">
                #snsSocialRoleDialog .modal-dialog {
                    max-width: 1200px !important;
                    width: 90vw !important;
                    display: flex;
                    flex-direction: column;
                    max-height: 90vh;
                }
                
                #snsSocialRoleDialog .modal-body {
                    flex: 1;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                }
                
                .social-role-container {
                    display: flex;
                    gap: 20px;
                    flex: 1;
                    min-height: 0;
                }
                
                .role-list-section {
                    flex: 0 0 45%;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                }
                
                .role-list-section h4 {
                    margin: 0 0 12px 0;
                    font-size: 14px;
                    font-weight: 600;
                    color: var(--text-primary, #333);
                }
                
                .role-list {
                    flex: 1;
                    overflow-y: auto;
                    border: 1px solid var(--border-color, #e0e0e0);
                    border-radius: 6px;
                    background: var(--bg-secondary, #fafafa);
                }
                
                .role-item {
                    padding: 12px;
                    border-bottom: 1px solid var(--border-color, #e0e0e0);
                    cursor: pointer;
                    transition: background-color 0.2s;
                    background: var(--bg-content, #fff);
                    color: var(--text-primary, #333);
                }
                
                .role-item:hover {
                    background-color: var(--bg-hover, #f5f5f5);
                }
                
                .role-item.selected {
                    background-color: var(--bg-active, #e3f2fd);
                    border-left: 3px solid var(--color-primary, #2196F3);
                }
                
                .role-item-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 6px;
                }
                
                .role-item-header h5 {
                    margin: 0;
                    font-size: 14px;
                    font-weight: 600;
                    color: var(--text-primary, #333);
                }
                
                .role-tags {
                    font-size: 11px;
                    color: var(--text-secondary, #666);
                    background: var(--bg-tertiary, #e0e0e0);
                    padding: 2px 6px;
                    border-radius: 3px;
                }
                
                .role-item-preview {
                    font-size: 12px;
                    color: var(--text-secondary, #666);
                    line-height: 1.4;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                }
                
                .role-detail-section {
                    flex: 0 0 55%;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                }
                
                .role-detail-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                }
                
                .role-detail-header h4 {
                    margin: 0;
                    font-size: 14px;
                    font-weight: 600;
                    color: var(--text-primary, #333);
                }
                
                #snsSocialRoleDialog .modal-footer {
                    display: flex;
                    justify-content: flex-end;
                    align-items: center;
                    gap: 8px;
                }
                
                .role-actions {
                    display: flex;
                    gap: 8px;
                }
                
                .role-preview {
                    flex: 1;
                    border: 1px solid var(--border-color, #e0e0e0);
                    border-radius: 6px;
                    padding: 16px;
                    overflow: hidden;
                    background: var(--bg-content, #fff);
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                }
                
                .role-preview-content {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                    overflow-y: auto;
                }
                
                .role-preview-content .placeholder {
                    text-align: center;
                    color: var(--text-muted, #999);
                    padding: 40px 20px;
                }
                
                .role-detail {
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }
                
                .role-detail-title {
                    font-size: 18px;
                    font-weight: 600;
                    color: var(--text-primary, #333);
                    margin: 0;
                    padding-bottom: 12px;
                    border-bottom: 2px solid var(--border-color, #e0e0e0);
                    user-select: text;
                    cursor: text;
                }
                
                .role-field {
                    display: flex;
                    flex-direction: column;
                    gap: 6px;
                }
                
                .role-field-label {
                    font-size: 13px;
                    font-weight: 600;
                    color: var(--text-secondary, #555);
                }
                
                .role-field-value {
                    font-size: 13px;
                    color: var(--text-primary, #333);
                    line-height: 1.6;
                    padding: 8px;
                    background: var(--bg-secondary, #f9f9f9);
                    border-radius: 4px;
                    white-space: pre-wrap;
                    user-select: text;
                    cursor: text;
                }
                
                .role-field-input,
                .role-field-textarea {
                    font-size: 13px;
                    padding: 8px;
                    border: 1px solid var(--border-color, #ddd);
                    border-radius: 4px;
                    font-family: inherit;
                    background: var(--bg-content, #fff);
                    color: var(--text-primary, #333);
                }
                
                .role-field-textarea {
                    flex: 1;
                    resize: vertical;
                }
                
                .role-detail.edit-mode {
                    display: flex;
                    flex-direction: column;
                    height: 100%;
                }
                
                .role-detail.edit-mode .role-field:last-child {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                }
                
                .role-detail.edit-mode .role-field:last-child .role-field-textarea {
                    height: 100%;
                }
                
                .btn-sm {
                    padding: 6px 12px;
                    font-size: 13px;
                }
                
                .role-field-input:focus,
                .role-field-textarea:focus {
                    outline: none;
                    border-color: var(--border-focus, #2196F3);
                    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
                }
                
                .loading, .empty-state, .error {
                    text-align: center;
                    padding: 20px;
                    color: var(--text-muted, #999);
                }
                
                .error {
                    color: var(--color-danger, #f44336);
                }
            </style>
        `;

        // Add to DOM
        document.head.insertAdjacentHTML('beforeend', styles);
        document.body.insertAdjacentHTML('beforeend', dialogHTML);
        this.dialog = document.getElementById('snsSocialRoleDialog');

        if (!this._isDialogAlive()) return;

        // Load social roles
        await this.loadSocialRoles();

        if (!this._isDialogAlive()) return;

        // Setup event listeners
        this.setupEventListeners();
    }

    async loadSocialRoles() {
        try {
            const response = await fetch(this.resolve('/api/sns/social-roles'));
            const roles = await response.json();

            if (!this._isDialogAlive()) return;

            const roleList = this._q('#socialRoleList');
            if (!roleList) return;
            roleList.innerHTML = '';

            if (roles.length === 0) {
                roleList.innerHTML = '<div class="empty-state">No prompts found.</div>';
                return;
            }

            roles.forEach(role => {
                const item = document.createElement('div');
                item.className = 'role-item';
                item.dataset.roleId = role.id;
                item.innerHTML = `
                    <div class="role-item-header">
                        <h5>${this.escapeHtml(role.caption)}</h5>
                        ${role.tags ? `<span class="role-tags">${this.escapeHtml(role.tags)}</span>` : ''}
                    </div>
                    <div class="role-item-preview">${this.escapeHtml(this.truncateText(role.content, 80))}</div>
                `;
                item.addEventListener('click', () => this.selectRole(item, role));
                roleList.appendChild(item);
            });
        } catch (error) {
            console.error('Error loading social roles:', error);
            const roleList = this._q('#socialRoleList');
            if (roleList) roleList.innerHTML = '<div class="error">Failed to load.</div>';
        }
    }

    selectRole(element, role) {
        // Remove previous selection
        this._qa('.role-item').forEach(item => {
            item.classList.remove('selected');
        });

        // Select current
        element.classList.add('selected');
        this.selectedRole = role;
        this.isEditing = false;

        // Show preview
        this.showRolePreview(role);

        // Show action buttons and reset to edit mode
        const actions = this._q('#roleActions');
        const editBtn = this._q('#editRoleBtn');
        const saveBtn = this._q('#saveRoleBtn');
        const cancelBtn = this._q('#cancelEditBtn');
        if (actions) actions.style.display = 'flex';
        if (editBtn) editBtn.style.display = 'inline-block';
        if (saveBtn) saveBtn.style.display = 'none';
        if (cancelBtn) cancelBtn.style.display = 'none';
    }

    showRolePreview(role) {
        const preview = this._q('#rolePreview .role-preview-content');
        if (!preview) return;
        preview.innerHTML = `
            <div class="role-detail" style="flex: 1; display: flex; flex-direction: column;">
                <h3 class="role-detail-title">${this.escapeHtml(role.caption)}</h3>
                
                <div class="role-field" style="flex: 1; display: flex; flex-direction: column; min-height: 0;">
                    <div class="role-field-label">Content</div>
                    <div class="role-field-value" data-field="content" style="flex: 1; overflow-y: auto;">${this.escapeHtml(role.content)}</div>
                </div>
            </div>
        `;
    }

    showEditMode() {
        if (!this.selectedRole) return;

        this.isEditing = true;
        const preview = this._q('#rolePreview .role-preview-content');
        if (!preview) return;
        const role = this.selectedRole;

        preview.innerHTML = `
            <div class="role-detail edit-mode">
                <div class="role-field">
                    <label class="role-field-label" for="editCaption">Caption</label>
                    <input id="editCaption" class="role-field-input" value="${this.escapeHtmlAttribute(role.caption)}" />
                </div>
                
                <div class="role-field">
                    <label class="role-field-label" for="editContent">Content</label>
                    <textarea id="editContent" class="role-field-textarea">${this.escapeHtml(role.content)}</textarea>
                </div>
            </div>
        `;

        // Toggle buttons
        const editBtn = this._q('#editRoleBtn');
        const saveBtn = this._q('#saveRoleBtn');
        const cancelBtn = this._q('#cancelEditBtn');
        if (editBtn) editBtn.style.display = 'none';
        if (saveBtn) saveBtn.style.display = 'inline-block';
        if (cancelBtn) cancelBtn.style.display = 'inline-block';
    }

    cancelEdit() {
        this.isEditing = false;
        this.showRolePreview(this.selectedRole);

        // Toggle buttons
        const editBtn = this._q('#editRoleBtn');
        const saveBtn = this._q('#saveRoleBtn');
        const cancelBtn = this._q('#cancelEditBtn');
        if (editBtn) editBtn.style.display = 'inline-block';
        if (saveBtn) saveBtn.style.display = 'none';
        if (cancelBtn) cancelBtn.style.display = 'none';
    }

    async saveRole() {
        if (!this.selectedRole) return;

        const captionEl = this._q('#editCaption');
        const caption = captionEl ? captionEl.value.trim() : '';
        const editEl = this._q('#editContent');
        const content = editEl ? editEl.value.trim() : '';

        if (!caption) {
            alert('Caption cannot be empty.');
            return;
        }

        if (!content) {
            alert('Content cannot be empty.');
            return;
        }

        try {
            const response = await fetch(this.resolve(`/api/sns/social-roles/${this.selectedRole.id}`), {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    caption: caption,
                    content: content
                })
            });

            const result = await response.json();

            if (result.success) {
                // Update local data
                this.selectedRole.caption = caption;
                this.selectedRole.content = content;

                // Refresh display
                this.cancelEdit();

                // Reload list to show updated preview
                await this.loadSocialRoles();

                if (!this._isDialogAlive()) return;

                // Re-select the updated role
                const roleItem = this._q(`.role-item[data-role-id="${this.selectedRole.id}"]`);
                if (roleItem) {
                    roleItem.click();
                }

                alert('Saved successfully.');
            } else {
                alert('Save failed: ' + result.message);
            }
        } catch (error) {
            console.error('Error saving role:', error);
            alert('Save failed: ' + error.message);
        }
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    escapeHtmlAttribute(text) {
        return this.escapeHtml(text)
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    setupEventListeners() {
        // Edit button
        const editBtn = this._q('#editRoleBtn');
        if (editBtn) {
            editBtn.addEventListener('click', () => {
                this.showEditMode();
            });
        }

        // Save button
        const saveBtn = this._q('#saveRoleBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveRole();
            });
        }

        // Cancel button
        const cancelBtn = this._q('#cancelEditBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.cancelEdit();
            });
        }
    }
}
