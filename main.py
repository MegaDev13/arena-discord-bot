#!/usr/bin/env python3
"""
Arena + Gemini - Conversa no Discord
"""
import os
import requests
from datetime import datetime

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
CHANNEL_ID = os.environ.get('DISCORD_CHANNEL_ID', '1387417968748793967')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
SANDBOX_URL = os.environ.get('SANDBOX_URL', 'https://arena-ai.dev')

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def ping_sandbox():
    try:
        r = requests.get(SANDBOX_URL, timeout=5)
        log(f'🏓 Sandbox: OK')
    except:
        log('⚠️ Sandbox offline')

def get_last_id():
    try:
        with open('.last_msg_id', 'r') as f:
            return f.read().strip()
    except:
        return None

def save_last_id(msg_id):
    with open('.last_msg_id', 'w') as f:
        f.write(str(msg_id))

def call_gemini(prompt):
    """Chama Gemini AI"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        r = requests.post(url, json=data, timeout=10)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        log(f'Gemini erro: {e}')
    return None

def send_message(content):
    """Envia mensagem no Discord"""
    headers = {'Authorization': f'Bot {DISCORD_TOKEN}', 'Content-Type': 'application/json'}
    payload = {'content': content}
    r = requests.post(f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages', 
                      headers=headers, json=payload, timeout=10)
    return r.status_code == 200

def fetch_messages():
    headers = {'Authorization': f'Bot {DISCORD_TOKEN}'}
    r = requests.get(f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=10', 
                     headers=headers, timeout=10)
    return r.json() if r.status_code == 200 else []

def main():
    log('🚀 Arena + Gemini Bot Started!')
    
    # Ping no sandbox
    ping_sandbox()
    
    last = get_last_id()
    msgs = fetch_messages()
    
    for msg in reversed(msgs):
        if msg['author'].get('bot') and msg['author']['username'] != 'Bod':
            continue
        if not msg.get('content'):
            continue
        if last and int(msg['id']) <= int(last):
            continue
        
        author = msg['author']['username']
        content = msg['content']
        
        # Pula mensagens do próprio bot
        if author == 'Bod':
            # Verifica se mencionou o bot
            if '@Bod' in content or 'arena' in content.lower():
                log(f'📩 {author} me chamou: {content[:50]}')
                
                # Gera resposta com Gemini
                prompt = f"Você é uma IA conversando no Discord. Responda de forma natural e amigável em português. Mensagem recebida: {content}"
                resposta = call_gemini(prompt)
                
                if resposta:
                    send_message(f'💭 {resposta[:1900]}')
                    log(f'✅ Respondi via Gemini')
        else:
            log(f'📩 {author}: {content[:50]}')
        
        save_last_id(msg['id'])

    log('🏁 Ciclo completo!')

if __name__ == '__main__':
    main()
