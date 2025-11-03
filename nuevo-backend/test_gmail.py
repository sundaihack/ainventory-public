from dotenv import load_dotenv
from gmail_tools import get_gmail_service

load_dotenv()

gmail = get_gmail_service()

result = gmail.send_email(
    to="u20211f955@upc.edu.pe",
    subject="Prueba Gmail MCP",
    body="Hola, este es un correo de prueba desde AInventory."
)

print(f"✅ Enviado: {result.get('success')}")
if not result.get('success'):
    print(f"❌ Error: {result.get('error')}")
