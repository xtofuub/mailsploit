# Advanced Email Spoofing Demonstration

This repository contains Python scripts that demonstrate how email spoofing works for **educational purposes only**. Email spoofing is a technique used to forge email headers so that messages appear to originate from someone other than the actual sender.

[![GitHub](https://img.shields.io/badge/github-Triotion-blue?style=flat&logo=github)](https://github.com/Triotion/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

## ⚠️ Disclaimer

**This tool is meant for educational purposes only.** Using this tool to send deceptive emails without consent is:

- **Illegal** in most jurisdictions
- **Unethical**
- May violate terms of service for email providers
- Could result in your IP/account being blacklisted

The author assumes no responsibility for any misuse of this information or script.

## Features

- Basic email spoofing with custom From header
- Advanced header manipulation
- Custom X-header generation
- Support for multiple recipients (To, CC, BCC)
- File attachments
- Reply-To address customization
- HTML email templates
- Debug mode for troubleshooting
- Bulk testing of SMTP servers from a file
- Multi-threaded SMTP server testing
- Colorized console output

## Requirements

- Python 3.6 or later
- Required Python packages:
  - colorama
- Access to an SMTP server (most email providers will require authentication)
- SMTP server that allows header manipulation (many public email services now block this)

## Installation

```bash
git clone https://github.com/Triotion/email-spoofing.git
cd email-spoofing
pip install colorama
```

## Basic Usage

```bash
python email_spoofer.py --server smtp.example.com --port 587 --user your_email@example.com --password your_password --from-name "Spoofed Name" --from-email spoofed@example.com --to recipient@example.com --subject "Test Subject" --message "<h1>This is a test</h1><p>This email demonstrates spoofing.</p>"
```

### Using SMTP Server File

You can provide multiple SMTP servers in a file and the script will test them all to find working ones:

```bash
python advanced_email_spoofer.py --smtp-file smtp_servers.txt --from-name "Spoofed Name" --from-email spoofed@example.com --to recipient@example.com --subject "Test Subject" --message "This is a test message"
```

The SMTP server file format is simple:
```
host|port|username|password
```

For example:
```
smtp.example.com|587|user@example.com|password123
smtp.another.com|465|admin@another.com|securepass
```

### Advanced SMTP Testing 

You can test which SMTP servers are working without sending emails:

```bash
python advanced_email_spoofer.py --smtp-file smtp_servers.txt --test-only --threads 10
```

This will:
1. Test all SMTP servers in the file
2. Use 10 threads to speed up the testing process
3. Show which servers are working
4. Exit without sending any emails

### Command Line Arguments

#### SMTP Settings:
- `--server`: SMTP server address
- `--port`: SMTP server port (default: 587)
- `--user`: SMTP username (typically your real email)
- `--password`: SMTP password
- `--smtp-file`: File containing SMTP credentials in format "host|port|username|password"
- `--test-only`: Only test SMTP servers, don't send emails
- `--threads`: Number of threads for testing SMTP servers (default: 5)
- `--debug`: SMTP debug level (0-2)

#### Spoofing Parameters:
- `--from-name`: Display name you want to show as the sender
- `--from-email`: Email address you want to show as the sender
- `--reply-to`: Reply-to email address
- `--to`: Recipient email(s), comma separated
- `--cc`: CC recipient(s), comma separated
- `--bcc`: BCC recipient(s), comma separated
- `--subject`: Email subject
- `--message`: Email body content (HTML supported)
- `--plain-text`: Send as plain text instead of HTML
- `--attach`: File(s) to attach (can be used multiple times)
- `--add-xheaders`: Add fake X-headers to make email look more legitimate
- `--custom-header`: Add custom header in format "Header:Value" (can be used multiple times)

## Usage Examples

### Basic Email Spoofing

#### Example 1: Basic spoofed email

```bash
python email_spoofer.py \
  --server smtp.example.com \
  --port 587 \
  --user your_real_email@example.com \
  --password your_password \
  --from-name "John Smith" \
  --from-email ceo@company.com \
  --to victim@example.com \
  --subject "Urgent: Action Required" \
  --message "Please review the attached document and respond ASAP."
```

#### Example 2: Using HTML content

```bash
python email_spoofer.py \
  --server smtp.example.com \
  --port 587 \
  --user your_real_email@example.com \
  --password your_password \
  --from-name "IT Department" \
  --from-email it-support@company.com \
  --to victim@example.com \
  --subject "Password Reset Required" \
  --message "<h2>Security Alert</h2><p>Your password needs to be reset. <a href='https://example.com'>Click here</a> to reset.</p>"
```

### Advanced Email Spoofing

#### Example 1: Using the HTML template

```bash
# First, read the HTML template
TEMPLATE=$(cat email_template.html)

# Then use it in the command
python advanced_email_spoofer.py \
  --server smtp.example.com \
  --port 587 \
  --user your_real_email@example.com \
  --password your_password \
  --from-name "Security Team" \
  --from-email security@trusted-company.com \
  --reply-to support@trusted-company.com \
  --to victim@example.com \
  --subject "Security Alert: Verify Your Account" \
  --message "$TEMPLATE"
```

#### Example 2: Adding custom headers and X-headers

```bash
python advanced_email_spoofer.py \
  --server smtp.example.com \
  --port 587 \
  --user your_real_email@example.com \
  --password your_password \
  --from-name "PayPal Security" \
  --from-email security@paypal.com \
  --to victim@example.com \
  --subject "Your account has been limited" \
  --message "<p>Dear customer,</p><p>Your PayPal account has been temporarily limited. Please <a href='https://example.com'>verify your information</a> to restore access.</p>" \
  --add-xheaders \
  --custom-header "List-Unsubscribe: <mailto:unsubscribe@paypal.com>" \
  --custom-header "Precedence: bulk"
```

#### Example 3: Using SMTP servers from a file

```bash
python advanced_email_spoofer.py \
  --smtp-file smtp_servers.txt \
  --from-name "HR Department" \
  --from-email hr@company.com \
  --to "employee1@example.com,employee2@example.com" \
  --cc "manager@example.com" \
  --subject "Updated Company Policy" \
  --message "<p>Please find attached the updated company policy document.</p><p>All employees must read and acknowledge by Friday.</p>" \
  --attach policy_document.pdf
```

#### Example 4: Testing SMTP servers only

```bash
python advanced_email_spoofer.py \
  --smtp-file smtp_servers.txt \
  --test-only \
  --threads 10
```

## Why This Doesn't Always Work

Modern email systems have multiple protections against spoofing:

1. **SPF (Sender Policy Framework)**: Validates if the sending server is authorized to send emails for the domain
2. **DKIM (DomainKeys Identified Mail)**: Cryptographically verifies email authenticity
3. **DMARC (Domain-based Message Authentication, Reporting & Conformance)**: Policy framework that uses SPF and DKIM results

These protections mean that while you can change the "From" header, receiving mail servers can detect that the email wasn't actually sent from the claimed domain, often marking such emails as spam or rejecting them entirely.

## Anti-Spoofing Measures

To protect yourself from email spoofing:

- Check email headers for discrepancies
- Be suspicious of unexpected emails, especially those requesting sensitive information
- Enable SPF, DKIM, and DMARC for your own domains
- Use email providers that implement strong anti-spoofing measures

## Legal Use Cases

Legitimate reasons to understand email spoofing include:

- Security research and education
- Penetration testing (with proper authorization)
- Testing your own email security systems

## Important Notes

1. Most modern email services will detect spoofed emails and mark them as spam or reject them entirely.

2. To see the email headers that were actually received, ask the recipient to view the full headers of the email.

3. For testing, it's recommended to send to email accounts you control.

4. Some email providers (like Gmail) may rewrite your From header to include your actual authenticated email, such as:
   ```
   From: "John Smith via your-email@gmail.com" <your-email@gmail.com>
   ```

## Donations

If you find this tool valuable, consider donating to support ongoing development:

- **BTC**: bc1qtkm7dzjp76gx8t9c02pshfd8rzarj6gj9yzglu
- **ETH**: 0x88Aa0E09a5A62919321f38Fb4782A17f4dc91A9B
- **XMR**: 0x6730c52B3369fD22E3ACc6090a3Ee7d5C617aBE0

## Author

Created by [@Triotion](https://github.com/Triotion/) - [Telegram](https://t.me/Triotion)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 