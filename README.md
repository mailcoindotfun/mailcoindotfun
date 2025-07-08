# Mailcoin

A system that automatically creates tokens on pump.fun by sending emails.

## Features

- Users send emails containing token parameters to a specified Gmail address
- The system automatically parses the email content and calls the pump.fun API to create a token
- The creation result is automatically replied to the user via email

## Usage

1. Configure Gmail API OAuth2 credentials (`credentials.json`)
2. Configure Pump.fun API Token (write to `.env` or `config.py`)
3. Install dependencies: `pip install -r requirements.txt`
4. Run the main program: `python main.py`

## Email Format Example

```
Name: MyMemeCoin
Ticker: MMC
```

Be sure to attach the token's avatar image (jpg/png) as an email attachment.

## Core Parameters

- Gmail OAuth2 credentials
- Pump.fun API Token

## Dependencies

See `requirements.txt` 
