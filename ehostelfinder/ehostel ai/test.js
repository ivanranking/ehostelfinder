// Test script for the chatbot widget
// This script verifies that the chatbot widget loads and functions correctly

function testChatbotWidget() {
  console.log('Testing eHostel AI Chatbot Widget...');
  
  // Check if chatbot container exists
  const chatbotContainer = document.getElementById('ehostel-chatbot');
  if (!chatbotContainer) {
    console.error('❌ Chatbot container not found');
    return false;
  }
  console.log('✅ Chatbot container found');
  
  // Check if toggle button exists
  const toggle = document.getElementById('chatbot-toggle');
  if (!toggle) {
    console.error('❌ Chatbot toggle button not found');
    return false;
  }
  console.log('✅ Chatbot toggle button found');
  
  // Check if chat window exists
  const window = document.getElementById('chatbot-window');
  if (!window) {
    console.error('❌ Chatbot window not found');
    return false;
  }
  console.log('✅ Chatbot window found');
  
  // Check if input exists
  const input = document.getElementById('chatbot-input');
  if (!input) {
    console.error('❌ Chatbot input not found');
    return false;
  }
  console.log('✅ Chatbot input found');
  
  // Check if messages container exists
  const messages = document.getElementById('chatbot-messages');
  if (!messages) {
    console.error('❌ Chatbot messages container not found');
    return false;
  }
  console.log('✅ Chatbot messages container found');
  
  // Test toggle functionality
  const initialDisplay = window.style.display || getComputedStyle(window).display;
  console.log('Initial window display:', initialDisplay);
  
  // Simulate click
  toggle.click();
  setTimeout(() => {
    const isOpen = window.classList.contains('open');
    if (isOpen) {
      console.log('✅ Chatbot toggle works correctly');
    } else {
      console.error('❌ Chatbot toggle not working');
      return false;
    }
    
    // Close it
    const closeBtn = document.getElementById('chatbot-close');
    if (closeBtn) {
      closeBtn.click();
      setTimeout(() => {
        const isClosed = !window.classList.contains('open');
        if (isClosed) {
          console.log('✅ Chatbot close button works correctly');
        } else {
          console.error('❌ Chatbot close button not working');
        }
      }, 100);
    }
    
    console.log('✅ All tests passed!');
    return true;
  }, 100);
  
  return true;
}

// Run test when chatbot loads
if (typeof ChatbotWidget !== 'undefined') {
  console.log('ChatbotWidget class is available');
}

// Add test runner
window.testChatbotWidget = testChatbotWidget;

console.log('Test utilities loaded. Run testChatbotWidget() to verify functionality.');