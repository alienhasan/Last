import re
import socket
import smtplib
from http.server import BaseHTTPRequestHandler

class EmailValidatorAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL and query parameters
        query_string = self.path.split('?')[1] if '?' in self.path else ''
        query_params = {k: v[0] for k, v in parse_qs(query_string).items()}
        emails = query_params.get('email', '').split(',')

        results = {}
        for email in emails:
            validation_result = self.validate_email(email)
            results[email] = validation_result

        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(str(results).encode())

    def validate_email(self, email):
        # 1) Syntactic Validity (RFC 5322 Compliance)
        if not self.check_syntax(email):
            return {"status": "invalid", "message": "Syntax error"}

        # 2) Domain Validity
        if not self.check_domain(email):
            return {"status": "invalid", "message": "Domain does not exist"}

        # 3) SMTP Deliverability
        if not self.check_smtp(email):
            return {"status": "invalid", "message": "SMTP server rejected the email"}

        # 4) Mailbox availability
        if not self.check_mailbox_availability(email):
            return {"status": "invalid", "message": "Mailbox does not exist"}

        return {"status": "valid", "message": "Email passed all checks"}

    def check_syntax(self, email):
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, email) is not None

    def check_domain(self, email):
        domain = email.split('@')[1]
        try:
            socket.gethostbyname(domain)
            return True
        except socket.error:
            return False

    def check_smtp(self, email):
        domain = email.split('@')[1]
        try:
            server = smtplib.SMTP(domain)
            server.quit()
            return True
        except smtplib.SMTPConnectError:
            return False

    def check_mailbox_availability(self, email):
        domain = email.split('@')[1]
        try:
            server = smtplib.SMTP(domain)
            server.mail('')
            server.rcpt(email)
            server.quit()
            return True
        except smtplib.SMTPRecipientsRefused:
            return False
