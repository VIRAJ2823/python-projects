# whatsapp.py
# This file handles sending WhatsApp messages via Twilio

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()  # Load keys from .env file

def send_whatsapp(to_number, message):
    """
    to_number = phone number with country code e.g. '+919876543210'
    message   = text message to send
    """
    try:
        client = Client(
            os.getenv('TWILIO_SID'),
            os.getenv('TWILIO_TOKEN')
        )
        client.messages.create(
            from_=os.getenv('TWILIO_FROM'),
            to=f'whatsapp:{to_number}',
            body=message
        )
        return True
    except Exception as e:
        print(f"WhatsApp error: {e}")
        return False


def build_message(name, transactions, total, share):
    """
    Builds a clean WhatsApp message for each person
    """
    msg = f"💰 *Expense Summary for {name}*\n"
    msg += f"━━━━━━━━━━━━━━━━\n"
    msg += f"Total Bill: ₹{total}\n"
    msg += f"Your Share: ₹{share}\n"
    msg += f"━━━━━━━━━━━━━━━━\n"

    # Find transactions involving this person
    my_transactions = [t for t in transactions
                       if t['from'] == name or t['to'] == name]

    if not my_transactions:
        msg += "✅ You are all settled up!\n"
    else:
        msg += "📋 *Settlements:*\n"
        for t in my_transactions:
            if t['from'] == name:
                msg += f"➡️ You pay *{t['to']}*: ₹{t['amount']}\n"
            else:
                msg += f"⬅️ *{t['from']}* pays you: ₹{t['amount']}\n"

    msg += f"━━━━━━━━━━━━━━━━\n"
    msg += "Sent by Expense Splitter App 🧾"
    return msg