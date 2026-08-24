#!/usr/bin/env python3
"""
Arena + Gemini - Conversa no Discord
"""
import os, requests
from datetime import datetime

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
CHANNEL_ID = os.environ.get('DISCORD_CHANNEL_ID', '1387417968748793967')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def call_gemini(prompt):
    log(f"DEBUG: GEMINI_KEY = {GEMINI_KEY[:10]}..." if GEMINI_KEY else "DEBUG: GEMINI_KEY = None")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_KEY}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=data, timeout=30)
        log(f"Gemini response: {r.status_code}")
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        log(f"Gemini error: {r.text[:200]}")
    except Exception as e:
        log(f"Gemini exception: {e}")
    return None

def send_message(content):
    headers = {'Authorization': f'Bot {DISCORD_TOKEN}', 'Content-Type': 'application/json'}
    r = requests.post(f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages', 
                      headers=headers, json={'content': content}, timeout=10)
    return r.status_code == 200

def fetch_messages():
    headers = {'Authorization': f'Bot {DISCORD_TOKEN}'}
    r = requests.get(f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=5', 
                     headers=headers, timeout=10)
    return r.json() if r.status_code == 200 else []

def main():
    log('🚀 Arena + Gemini Bot!')
    log(f"DEBUG: DISCORD_TOKEN = {DISCORD_TOKEN[:10] if DISCORD_TOKEN else 'None'}...")
    msgs = fetch_messages()
    
    for msg in msgs:
        author = msg['author']['username']
        content = msg.get('content', '')
        
        if not msg['author'].get('bot', False) and content:
            log(f'📩 {author}: {content[:30]}')
            resposta = call_gemini(f"Responda de forma natural em português: {content}")
            
            if resposta:
                send_message(f'💭 **{author}**: {resposta[:1900]}')
                log(f'✅ Gemini respondeu!')
    
    log('🏁 OK!')

if __name__ == '__main__':
    main()
