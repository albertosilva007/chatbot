#!/usr/bin/env python3
"""
Frontend Gradio com LLaMA Real
Interface integrada com chatbot inteligente
"""

import os
import sys
from pathlib import Path
import gradio as gr
from datetime import datetime

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

# Tentar importar chatbot real
try:
    from chatbot import LlamaTriagemBot
    CHATBOT_REAL_DISPONIVEL = True
    print("✅ Chatbot real importado com sucesso!")
except ImportError as e:
    print(f"⚠️ Chatbot real não disponível: {e}")
    CHATBOT_REAL_DISPONIVEL = False

# CSS customizado
custom_css = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}

.main-header {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.urgente {
    background: linear-gradient(135deg, #ff4444, #cc0000) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 10px !important;
    animation: pulse 2s infinite;
}

.status-llama {
    background: #28a745;
    color: white;
    padding: 8px 15px;
    border-radius: 20px;
    text-align: center;
    font-weight: bold;
    margin: 10px 0;
}

.status-demo {
    background: #ffc107;
    color: #333;
    padding: 8px 15px;
    border-radius: 20px;
    text-align: center;
    font-weight: bold;
    margin: 10px 0;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
"""

class GradioInterfaceReal:
    """Interface Gradio com chatbot real"""
    
    def __init__(self):
        print("🚀 Inicializando interface com LLaMA...")
        
        if CHATBOT_REAL_DISPONIVEL:
            # Usar chatbot real
            model_name = os.getenv("MODEL_NAME", "microsoft/DialoGPT-medium")
            print(f"📥 Carregando modelo: {model_name}")
            
            try:
                self.chatbot = LlamaTriagemBot(model_name)
                self.modo = "REAL"
                print("✅ Chatbot real inicializado!")
            except Exception as e:
                print(f"❌ Erro ao inicializar chatbot real: {e}")
                self.chatbot = None
                self.modo = "DEMO"
        else:
            self.chatbot = None
            self.modo = "DEMO"
            
        print(f"🤖 Modo: {self.modo}")
        
    def process_message(self, message, history, user_id):
        """Processar mensagem - REAL ou DEMO"""
        if not message.strip():
            return history, ""
        
        # Adicionar mensagem do usuário (formato messages)
        history.append({"role": "user", "content": message})
        
        try:
            if self.modo == "REAL" and self.chatbot:
                # Usar chatbot REAL com LLaMA
                response = self.chatbot.processar_mensagem(message, user_id)
                print(f"🤖 Resposta LLaMA gerada para: {message[:30]}...")
            else:
                # Fallback para modo demo
                response = self.demo_response(message)
                print(f"🎭 Resposta demo gerada para: {message[:30]}...")
            
            # Adicionar resposta do bot (formato messages)
            history.append({"role": "assistant", "content": response})
            
        except Exception as e:
            print(f"❌ Erro no processamento: {e}")
            error_response = f"❌ Erro no processamento: {str(e)}\n\nTentando novamente..."
            history.append({"role": "assistant", "content": error_response})
        
        return history, ""
    
    def demo_response(self, message):
        """Resposta demo aprimorada"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['suicídio', 'matar', 'morrer']):
            return """🚨 **PROTOCOLO URGENTE ATIVADO** 🚨

✅ Dr. José seria notificado IMEDIATAMENTE
✅ Contato familiar seria acionado
✅ SAMU 192 disponível se necessário

**VOCÊ NÃO ESTÁ SOZINHO(A)!**

*Modo demonstração - em caso real, protocolos seriam ativados automaticamente.*"""
        
        elif any(word in message_lower for word in ['triste', 'depressão', 'ansiedade']):
            return """Entendo que você está enfrentando dificuldades emocionais.

**Para uma triagem completa, o sistema real:**
🤖 Usaria LLaMA para análise avançada
📋 Seguiria protocolos médicos rigorosos
🎯 Classificaria automaticamente a gravidade
📊 Salvaria no histórico do paciente

**Perguntas que faria:**
1. Há quanto tempo se sente assim?
2. Interfere no dia a dia?
3. Tem apoio familiar?

*Configure LLaMA para funcionalidade completa!*"""
        
        elif 'olá' in message_lower:
            return f"""🏥 **Olá! Sistema de Triagem Psicológica**

**Status atual:** {self.modo}
{'🤖 IA LLaMA ativa' if self.modo == 'REAL' else '🎭 Modo demonstração'}

Para começar a triagem, me diga:
• Seu nome completo
• Como está se sentindo hoje

*Todas as informações são confidenciais.*"""
        
        else:
            return f"""**Sistema processando:** "{message}"

**Modo atual:** {self.modo}
{'🤖 Análise com IA CURAI' if self.modo == 'REAL' else '🎭 Resposta demonstração'}

Continue me contando mais sobre como você está se sentindo."""
    
    def nova_conversa(self):
        """Nova conversa"""
        print("🔄 Nova conversa iniciada")
        return [], ""
    
    def get_stats(self):
        """Estatísticas do sistema"""
        now = datetime.now()
        
        if self.modo == "REAL":
            stats = f"""📊 **Estatísticas do Sistema Real** 
*Atualizado: {now.strftime('%H:%M')}*

🤖 **Status LLaMA:** Ativo
📋 **Protocolos:** Implementados
💾 **Banco de dados:** Funcionando

**Triagens hoje:** Em tempo real
**Modelo:** {os.getenv('MODEL_NAME', 'Não configurado')}
**Modo:** Produção com IA"""
        else:
            stats = f"""📊 **Estatísticas Demo**
*Atualizado: {now.strftime('%H:%M')}*

🎭 **Status:** Modo demonstração
⚠️ **CURAI:** Não configurado
📋 **Protocolos:** Simulados

**Para ativar modo real:**
1. Configure HUGGINGFACE_TOKEN no .env
2. Defina MODEL_NAME no .env
3. Reinicie a aplicação"""
        
        return stats
    
    def get_system_info(self):
        """Informações do sistema"""
        if self.modo == "REAL":
            return """🤖 **SISTEMA REAL ATIVO**

✅ Chatbot CURAI carregado
✅ Protocolos médicos ativos
✅ Banco de dados conectado
✅ Detecção de emergência ativa

*Triagem completa disponível!*"""
        else:
            return """⚠️ **MODO DEMONSTRAÇÃO**

❌ LLaMA não configurado
❌ Funcionalidades limitadas
✅ Interface funcional

*Configure .env para ativar IA real*"""

def create_interface():
    """Criar interface integrada"""
    
    # Inicializar sistema
    interface = GradioInterfaceReal()
    
    # Criar interface
    with gr.Blocks(
        css=custom_css,
        title="🏥 Triagem Psicológica com IA",
        theme=gr.themes.Soft()
    ) as demo:
        
        # Header dinâmico
        header_class = "status-llama" if interface.modo == "REAL" else "status-demo"
        status_text = "🤖 IA CURAI ATIVA" if interface.modo == "REAL" else "🎭 MODO DEMONSTRAÇÃO"
        
        gr.HTML(f"""
        <div class="main-header">
            <h1>🏥 Sistema de Triagem Psicológica</h1>
            <p>Assistente Inteligente baseado em LLaMA e Protocolos Médicos</p>
            <div class="{header_class}">{status_text}</div>
            <p><small>Confidencial • Seguro • Profissional</small></p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                # Chat principal - CORRIGIDO para evitar warnings
                chatbot_component = gr.Chatbot(
                    label="💬 Conversa com Assistente de Triagem",
                    height=500,
                    show_label=True,
                    avatar_images=[
                        "https://cdn-icons-png.flaticon.com/512/3774/3774299.png",
                        "https://cdn-icons-png.flaticon.com/512/4712/4712027.png"
                    ],
                    type="messages"  # Corrigido para evitar warning
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        label="",
                        placeholder="Digite sua mensagem... (Ex: Olá, estou me sentindo triste)",
                        lines=2,
                        scale=4
                    )
                    send_btn = gr.Button("Enviar 📤", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("🔄 Nova Conversa", variant="secondary")
                    emergency_btn = gr.Button("🚨 Emergência", variant="stop")
        
            with gr.Column(scale=1):
                # Status do sistema
                system_info = gr.HTML(interface.get_system_info())
                
                # Níveis de gravidade
                gr.HTML("""
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border: 1px solid #dee2e6;">
                    <h4 style="margin-top: 0; color: #333;">📊 Níveis de Gravidade</h4>
                    <div style="background: #28a745; color: white; padding: 8px 10px; border-radius: 8px; margin: 8px 0; text-align: center; font-size: 0.9rem;">
                        🟢 Leve - Acompanhamento preventivo
                    </div>
                    <div style="background: #ffc107; color: white; padding: 8px 10px; border-radius: 8px; margin: 8px 0; text-align: center; font-size: 0.9rem;">
                        🟡 Moderado - Consulta em 7 dias
                    </div> 
                    <div style="background: #fd7e14; color: white; padding: 8px 10px; border-radius: 8px; margin: 8px 0; text-align: center; font-size: 0.9rem;">
                        🟠 Intenso - Urgente em 48h
                    </div>
                    <div style="background: #dc3545; color: white; padding: 8px 10px; border-radius: 8px; margin: 8px 0; text-align: center; font-size: 0.9rem;">
                        🔴 Urgente - Ação imediata
                    </div>
                </div>
                """)
                
                # Estatísticas
                stats_display = gr.HTML()
                stats_btn = gr.Button("📊 Atualizar Stats", variant="secondary")
                
                # Contatos de emergência
                gr.HTML("""
                <div style="background: #fff5f5; border: 2px solid #fed7d7; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
                    <h4 style="color: #c53030; margin-top: 0;">🆘 Emergência</h4>
                    <p><strong>SAMU:</strong> 192</p>
                    <p><strong>CVV:</strong> 188</p>
                    <p><strong>Dr. José:</strong> (11) 99999-9999</p>
                </div>
                """)
        
        # Estados
        user_id_state = gr.State(value=f"user_{datetime.now().timestamp()}")
        
        # Eventos
        msg_input.submit(
            interface.process_message,
            [msg_input, chatbot_component, user_id_state],
            [chatbot_component, msg_input]
        )
        
        send_btn.click(
            interface.process_message,
            [msg_input, chatbot_component, user_id_state],
            [chatbot_component, msg_input]
        )
        
        clear_btn.click(
            interface.nova_conversa,
            outputs=[chatbot_component, msg_input]
        )
        
        stats_btn.click(
            interface.get_stats,
            outputs=[stats_display]
        )
        
        emergency_btn.click(
            lambda: ([{"role": "assistant", "content": "🚨 **PROTOCOLO DE EMERGÊNCIA** 🚨\n\n**Se você está em risco IMEDIATO:**\n• 📞 Ligue **192 (SAMU)**\n• 📞 Ligue **188 (CVV)**\n• 🏥 Procure emergência médica\n\n**VOCÊ NÃO ESTÁ SOZINHO!**"}], ""),
            outputs=[chatbot_component, msg_input]
        )
        
        # Mensagem inicial personalizada
        mensagem_inicial = f"""🏥 **Bem-vindo ao Sistema de Triagem Psicológica**

**Status:** {interface.modo} {'🤖' if interface.modo == 'REAL' else '🎭'}

Sou seu assistente {'inteligente com IA LLaMA' if interface.modo == 'REAL' else 'demonstração'} especializado em saúde mental.

**Para começar, me diga:**
• Seu nome
• Como está se sentindo hoje
• O que te trouxe aqui

*Todas as informações são confidenciais e seguem protocolos médicos.*"""
        
        demo.load(
            lambda: ([{"role": "assistant", "content": mensagem_inicial}], ""),
            outputs=[chatbot_component, msg_input]
        )
    
    return demo

def main():
    """Função principal"""
    print("🚀 Iniciando Sistema de Triagem com LLaMA...")
    
    # Verificar configuração
    model_name = os.getenv("MODEL_NAME")
    huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
    
    if model_name and huggingface_token:
        print(f"🤖 Modelo configurado: {model_name}")
        print("✅ Token Hugging Face presente")
    else:
        print("⚠️ Configuração incompleta - rodando em modo demo")
        print("📝 Para ativar LLaMA:")
        print("   1. Configure HUGGINGFACE_TOKEN no .env")
        print("   2. Configure MODEL_NAME no .env")
    
    # Criar e lançar
    demo = create_interface()
    
    print("✅ Interface criada!")
    print("🌐 Abrindo navegador...")
    
    # MUDANÇA PRINCIPAL: Porta alterada para 7861
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,  # ← MUDANÇA: 7860 para 7861
        share=False,
        show_error=True,
        inbrowser=True
    )

if __name__ == "__main__":
    main()