# -*- coding: utf-8 -*-
"""
Module for calling pump.fun API to create tokens.
"""
import os
import requests
from config import PUMPFUN_API_KEY
from solders.keypair import Keypair
import mimetypes

def upload_avatar_to_ipfs(form_data, image_path):
    print("DEBUG: Uploading avatar to IPFS, form_data =", form_data, "image_path =", image_path)
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    files = {'file': (os.path.basename(image_path), open(image_path, 'rb'), mime_type)}
    response = requests.post("https://pump.fun/api/ipfs", data=form_data, files=files)
    print("DEBUG: IPFS response status code =", response.status_code)
    print("DEBUG: IPFS response content =", response.text)
    if response.status_code == 200:
        metadata_uri = response.json().get('metadataUri')
        print("DEBUG: metadataUri =", metadata_uri)
        return metadata_uri
    else:
        return None

def create_token_with_avatar(name, ticker, image_path):
    print(f"DEBUG: Calling create_token_with_avatar, name={name}, ticker={ticker}, image_path={image_path}")
    # Build metadata
    form_data = {
        'name': name,
        'symbol': ticker,
        'description': f'{name} created via Mailcoin',
        'showName': 'true'
    }
    metadata_uri = upload_avatar_to_ipfs(form_data, image_path)
    if not metadata_uri:
        print('DEBUG: Avatar upload failed, cannot create token.')
        return 'Avatar upload failed, cannot create token.'
    # Generate mint keypair
    mint_keypair = Keypair()
    mint = str(mint_keypair)  # Pass base58 private key string
    print(f"DEBUG: Generated mint = {mint}")
    token_metadata = {
        'name': name,
        'symbol': ticker,
        'uri': metadata_uri
    }
    payload = {
        'action': 'create',
        'tokenMetadata': token_metadata,
        'mint': mint,  # Pass private key
        'denominatedInSol': 'true',
        'amount': 0,  # Only create token, no buy
        'slippage': 10,
        'priorityFee': 0.0005,
        'pool': 'pump'
    }
    print(f"DEBUG: Request payload = {payload}")
    url = f"https://pumpportal.fun/api/trade?api-key={PUMPFUN_API_KEY}"
    response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
    print("DEBUG: pump.fun response status code =", response.status_code)
    print("DEBUG: pump.fun response content =", response.text)
    if response.status_code == 200:
        data = response.json()
        return f"Token created successfully! Transaction link: https://solscan.io/tx/{data.get('signature')}"
    else:
        return f"Token creation failed: {response.reason}" 