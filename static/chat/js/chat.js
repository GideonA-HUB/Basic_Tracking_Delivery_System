/**
 * Live Chat Widget JavaScript
 * Meridian Asset Logistics
 */

class LiveChatWidget {
    constructor() {
        this.isOpen = false;
        this.conversationId = null;
        this.isTyping = false;
        this.typingTimeout = null;
        this.messageCheckInterval = null;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeChat();
    }
    
    initializeElements() {
        this.toggleBtn = document.getElementById('chat-toggle');
        this.chatWindow = document.getElementById('chat-window');
        this.chatIcon = document.getElementById('chat-icon');
        this.chatBadge = document.getElementById('chat-badge');
        this.messagesContainer = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-message');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.customerInfoForm = document.getElementById('customer-info-form');
        this.welcomeMessage = document.getElementById('welcome-message');
        this.onlineIndicator = document.getElementById('online-indicator');
        this.staffStatus = document.getElementById('staff-status');
    }
    
    bindEvents() {
        // Toggle chat window
        this.toggleBtn.addEventListener('click', () => this.toggleChat());
        
        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Typing indicator
        this.messageInput.addEventListener('input', () => this.handleTyping());
        
        // Close buttons
        document.getElementById('chat-close')?.addEventListener('click', () => this.closeChat());
        document.getElementById('chat-minimize')?.addEventListener('click', () => this.minimizeChat());
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
    }
    
    async initializeChat() {
        try {
            // Check if chat is enabled
            const response = await this.makeRequest('/chat/widget/');
            
            if (!response.enabled) {
                this.hideChatWidget();
                return;
            }
            
            // Update online status
            this.updateOnlineStatus(response.is_online, response.online_staff_count);
            
            // Check for existing conversation
            if (response.conversation) {
                this.conversationId = response.conversation.id;
                this.hideWelcomeMessage();
                this.loadMessages();
                this.startMessagePolling();
            }
            
        } catch (error) {
            console.error('Error initializing chat:', error);
            this.showError('Unable to connect to chat service. Please refresh the page.');
        }
    }
    
    updateOnlineStatus(isOnline, staffCount) {
        if (isOnline) {
            this.onlineIndicator.className = 'w-2 h-2 bg-green-400 rounded-full';
            this.staffStatus.textContent = `${staffCount} staff online`;
        } else {
            this.onlineIndicator.className = 'w-2 h-2 bg-red-400 rounded-full';
            this.staffStatus.textContent = 'Offline';
        }
    }
    
    toggleChat() {
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            this.openChat();
        } else {
            this.closeChat();
        }
    }
    
    openChat() {
        this.chatWindow.classList.remove('hidden');
        this.chatIcon.className = 'fas fa-times text-xl';
        this.messageInput.focus();
        
        // Load messages if conversation exists
        if (this.conversationId) {
            this.loadMessages();
        }
        
        // Start polling for new messages
        this.startMessagePolling();
    }
    
    closeChat() {
        this.isOpen = false;
        this.chatWindow.classList.add('hidden');
        this.chatIcon.className = 'fas fa-comments text-xl';
        
        // Stop polling when closed
        this.stopMessagePolling();
    }
    
    minimizeChat() {
        this.closeChat();
    }
    
    async startConversation() {
        // Check if user is authenticated first
        if (this.isUserAuthenticated()) {
            // For authenticated users, try to get existing conversation or create one
            try {
                const response = await this.makeRequest('/chat/start-conversation/', {
                    method: 'POST',
                    body: JSON.stringify({
                        subject: 'General Inquiry'
                    })
                });
                
                if (response.success) {
                    this.conversationId = response.conversation_id;
                    this.hideCustomerInfoForm();
                    this.hideWelcomeMessage();
                    this.startMessagePolling();
                    this.addSystemMessage('Conversation started! A staff member will be with you shortly.');
                    return true;
                }
            } catch (error) {
                console.error('Error starting conversation for authenticated user:', error);
            }
        }
        
        // For non-authenticated users or if authenticated method failed
        const customerName = document.getElementById('customer-name').value.trim();
        const customerEmail = document.getElementById('customer-email').value.trim();
        const customerPhone = document.getElementById('customer-phone').value.trim();
        const subject = document.getElementById('conversation-subject').value.trim();
        
        // Validate required fields
        if (!customerName || !customerEmail) {
            this.showError('Please provide your name and email to start a conversation.');
            return false;
        }
        
        // Validate email format
        if (!this.isValidEmail(customerEmail)) {
            this.showError('Please provide a valid email address.');
            return false;
        }
        
        try {
            this.showLoading('Starting conversation...');
            
            const response = await this.makeRequest('/chat/start-conversation/', {
                method: 'POST',
                body: JSON.stringify({
                    customer_name: customerName,
                    customer_email: customerEmail,
                    customer_phone: customerPhone,
                    subject: subject || 'General Inquiry'
                })
            });
            
            if (response.success) {
                this.conversationId = response.conversation_id;
                this.hideCustomerInfoForm();
                this.hideWelcomeMessage();
                this.startMessagePolling();
                this.addSystemMessage('Conversation started! A staff member will be with you shortly.');
                this.hideLoading();
                return true;
            } else {
                this.hideLoading();
                this.showError(response.error || 'Error starting conversation. Please try again.');
                return false;
            }
        } catch (error) {
            this.hideLoading();
            console.error('Error starting conversation:', error);
            this.showError('Error starting conversation. Please try again.');
            return false;
        }
    }
    
    async sendMessage() {
        const content = this.messageInput.value.trim();
        
        if (!content) return;
        
        // If no conversation exists, always try to start one
        if (!this.conversationId) {
            const started = await this.startConversation();
            if (!started) return;
        }
        
        if (!this.conversationId) {
            this.showError('Please start a conversation first.');
            return;
        }
        
        try {
            // Add message to UI immediately for better UX
            this.addMessage(content, 'customer');
            this.messageInput.value = '';
            this.autoResizeTextarea();
            this.stopTyping();
            
            const response = await this.makeRequest('/chat/send-message/', {
                method: 'POST',
                body: JSON.stringify({
                    conversation_id: this.conversationId,
                    content: content,
                    message_type: 'text'
                })
            });
            
            if (!response.success) {
                this.showError(response.error || 'Error sending message. Please try again.');
                // Remove the message from UI if sending failed
                this.removeLastMessage();
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.showError('Error sending message. Please try again.');
            this.removeLastMessage();
        }
    }
    
    async loadMessages() {
        if (!this.conversationId) return;
        
        try {
            const response = await this.makeRequest(`/chat/messages/${this.conversationId}/`);
            
            if (response.success) {
                this.renderMessages(response.messages);
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }
    
    renderMessages(messages) {
        // Clear existing messages except welcome message
        const existingMessages = this.messagesContainer.querySelectorAll('.message');
        existingMessages.forEach(msg => msg.remove());
        
        messages.forEach(message => {
            this.addMessage(
                message.content, 
                message.is_from_customer ? 'customer' : 'staff', 
                message.created_at,
                message.sender_display_name
            );
        });
    }
    
    addMessage(content, sender, timestamp = null, senderName = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender} p-3 mb-2 fade-in`;
        
        const time = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
        
        let messageHtml = '';
        
        if (senderName && sender === 'staff') {
            messageHtml += `<div class="message-sender">${this.escapeHtml(senderName)}</div>`;
        }
        
        messageHtml += `
            <div class="message-content">${this.escapeHtml(content)}</div>
            <div class="message-time">${time}</div>
        `;
        
        messageDiv.innerHTML = messageHtml;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addSystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system p-3 mb-2 text-sm fade-in';
        messageDiv.textContent = content;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    removeLastMessage() {
        const messages = this.messagesContainer.querySelectorAll('.message');
        if (messages.length > 0) {
            messages[messages.length - 1].remove();
        }
    }
    
    handleTyping() {
        if (!this.isTyping) {
            this.isTyping = true;
            // Send typing indicator to server (if implemented)
        }
        
        clearTimeout(this.typingTimeout);
        this.typingTimeout = setTimeout(() => {
            this.stopTyping();
        }, 1000);
    }
    
    stopTyping() {
        this.isTyping = false;
        // Send stop typing indicator to server (if implemented)
    }
    
    startMessagePolling() {
        if (this.messageCheckInterval) {
            clearInterval(this.messageCheckInterval);
        }
        
        this.messageCheckInterval = setInterval(() => {
            if (this.conversationId) {
                this.loadMessages();
            }
        }, 3000); // Check for new messages every 3 seconds
    }
    
    stopMessagePolling() {
        if (this.messageCheckInterval) {
            clearInterval(this.messageCheckInterval);
            this.messageCheckInterval = null;
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 100) + 'px';
    }
    
    hideCustomerInfoForm() {
        if (this.customerInfoForm) {
            this.customerInfoForm.classList.add('hidden');
        }
    }
    
    hideWelcomeMessage() {
        if (this.welcomeMessage) {
            this.welcomeMessage.classList.add('hidden');
        }
    }
    
    hideChatWidget() {
        if (this.toggleBtn) {
            this.toggleBtn.style.display = 'none';
        }
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showLoading(message) {
        this.showNotification(message, 'loading');
    }
    
    hideLoading() {
        const loading = this.messagesContainer.querySelector('.chat-loading');
        if (loading) {
            loading.remove();
        }
    }
    
    showNotification(message, type) {
        // Remove existing notifications
        const existingNotifications = this.messagesContainer.querySelectorAll('.chat-error, .chat-success, .chat-loading');
        existingNotifications.forEach(notification => notification.remove());
        
        const notificationDiv = document.createElement('div');
        notificationDiv.className = `chat-${type} fade-in`;
        
        if (type === 'loading') {
            notificationDiv.innerHTML = `
                <i class="fas fa-spinner"></i>
                ${message}
            `;
        } else {
            notificationDiv.textContent = message;
        }
        
        this.messagesContainer.appendChild(notificationDiv);
        this.scrollToBottom();
        
        // Auto-remove error/success notifications after 5 seconds
        if (type === 'error' || type === 'success') {
            setTimeout(() => {
                if (notificationDiv.parentNode) {
                    notificationDiv.remove();
                }
            }, 5000);
        }
    }
    
    async makeRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.retryCount = 0; // Reset retry count on success
            return data;
            
        } catch (error) {
            console.error('Request failed:', error);
            
            // Retry logic for network errors
            if (this.retryCount < this.maxRetries && error.name === 'TypeError') {
                this.retryCount++;
                console.log(`Retrying request (${this.retryCount}/${this.maxRetries})...`);
                await this.delay(1000 * this.retryCount); // Exponential backoff
                return this.makeRequest(url, options);
            }
            
            throw error;
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    isUserAuthenticated() {
        // Check if user is authenticated (implement based on your auth system)
        return document.body.classList.contains('user-authenticated') || 
               window.location.pathname.includes('/dashboard/') ||
               document.querySelector('[data-user-authenticated]') !== null;
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    getCSRFToken() {
        // Try multiple methods to get CSRF token
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) return csrfInput.value;
        
        const csrfMeta = document.querySelector('meta[name=csrf-token]');
        if (csrfMeta) return csrfMeta.getAttribute('content');
        
        // Try to get from cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') return value;
        }
        
        return '';
    }
    
    // Public methods for external access
    openChatWidget() {
        if (!this.isOpen) {
            this.openChat();
        }
    }
    
    closeChatWidget() {
        if (this.isOpen) {
            this.closeChat();
        }
    }
    
    isChatOpen() {
        return this.isOpen;
    }
    
    getConversationId() {
        return this.conversationId;
    }
}

// Initialize chat widget when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if chat widget elements exist
    if (document.getElementById('chat-widget')) {
        window.liveChatWidget = new LiveChatWidget();
        
        // Expose global methods for external access
        window.openChat = () => window.liveChatWidget?.openChatWidget();
        window.closeChat = () => window.liveChatWidget?.closeChatWidget();
        window.isChatOpen = () => window.liveChatWidget?.isChatOpen();
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (window.liveChatWidget) {
        if (document.hidden) {
            // Page is hidden, stop polling to save resources
            window.liveChatWidget.stopMessagePolling();
        } else {
            // Page is visible, resume polling
            if (window.liveChatWidget.isOpen && window.liveChatWidget.conversationId) {
                window.liveChatWidget.startMessagePolling();
            }
        }
    }
});

// Handle beforeunload to clean up
window.addEventListener('beforeunload', function() {
    if (window.liveChatWidget) {
        window.liveChatWidget.stopMessagePolling();
    }
});
