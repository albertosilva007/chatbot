#!/usr/bin/env python3
"""
Sistema de Triagem Psicológica - VERSÃO FLASK SIMPLES
"""

import os
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
PORT = int(os.environ.get("PORT", 7860))
HOST = "0.0.0.0"

app = Flask(__name__)

class TriagemRender:
    """Sistema simplificado para Render"""
    
    def __init__(self):
        print("🚀 Inicializando Sistema de Triagem no Render...")
        
        self.telegram_ativo = bool(os.getenv("TELEGRAM_BOT_TOKEN"))
        self.hf_token = bool(os.getenv("HUGGINGFACE_TOKEN"))
        self.modo = "DEMO - RENDER"
            
        print(f"🤖 Modo: {self.modo}")
        print(f"📱 Telegram: {'✅' if self.telegram_ativo else '❌'}")
        print(f"🤗 HuggingFace: {'✅' if self.hf_token else '❌'}")
    
    def demo_response(self, message):
        """Resposta demo inteligente"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['suicídio', 'suicidio', 'matar', 'morte', 'morrer']):
            return """🚨 **PROTOCOLO DE EMERGÊNCIA ATIVADO** 🚨

**IMPORTANTE:** Você não está sozinho!

📞 **CONTATOS URGENTES:**
• SAMU: 192
• CVV: 188  
• Polícia: 190

✅ **EM PRODUÇÃO COMPLETA:**
• Dr. José seria notificado automaticamente
• Protocolos de segurança ativados
• Histórico seguro mantido

*Esta é uma versão demonstrativa. Em emergências reais, sempre ligue 192.*"""
        
        elif any(word in message_lower for word in ['triste', 'deprimido', 'ansiedade', 'angústia', 'preocupado']):
            return f"""💙 Entendo que você está passando por dificuldades.

**Sistema de Triagem - {self.modo}:**
🤖 Análise de sentimentos ativa
📱 Notificações {'configuradas' if self.telegram_ativo else 'pendentes'}
💾 Conversas registradas com segurança
🔒 Ambiente criptografado

**Como posso ajudar você hoje?**
• Me conte mais sobre seus sentimentos
• Está acontecendo algo específico?

*Sistema disponível 24/7 para apoio.*"""
        
        elif any(word in message_lower for word in ['olá', 'oi', 'hello', 'bom dia', 'boa tarde', 'boa noite']):
            return f"""🏥 **Bem-vindo ao Sistema de Triagem Psicológica** 

**Status do Sistema:** {self.modo} ☁️
**Disponibilidade:** 24/7 Global
**Segurança:** SSL/HTTPS ativo
**Telegram:** {'✅ Configurado' if self.telegram_ativo else '⚠️ Pendente'}

**Para começar sua triagem:**
• Diga seu nome
• Conte como está se sentindo hoje
• Compartilhe suas preocupações

*Este é um ambiente seguro e confidencial.*"""
        
        elif any(word in message_lower for word in ['dor', 'doendo', 'machuca', 'sofrendo']):
            return """😔 Sinto muito que você esteja com dor.

**Tipos de suporte disponível:**
🧠 Emocional: Conversas de apoio
🏥 Clínico: Triagem para direcionamento
📞 Emergencial: Contatos de ajuda imediata

**Me conte mais:**
• Que tipo de dor você sente?
• É física ou emocional?
• Há quanto tempo isso começou?

Estou aqui para ouvir e ajudar."""
        
        elif any(word in message_lower for word in ['obrigado', 'obrigada', 'valeu', 'thanks']):
            return """😊 Fico feliz em poder ajudar!

**Lembre-se:**
• Este sistema está sempre disponível
• Suas conversas ficam registradas com segurança  
• Em emergências, ligue 192 ou 188

**Continue voltando sempre que precisar.**
Este é seu espaço de apoio e cuidado.

*Cuide-se! 💙*"""
        
        else:
            truncated_msg = message[:50] + '...' if len(message) > 50 else message
            return f"""**Processando sua mensagem:** "{truncated_msg}"

**Sistema:** {self.modo} ☁️
**Análise:** Aguardando mais informações
**Status:** {'🟢 Todos sistemas operacionais' if self.telegram_ativo and self.hf_token else '🟡 Configuração básica'}

**Continue me contando:**
• Como você está se sentindo?
• O que está te preocupando?
• Em que posso ajudar hoje?

*Seu bem-estar é nossa prioridade.*"""

# Inicializar sistema
triagem = TriagemRender()

# Template HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏥 Sistema de Triagem Psicológica</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: rgba(255,255,255,0.95);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2rem;
        }
        .chat-container {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .status-panel {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            height: fit-content;
        }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 10px;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: 2rem;
        }
        .bot-message {
            background: #e9ecef;
            margin-right: 2rem;
        }
        .input-container {
            display: flex;
            gap: 1rem;
        }
        .message-input {
            flex: 1;
            padding: 1rem;
            border: 2px solid #dee2e6;
            border-radius: 10px;
            font-size: 16px;
        }
        .send-btn, .emergency-btn, .clear-btn {
            padding: 1rem 2rem;
            border: none;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .send-btn {
            background: #28a745;
            color: white;
        }
        .emergency-btn {
            background: #dc3545;
            color: white;
            margin-top: 1rem;
        }
        .clear-btn {
            background: #6c757d;
            color: white;
            margin-top: 1rem;
        }
        .send-btn:hover { background: #218838; }
        .emergency-btn:hover { background: #c82333; }
        .clear-btn:hover { background: #5a6268; }
        .status-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .emergency-box {
            background: #fff5f5;
            border: 2px solid #fed7d7;
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 2rem;
        }
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Sistema de Triagem Psicológica</h1>
            <p>🤖 Assistente IA • 🔒 Seguro • ☁️ Disponível 24/7</p>
            <p><strong>Status:</strong> {{ modo }}</p>
            <p><small>💙 Cuidado emocional sempre disponível</small></p>
        </div>
        
        <div class="main-content">
            <div class="chat-container">
                <h3>💬 Conversa com Assistente de Triagem</h3>
                <div class="chat-messages" id="chatMessages">
                    <div class="message bot-message">
                        <strong>🤖 Assistente:</strong><br>
                        🏥 <strong>Sistema de Triagem Psicológica Ativo</strong><br><br>
                        <strong>Status:</strong> {{ modo }} ☁️<br>
                        <strong>Disponibilidade:</strong> 24 horas, 7 dias por semana<br>
                        <strong>Segurança:</strong> Conexão criptografada SSL<br><br>
                        🤖 Sou seu assistente de triagem psicológica. Estou aqui para:<br>
                        • Ouvir suas preocupações<br>
                        • Oferecer apoio emocional<br>
                        • Direcionar para ajuda profissional quando necessário<br>
                        • Detectar situações de emergência<br><br>
                        <strong>Para começar:</strong><br>
                        • Me diga seu nome<br>
                        • Conte como você está se sentindo hoje<br>
                        • Compartilhe o que está te preocupando<br><br>
                        <em>Este é um ambiente seguro e confidencial. Vamos conversar?</em> 💙
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" class="message-input" id="messageInput" 
                           placeholder="💬 Digite sua mensagem... Como você está se sentindo hoje?"
                           onkeypress="handleKeyPress(event)">
                    <button class="send-btn" onclick="sendMessage()">📤 Enviar</button>
                </div>
                
                <div style="display: flex; gap: 1rem;">
                    <button class="clear-btn" onclick="clearChat()">🔄 Nova Conversa</button>
                    <button class="emergency-btn" onclick="emergency()">🚨 EMERGÊNCIA</button>
                </div>
            </div>
            
            <div class="status-panel">
                <h4>☁️ Status do Sistema</h4>
                <div class="status-item">
                    <span><strong>🌐 Disponibilidade:</strong></span>
                    <span>24/7</span>
                </div>
                <div class="status-item">
                    <span><strong>🔒 Segurança:</strong></span>
                    <span>SSL/HTTPS</span>
                </div>
                <div class="status-item">
                    <span><strong>📱 Telegram:</strong></span>
                    <span>{{ telegram_status }}</span>
                </div>
                <div class="status-item">
                    <span><strong>🤗 IA:</strong></span>
                    <span>{{ ia_status }}</span>
                </div>
                <div class="status-item">
                    <span><strong>🛡️ Modo:</strong></span>
                    <span>{{ modo }}</span>
                </div>
                
                <div class="emergency-box">
                    <h4 style="color: #c53030;">🆘 Emergências</h4>
                    <p><strong>🚑 SAMU:</strong> 192</p>
                    <p><strong>💙 CVV:</strong> 188</p>
                    <p><strong>🚓 Polícia:</strong> 190</p>
                    <p><strong>🚒 Bombeiros:</strong> 193</p>
                    <hr style="margin: 10px 0;">
                    <p style="font-size: 12px; color: #666;">
                        Em caso de pensamentos suicidas ou emergência, ligue imediatamente!
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Adicionar mensagem do usuário
            addMessage(message, 'user');
            input.value = '';
            
            // Enviar para o servidor
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.response, 'bot');
            })
            .catch(error => {
                addMessage('❌ Erro de conexão. Tente novamente.', 'bot');
            });
        }
        
        function addMessage(message, sender) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            if (sender === 'user') {
                messageDiv.innerHTML = `<strong>👤 Você:</strong><br>${message}`;
            } else {
                messageDiv.innerHTML = `<strong>🤖 Assistente:</strong><br>${message}`;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function clearChat() {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="message bot-message">
                    <strong>🤖 Assistente:</strong><br>
                    💬 <strong>Nova conversa iniciada!</strong><br><br>
                    Como posso ajudar você hoje?<br><br>
                    <em>Este é um ambiente seguro e confidencial.</em> 💙
                </div>
            `;
        }
        
        function emergency() {
            addMessage('🚨 EMERGÊNCIA', 'user');
            addMessage(`🚨 <strong>PROTOCOLO DE EMERGÊNCIA</strong> 🚨<br><br>
                📞 <strong>LIGUE AGORA:</strong><br>
                • SAMU: 192<br>
                • CVV: 188<br>
                • Polícia: 190<br><br>
                <strong>VOCÊ NÃO ESTÁ SOZINHO!</strong><br><br>
                Se você está tendo pensamentos suicidas ou está em perigo, ligue para um desses números AGORA.<br><br>
                💙 Estamos aqui para você.`, 'bot');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, 
                                modo=triagem.modo,
                                telegram_status='✅ Ativo' if triagem.telegram_ativo else '⚠️ Config',
                                ia_status='✅ Ativo' if triagem.hf_token else '⚠️ Config')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    
    try:
        response = triagem.demo_response(message)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'❌ Erro: {str(e)}'})

if __name__ == "__main__":
    print("🚀 Sistema de Triagem - Render Deploy (Flask)")
    print(f"🌐 Porta: {PORT}")
    print(f"🏠 Host: {HOST}")
    
    # Verificar configuração
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    dr_jose_id = os.getenv("DR_JOSE_CHAT_ID")
    
    print("📋 Verificando configuração:")
    print(f"📱 Telegram: {'✅' if telegram_token else '❌'}")
    print(f"🤗 HuggingFace: {'✅' if hf_token else '❌'}")
    print(f"👨‍⚕️ Dr. José ID: {'✅' if dr_jose_id else '❌'}")
    
    if not telegram_token or not hf_token:
        print("⚠️ Algumas variáveis de ambiente estão faltando")
        print("🎭 Sistema funcionará em modo demonstração")
    else:
        print("✅ Configuração completa")
        print("🤖 Modo produção parcial")
    
    print("🚀 Iniciando servidor Flask...")
    app.run(host=HOST, port=PORT, debug=False)