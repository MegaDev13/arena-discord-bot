# Arena Discord Bot

Mantém sandbox ativo e monitora Discord via GitHub Actions.

## Como funciona
- Roda a cada 5 minutos via GitHub Actions
- Verifica novas mensagens no Discord
- Responde automaticamente

## Setup

1. Settings > Secrets > Actions > New secret
2. Adicione:
   - DISCORD_BOT_TOKEN: seu token do bot
   - DISCORD_CHANNEL_ID: ID do canal

3. Actions > Arena Discord Monitor > Run workflow

Pronto! 24/7! 🎮
