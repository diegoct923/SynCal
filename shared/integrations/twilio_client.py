from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_SID")
AUTH_TOKEN = os.getenv("TWILIO_TOKEN")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def update_webhook(base_url):
    webhook_url = f"{base_url}/webhook"

    try:
        numbers = client.incoming_phone_numbers.list()
        if numbers:
            numbers[0].update(sms_url=webhook_url)
            print(f"Webhook actualizado: {webhook_url}")
    except Exception as e:
        print("Error actualizando webhook:", e)

FROM_WHATSAPP = os.getenv("TWILIO_FROM_WHATSAPP", "whatsapp:+14155238886")  # sandbox

def send_whatsapp_message(to, message):
    client.messages.create(
        body=message,
        from_=FROM_WHATSAPP,
        to=to
    )
