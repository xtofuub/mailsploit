#!/usr/bin/env python3
"""
Email Spoofing Demonstration
This script demonstrates email spoofing techniques for educational purposes only.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import argparse
import sys

def send_spoofed_email(smtp_server, smtp_port, username, password, 
                      from_name, from_email, 
                      to_email, subject, message):
    """
    Send an email with spoofed headers.
    
    Args:
        smtp_server (str): SMTP server address
        smtp_port (int): SMTP server port
        username (str): SMTP authentication username
        password (str): SMTP authentication password
        from_name (str): Display name for the spoofed sender
        from_email (str): Email address shown as the sender
        to_email (str): Recipient's email address
        subject (str): Email subject
        message (str): Email body content
    """
    # Create message container
    msg = MIMEMultipart('alternative')
    
    # Set headers - this is where the spoofing happens
    msg['Subject'] = subject
    msg['From'] = formataddr((from_name, from_email))
    msg['To'] = to_email
    
    # Attach message body
    msg.attach(MIMEText(message, 'html'))
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        # Login to SMTP server
        server.login(username, password)
        
        # Send email
        server.sendmail(username, to_email, msg.as_string())
        print(f"[+] Email sent successfully to {to_email}")
        
        # Disconnect from server
        server.quit()
        
    except Exception as e:
        print(f"[-] Error: {e}")
        return False
    
    return True

def main():
    """Parse command line arguments and send spoofed email."""
    parser = argparse.ArgumentParser(description='Email Spoofing Tool')
    
    # SMTP Settings
    parser.add_argument('--server', required=True, help='SMTP server address')
    parser.add_argument('--port', type=int, default=587, help='SMTP server port (default: 587)')
    parser.add_argument('--user', required=True, help='SMTP username')
    parser.add_argument('--password', required=True, help='SMTP password')
    
    # Spoofing Parameters
    parser.add_argument('--from-name', required=True, help='Spoofed sender name')
    parser.add_argument('--from-email', required=True, help='Spoofed sender email')
    parser.add_argument('--to', required=True, help='Recipient email')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--message', required=True, help='Email message (HTML supported)')
    
    args = parser.parse_args()
    
    print("[*] Email Spoofing Demonstration")
    print("[*] Note: This tool is for educational purposes only")
    print(f"[*] Sending spoofed email from {args.from_name} <{args.from_email}> to {args.to}")
    
    send_spoofed_email(
        args.server, args.port, args.user, args.password,
        args.from_name, args.from_email,
        args.to, args.subject, args.message
    )

if __name__ == "__main__":
    print("=" * 60)
    print("       EMAIL SPOOFING DEMONSTRATION TOOL")
    print("       FOR EDUCATIONAL PURPOSES ONLY")
    print("=" * 60)
    
    main() 