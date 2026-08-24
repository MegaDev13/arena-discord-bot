#!/usr/bin/env python3
"""
Arena + Gemini - Loop contínuo (55 minutos)
"""
import os, requests, time
from datetime import datetime

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
CHANNEL_ID = os.environ.get('DISCORD_CHANNEL_ID', '1387417968748793967')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

MAX_TIME = 55 * 60  # 55 minutos
start = time.time()

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_KEY}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        pass
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
    log(f'🚀 Arena + Gemini - Loop por 55 min!')
    last_id = None
    
    while time.time() - start < MAX_TIME:
        msgs = fetch_messages()
        
        for msg in reversed(msgs):
            if msg['id'] == last_id:
                continue
            if msg['author'].get('bot'):
                continue
            if not msg.get('content'):
                continue
            
            author = msg['author']['username']
            content = msg['content']
            log(f'📩 {author}: {content[:30]}')
            
            resposta = call_gemini(f"Responda de forma natural em português: {content}")
            if resposta:
                send_message(f'💭 **{author}**: {resposta[:1900]}')
                log(f'✅ Gemini respondeu!')
            
            last_id = msg['id']
        
        time.sleep(5)  # 5 segundos entre cada verificação
    
    log('🏁 Tempo esgotado!')

if __name__ == '__main__':
    main()
