import re
import socket
import smtplib
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

class EmailValidatorAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL and query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        emails = query_params.get('email', [])

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

        # 4) Authentication & Anti-Spam Measures
        # This is complex and often requires external services
        # Placeholder for implementation

        # 5) User Engagement
        # This requires access to email marketing data
        # Placeholder for implementation

        # 6) Mailbox availability
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
            server = smtplib.SMTP()
            server.connect(domain)
            server.quit()
            return True
        except smtplib.SMTPConnectError:
            return False

    def check_mailbox_availability(self, email):
        # This is a simplified check
        # Real implementation should handle more SMTP responses
        domain = email.split('@')[1]
        try:
            server = smtplib.SMTP(domain)
            server.mail('')
            server.rcpt(email)
            server.quit()
            return True
        except smtplib.SMTPRecipientsRefused:
            return False

def run(server_class=HTTPServer, handler_class=EmailValidatorAPI, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
