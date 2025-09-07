# 🛡️ Email Spoofing Security Project  

[![Python](https://img.shields.io/badge/python-3.7%2B-blue?logo=python)](https://www.python.org/) 
[![License](https://img.shields.io/badge/license-Educational-green)](LICENSE) 
[![Educational Use](https://img.shields.io/badge/Use-Educational-yellow)](https://github.com/) 
[![Status](https://img.shields.io/badge/status-Active-brightgreen)](https://github.com/)  

A modern **security-focused web application** designed to test whether a website or domain is vulnerable to **email spoofing**.  
This tool demonstrates advanced spoofing techniques **strictly for educational and research purposes**.  

It provides a **user-friendly web interface** on top of the original command-line email spoofing utility, making it easier to:  
- Perform spoofing tests in a controlled environment  
- Analyze results and identify potential risks  
- Understand vulnerabilities and how to mitigate them  

By simulating spoofing attempts safely, this project helps raise awareness about email security and encourages implementing proper defenses such as **SPF, DKIM, and DMARC**.

---

## ⚠️ Disclaimer
> [!WARNING]
>**For educational and security purpose only!**  
>The developers are **not responsible for any misuse** of this application. Email spoofing can be illegal and should only be used for **authorized testing, learning, or security research**.

---

## 🌐 User Interface
<img width="1471" height="745" alt="image" src="https://github.com/user-attachments/assets/a156daa1-41d5-4740-b585-94d536d68d91" />


The tool includes a built-in scanning feature that analyzes a domain or website to quickly identify if it is vulnerable to spoofing.  
After scanning, it provides **clear results** and **actionable recommendations** to help users improve email security.



## 🚀 Features

- **Modern Web Interface**: Clean, responsive design using Bootstrap 5  
- **Email Spoofing**: Send emails with spoofed sender information  
- **SMTP Testing**: Test individual SMTP server connections  
- **Batch Server Testing**: Test multiple SMTP servers from a file  
- **File Attachments**: Supports various file types  
- **Custom Headers**: Add custom email headers  
- **X-Headers Spoofing**: Add fake X-headers to improve spoof legitimacy  
- **Real-time Validation**: Form validation with visual feedback  
- **Auto-save**: Automatically saves form data to `localStorage`  
- **Responsive Design**: Works on desktop and mobile devices  

---

## 📋 Requirements

- Python 3.7+  
- Flask 2.3.3  
- SMTP server credentials  

---

## 🛠️ Installation
> [!CAUTION]
> **Recommendation:** For best results, run this application on **Linux** or **Google Cloud Shell**.  
> Running on Windows may block SMTP connections due to OS-level restrictions or firewall rules.

1. **Clone the repository**
```bash
git clone https://github.com/xtofuub/mailsploit.git
cd mailsploit
````

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the application**

```bash
python app.py
```

4. **Access the web interface**
   Open your browser and navigate to `http://localhost:5000`



---
## 📁 Project Structure

```
email-spoofing-web/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   └── index.html         # Main page template
├── static/                # Static files
│   ├── css/
│   │   └── style.css      # Custom CSS styles
│   └── js/
│       └── script.js      # JavaScript functionality
└── uploads/               # Temporary file uploads (auto-created)
```

---

## 🎯 Usage

### Send Email Tab

* Configure SMTP settings
* Set spoofed sender information
* Add TO, CC, BCC recipients
* Write email subject and body
* Add attachments or custom headers
* Enable X-Headers spoofing

### Test Connection Tab

* Test single SMTP server connections
* Verify credentials before sending emails

### Test Servers Tab

* Upload multiple SMTP servers (`host|port|username|password`)
* Test all servers and view working connections

---

## 📝 SMTP Server File Format

```
smtp.gmail.com|587|your-email@gmail.com|your-password
smtp.outlook.com|587|your-email@outlook.com|your-password
smtp.yahoo.com|587|your-email@yahoo.com|your-password
```

---

## 🔧 Configuration

### Environment Variables

* `FLASK_ENV`: `development` for debug mode
* `SECRET_KEY`: Change for production

### Security Notes

* Change `SECRET_KEY` in `app.py` for production
* Runs on all interfaces (`0.0.0.0`) by default
* File uploads limited to 16MB; only allowed file types

---

## 🎨 Customization

* **Styling**: Modify `static/css/style.css` or use Bootstrap variables
* **Functionality**: Extend `app.py`, `script.js`, or HTML templates

---

## 🐛 Troubleshooting

* **Port in use**: Change port in `app.py` (`app.run(port=5001)`)
* **File upload errors**: Check size/type and ensure `uploads/` exists
* **SMTP connection issues**: Verify credentials, 2FA, and server access
* **Template not found**: Ensure `templates/` directory exists

Enable debug mode:

```python
app.run(debug=True)
```

---

## 📚 Educational Use Cases

* Security research & learning about spoofing techniques
* Penetration testing of email security measures
* Raising awareness about email protocol vulnerabilities

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes & test thoroughly
4. Submit a pull request

---

## 📄 License

**Educational purposes only.** Use responsibly and legally.

---

## 🔗 Original Tool

Based on the command-line email spoofing tool developed by Triotion.

---

**Remember: Use responsibly and only for legitimate educational purposes!**




