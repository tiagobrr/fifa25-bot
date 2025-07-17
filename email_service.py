import smtplib
from email.message import EmailMessage
import os

class EmailService:
    def send_report(self, email_to, file_path):
        SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
        SMTP_USER = os.environ.get('SMTP_USER')
        SMTP_PASS = os.environ.get('SMTP_PASS')

        if not SMTP_USER or not SMTP_PASS:
            print("SMTP_USER ou SMTP_PASS não configurados.")
            return False

        msg = EmailMessage()
        msg['Subject'] = 'Relatório Diário FIFA 25'
        msg['From'] = SMTP_USER
        msg['To'] = email_to
        msg.set_content('Segue em anexo o relatório diário das partidas FIFA 25.')

        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(file_path)
            msg.add_attachment(file_data, maintype='application',
                               subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                               filename=file_name)
        except Exception as e:
            print(f"Erro ao anexar arquivo: {e}")
            return False

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            print(f"E-mail enviado para {email_to}")
            return True
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            return False
