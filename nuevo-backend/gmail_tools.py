import os
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()


class GmailService:
    def __init__(self):
        self.email = os.getenv('GMAIL_USER')
        self.password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not self.email or not self.password:
            raise ValueError("GMAIL_USER y GMAIL_APP_PASSWORD requeridos en .env")
    
    def send_email(self, to, subject, body, html_body=None, cc=None, bcc=None):
        try:
            if not to or not subject or not body:
                return {"success": False, "error": "Falta: to, subject, body"}
            
            message = MIMEMultipart('alternative')
            message['From'] = self.email
            message['To'] = to
            message['Subject'] = subject
            if cc:
                message['Cc'] = cc
            if bcc:
                message['Bcc'] = bcc
            
            message.attach(MIMEText(body, 'plain'))
            if html_body:
                message.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.email, self.password)
                server.send_message(message)
            
            return {
                "success": True,
                "message": "Email enviado",
                "to": to,
                "subject": subject
            }
        except Exception as error:
            return {"success": False, "error": str(error), "to": to}


_gmail_service = None

def get_gmail_service() -> GmailService:
    global _gmail_service
    if _gmail_service is None:
        _gmail_service = GmailService()
    return _gmail_service


def register_tools(app: FastMCP):
    """
    Registra las tools de Gmail sobre 'app' pasado desde main.py.
    """

    @app.tool()
    def send_gmail_email(
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía un correo electrónico a través de Gmail.
        
        Args:
            to: Dirección de correo del destinatario
            subject: Asunto del correo
            body: Cuerpo del correo en texto plano
            html_body: Cuerpo del correo en HTML (opcional)
            cc: Direcciones de CC separadas por comas (opcional)
            bcc: Direcciones de BCC separadas por comas (opcional)
        """
        try:
            gmail_service = get_gmail_service()
            result = gmail_service.send_email(
                to=to,
                subject=subject,
                body=body,
                html_body=html_body,
                cc=cc,
                bcc=bcc
            )
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al enviar email: {str(e)}",
                "to": to
            }
