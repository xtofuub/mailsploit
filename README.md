# Advanced Email Spoofing Web Application

A modern web application that demonstrates advanced email spoofing techniques for educational purposes only. This tool provides a user-friendly web interface for the original command-line email spoofing tool.

## ⚠️ DISCLAIMER

**This tool is for educational purposes only!** The developers are not responsible for any misuse of this application. Email spoofing can be used for malicious purposes, and users should only use this tool for legitimate educational, testing, or security research purposes.

## 🚀 Features

- **Modern Web Interface**: Clean, responsive design with Bootstrap 5
- **Email Spoofing**: Send emails with spoofed sender information
- **SMTP Testing**: Test individual SMTP server connections
- **Batch Server Testing**: Test multiple SMTP servers from a file
- **File Attachments**: Support for various file types
- **Custom Headers**: Add custom email headers
- **X-Headers Spoofing**: Add fake X-headers for legitimacy
- **Real-time Validation**: Form validation with visual feedback
- **Auto-save**: Form data is automatically saved to localStorage
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Requirements

- Python 3.7 or higher
- Flask 2.3.3
- SMTP server credentials

## 🛠️ Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd email-spoofing-web
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the web interface**
   Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
email-spoofing-web/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   └── index.html        # Main page template
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom CSS styles
│   └── js/
│       └── script.js     # JavaScript functionality
└── uploads/              # Temporary file uploads (auto-created)
```

## 🎯 Usage

### 1. Send Email Tab

- **SMTP Settings**: Configure your SMTP server details
- **Email Settings**: Set the spoofed sender information
- **Recipients**: Add TO, CC, and BCC recipients
- **Message Content**: Write your email subject and body
- **Advanced Options**: Add attachments and custom headers
- **X-Headers**: Enable fake X-headers for legitimacy

### 2. Test Connection Tab

- Test individual SMTP server connections
- Verify credentials before sending emails
- SMTP settings are automatically copied from the Send Email tab

### 3. Test Servers Tab

- Upload a text file with multiple SMTP servers
- Format: `host|port|username|password` (one per line)
- Test all servers and see which ones work
- Results show working servers with connection details

## 📝 SMTP Server File Format

Create a text file with your SMTP servers in the following format:

```
smtp.gmail.com|587|your-email@gmail.com|your-password
smtp.outlook.com|587|your-email@outlook.com|your-password
smtp.yahoo.com|587|your-email@yahoo.com|your-password
```

## 🔧 Configuration

### Environment Variables

You can set the following environment variables:

- `FLASK_ENV`: Set to `development` for debug mode
- `SECRET_KEY`: Change the secret key for production

### Security Notes

- Change the `SECRET_KEY` in `app.py` for production use
- The application runs on all interfaces (`0.0.0.0`) by default
- File uploads are limited to 16MB
- Only specific file types are allowed for attachments

## 🎨 Customization

### Styling

- Modify `static/css/style.css` for custom styling
- The application uses Bootstrap 5 for the base framework
- Custom CSS variables can be added for easy theming

### Functionality

- Add new features by modifying `app.py`
- Extend the JavaScript functionality in `static/js/script.js`
- Modify HTML templates in the `templates/` directory

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `app.py`: `app.run(port=5001)`

2. **File upload errors**
   - Check file size (max 16MB)
   - Verify file type is allowed
   - Ensure uploads directory exists

3. **SMTP connection errors**
   - Verify server credentials
   - Check if 2FA is enabled (use app passwords)
   - Ensure server allows SMTP connections

4. **Template not found errors**
   - Ensure `templates/` directory exists
   - Check file permissions

### Debug Mode

Enable debug mode by setting:
```python
app.run(debug=True)
```

## 📚 Educational Use Cases

- **Security Research**: Understanding email spoofing techniques
- **Penetration Testing**: Testing email security measures
- **Educational Purposes**: Learning about email protocols
- **Security Awareness**: Demonstrating email vulnerabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes only. Use responsibly and in accordance with applicable laws and regulations.

## ⚖️ Legal Notice

The developers of this tool are not responsible for any misuse. Users must comply with all applicable laws and regulations when using this software. Email spoofing for malicious purposes is illegal in most jurisdictions.

## 🔗 Original Tool

This web application is based on the original command-line email spoofing tool developed by Triotion.

---

**Remember: Use this tool responsibly and only for legitimate educational purposes!**
