#!/usr/bin/env python3
"""
Corrigir erro de indentação no chatbot.py
"""

import re
import shutil
from pathlib import Path

def corrigir_indentacao():
    """Corrigir indentação da função detectar_sintomas_criticos"""
    
    arquivo = Path("src/chatbot.py")
    arquivo_backup = Path("src/chatbot.py.bkp2")
    
    print("🔧 CORRIGINDO INDENTAÇÃO...")
    print("=" * 40)
    
    # Backup
    shutil.copy2(arquivo, arquivo_backup)
    print("✅ Backup criado: src/chatbot.py.bkp2")
    
    # Ler arquivo
    with open(arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    # Encontrar função problemática
    inicio_funcao = None
    for i, linha in enumerate(linhas):
        if 'def detectar_sintomas_criticos(self, texto: str) -> bool:' in linha:
            inicio_funcao = i
            break
    
    if inicio_funcao is None:
        print("❌ Função não encontrada!")
        return False
    
    # Função corrigida com indentação correta (4 espaços)
    funcao_corrigida = [
        '    def detectar_sintomas_criticos(self, texto: str) -> bool:\n',
        '        """Detectar sintomas críticos - VERSÃO CORRIGIDA"""\n',
        '        texto_lower = texto.lower()\n',
        '        \n',
        '        padroes_criticos = [\n',
        '            r"pensando em suicídio",\n',
        '            r"pensando em suicidio",\n', 
        '            r"quero (me )?matar",\n',
        '            r"vou (me )?suicidar",\n',
        '            r"quero morrer",\n',
        '            r"não aguento mais",\n',
        '            r"nao aguento mais",\n',
        '            r"não suporto mais",\n',
        '            r"cansei de viver",\n',
        '            r"vou acabar com tudo",\n',
        '            r"tentei me matar",\n',
        '            r"escuto vozes",\n',
        '            r"ouço vozes",\n',
        '            r"vejo coisas",\n',
        '            r"\\bsuicídio\\b",\n',
        '            r"\\bsuicidio\\b",\n',
        '        ]\n',
        '        \n',
        '        for padrao in padroes_criticos:\n',
        '            if re.search(padrao, texto_lower):\n',
        '                logger.critical(f"🚨 PADRÃO CRÍTICO DETECTADO: \'{padrao}\' em \'{texto[:50]}...\'")\n',
        '                return True\n',
        '        \n',
        '        return False\n',
    ]
    
    # Encontrar fim da função (próxima função com mesma indentação)
    fim_funcao = None
    for i in range(inicio_funcao + 1, len(linhas)):
        linha = linhas[i]
        # Encontrar próxima função com indentação de classe (4 espaços)
        if linha.startswith('    def ') and i > inicio_funcao + 5:
            fim_funcao = i
            break
    
    if fim_funcao is None:
        # Não encontrou próxima função, ir até encontrar classe ou fim
        for i in range(inicio_funcao + 1, len(linhas)):
            if linhas[i].startswith('class ') or linhas[i].startswith('def '):
                fim_funcao = i
                break
        if fim_funcao is None:
            fim_funcao = len(linhas)
    
    print(f"📍 Função encontrada: linhas {inicio_funcao + 1} a {fim_funcao}")
    
    # Construir novo arquivo
    novas_linhas = (
        linhas[:inicio_funcao] +  # Antes da função
        funcao_corrigida +        # Função corrigida
        linhas[fim_funcao:]       # Depois da função
    )
    
    # Salvar arquivo corrigido
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.writelines(novas_linhas)
    
    print("✅ Indentação corrigida!")
    print("✅ Função detectar_sintomas_criticos reescrita")
    print("✅ Arquivo salvo")
    
    return True

def verificar_sintaxe():
    """Verificar se arquivo está com sintaxe correta"""
    print("\n🔍 VERIFICANDO SINTAXE...")
    print("-" * 30)
    
    try:
        import py_compile
        py_compile.compile('src/chatbot.py', doraise=True)
        print("✅ Sintaxe correta!")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def teste_rapido():
    """Teste rápido da correção"""
    print("\n🧪 TESTE RÁPIDO...")
    print("-" * 20)
    
    try:
        import sys
        sys.path.append('src')
        
        # Remover módulo se carregado
        if 'chatbot' in sys.modules:
            del sys.modules['chatbot']
        
        from chatbot import LlamaTriagemBot
        
        bot = LlamaTriagemBot()
        
        # Teste
        frase = "Estou pensando em suicídio"
        detectado = bot.detectar_sintomas_criticos(frase)
        
        if detectado:
            print(f"✅ SUCESSO: '{frase}' foi detectado!")
            print("🎉 Correção funcionando!")
        else:
            print(f"❌ FALHA: '{frase}' NÃO foi detectado!")
        
        return detectado
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("🔧 CORREÇÃO DE INDENTAÇÃO")
    print("Corrigindo erro: unindent does not match any outer indentation level")
    print("=" * 60)
    
    # Aplicar correção
    sucesso = corrigir_indentacao()
    
    if sucesso:
        # Verificar sintaxe
        sintaxe_ok = verificar_sintaxe()
        
        if sintaxe_ok:
            # Teste rápido
            funciona = teste_rapido()
            
            if funciona:
                print("\n🎉 CORREÇÃO COMPLETA!")
                print("✅ Indentação corrigida")
                print("✅ Sintaxe válida") 
                print("✅ Detecção funcionando")
                print("\n🚀 EXECUTE AGORA:")
                print("   python main.py")
                print("   Digite: 'Estou pensando em suicídio'")
                print("   Verifique @curai1bot")
            else:
                print("\n⚠️ Correção aplicada mas teste falhou")
                print("Execute python main.py para testar completo")
        else:
            print("\n❌ Ainda há erro de sintaxe")
            print("Verifique o arquivo manualmente")
    else:
        print("\n❌ Falha na correção")
        print("Edite o arquivo manualmente")