// Floating Chatbot Widget
class ChatbotWidget {
  constructor() {
    this.isOpen = false;
    this.messages = [];
    this.init();
  }

  init() {
    this.createWidget();
    this.attachEventListeners();
  }

  createWidget() {
    // Create main chatbot container
    const container = document.createElement('div');
    container.id = 'ehostel-chatbot';
    container.innerHTML = `
      <!-- Chatbot Toggle Button -->
      <div class="chatbot-toggle" id="chatbot-toggle">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <span class="chatbot-badge" id="chatbot-badge" style="display:none;">0</span>
      </div>

      <!-- Chatbot Window -->
      <div class="chatbot-window" id="chatbot-window">
        <div class="chatbot-header">
          <h3>eHostel AI Assistant</h3>
          <button class="chatbot-close" id="chatbot-close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <div class="chatbot-messages" id="chatbot-messages">
          <div class="message bot-message">
            <div class="message-content">
              Hello! I'm your eHostel AI assistant. How can I help you today?
            </div>
          </div>
        </div>

        <div class="chatbot-input-container">
          <textarea 
            class="chatbot-input" 
            id="chatbot-input" 
            placeholder="Type your message here..." 
            rows="1"
          ></textarea>
          <button class="chatbot-send" id="chatbot-send">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22,2 15,22 11,13 2,9"></polygon>
            </svg>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(container);

    // Style element
    const style = document.createElement('style');
    style.textContent = `
      #ehostel-chatbot {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
      }

      .chatbot-toggle {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        color: white;
        position: relative;
      }

      .chatbot-toggle:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
      }

      .chatbot-toggle svg {
        width: 24px;
        height: 24px;
      }

      .chatbot-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background: #ff4757;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        font-size: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulse 2s infinite;
      }

      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }

      .chatbot-window {
        width: 380px;
        max-width: 90vw;
        background: white;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        display: none;
        position: absolute;
        bottom: 80px;
        right: 0;
        flex-direction: column;
        max-height: 500px;
        animation: slideUp 0.3s ease;
      }

      .chatbot-window.open {
        display: flex;
      }

      @keyframes slideUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .chatbot-header h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }

      .chatbot-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 5px;
        border-radius: 50%;
        transition: background 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .chatbot-close:hover {
        background: rgba(255, 255, 255, 0.2);
      }

      .chatbot-messages {
        flex: 1;
        padding: 20px;
        overflow-y: auto;
        max-height: 350px;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .message {
        display: flex;
        flex-direction: column;
        max-width: 80%;
      }

      .message.user-message {
        align-self: flex-end;
      }

      .message.bot-message {
        align-self: flex-start;
      }

      .message-content {
        padding: 12px 16px;
        border-radius: 18px;
        line-height: 1.5;
        word-wrap: break-word;
      }

      .user-message .message-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 5px;
      }

      .bot-message .message-content {
        background: #f0f0f0;
        color: #333;
        border-bottom-left-radius: 5px;
      }

      .message-time {
        font-size: 11px;
        color: #999;
        margin-top: 4px;
        padding: 0 4px;
      }

      .chatbot-input-container {
        display: flex;
        padding: 16px;
        border-top: 1px solid #e0e0e0;
        gap: 10px;
        background: white;
      }

      .chatbot-input {
        flex: 1;
        border: 1px solid #ddd;
        border-radius: 20px;
        padding: 10px 16px;
        font-size: 14px;
        resize: none;
        max-height: 100px;
        min-height: 20px;
        outline: none;
        transition: border-color 0.2s;
      }

      .chatbot-input:focus {
        border-color: #667eea;
      }

      .chatbot-send {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 50%;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s, box-shadow 0.2s;
      }

      .chatbot-send:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
      }

      .chatbot-send:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      .chatbot-send svg {
        width: 18px;
        height: 18px;
        margin-left: 2px;
      }

      /* Responsive */
      @media (max-width: 480px) {
        #ehostel-chatbot {
          bottom: 15px;
          right: 15px;
        }

        .chatbot-toggle {
          width: 50px;
          height: 50px;
        }

        .chatbot-window {
          bottom: 70px;
        }

        .chatbot-messages {
          max-height: 300px;
        }
      }
    `;
    document.head.appendChild(style);
  }

  attachEventListeners() {
    const toggle = document.getElementById('chatbot-toggle');
    const close = document.getElementById('chatbot-close');
    const window = document.getElementById('chatbot-window');
    const input = document.getElementById('chatbot-input');
    const send = document.getElementById('chatbot-send');
    const messages = document.getElementById('chatbot-messages');
    const badge = document.getElementById('chatbot-badge');

    // Toggle chatbot
    toggle.addEventListener('click', () => {
      this.toggleChatbot();
    });

    // Close button
    close.addEventListener('click', () => {
      this.closeChatbot();
    });

    // Send message on button click
    send.addEventListener('click', () => {
      this.sendMessage();
    });

    // Send message on Enter key (without Shift)
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Auto-resize textarea
    input.addEventListener('input', () => {
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    });

    // Close on outside click (optional, can be removed)
    window.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }

  toggleChatbot() {
    const window = document.getElementById('chatbot-window');
    const badge = document.getElementById('chatbot-badge');
    
    if (this.isOpen) {
      this.closeChatbot();
    } else {
      this.openChatbot();
      badge.style.display = 'none';
      badge.textContent = '0';
    }
  }

  openChatbot() {
    document.getElementById('chatbot-window').classList.add('open');
    this.isOpen = true;
    document.getElementById('chatbot-input').focus();
  }

  closeChatbot() {
    document.getElementById('chatbot-window').classList.remove('open');
    this.isOpen = false;
  }

  addMessage(content, isUser = false) {
    const messages = document.getElementById('chatbot-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const time = new Date().toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
      <div class="message-content">${this.escapeHtml(content)}</div>
      <div class="message-time">${time}</div>
    `;
    
    messages.appendChild(messageDiv);
    
    // Scroll to bottom
    messages.scrollTop = messages.scrollHeight;
  }

  async sendMessage() {
    const input = document.getElementById('chatbot-input');
    const message = input.value.trim();
    const sendBtn = document.getElementById('chatbot-send');

    if (!message) return;

    // Add user message
    this.addMessage(message, true);
    input.value = '';
    input.style.height = 'auto';

    // Disable send button while processing
    sendBtn.disabled = true;

    // Add typing indicator
    const typingMessage = this.addTypingIndicator();

    try {
      // Call the AI API
      const response = await fetch(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AIzaSyDST-CssEljn9b57fxyLzxPSsDvW3udlmA",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            contents: [
              {
                parts: [
                  {
                    text: `You are a helpful eHostel assistant. Answer questions about hostel services, bookings, amenities, and policies. Be friendly and concise. Question: ${message}`
                  }
                ]
              }
            ]
          })
        }
      );

      const data = await response.json();
      const aiText = data.candidates[0].content.parts[0].text;

      // Remove typing indicator
      typingMessage.remove();

      // Add bot response
      this.addMessage(aiText, false);

    } catch (error) {
      // Remove typing indicator
      typingMessage.remove();

      console.error(error);
      this.addMessage("Sorry, I'm having trouble connecting to the AI service. Please try again later.", false);
    } finally {
      sendBtn.disabled = false;
    }
  }

  addTypingIndicator() {
    const messages = document.getElementById('chatbot-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.innerHTML = `
      <div class="message-content">
        <div style="display: flex; gap: 5px; padding: 5px 0;">
          <div style="width: 8px; height: 8px; background: #999; border-radius: 50%; animation: typing 1.4s infinite ease-in-out both;"></div>
          <div style="width: 8px; height: 8px; background: #999; border-radius: 50%; animation: typing 1.4s infinite ease-in-out both; animation-delay: 0.2s;"></div>
          <div style="width: 8px; height: 8px; background: #999; border-radius: 50%; animation: typing 1.4s infinite ease-in-out both; animation-delay: 0.4s;"></div>
        </div>
      </div>
    `;
    messages.appendChild(typingDiv);
    messages.scrollTop = messages.scrollHeight;
    
    // Add typing animation to styles if not exists
    if (!document.getElementById('typing-animation')) {
      const style = document.createElement('style');
      style.id = 'typing-animation';
      style.textContent = `
        @keyframes typing {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1.0); }
        }
      `;
      document.head.appendChild(style);
    }

    return typingDiv;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Increment unread message badge
  incrementBadge() {
    const badge = document.getElementById('chatbot-badge');
    if (badge) {
      const current = parseInt(badge.textContent) || 0;
      badge.textContent = current + 1;
      badge.style.display = 'flex';
    }
  }
}

// Initialize chatbot when DOM is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new ChatbotWidget();
  });
} else {
  new ChatbotWidget();
}

// Optional: Expose globally for manual control
window.ehostelChatbot = {
  open: () => {
    const chatbot = document.querySelector('#ehostel-chatbot');
    if (chatbot) {
      document.getElementById('chatbot-window').classList.add('open');
    }
  },
  close: () => {
    const chatbot = document.querySelector('#ehostel-chatbot');
    if (chatbot) {
      document.getElementById('chatbot-window').classList.remove('open');
    }
  },
  addMessage: (content, isUser = false) => {
    const chatbot = document.querySelector('#ehostel-chatbot');
    if (chatbot && window.chatbotInstance) {
      window.chatbotInstance.addMessage(content, isUser);
    }
  }
};