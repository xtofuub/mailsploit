<div align="center">
  <img width="200" height="200" alt="favicon" src="https://github.com/user-attachments/assets/7e97acdc-1d9d-4d88-9400-153b3f6ed4cf" />

  **Advanced infrastructure validation, security reconnaissance, and tactical payload engineering for enterprise mail systems.**

  [![System Audit](https://img.shields.io/badge/Security-Audit--Ready-blue?style=flat-square)](https://github.com/xtofuub/mailsploit)
  [![Compliance](https://img.shields.io/badge/Compliance-DMARC--Focused-green?style=flat-square)](https://github.com/xtofuub/mailsploit)
  [![Access](https://img.shields.io/badge/Endpoint-Port--5000-orange?style=flat-square)](http://localhost:5000)
  ![Systems Monitoring](https://api.visitorbadge.io/api/visitors?path=xtofuub%2Fmailsploit&countColor=%23263759&style=flat-square)

</div>

---

## Executive Summary

Mailsploit is a dedicated security framework designed for infrastructure auditing and email vulnerability assessment. It provides security administrators and researchers with a unified dashboard to validate domain integrity, assess risk profiles, and harden mail delivery systems against unauthorized exploitation.

By facilitating controlled security simulations and deep domain reconnaissance, Mailsploit assists organizations in identifying architectural weaknesses and enforcing global standards such as **SPF, DKIM, and DMARC**.

---

## 💻 Operating Procedures (Functional Overview)

Mailsploit is divided into distinct operational modules to streamline the security audit workflow.

### 🛡️ Transmission Audit (Send Email)
The primary interface for simulating email delivery.
* **Sender Spoofing**: Validate how mail clients render spoofed envelopes and from-addresses.
* **Attachment Analysis**: Test filter resilience with various file types and payloads.
* **X-Header Injection**: Inject custom X-headers to evaluate header-based filtering logic.
* **Persistance**: Configurations are automatically synchronized to local storage for session continuity.

### 🔍 Intelligence Modules (Intel Menu)
* **Domain Recon**: Performs an automated security audit of any domain, specifically flagging missing or weak DMARC policies.
* **Header Parse**: Deconstructs raw email headers to identify delivery paths and calculate a security confidence score.
* **DNSBL Verification**: Checks host IPs against global blacklists to assess reputation-based filtering risk.
* **SMTP Validation**: Verifies server connection stability and protocol support (TLS/SSL).

### 🛠️ Tactical Utilities
* **Phishing Simulation**: Access pre-configured templates with OpSec guidelines for internal security training.
* **Macro Generation**: Audit VBA-based attachment risks with integrated builder tools.
* **Look-alike Testing**: Use the Homoglyph generator to identify and test against typographic squatting attacks.

---

## 🏗️ Technical Architecture

```text
mailsploit-main/
├── app.py                 # Core Flask application & API controller
├── requirements.txt       # Unified dependency manifest
├── email_template.html    # Base render for spoofed communications
├── static/                # Frontend assets
│   ├── css/style.css      # Enterprise UI design system
│   └── js/script.js       # Asynchronous bridge and tool logic
├── templates/             # HTML5 Jinja2 components
│   ├── base.html          # Global navigation & layout
│   └── index.html         # High-density tool dashboard
├── uploads/               # Secure temporary storage for audit attachments
└── smtp_servers.txt       # Configuration file for batch server testing
```

---

## 🚀 Deployment & System Access

### Prerequisites
* **Runtime**: Python 3.8+ (LTS recommended)
* **Network**: Outbound access to standard SMTP ports (25, 465, 587)

### Installation Guide
1. **Provision Environment**
   ```bash
   git clone https://github.com/xtofuub/mailsploit.git
   cd mailsploit
   ```
2. **Setup Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize Platform**
   ```bash
   python app.py
   ```

### Accessing the Interface
Once initialized, the platform is accessible via your primary browser at the following endpoint:
> [!IMPORTANT]
> **Endpoint:** `http://localhost:5000`

---

## 🔧 Maintenance & Troubleshooting

* **Conflict Resolution**: If port `5000` is occupied, update `app.run(port=XXXX)` in `app.py`.
* **Firewall Configuration**: Ensure your OS or Cloud environment permits outbound SMTP traffic. Windows environments often block these by default.
* **Debug Protocol**: For detailed logging, enable debug mode by setting `app.debug = True`.

---

## ⚖️ Corporate Disclosure & Policy

> [!CAUTION]
> **Use Case Policy:** Mailsploit is intended exclusively for authorized security auditing and professional training. The developers emphasize that any use must strictly comply with regional and international laws regarding digital security. The end-user assumes all liability for authorized and unauthorized use.

---

<div align="center">
  <sub>Optimized for Corporate Security Teams | Developed by xtofuub</sub>
</div>








