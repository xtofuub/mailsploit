#!/usr/bin/env python3
"""
Advanced Email Spoofing Web Application
This web application demonstrates advanced email spoofing techniques for educational purposes only.

Developed by Triotion (https://t.me/Triotion)
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import smtplib
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

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
            server.sendmail(self.username, recipient_list, msg.as_string())
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
    
    try:
        # Check SPF record
        try:
            spf_records = dns.resolver.resolve(domain, 'TXT')
            for record in spf_records:
                record_text = str(record).strip('"')
                if record_text.startswith('v=spf1'):
                    analysis['spf']['status'] = 'present'
                    analysis['spf']['record'] = record_text
                    analysis['spf']['vulnerable'] = False
                    break
        except dns.exception.DNSException:
            pass
        
        # Check DMARC record
        try:
            dmarc_records = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
            for record in dmarc_records:
                record_text = str(record).strip('"')
                if record_text.startswith('v=DMARC1'):
                    analysis['dmarc']['status'] = 'present'
                    analysis['dmarc']['record'] = record_text

                    # Normalize lowercase for parsing
                    record_lower = record_text.lower()
                    
                    # Parse DMARC policy (p=)
                    if 'p=quarantine' in record_lower:
                        analysis['dmarc']['policy'] = 'quarantine'
                        analysis['dmarc']['vulnerable'] = False
                    elif 'p=reject' in record_lower:
                        analysis['dmarc']['policy'] = 'reject'
                        analysis['dmarc']['vulnerable'] = False
                    elif 'p=none' in record_lower:
                        analysis['dmarc']['policy'] = 'none'
                        analysis['dmarc']['vulnerable'] = True
                    else:
                        analysis['dmarc']['policy'] = 'unknown'
                        analysis['dmarc']['vulnerable'] = True

                    # Parse subdomain policy (sp=). If absent, DMARC inherits p= for subdomains.
                    if 'sp=quarantine' in record_lower:
                        analysis['dmarc']['subdomain_policy'] = 'quarantine'
                        analysis['dmarc']['subdomain_vulnerable'] = False
                    elif 'sp=reject' in record_lower:
                        analysis['dmarc']['subdomain_policy'] = 'reject'
                        analysis['dmarc']['subdomain_vulnerable'] = False
                    elif 'sp=none' in record_lower:
                        analysis['dmarc']['subdomain_policy'] = 'none'
                        analysis['dmarc']['subdomain_vulnerable'] = True
                    else:
                        # Inherit primary policy
                        analysis['dmarc']['subdomain_policy'] = analysis['dmarc']['policy']
                        analysis['dmarc']['subdomain_vulnerable'] = analysis['dmarc']['policy'] in (None, 'unknown', 'none')
                    break
        except dns.exception.DNSException:
            pass
        
        # Determine overall status
        if analysis['spf']['status'] == 'present' and analysis['dmarc']['status'] == 'present' and not analysis['dmarc']['vulnerable']:
            analysis['overall_status'] = 'secure'
            analysis['summary'] = 'Domain has proper SPF and DMARC records configured.'
        elif analysis['spf']['status'] == 'present' or analysis['dmarc']['status'] == 'present':
            analysis['overall_status'] = 'partially_secure'
            analysis['summary'] = 'Domain has some email security measures but may still be vulnerable.'
        else:
            analysis['overall_status'] = 'vulnerable'
            analysis['summary'] = 'Domain lacks proper SPF and DMARC records and is vulnerable to email spoofing.'

        # If subdomains are spoofable, downgrade overall status to potentially spoofable
        if analysis['dmarc'].get('subdomain_vulnerable'):
            if analysis['overall_status'] == 'secure':
                analysis['overall_status'] = 'partially_secure'
            # Ensure summary mentions subdomain risk
            extra_note = ' Subdomains may be spoofable due to DMARC subdomain policy (sp).' 
            if extra_note.strip() not in analysis['summary']:
                analysis['summary'] = (analysis['summary'] + extra_note).strip()
        
        # Generate recommendations
        recommendations = []
        if analysis['spf']['status'] == 'not_found':
            recommendations.append('Add an SPF record to specify which servers are authorized to send emails for this domain.')
        if analysis['dmarc']['status'] == 'not_found':
            recommendations.append('Add a DMARC record to specify how to handle emails that fail SPF or DKIM authentication.')
        elif analysis['dmarc']['policy'] == 'none':
            recommendations.append('Change DMARC policy from "none" to "quarantine" or "reject" for better protection.')
        # Subdomain-specific recommendation
        if analysis['dmarc']['subdomain_policy'] == 'none':
            recommendations.append('Change DMARC subdomain policy (sp=) from "none" to "quarantine" or "reject" to protect subdomains.')
        
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
    
    try:
        for selector in selectors:
            dkim_domain = f"{selector}._domainkey.{domain}"
            try:
                dkim_records = dns.resolver.resolve(dkim_domain, 'TXT')
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

@app.route('/send_email', methods=['POST'])
def send_email():
    """Send spoofed email"""
    try:
        # Get form data
        smtp_server = request.form.get('smtp_server')
        smtp_port = int(request.form.get('smtp_port', 25))
        username = request.form.get('username')
        password = request.form.get('password')
        from_name = request.form.get('from_name')
        from_email = request.form.get('from_email')
        reply_to = request.form.get('reply_to')
        to_email = request.form.get('to_email')
        cc = request.form.get('cc')
        bcc = request.form.get('bcc')
        subject = request.form.get('subject', '')
        message = request.form.get('message', '')
        html = request.form.get('html') == 'on'
        add_xheaders = request.form.get('add_xheaders') == 'on'
        
        # Validate required fields
        if not all([smtp_server, username, password, from_name, from_email, to_email]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        # Parse recipients
        to_list = [email.strip() for email in to_email.split(',') if email.strip()]
        cc_list = [email.strip() for email in cc.split(',') if email.strip()] if cc else None
        bcc_list = [email.strip() for email in bcc.split(',') if email.strip()] if bcc else None
        
        # Handle file attachments
        attachments = []
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    attachments.append(file_path)
        
        # Create spoofer instance
        spoofer = EmailSpoofer(smtp_server, smtp_port, username, password)
        
        # Create message
        msg = spoofer.create_message(
            from_name,
            from_email,
            reply_to if reply_to else None,  # Only use reply_to if provided
            to_list,
            cc_list,
            None,  # BCC is handled differently
            subject,
            message,
            html,
            attachments if attachments else None
        )
        
        # Add fake X-headers if requested
        if add_xheaders:
            msg = spoofer.spoof_x_headers(msg)
        
        # Get all recipients for sending
        all_recipients = to_list[:]
        if cc_list:
            all_recipients.extend(cc_list)
        if bcc_list:
            all_recipients.extend(bcc_list)
        
        # Send email
        success, error_msg = spoofer.send_email(msg, all_recipients)
        
        # Clean up uploaded files
        for attachment in attachments:
            try:
                os.remove(attachment)
            except:
                pass
        
        if success:
            return jsonify({'success': True, 'message': 'Email sent successfully!'})
        else:
            return jsonify({'success': False, 'error': error_msg})
            
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

@app.route('/check_multiple_domains', methods=['POST'])
def check_multiple_domains_endpoint():
    """Check multiple domains for spoofing vulnerability"""
    try:
        data = request.get_json()
        domains_text = data.get('domains', '').strip()
        
        if not domains_text:
            return jsonify({'success': False, 'error': 'Domain list is required'})
        
        # Parse domains (one per line or comma-separated)
        domains_list = []
        for line in domains_text.replace(',', '\n').split('\n'):
            domain = line.strip()
            if domain:
                domains_list.append(domain)
        
        if not domains_list:
            return jsonify({'success': False, 'error': 'No valid domains found'})
        
        # Check domains
        results = check_multiple_domains(domains_list)
        
        return jsonify({
            'success': True,
            'results': results
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
