#!/usr/bin/env python3
import requests

# Dados do @curai1bot
bot_token = "7505201367:AAFGbaJbVy_2zh9NKHD1ny2jtpTLy6s6WGo"
chat_id = "1648736550"

print("🧪 TESTE DIRETO @curai1bot")
print("=" * 30)

try:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": "🧪 TESTE!\n\nSe você recebeu isso no @curai1bot, funciona!"
    }
    
    response = requests.post(url, json=payload, timeout=10)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCESSO! Mensagem enviada!")
        print("📱 Verifique @curai1bot no Telegram!")
    else:
        print(f"❌ Erro: {response.status_code}")
        data = response.json()
        print(f"Detalhes: {data.get('description', 'Erro desconhecido')}")
        
        # Soluções específicas
        desc = data.get('description', '').lower()
        if 'chat not found' in desc:
            print("\n💡 SOLUÇÃO:")
            print("1. Abra Telegram")
            print("2. Procure @curai1bot")
            print("3. Digite /start")
            print("4. Converse com o bot")
            print("5. Execute este teste novamente")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "=" * 30)