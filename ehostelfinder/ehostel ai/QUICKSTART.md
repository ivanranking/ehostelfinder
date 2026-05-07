# Quick Start Guide - eHostel AI Chatbot

## 🚀 Get Started in 30 Seconds

### Step 1: Add the Script
Open your website's HTML template and add this line just before `</body>`:

```html
<script src="ehostelfinder/ehostel%20ai/chatbot-widget.js" async></script>
```

### Step 2: Save and Upload
Save your changes and upload to your web server.

### Step 3: Test It!
Open your website in a browser. You should see a purple circular icon in the bottom-right corner. Click it to chat!

---

## 🎨 What It Looks Like

- **Closed State**: Purple circle with chat icon (bottom-right)
- **Open State**: 380px chat window slides up
- **On Mobile**: Adapts to screen size (responsive)

## ⚙️ Customize (Optional)

### Change Colors
Edit `chatbot-widget.js` line ~18:
```javascript
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
```
Change the hex codes to your brand colors.

### Change Position
Edit `chatbot-widget.js` line ~8:
```css
bottom: 20px;  /* Distance from bottom */
right: 20px;   /* Distance from right */
```

### Change Size
Edit `chatbot-widget.js` line ~7:
```css
width: 60px;   /* Toggle button size */
height: 60px;
```

---

## 🔧 Troubleshooting

### Chatbot Not Showing?
1. **Check the path**: Make sure `chatbot-widget.js` is in the correct folder
2. **Check console**: Press F12 and look for errors
3. **Clear cache**: Sometimes browsers cache old files

### AI Not Responding?
1. **Check API key**: Verify it's correct in the fetch URL
2. **Internet connection**: The AI requires internet access
3. **API limits**: Check if API quota is exceeded

### Wrong Position?
1. **Check CSS**: Look for conflicting z-index values
2. **Parent elements**: Make sure no parent has `overflow: hidden`
3. **Transform conflicts**: Parent transforms can affect positioning

---

## 📱 Test on Mobile

The chatbot is fully responsive, but you should test on actual devices:

- **iPhone**: Safari
- **Android**: Chrome
- **Tablets**: Both orientations

---## 💡 Tips

### Best Practices
1. **Place script before `</body>`**: Ensures all page content loads first
2. **Use async attribute**: Doesn't block page loading
3. **Test thoroughly**: Check all pages where chatbot appears
4. **Monitor usage**: Check browser console for errors

### Performance
- Script size: ~5KB (very lightweight)
- Async loading: Won't slow down your pages
- No external dependencies

### User Experience
1. **Clear icon**: Users recognize chat symbol
2. **Pulse animation**: Draws attention when badge shows
3. **Smooth animations**: Professional feel
4. **24/7 availability**: Always ready to help

---

## 🎯 Common Questions

**Q: Can I move it to the left side?**
A: Yes! Change `right: 20px` to `left: 20px` in `chatbot-widget.js`

**Q: Can I change the toggle button shape?**
A: Yes! Edit `.chatbot-toggle` in `chatbot-widget.js` (line ~7)

**Q: How do I handle API errors?**
A: The chatbot shows "Sorry, I'm having trouble connecting..." to users

**Q: Can users send attachments?**
A: Not yet, but it's a planned future feature

**Q: Is the API key secure?**
A: Currently exposed in client-side code. For production, use a server-side proxy.

---

## 📄 Files Overview

- `chatbot-widget.js` - Main widget (required)
- `script.js` - Standalone page version
- `style.css` - Standalone page styles
- `index.html` - Standalone page template
- `demo-page.html` - Live demo
- `README.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical details

---

## 🆘 Need Help?

1. **Quick test**: Open `demo-page.html` in your browser
2. **Check console**: F12 for error messages
3. **Review logs**: Look for load errors
4. **Verify path**: Ensure `chatbot-widget.js` exists

---

## ✅ Checklist

- [ ] Added script tag to HTML
- [ ] Uploaded files to server
- [ ] Tested on desktop
- [ ] Tested on mobile
- [ ] Verified positioning
- [ ] Tested AI responses
- [ ] Checked error handling
- [ ] Reviewed customization

---

**Ready to go!** 🎉

Your eHostel AI Chatbot is now integrated and ready to help users 24/7!
