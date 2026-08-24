#!/usr/bin/env python3
"""
Arena + Gemini - Com contexto da conversa
"""
import os, requests, time
from datetime import datetime

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
CHANNEL_ID = os.environ.get('DISCORD_CHANNEL_ID', '1387417968748793967')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

MAX_TIME = 55 * 60
start = time.time()

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_context():
    """Pega as últimas mensagens do canal como contexto"""
    headers = {'Authorization': f'Bot {DISCORD_TOKEN}'}
    r = requests.get(f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=20', 
                     headers=headers, timeout=10)
    if r.status_code != 200:
        return None
    
    msgs = r.json()
    # Monta contexto com as últimas mensagens
    contexto = []
    for msg in reversed(msgs):
        author = msg['author']['username']
        content = msg.get('content', '')
        if content:
            contexto.append(f"{author}: {content}")
    
    return "\n".join(contexto[-10:])  # Últimas 10 mensagens

def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_KEY}"
    
    # Monta prompt com contexto
    contexto = get_context()
    
    full_prompt = f"""Você está conversando no Discord. Aqui está o histórico recente:

{contexto}

Agora responda à última mensagem de forma natural e contextual."""

    data = {"contents": [{"parts": [{"text": full_prompt}]}]}
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

def main():
    log(f'🚀 Arena + Gemini com contexto!')
    last_id = None
    
    while time.time() - start < MAX_TIME:
        headers = {'Authorization': f'Bot {DISCORD_TOKEN}'}
        r = requests.get(f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=5', 
                         headers=headers, timeout=10)
        
        if r.status_code == 200:
            msgs = r.json()
            
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
                
                resposta = call_gemini(content)
                if resposta:
                    send_message(f'💭 **{author}**: {resposta[:1900]}')
                    log(f'✅ Resposta contextualizada!')
                
                last_id = msg['id']
        
        time.sleep(5)
    
    log('🏁 Fim!')

if __name__ == '__main__':
    main()
