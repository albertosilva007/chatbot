#!/usr/bin/env python3
"""
Sistema de Triagem Psicológica - VERSÃO RENDER
"""

import os
import sys
from pathlib import Path
import gradio as gr
from datetime import datetime

# Configurações para Render
PORT = int(os.environ.get("PORT", 7860))
HOST = "0.0.0.0"

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

# Importar sistema
try:
    from chatbot import LlamaTriagemBot
    CHATBOT_DISPONIVEL = True
    print("✅ Sistema de triagem carregado!")
except ImportError as e:
    print(f"❌ Erro ao carregar sistema: {e}")
    CHATBOT_DISPONIVEL = False

class TriagemRender:
    """Sistema adaptado para Render"""
    
    def __init__(self):
        print("🚀 Inicializando Sistema de Triagem no Render...")
        
        self.model_name = os.getenv("MODEL_NAME", "microsoft/DialoGPT-medium")
        self.telegram_ativo = bool(os.getenv("TELEGRAM_BOT_TOKEN"))
        
        if CHATBOT_DISPONIVEL:
            try:
                self.chatbot = LlamaTriagemBot(self.model_name)
                self.modo = "PRODUÇÃO"
                print("✅ Chatbot REAL inicializado!")
            except Exception as e:
                print(f"⚠️ Erro no chatbot: {e}")
                self.chatbot = None
                self.modo = "DEMO"
        else:
            self.chatbot = None
            self.modo = "DEMO"
            
        print(f"🤖 Modo: {self.modo}")
        print(f"📱 Telegram: {'✅' if self.telegram_ativo else '❌'}")
    
    def process_message(self, message, history, user_id):
        """Processar mensagem"""
        if not message.strip():
            return history, ""
        
        history.append({"role": "user", "content": message})
        
        try:
            if self.modo == "PRODUÇÃO" and self.chatbot:
                response = self.chatbot.processar_mensagem(message, user_id)
            else:
                response = self.demo_response(message)
            
            history.append({"role": "assistant", "content": response})
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            error_msg = f"❌ Erro: {str(e)}"
            history.append({"role": "assistant", "content": error_msg})
        
        return history, ""
    
    def demo_response(self, message):
        """Resposta demo"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['suicídio', 'suicidio', 'matar']):
            return """🚨 **PROTOCOLO URGENTE** 🚨

**EM PRODUÇÃO:**
✅ Dr. José seria notificado via Telegram
✅ Protocolos de segurança ativados
✅ SAMU 192 disponível

**VOCÊ NÃO ESTÁ SOZINHO!**

*Demo - Em produção todos protocolos seriam ativados.*"""
        
        elif any(word in message_lower for word in ['triste', 'ansiedade']):
            return """Entendo suas dificuldades.

**Sistema Completo na Nuvem:**
🤖 IA avançada 24/7
📱 Notificações automáticas  
💾 Histórico seguro
🔒 SSL criptografado

Como posso ajudar você hoje?"""
        
        elif any(word in message_lower for word in ['olá', 'oi']):
            return f"""🏥 **Sistema de Triagem na Nuvem** ☁️

**Status:** {self.modo}
**Disponível:** 24/7 Global
**Segurança:** SSL/HTTPS

Para começar:
• Me diga seu nome
• Como está se sentindo

*Sistema confidencial e seguro.*"""
        
        else:
            return f"""**Analisando:** "{message}"

**Modo:** {self.modo} ☁️
**Processamento:** {'🤖 IA Real' if self.modo == 'PRODUÇÃO' else '🎭 Demo'}

Continue me contando sobre seus sentimentos."""

def create_interface():
    """Criar interface para Render"""
    
    triagem = TriagemRender()
    
    css = """
    .gradio-container { max-width: 1200px !important; margin: auto !important; }
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
    }
    .cloud-badge {
        background: #28a745; color: white; padding: 8px 15px;
        border-radius: 20px; text-align: center; font-weight: bold;
    }
    """
    
    with gr.Blocks(css=css, title="🏥 Triagem Psicológica Cloud") as demo:
        
        gr.HTML(f"""
        <div class="main-header">
            <h1>🏥 Sistema de Triagem Psicológica</h1>
            <p>Assistente IA disponível 24/7 na Nuvem</p>
            <div class="cloud-badge">☁️ {triagem.modo} - RENDER</div>
            <p><small>Confidencial • Seguro • Global</small></p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="💬 Conversa com Assistente",
                    height=500,
                    type="messages"
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Digite sua mensagem... Sistema 24/7",
                        lines=2, scale=4
                    )
                    send = gr.Button("📤", variant="primary", scale=1)
                
                with gr.Row():
                    clear = gr.Button("🔄 Nova Conversa")
                    emergency = gr.Button("🚨 Emergência", variant="stop")
            
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 10px;">
                    <h4 style="color: #28a745;">☁️ Sistema Cloud</h4>
                    <p>✅ Disponível 24/7</p>
                    <p>🔒 SSL/HTTPS</p>
                    <p>🌍 Acesso Global</p>
                    <p>📱 Telegram Ativo</p>
                </div>
                """)
                
                gr.HTML("""
                <div style="background: #fff5f5; border: 2px solid #fed7d7; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                    <h4 style="color: #c53030;">🆘 Emergência</h4>
                    <p><strong>SAMU:</strong> 192</p>
                    <p><strong>CVV:</strong> 188</p>
                    <p><strong>Polícia:</strong> 190</p>
                </div>
                """)
        
        user_id = gr.State(value=f"user_{datetime.now().timestamp()}")
        
        # Eventos
        for trigger in [msg.submit, send.click]:
            trigger(triagem.process_message, [msg, chatbot, user_id], [chatbot, msg])
        
        clear.click(lambda: ([], ""), outputs=[chatbot, msg])
        
        emergency.click(
            lambda: ([{"role": "assistant", "content": "🚨 **EMERGÊNCIA** 🚨\n\n📞 SAMU: 192\n📞 CVV: 188\n📞 Polícia: 190\n\n**VOCÊ NÃO ESTÁ SOZINHO!**"}], ""),
            outputs=[chatbot, msg]
        )
        
        # Mensagem inicial
        demo.load(
            lambda: ([{"role": "assistant", "content": f"""🏥 **Sistema de Triagem na Nuvem** ☁️

**Status:** {triagem.modo}
**Disponibilidade:** 24/7 Global  
**Segurança:** SSL criptografado

Seu assistente de triagem psicológica sempre disponível.

**Para começar:**
• Seu nome
• Como se sente hoje

*Sistema confidencial.*"""}], ""),
            outputs=[chatbot, msg]
        )
    
    return demo

def main():
    """Função principal"""
    print("🚀 Sistema de Triagem - Render Deploy")
    print(f"🌐 Porta: {PORT}")
    print(f"🏠 Host: {HOST}")
    
    # Verificar configuração
    missing = [var for var in ["TELEGRAM_BOT_TOKEN", "DR_JOSE_CHAT_ID"] 
               if not os.getenv(var)]
    
    if missing:
        print(f"⚠️ Variáveis faltando: {missing}")
        print("🎭 Modo demonstração")
    else:
        print("✅ Configuração completa")
        print("🤖 Modo produção")
    
    demo = create_interface()
    print("✅ Interface criada!")
    
    demo.launch(
        server_name=HOST,
        server_port=PORT,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()