/**
 * Educational Assistant - Interactive JavaScript
 * Handles all client-side functionality for the lesson plan generator
 */

class EducationalAssistantUI {
    constructor() {
        this.currentQuery = '';
        this.currentResponse = '';
        this.isGenerating = false;
        this.loadingStepIndex = 0;
        this.loadingSteps = ['step1', 'step2', 'step3', 'step4'];

        // Initialize the application
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.bindEvents();
        this.setupFormValidation();
        this.checkOnlineStatus();
        this.setupKeyboardShortcuts();

        // Focus on the main textarea
        const textarea = document.getElementById('lessonQuery');
        if (textarea) {
            textarea.focus();
        }

        console.log('🚀 Educational Assistant UI initialized');
    }

    /**
     * Bind all event listeners
     */
    bindEvents() {
        // Form submission
        const form = document.getElementById('lessonForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Duration selection
        const durationSelect = document.getElementById('duration');
        if (durationSelect) {
            durationSelect.addEventListener('change', (e) => this.handleDurationChange(e));
        }

        // Character counter
        const textarea = document.getElementById('lessonQuery');
        if (textarea) {
            textarea.addEventListener('input', (e) => this.updateCharCounter(e));
        }

        // Action buttons
        this.bindActionButtons();

        // Window events
        window.addEventListener('online', () => this.handleOnlineStatus(true));
        window.addEventListener('offline', () => this.handleOnlineStatus(false));
        window.addEventListener('beforeunload', (e) => this.handleBeforeUnload(e));
    }

    /**
     * Bind action button events
     */
    bindActionButtons() {
        const buttons = {
            'copyBtn': () => this.copyToClipboard(),
            'downloadBtn': () => this.downloadAsMarkdown(),
            'newLessonBtn': () => this.startNewLesson(),
            'retryBtn': () => this.retryGeneration(),
            'backToFormBtn': () => this.backToForm()
        };

        Object.entries(buttons).forEach(([id, handler]) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', handler);
            }
        });
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        const textarea = document.getElementById('lessonQuery');
        const form = document.getElementById('lessonForm');

        if (textarea && form) {
            textarea.addEventListener('input', () => {
                this.validateForm();
            });
        }
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to submit form
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                const form = document.getElementById('lessonForm');
                if (form && !this.isGenerating) {
                    form.dispatchEvent(new Event('submit'));
                }
            }

            // Escape to cancel or go back
            if (e.key === 'Escape') {
                if (this.isGenerating) {
                    // Could implement cancellation here
                } else {
                    this.backToForm();
                }
            }
        });
    }

    /**
     * Handle form submission
     */
    async handleFormSubmit(event) {
        event.preventDefault();

        if (this.isGenerating) {
            return;
        }

        const formData = this.getFormData();
        if (!this.validateFormData(formData)) {
            return;
        }

        this.currentQuery = formData.query;

        try {
            this.showLoadingState();
            this.startLoadingAnimation();

            const response = await this.generateLessonPlan(formData);

            if (response.error) {
                throw new Error(response.error);
            }

            this.showResponse(response);
            this.showToast('Lesson plan generated successfully!', 'success');

        } catch (error) {
            console.error('Error generating lesson plan:', error);
            this.showError(error.message || 'Failed to generate lesson plan');
            this.showToast('Failed to generate lesson plan', 'error');
        } finally {
            this.stopLoadingAnimation();
            this.isGenerating = false;
        }
    }

    /**
     * Get form data
     */
    getFormData() {
        const query = document.getElementById('lessonQuery')?.value?.trim() || '';
        const duration = document.getElementById('duration')?.value || '';
        const customDuration = document.getElementById('customDuration')?.value?.trim() || '';
        const externalKnowledge = document.getElementById('externalKnowledge')?.checked || false;

        // Use custom duration if selected
        const finalDuration = duration === 'custom' ? customDuration : duration;

        // Add external knowledge trigger to query if checked
        let finalQuery = query;
        if (externalKnowledge) {
            finalQuery += ' (Please include external ideas and best practices beyond the documents)';
        }

        return {
            query: finalQuery,
            duration: finalDuration
        };
    }

    /**
     * Validate form data
     */
    validateFormData(data) {
        if (!data.query) {
            this.showToast('Please describe the lesson you need', 'warning');
            document.getElementById('lessonQuery')?.focus();
            return false;
        }

        if (data.query.length < 10) {
            this.showToast('Please provide a more detailed lesson description', 'warning');
            document.getElementById('lessonQuery')?.focus();
            return false;
        }

        return true;
    }

    /**
     * Validate form in real-time
     */
    validateForm() {
        const textarea = document.getElementById('lessonQuery');
        const submitBtn = document.getElementById('generateBtn');

        if (textarea && submitBtn) {
            const isValid = textarea.value.trim().length >= 10;
            submitBtn.disabled = !isValid || this.isGenerating;
        }
    }

    /**
     * Handle duration selection change
     */
    handleDurationChange(event) {
        const customGroup = document.getElementById('customDurationGroup');
        if (customGroup) {
            if (event.target.value === 'custom') {
                customGroup.style.display = 'block';
                document.getElementById('customDuration')?.focus();
            } else {
                customGroup.style.display = 'none';
            }
        }
    }

    /**
     * Update character counter
     */
    updateCharCounter(event) {
        const charCount = document.getElementById('charCount');
        if (charCount) {
            const length = event.target.value.length;
            charCount.textContent = length;

            // Change color based on length
            if (length > 900) {
                charCount.style.color = '#ef4444'; // Red
            } else if (length > 700) {
                charCount.style.color = '#f59e0b'; // Yellow
            } else {
                charCount.style.color = '#64748b'; // Gray
            }
        }

        this.validateForm();
    }

    /**
     * Generate lesson plan via API
     */
    async generateLessonPlan(data) {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        this.hideAllSections();
        document.getElementById('loadingSection').style.display = 'block';
        this.isGenerating = true;

        // Update button state
        const btn = document.getElementById('generateBtn');
        if (btn) {
            btn.disabled = true;
            btn.querySelector('.btn-text').style.display = 'none';
            btn.querySelector('.btn-loader').style.display = 'inline-block';
        }
    }

    /**
     * Start loading animation
     */
    startLoadingAnimation() {
        this.loadingStepIndex = 0;
        this.updateLoadingStep();

        this.loadingInterval = setInterval(() => {
            this.loadingStepIndex = (this.loadingStepIndex + 1) % this.loadingSteps.length;
            this.updateLoadingStep();
        }, 2000);
    }

    /**
     * Update loading step
     */
    updateLoadingStep() {
        this.loadingSteps.forEach((stepId, index) => {
            const step = document.getElementById(stepId);
            if (step) {
                if (index === this.loadingStepIndex) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
            }
        });
    }

    /**
     * Stop loading animation
     */
    stopLoadingAnimation() {
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
            this.loadingInterval = null;
        }

        // Reset button state
        const btn = document.getElementById('generateBtn');
        if (btn) {
            btn.disabled = false;
            btn.querySelector('.btn-text').style.display = 'inline';
            btn.querySelector('.btn-loader').style.display = 'none';
        }
    }

    /**
     * Show response
     */
    showResponse(data) {
        this.hideAllSections();

        const responseSection = document.getElementById('responseSection');
        const responseContent = document.getElementById('responseContent');
        const responseMeta = document.getElementById('responseMeta');

        if (responseSection && responseContent) {
            // Store response for copying/downloading
            this.currentResponse = data.response || '';

            // Render the response with markdown
            responseContent.innerHTML = this.renderMarkdown(this.currentResponse);

            // Show metadata
            if (responseMeta && data) {
                const metaInfo = [];
                if (data.context_used) {
                    metaInfo.push(`📚 Used ${data.context_used} document chunks`);
                }
                if (data.query_type) {
                    metaInfo.push(`🎯 Lesson type: ${data.query_type}`);
                }
                if (data.external_knowledge) {
                    metaInfo.push(`🌐 Included external knowledge`);
                }
                if (data.timestamp) {
                    metaInfo.push(`⏰ Generated: ${new Date(data.timestamp).toLocaleString()}`);
                }

                responseMeta.innerHTML = metaInfo.join(' • ');
            }

            responseSection.style.display = 'block';

            // Scroll to response
            responseSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    /**
     * Show error state
     */
    showError(message) {
        this.hideAllSections();

        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');

        if (errorSection && errorMessage) {
            errorMessage.textContent = message || 'An unexpected error occurred.';
            errorSection.style.display = 'block';
        }
    }

    /**
     * Hide all sections
     */
    hideAllSections() {
        const sections = ['responseSection', 'loadingSection', 'errorSection'];
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.style.display = 'none';
            }
        });
    }

    /**
     * Render markdown content
     */
    renderMarkdown(text) {
        if (!text) return '';

        // Simple markdown rendering
        let html = text
            // Headers
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')

            // Bold and italic
            .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')

            // Code blocks
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')

            // Lists
            .replace(/^\* (.+$)/gm, '<li>$1</li>')
            .replace(/^- (.+$)/gm, '<li>$1</li>')
            .replace(/^\d+\. (.+$)/gm, '<li>$1</li>')

            // Line breaks
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');

        // Wrap in paragraphs
        html = '<p>' + html + '</p>';

        // Clean up empty paragraphs
        html = html.replace(/<p><\/p>/g, '');
        html = html.replace(/<p>\s*<\/p>/g, '');

        // Handle lists
        html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
        html = html.replace(/<\/li>\s*<li>/g, '</li><li>');

        // Handle tables (basic support)
        html = this.renderTables(html);

        return html;
    }

    /**
     * Render tables from markdown
     */
    renderTables(html) {
        // Simple table rendering for | column | column | format
        const tableRegex = /\|(.+?)\|/g;
        const lines = html.split('\n');
        let inTable = false;
        let tableHtml = '';
        let result = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();

            if (line.match(tableRegex)) {
                if (!inTable) {
                    inTable = true;
                    tableHtml = '<table>';

                    // Check if next line is separator
                    const nextLine = lines[i + 1];
                    const isHeader = nextLine && nextLine.match(/^\|?\s*:?-+:?\s*\|/);

                    if (isHeader) {
                        tableHtml += '<thead>';
                    }
                }

                const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
                const tag = (i === 0 || lines[i-1].match(/^\|?\s*:?-+:?\s*\|/)) ? 'th' : 'td';

                tableHtml += '<tr>';
                cells.forEach(cell => {
                    tableHtml += `<${tag}>${cell}</${tag}>`;
                });
                tableHtml += '</tr>';

                // Close thead if this was header
                if (lines[i + 1] && lines[i + 1].match(/^\|?\s*:?-+:?\s*\|/)) {
                    tableHtml += '</thead><tbody>';
                }

            } else if (inTable) {
                // End of table
                if (tableHtml.includes('<tbody>')) {
                    tableHtml += '</tbody>';
                }
                tableHtml += '</table>';
                result.push(tableHtml);
                tableHtml = '';
                inTable = false;
                result.push(line);
            } else {
                result.push(line);
            }
        }

        // Handle table at end of content
        if (inTable) {
            if (tableHtml.includes('<tbody>')) {
                tableHtml += '</tbody>';
            }
            tableHtml += '</table>';
            result.push(tableHtml);
        }

        return result.join('\n');
    }

    /**
     * Copy response to clipboard
     */
    async copyToClipboard() {
        if (!this.currentResponse) {
            this.showToast('No content to copy', 'warning');
            return;
        }

        try {
            await navigator.clipboard.writeText(this.currentResponse);
            this.showToast('Lesson plan copied to clipboard!', 'success');

            // Visual feedback
            const btn = document.getElementById('copyBtn');
            if (btn) {
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                }, 2000);
            }

        } catch (error) {
            console.error('Failed to copy to clipboard:', error);

            // Fallback: select text
            this.selectResponseText();
            this.showToast('Please copy the selected text manually', 'warning');
        }
    }

    /**
     * Select response text as fallback
     */
    selectResponseText() {
        const responseContent = document.getElementById('responseContent');
        if (responseContent) {
            const range = document.createRange();
            range.selectNodeContents(responseContent);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }

    /**
     * Download response as markdown file
     */
    downloadAsMarkdown() {
        if (!this.currentResponse) {
            this.showToast('No content to download', 'warning');
            return;
        }

        try {
            const blob = new Blob([this.currentResponse], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = `lesson-plan-${this.formatDateForFilename()}.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            URL.revokeObjectURL(url);

            this.showToast('Lesson plan downloaded!', 'success');

        } catch (error) {
            console.error('Failed to download file:', error);
            this.showToast('Failed to download file', 'error');
        }
    }

    /**
     * Format date for filename
     */
    formatDateForFilename() {
        const now = new Date();
        return now.toISOString().slice(0, 19).replace(/[T:]/g, '-');
    }

    /**
     * Start new lesson
     */
    startNewLesson() {
        // Reset form
        const form = document.getElementById('lessonForm');
        if (form) {
            form.reset();
        }

        // Reset custom duration
        const customGroup = document.getElementById('customDurationGroup');
        if (customGroup) {
            customGroup.style.display = 'none';
        }

        // Reset character counter
        const charCount = document.getElementById('charCount');
        if (charCount) {
            charCount.textContent = '0';
            charCount.style.color = '#64748b';
        }

        // Clear stored data
        this.currentQuery = '';
        this.currentResponse = '';

        // Show input section
        this.hideAllSections();
        document.getElementById('inputSection').scrollIntoView({ behavior: 'smooth' });

        // Focus on textarea
        setTimeout(() => {
            document.getElementById('lessonQuery')?.focus();
        }, 300);

        this.showToast('Ready for new lesson plan', 'success');
    }

    /**
     * Retry generation
     */
    retryGeneration() {
        if (this.currentQuery) {
            // Restore the form with previous data
            const textarea = document.getElementById('lessonQuery');
            if (textarea) {
                textarea.value = this.currentQuery;
                this.updateCharCounter({ target: textarea });
            }

            // Submit the form again
            const form = document.getElementById('lessonForm');
            if (form) {
                form.dispatchEvent(new Event('submit'));
            }
        } else {
            this.backToForm();
        }
    }

    /**
     * Back to form
     */
    backToForm() {
        this.hideAllSections();
        document.getElementById('inputSection').scrollIntoView({ behavior: 'smooth' });

        // Focus on textarea
        setTimeout(() => {
            document.getElementById('lessonQuery')?.focus();
        }, 300);
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <div class="toast-icon">
                <i class="${icons[type] || icons.info}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        container.appendChild(toast);

        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);
    }

    /**
     * Check online status
     */
    checkOnlineStatus() {
        this.handleOnlineStatus(navigator.onLine);
    }

    /**
     * Handle online/offline status
     */
    handleOnlineStatus(isOnline) {
        if (!isOnline) {
            this.showToast('You are offline. Some features may not work.', 'warning', 10000);
        }
    }

    /**
     * Handle before unload
     */
    handleBeforeUnload(event) {
        if (this.isGenerating) {
            event.preventDefault();
            event.returnValue = 'A lesson plan is being generated. Are you sure you want to leave?';
            return event.returnValue;
        }
    }

    /**
     * Utility: Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Utility: Throttle function
     */
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.educationalAssistant = new EducationalAssistantUI();
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EducationalAssistantUI;
}