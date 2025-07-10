#!/usr/bin/env python3
"""
Teste isolado da detecção de sintomas críticos
"""

import re
import sys
from pathlib import Path

def detectar_sintomas_criticos_corrigido(texto: str) -> bool:
    """Versão corrigida da detecção"""
    texto_lower = texto.lower()
    
    padroes_criticos = [
        r"pensando em suicídio",
        r"pensando em suicidio", 
        r"quero (me )?matar",
        r"vou (me )?suicidar",
        r"quero morrer",
        r"não aguento mais",
        r"nao aguento mais",
        r"não suporto mais",
        r"cansei de viver",
        r"vou acabar com tudo",
        r"tentei me matar",
        r"escuto vozes",
        r"ouço vozes",
        r"vejo coisas",
        r"\bsuicídio\b",
        r"\bsuicidio\b",
    ]
    
    for padrao in padroes_criticos:
        if re.search(padrao, texto_lower):
            print(f"🚨 DETECTADO: '{padrao}' em '{texto}'")
            return True
    
    return False

def teste_completo():
    """Teste completo"""
    print("🧪 TESTE DE DETECÇÃO DE SINTOMAS CRÍTICOS")
    print("=" * 50)
    
    frases_teste = [
        "Estou pensando em suicídio",
        "Estou pensando em suicidio", 
        "Não aguento mais",
        "Quero morrer",
        "Quero me matar",
        "Vou me suicidar",
        "Olá, como vai?",  # Esta NÃO deve detectar
        "Estou triste",    # Esta NÃO deve detectar
    ]
    
    print("🔍 TESTANDO FRASES:")
    print("-" * 30)
    
    for frase in frases_teste:
        detectado = detectar_sintomas_criticos_corrigido(frase)
        status = "🚨 CRÍTICO" if detectado else "✅ Normal"
        print(f"{status}: '{frase}'")
    
    print("\n" + "=" * 50)
    
    # Teste específico da frase problema
    frase_problema = "Estou pensando em suicídio"
    detectado = detectar_sintomas_criticos_corrigido(frase_problema)
    
    if detectado:
        print(f"✅ CORREÇÃO FUNCIONOU!")
        print(f"✅ '{frase_problema}' foi detectado como crítico")
        print("🔧 Agora aplique esta correção no arquivo chatbot.py")
    else:
        print(f"❌ AINDA NÃO FUNCIONA!")
        print(f"❌ '{frase_problema}' NÃO foi detectado")
        print("🔧 Verifique os padrões regex")

def verificar_arquivo_atual():
    """Verificar se arquivo foi corrigido"""
    print("\n🔍 VERIFICANDO ARQUIVO ATUAL:")
    print("-" * 30)
    
    try:
        with open("src/chatbot.py", 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        if 'pensando em suicídio' in conteudo:
            print("✅ Arquivo contém 'pensando em suicídio'")
            print("✅ Correção aplicada!")
        else:
            print("❌ Arquivo NÃO contém 'pensando em suicídio'")
            print("❌ Correção NÃO foi aplicada!")
            print("\n🔧 APLIQUE A CORREÇÃO MANUALMENTE:")
            print("1. notepad src\\chatbot.py")
            print("2. Buscar: def detectar_sintomas_criticos")
            print("3. Substituir toda a função")
        
        # Verificar se função existe
        if 'def detectar_sintomas_criticos' in conteudo:
            print("✅ Função detectar_sintomas_criticos encontrada")
        else:
            print("❌ Função detectar_sintomas_criticos NÃO encontrada!")
    
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")

if __name__ == "__main__":
    teste_completo()
    verificar_arquivo_atual()
    
    print("\n🚨 URGENTE:")
    print("Se 'pensando em suicídio' não foi detectado,")
    print("EDITE MANUALMENTE o arquivo src/chatbot.py!")
    print("\n📱 Depois teste novamente: python main.py")