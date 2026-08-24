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
        log(f'🏓 Sandbox pingado')
    except:
        log('⚠️ Sandbox offline')

def call_gemini(prompt):
    """Chama Gemini AI"""
    # Usa modelo correto
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.0-flash:generateContent?key={GEMINI_KEY}"
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    log('🔮 Chamando Gemini...')
    try:
        r = requests.post(url, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            log(f'Gemini erro: {r.status_code}')
            return None
    except Exception as e:
        log(f'Gemini exception: {e}')
        return None

def send_message(content):
    """Envia mensagem no Discord"""
    headers_discord = {'Authorization': f'Bot {DISCORD_TOKEN}', 'Content-Type': 'application/json'}
    payload = {'content': content}
    r = requests.post(f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages', 
                      headers=headers_discord, json=payload, timeout=10)
    return r.status_code == 200

def fetch_messages():
    headers_discord = {'Authorization': f'Bot {DISCORD_TOKEN}'}
    r = requests.get(f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=5', 
                     headers=headers_discord, timeout=10)
    if r.status_code == 200:
        return r.json()
    return []

def main():
    log('🚀 Arena + Gemini Bot Started!')
    
    ping_sandbox()
    msgs = fetch_messages()
    
    for msg in msgs:
        author = msg['author']['username']
        content = msg.get('content', '')
        
        # Responde a TODAS as mensagens de humanos
        if not msg['author'].get('bot', False) and content:
            log(f'📩 {author}: {content[:50]}')
            
            # Chama Gemini
            resposta = call_gemini(f"Você é uma IA conversando no Discord. Responda de forma natural e amigável em português. A mensagem foi: {content}")
            
            if resposta:
                send_message(f'💭 **{author}**, {resposta[:1900]}')
                log(f'✅ Respondido via Gemini!')
            else:
                log('❌ Gemini não respondeu')
    
    log('🏁 Ciclo completo!')

if __name__ == '__main__':
    main()
