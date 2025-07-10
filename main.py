#!/usr/bin/env python3
"""
Chatbot de Triagem Psicológica com LLaMA
Arquivo Principal - main.py (ATUALIZADO)
"""

import os
import sys
from pathlib import Path

# Adicionar src ao path para imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from dotenv import load_dotenv
    from loguru import logger
    from rich.console import Console
    from rich.panel import Panel
    DEPENDENCIES_OK = True
except ImportError as e:
    print(f"❌ Erro: Dependências não instaladas: {e}")
    print("Execute: pip install -r requirements.txt")
    DEPENDENCIES_OK = False
    sys.exit(1)

# Carregar variáveis de ambiente
load_dotenv()

# Console colorido
console = Console()


def main():
    """Função principal do chatbot"""

    # Banner inicial
    console.print(Panel.fit(
        "[bold blue]🏥 Chatbot de Triagem Psicológica[/bold blue]\n"
        "[green]Baseado em LLaMA e Protocolos Médicos[/green]\n"
        "[yellow]Versão: 2.0.0 - CHATBOT REAL[/yellow]",
        border_style="blue",
        title="Sistema de Triagem"
    ))

    # Verificar estrutura do projeto
    console.print("[yellow]🔍 Verificando estrutura do projeto...[/yellow]")

    required_folders = ["src", "config", "data", "interfaces"]
    missing_folders = []

    for folder in required_folders:
        if not Path(folder).exists():
            missing_folders.append(folder)

    if missing_folders:
        console.print(f"[red]❌ Pastas faltando: {missing_folders}[/red]")
        return

    console.print("[green]✅ Estrutura do projeto OK![/green]")

    # Tentar importar e usar o chatbot REAL
    try:
        console.print("[yellow]🤖 Carregando chatbot REAL...[/yellow]")

        # Importar chatbot implementado
        from chatbot import LlamaTriagemBot

        # Escolher modelo (começar com menor para teste)
        model_name = os.getenv("MODEL_NAME", None)  # None = modo simulação

        if model_name:
            console.print(f"[cyan]📥 Carregando modelo: {model_name}[/cyan]")
        else:
            console.print(
                "[yellow]⚠️  Usando modo simulação (sem LLaMA)[/yellow]")

        # Inicializar chatbot
        bot = LlamaTriagemBot(model_name)

        console.print("[green]✅ Chatbot inicializado com sucesso![/green]")

        # Instruções
        console.print("\n[bold cyan]🎯 INSTRUÇÕES:[/bold cyan]")
        console.print("• Este é o chatbot REAL de triagem psicológica")
        console.print("• Segue protocolos médicos rigorosos")
        console.print("• Detecta emergências automaticamente")
        console.print("• Salva histórico no banco de dados")
        console.print("• Digite 'sair' para encerrar")

        # Loop principal do chatbot
        chatbot_loop(bot)

    except ImportError as e:
        console.print(f"[red]❌ Erro ao importar chatbot: {e}[/red]")
        console.print(
            "[yellow]Verifique se o arquivo src/chatbot.py existe[/yellow]")
    except Exception as e:
        logger.error(f"Erro geral: {e}")
        console.print(f"[red]❌ Erro inesperado: {e}[/red]")


def chatbot_loop(bot):
    """Loop principal do chatbot"""
    console.print("\n[bold green]🚀 CHATBOT DE TRIAGEM ATIVO![/bold green]")
    console.print(
        "[cyan]Comece dizendo olá ou contando como se sente...[/cyan]")

    user_id = "user_main"

    while True:
        try:
            # Input do usuário
            mensagem = console.input("\n[bold cyan]Você:[/bold cyan] ")

            # Comandos especiais
            if mensagem.lower() in ['sair', 'exit', 'quit']:
                console.print("[yellow]👋 Encerrando triagem...[/yellow]")
                break
            elif mensagem.lower() == 'novo':
                # Reiniciar sessão
                if user_id in bot.sessoes:
                    del bot.sessoes[user_id]
                console.print("[green]🔄 Nova triagem iniciada![/green]")
                continue
            elif mensagem.lower() == 'historico':
                # Mostrar histórico (se implementado)
                console.print(
                    "[yellow]📊 Funcionalidade de histórico em desenvolvimento[/yellow]")
                continue

            # Processar mensagem
            resposta = bot.processar_mensagem(mensagem, user_id)

            # Exibir resposta
            console.print(f"[bold green]Assistente:[/bold green] {resposta}")

            # Log da interação
            logger.info(f"User: {mensagem[:50]}... | Bot: {resposta[:50]}...")

        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Encerrando...[/yellow]")
            break
        except Exception as e:
            logger.error(f"Erro no loop: {e}")
            console.print(f"[red]❌ Erro: {e}[/red]")
            console.print("[yellow]Continuando...[/yellow]")


def mostrar_informacoes():
    """Mostra informações do sistema"""
    console.print("\n[bold blue]ℹ️  INFORMAÇÕES DO SISTEMA:[/bold blue]")
    console.print("• Protocolos baseados em fluxograma médico")
    console.print("• 4 níveis de gravidade: Leve, Moderado, Intenso, Urgente")
    console.print("• Detecção automática de sintomas críticos")
    console.print("• Banco de dados SQLite para histórico")
    console.print("• Logs detalhados em data/logs/")


if __name__ == "__main__":
    if DEPENDENCIES_OK:
        main()
    else:
        print("Instale as dependências primeiro!")
