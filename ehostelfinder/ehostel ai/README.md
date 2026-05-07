# eHostel AI Chatbot Integration Guide

## Overview
The eHostel AI Chatbot can be integrated into your site in two ways:
1. **Floating Widget** - A chatbot that appears as an icon in the bottom-right corner
2. **Standalone Page** - Full chat interface page

## Integration Methods

### Method 1: Floating Widget (Recommended)

Add this script tag just before the closing `</body>` tag on every page of your site:

```html
<script src="ehostelfinder/ehostel ai/chatbot-widget.js" async></script>
```

That's it! The chatbot will automatically appear on all pages with this script.

### Method 2: Standalone Page

Link directly to the chatbot page:
```html
<a href="ehostelfinder/ehostel ai/index.html">Chat with AI Assistant</a>
```

## Features

### Floating Widget
- **Position**: Fixed in bottom-right corner (20px from edges)
- **Size**: 60px circular toggle button with gradient
- **Window**: 380px wide chat interface with smooth animations
- **Features**:
  - Real-time messaging with AI
  - Message history with timestamps
  - Typing indicators
  - Unread message badge
  - Auto-resizing text input
  - Responsive design (mobile-friendly)
  - Gradient designs and smooth animations

### Standalone Page
- Full-screen chat interface
- Enhanced styling with gradients
- Supports Enter-to-send (Shift+Enter for new line)
- Auto-resizing textarea
- Typing indicators

## Customization

### Colors
The default colors use a purple gradient (#667eea to #764ba2). To customize:

1. **Floating Widget**: Edit `chatbot-widget.js` - look for `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
2. **Standalone Page**: Edit `style.css` - look for `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

### Position
To change widget position, edit `chatbot-widget.js`:
- Bottom: Modify `bottom: 20px` in `#ehostel-chatbot`
- Right: Modify `right: 20px` in `#ehostel-chatbot`

### Size
To change toggle button size:
- Width/Height: Modify `.chatbot-toggle` dimensions in `chatbot-widget.js`
- Window size: Modify `.chatbot-window` width in `chatbot-widget.js`

## API Configuration

The chatbot uses the Gemini 2.5 Flash model with the following endpoint:
```
https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
```

**Current API Key**: `AIzaSyDST-CssEljn9b57fxyLzxPSsDvW3udlmA`

### To Update API Key
1. Edit `chatbot-widget.js` - Update key in fetch URL
2. Edit `script.js` - Update key in fetch URL

## Testing

1. **Widget Test**: Open any page with the script included, click the circular icon in bottom-right
2. **Standalone Test**: Open `ehostelfinder/ehostel ai/index.html` in browser
3. **API Test**: Send a test message like "What are your check-in hours?"

## Troubleshooting

### Chatbot Not Appearing
- Check browser console for JavaScript errors
- Verify script path is correct
- Ensure no CSS conflicts (z-index issues)

### API Connection Errors
- Verify API key is valid
- Check internet connectivity
- Review browser console for CORS errors
- Ensure API endpoint is accessible

### Mobile Issues
- Test on actual mobile devices
- Check viewport meta tag is present
- Test landscape/portrait orientations

## Files

- `chatbot-widget.js` - Main floating widget implementation
- `script.js` - Standalone page functionality
- `style.css` - Standalone page styling
- `index.html` - Standalone page template
- `embed.html` - Embed code examples

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Lightweight: ~5KB minified
- No external dependencies
- Async loading
- Smooth animations (CSS-based where possible)
- Efficient DOM updates

## Security Notes

- API key is exposed in client-side code (consider server-side proxy for production)
- Uses HTTPS for all API calls
- Input sanitization to prevent XSS
- CORS-compliant API endpoints

## Future Enhancements

- [ ] Server-side API key proxy
- [ ] Message persistence (localStorage)
- [ ] Conversation history
- [ ] Multiple AI model options
- [ ] Voice input support
- [ ] File attachment capability
- [ ] Multi-language support
- [ ] Custom response templates
