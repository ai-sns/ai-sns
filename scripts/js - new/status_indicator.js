
    // status indicator

    class StatusIndicator {
        constructor() {
            this.element = document.querySelector('.status-indicator');
            this.textElement = this.element.querySelector('.status-text');
            this.indicatorElement = this.element.querySelector('.activity-indicator');
            this.visibilityTimeout = null;
            this.currentState = '';

            // Predefine HTML templates for all states
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
         * Show the status indicator
         * @param {string} state - state type (thinking|talking|moving|using-tool|standby|watching)
         * @param {string} [customText] - optional custom text
         */
        show(state = 'thinking', customText) {
            if (this.currentState === state) return;

            clearTimeout(this.visibilityTimeout);

            // Remove all state classes
            this.indicatorElement.className = 'activity-indicator';
            this.indicatorElement.classList.add(state);
            this.currentState = state;

            // Set state content and animation
            this.indicatorElement.innerHTML = this.stateTemplates[state] || this.stateTemplates.thinking;


            // Set state text
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
         * Hide the status indicator
         * @param {number} [delay=300] - hide delay (ms)
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

    // Usage example
    const aimodel_status = new StatusIndicator();
    aimodel_status.show('standby');


    // // Test all states - switch every 2 seconds
    // const states = ['thinking', 'talking', 'moving', 'using-tool', 'standby', 'watching'];
    // let currentIndex = 0;
    //
    // setInterval(() => {
    //     currentIndex = (currentIndex + 1) % states.length;
    //     status.show(states[currentIndex]);
    // }, 2000);
