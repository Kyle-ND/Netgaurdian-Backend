from twilio.rest import Client
from dotenv import load_dotenv
import os

verify = []
load_dotenv()  # Load environment variables from .env file

def send_multichoice_sms(device):

    try:
        client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
        message = client.messages.create(
        from_='whatsapp:+14155238886',  # Twilio WhatsApp sandbox number
        to='whatsapp:+27624607085',
        body=(
            f"New device on your network has been detected do you Authorize this?{device}\n"
            "1️⃣ Yes\n"
            "2️⃣ No\n"
            "Reply with the number of your choice."
        )
    )
        verify.append(device)

        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None

def send_open_sms(device):

    try:
        client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
        message = client.messages.create(
        from_='whatsapp:+14155238886',  # Twilio WhatsApp sandbox number
        to='whatsapp:+27624607085',
        body=(
            f"A device on your network has an open port?{device}\n"
            "please resolve this as soon as possible."
        )
    )

        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None
