import os
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from time import sleep
import smtplib
from email.mime.text import MIMEText
load_dotenv()
INFURA_API_KEY = os.getenv('INFURA_API_KEY')

# Connect to an Ethereum node using Infura
def connect_to_ethereum_node():
    try :
        w3 = Web3(HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_API_KEY}"))
        if w3.is_connected():
            print("Connected to Ethereum node successfully!")
            return w3

        else:
            print("Failed to connect to Ethereum node!")
            exit(1)  
    except Exception as e:
        print("An error occurred while connecting to the Ethereum node:", e)
        exit(1)  

def handle_event(event):
    print("Token transfer to ZERO address detected!" , event)
    send_email_notification(event)

def send_email_notification(event):
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    receiver_email = 'another_jaru@hotmail.com' 

    message = MIMEText(f"Token transfer to ZERO address detected! Go Check in this link: https://etherscan.io/tx/{event['transactionHash'].hex()}")
    message['Subject'] = 'Token Transfer to ZERO address Notification'
    message['From'] = sender_email
    message['To'] = receiver_email

    try:
        # Connect to the Outlook/Hotmail SMTP server
        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email notification sent successfully!")
    except Exception as e:
        print("Failed to send email notification:", e)

def start_listener(w3):
    zero_address = "0x0000000000000000000000000000000000000000"

    usdt_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    # usdc_address ="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" #For testing
    # Event filter to listen for Transfer event to ZERO address
    filter_params = {
        'address': usdt_address,
        # 'fromBlock': last_processed_block + 1,
        # 'toBlock': 'latest',
        'topics': [
            Web3.keccak(text="Transfer(address,address,uint256)"),  # Transfer topic (32byte)
            None, # From anyone to zero adress 
            '0x' + zero_address.replace('0x', '').zfill(64),  # Filter for transfers to the ZERO address (32byte)
        ]
    }
    temp = 0
    while True:
        try:
            events = w3.eth.get_logs(filter_params)
            for event in events:
                if event['blockNumber'] != temp :
                    handle_event(event)
                    temp = event['blockNumber']
            # print("last_block_beforesleep", temp)
            sleep(5)  # Check every 5 seconds for new events
        except Exception as e:
            print("An error occurred while fetching events:", e)
            sleep(5)


w3 = connect_to_ethereum_node()
if w3:
    start_listener(w3)