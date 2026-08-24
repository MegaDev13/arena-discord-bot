#!/usr/bin/env python3
"""
Arena Discord Bot - Mantém sandbox ativo e monitora Discord
"""
import os, requests
from datetime import datetime

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
CHANNEL_ID = os.environ.get('DISCORD_CHANNEL_ID', '1387417968748793967')
SANDBOX_URL = os.environ.get('SANDBOX_URL', 'https://arena-ai.dev')

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def ping_sandbox():
    """Ping no sandbox para manter ativo"""
    try:
        r = requests.get(SANDBOX_URL, timeout=5)
        log(f'🏓 Sandbox pingado: {r.status_code}')
        return True
    except Exception as e:
        log(f'⚠️ Sandbox offline ou erro: {e}')
        return False

def get_last_id():
    try:
        with open('.last_msg_id', 'r') as f:
            return f.read().strip()
    except:
        return None

def save_last_id(msg_id):
    with open('.last_msg_id', 'w') as f:
        f.write(str(msg_id))

def fetch_messages():
    if not DISCORD_TOKEN:
        log('ERRO: Token nao configurado!')
        return []
    headers = {'Authorization': f'Bot {DISCORD_TOKEN}'}
    r = requests.get(f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=10', headers=headers, timeout=10)
    return r.json() if r.status_code == 200 else []

def respond(author, content):
    if not DISCORD_TOKEN:
        return False
    headers = {'Authorization': f'Bot {DISCORD_TOKEN}', 'Content-Type': 'application/json'}
    payload = {'content': f'@{author}收到! Voce disse: "{content}"'}
    r = requests.post(f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages', headers=headers, json=payload, timeout=10)
    return r.status_code == 200

def main():
    log('🚀 Arena Bot Started!')
    
    # 1. Ping no sandbox
    ping_sandbox()
    
    # 2. Processa mensagens do Discord
    last = get_last_id()
    msgs = fetch_messages()
    
    count = 0
    for msg in reversed(msgs):
        if msg['author'].get('bot'):
            continue
        if not msg.get('content'):
            continue
        if last and int(msg['id']) <= int(last):
            continue
        
        author = msg['author']['username']
        content = msg['content']
        log(f'📩 {author}: {content[:40]}')
        
        if respond(author, content):
            log(f'✅ Respondi para {author}')
            count += 1
        
        save_last_id(msg['id'])
    
    log(f'🏁 Ciclo completo! ({count} respostas)')

if __name__ == '__main__':
    main()
