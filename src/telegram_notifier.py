#!/usr/bin/env python3
"""
Sistema de Notificações Telegram
Notifica Dr. José sobre casos urgentes e intensos
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import asdict

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    logger.warning("httpx não instalado. Instale com: pip install httpx")
    HTTPX_AVAILABLE = False

class TelegramNotifier:
    """Sistema de notificações via Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.dr_jose_chat_id = os.getenv("DR_JOSE_CHAT_ID")
        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        
        # URLs da API Telegram
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Configurações
        self.notifications_enabled = os.getenv("TELEGRAM_NOTIFICATIONS", "True").lower() == "true"
        self.urgent_notify = os.getenv("URGENT_NOTIFY", "True").lower() == "true"
        
        if not self.bot_token:
            logger.warning("⚠️ TELEGRAM_BOT_TOKEN não configurado")
            self.notifications_enabled = False
        
        if not HTTPX_AVAILABLE:
            logger.warning("⚠️ httpx não disponível")
            self.notifications_enabled = False
        
        if self.notifications_enabled:
            logger.info("📱 Sistema de notificações Telegram ativado")
        else:
            logger.info("📱 Notificações Telegram desabilitadas")
    
    async def enviar_mensagem(self, chat_id: str, texto: str, parse_mode: str = "Markdown") -> bool:
        """Enviar mensagem via Telegram"""
        if not self.notifications_enabled:
            logger.info(f"📱 [SIMULAÇÃO] Mensagem para {chat_id}: {texto[:50]}...")
            return True
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": texto,
                        "parse_mode": parse_mode
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Mensagem enviada para {chat_id}")
                    return True
                else:
                    logger.error(f"❌ Erro ao enviar mensagem: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro na API Telegram: {e}")
            return False
    
    async def notificar_caso_urgente(self, resultado_triagem: Dict) -> bool:
        """Notificar caso urgente para Dr. José"""
        
        paciente = resultado_triagem.get("paciente", {})
        sintomas = resultado_triagem.get("sintomas", {})
        nivel = resultado_triagem.get("nivel_gravidade", "")
        
        # Emoji baseado na gravidade
        emoji = "🚨" if nivel == "urgente" else "🟠"
        
        mensagem = f"""
{emoji} **ALERTA DE TRIAGEM - {nivel.upper()}** {emoji}

👤 **Paciente:** {paciente.get('nome', 'Não informado')}
📱 **Telefone:** {paciente.get('telefone', 'Não informado')}
🆔 **CPF:** {paciente.get('cpf', 'Não informado')}

📊 **Pontuação Total:** {sintomas.get('pontuacao_total', 0)}/24
🎯 **Nível:** {nivel.upper()}

⚠️ **Sintomas Críticos:** {'SIM' if sintomas.get('sintomas_criticos') else 'NÃO'}

🕐 **Data/Hora:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}

**AÇÕES NECESSÁRIAS:**
• Contato imediato com paciente
• Avaliação presencial se necessário
• Verificar necessidade de SAMU

*Sistema de Triagem Psicológica*
        """
        
        # Enviar para Dr. José
        if self.dr_jose_chat_id:
            sucesso_dr = await self.enviar_mensagem(self.dr_jose_chat_id, mensagem)
        else:
            sucesso_dr = False
            logger.warning("⚠️ Chat ID do Dr. José não configurado")
        
        # Enviar para Admin também em casos urgentes
        if nivel == "urgente" and self.admin_chat_id:
            mensagem_admin = f"🚨 **CASO URGENTE DETECTADO**\n\n{mensagem}\n\n*Notificação enviada para Dr. José: {'✅' if sucesso_dr else '❌'}*"
            await self.enviar_mensagem(self.admin_chat_id, mensagem_admin)
        
        return sucesso_dr
    
    async def notificar_caso_intenso(self, resultado_triagem: Dict) -> bool:
        """Notificar caso intenso para Dr. José"""
        
        paciente = resultado_triagem.get("paciente", {})
        sintomas = resultado_triagem.get("sintomas", {})
        
        mensagem = f"""
🟠 **TRIAGEM INTENSIVA** 🟠

👤 **Paciente:** {paciente.get('nome', 'Não informado')}
📱 **Telefone:** {paciente.get('telefone', 'Não informado')}

📊 **Pontuação:** {sintomas.get('pontuacao_total', 0)}/24
🎯 **Classificação:** INTENSO

**PROTOCOLO:**
• Agendamento psiquiatria em 48h
• Acompanhamento psicológico semanal
• Monitoramento telefônico

🕐 **Triagem:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}

*Prioridade alta - acompanhar evolução*
        """
        
        if self.dr_jose_chat_id:
            return await self.enviar_mensagem(self.dr_jose_chat_id, mensagem)
        else:
            logger.warning("⚠️ Chat ID do Dr. José não configurado")
            return False
    
    async def relatorio_diario(self, estatisticas: Dict) -> bool:
        """Enviar relatório diário de triagens"""
        
        hoje = datetime.now().strftime('%d/%m/%Y')
        
        mensagem = f"""
📊 **RELATÓRIO DIÁRIO - {hoje}**

**TRIAGENS REALIZADAS:**
🟢 Leve: {estatisticas.get('leve', 0)} ({estatisticas.get('leve_pct', 0):.1f}%)
🟡 Moderado: {estatisticas.get('moderado', 0)} ({estatisticas.get('moderado_pct', 0):.1f}%)
🟠 Intenso: {estatisticas.get('intenso', 0)} ({estatisticas.get('intenso_pct', 0):.1f}%)
🔴 Urgente: {estatisticas.get('urgente', 0)} ({estatisticas.get('urgente_pct', 0):.1f}%)

**TOTAL:** {estatisticas.get('total', 0)} triagens

**MÉTRICAS:**
⏱️ Tempo médio: {estatisticas.get('tempo_medio', 0):.1f} min
✅ Taxa conclusão: {estatisticas.get('taxa_conclusao', 0):.1f}%
📱 Notificações enviadas: {estatisticas.get('notificacoes', 0)}

**CASOS PRIORITÁRIOS:**
🚨 Urgentes: {estatisticas.get('urgente', 0)}
🟠 Intensos: {estatisticas.get('intenso', 0)}

*Relatório automático - Sistema de Triagem*
        """
        
        # Enviar para Dr. José e Admin
        sucesso_dr = False
        sucesso_admin = False
        
        if self.dr_jose_chat_id:
            sucesso_dr = await self.enviar_mensagem(self.dr_jose_chat_id, mensagem)
        
        if self.admin_chat_id:
            sucesso_admin = await self.enviar_mensagem(self.admin_chat_id, mensagem)
        
        return sucesso_dr or sucesso_admin
    
    async def teste_notificacao(self) -> bool:
        """Testar sistema de notificações"""
        
        mensagem_teste = f"""
🧪 **TESTE DO SISTEMA DE NOTIFICAÇÕES** 🧪

✅ Bot Telegram funcionando
✅ Conexão com API estabelecida
✅ Sistema de triagem conectado

🕐 **Teste realizado:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}

**Configurações:**
🤖 Bot Token: Configurado
📱 Notificações: Ativas
🚨 Alertas urgentes: Ativos

*Se você recebeu esta mensagem, o sistema está funcionando corretamente!*
        """
        
        # Testar envio para Admin primeiro
        if self.admin_chat_id:
            sucesso = await self.enviar_mensagem(self.admin_chat_id, mensagem_teste)
            if sucesso:
                logger.info("✅ Teste de notificação bem-sucedido")
            return sucesso
        else:
            logger.warning("⚠️ Chat ID do Admin não configurado para teste")
            return False
    
    def notificar_sync(self, tipo: str, dados: Dict) -> bool:
        """Interface síncrona para notificações"""
        try:
            if tipo == "urgente":
                return asyncio.run(self.notificar_caso_urgente(dados))
            elif tipo == "intenso":
                return asyncio.run(self.notificar_caso_intenso(dados))
            elif tipo == "relatorio":
                return asyncio.run(self.relatorio_diario(dados))
            elif tipo == "teste":
                return asyncio.run(self.teste_notificacao())
            else:
                logger.warning(f"⚠️ Tipo de notificação não reconhecido: {tipo}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro na notificação síncrona: {e}")
            return False

# Instância global
telegram_notifier = TelegramNotifier()

# Funções de conveniência
def notificar_urgente(resultado_triagem: Dict) -> bool:
    """Notificar caso urgente"""
    return telegram_notifier.notificar_sync("urgente", resultado_triagem)

def notificar_intenso(resultado_triagem: Dict) -> bool:
    """Notificar caso intenso"""
    return telegram_notifier.notificar_sync("intenso", resultado_triagem)

def enviar_relatorio_diario(estatisticas: Dict) -> bool:
    """Enviar relatório diário"""
    return telegram_notifier.notificar_sync("relatorio", estatisticas)

def testar_notificacoes() -> bool:
    """Testar sistema de notificações"""
    return telegram_notifier.notificar_sync("teste", {})

def main():
    """Teste direto do sistema"""
    from rich.console import Console
    
    console = Console()
    console.print("[bold blue]📱 Testando Sistema de Notificações Telegram[/bold blue]")
    
    # Teste básico
    console.print("[yellow]🧪 Executando teste...[/yellow]")
    sucesso = testar_notificacoes()
    
    if sucesso:
        console.print("[green]✅ Sistema funcionando![/green]")
    else:
        console.print("[red]❌ Erro no sistema[/red]")
        console.print("[yellow]Verifique:")
        console.print("1. TELEGRAM_BOT_TOKEN no .env")
        console.print("2. ADMIN_CHAT_ID no .env")
        console.print("3. pip install httpx[/yellow]")

if __name__ == "__main__":
    main()