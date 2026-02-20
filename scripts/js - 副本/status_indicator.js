
    // status indicator

    class StatusIndicator {
        constructor() {
            this.element = document.querySelector('.status-indicator');
            this.textElement = this.element.querySelector('.status-text');
            this.indicatorElement = this.element.querySelector('.activity-indicator');
            this.visibilityTimeout = null;
            this.currentState = '';

            // 预定义所有状态的HTML结构
            this.stateTemplates = {
                thinking: `
                        <div class="dots-container">
                            <div class="dot"></div>
                            <div class="dot"></div>
                            <div class="dot"></div>
                        </div>
                    `,
                talking: `
                        <div class="voice-bars">
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                        </div>
                    `,
                moving: `
                        <div class="arrow-container">
                            <div class="arrow"></div>
                            <div class="arrow"></div>
                        </div>
                    `,
                'using-tool': `
                        <div class="tool-icon"></div>
                    `,
                standby: `
                        <div class="idle-dot"></div>
		<div class="idle-dot"></div>
		<div class="idle-dot"></div>
                    `,
                watching: `
                        <div class="eyes-container">
                            <div class="eye left"></div>
                            <div class="eye right"></div>
                        </div>
                    `
            };
        }

        /**
         * 显示状态指示器
         * @param {string} state - 状态类型 (thinking|talking|moving|using-tool|standby|watching)
         * @param {string} [customText] - 可选的自定义文本
         */
        show(state = 'thinking', customText) {
            if (this.currentState === state) return;

            clearTimeout(this.visibilityTimeout);

            // 移除所有状态类
            this.indicatorElement.className = 'activity-indicator';
            this.indicatorElement.classList.add(state);
            this.currentState = state;

            // 设置状态内容和动画
            this.indicatorElement.innerHTML = this.stateTemplates[state] || this.stateTemplates.thinking;


            // 设置状态文本
            const stateTexts = {
                'thinking': 'Thinking',
                'talking': 'Talking',
                'moving': 'Moving',
                'using-tool': 'Using Tool',
                'standby': 'Standby',
                'watching': 'Watching'
            };
            this.textElement.textContent = customText || stateTexts[state] || 'Thinking';

            this.element.classList.add('visible');
        }

        /**
         * 隐藏状态指示器
         * @param {number} [delay=300] - 隐藏延迟(毫秒)
         */
        hide(delay = 300) {
            this.element.classList.remove('visible');
            this.visibilityTimeout = setTimeout(() => {
                this.textElement.textContent = '';
                this.currentState = '';
            }, delay);
        }

        setVisible(flag) {
            if (flag) {
                this.element.style.display = "block";
            }else
            {
                this.element.style.display = "none";
            }
        }
    }

    // 使用示例
    const aimodel_status = new StatusIndicator();
    aimodel_status.show('standby');


    // // 测试所有状态 - 每2秒切换一次状态
    // const states = ['thinking', 'talking', 'moving', 'using-tool', 'standby', 'watching'];
    // let currentIndex = 0;
    //
    // setInterval(() => {
    //     currentIndex = (currentIndex + 1) % states.length;
    //     status.show(states[currentIndex]);
    // }, 2000);
