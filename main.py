# -*- coding: utf-8 -*-
"""
Main entry: Polls for new emails, parses content, calls pump.fun API to create tokens, and automatically replies via email.
"""
from mail_handler import fetch_new_emails, send_reply
from pumpfun_api import create_token_with_avatar
import time
from config import GMAIL_ADDRESS

POLL_INTERVAL = 5  # Polling interval (seconds)

def main():
    print("[INFO] Mailcoin system started, polling inbox...")
    print(f"Current receiving email address: {GMAIL_ADDRESS}")
    while True:
        emails = fetch_new_emails()
        print(f"DEBUG: fetch_new_emails returned {len(emails)} emails: {emails}")
        for email in emails:
            print("DEBUG: Processing email:", email)
            params = email['params']
            image_path = email['image_path']
            if params and image_path:
                result = create_token_with_avatar(params['name'], params['ticker'], image_path)
                print("DEBUG: Token creation result:", result)
                send_reply(email['from'], result)
            elif not params:
                print("DEBUG: Email parameter format error, raw content:", email)
                send_reply(email['from'], "Parameter format error. Please refer to the template:\nName: xxx\nTicker: xxx\nAnd attach an avatar image.")
            elif not image_path:
                print("DEBUG: No avatar image detected, raw content:", email)
                send_reply(email['from'], "No avatar image detected. Please upload the token's avatar as an attachment (jpg/png)")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main() 