async function askAI() {
  const question = document.getElementById("question").value;
  const responseBox = document.getElementById("response");

  if (!question.trim()) {
    responseBox.innerHTML = "Please enter a question.";
    return;
  }

  responseBox.innerHTML = "<div class='typing-indicator'><span></span><span></span><span></span></div>";

  try {
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
                  text: `You are a helpful hostel assistant. Answer questions about hostel services, bookings, and amenities. Be friendly and concise. Question: ${question}`
                }
              ]
            }
          ]
        })
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (data.candidates && data.candidates[0] && data.candidates[0].content) {
      const aiText = data.candidates[0].content.parts[0].text;
      responseBox.innerHTML = formatResponse(aiText);
    } else {
      throw new Error("Invalid response from AI");
    }
  } catch (error) {
    console.error("AI Error:", error);
    responseBox.innerHTML = `
      <div class="error-message">
        <strong>Connection Error</strong>
        <p>Sorry, we couldn't connect to the AI service.</p>
        <p><small>${error.message}</small></p>
      </div>
    `;
  }
}

function formatResponse(text) {
  // Format the response with proper line breaks and paragraphs
  return text
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^(.+)$/, '<p>$1</p>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
}

// Enhanced version with keyboard support
function handleKeyPress(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    askAI();
  }
}

// Add auto-resize to textarea
document.addEventListener('DOMContentLoaded', function() {
  const textarea = document.getElementById('question');
  if (textarea) {
    textarea.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
    });
  }
});