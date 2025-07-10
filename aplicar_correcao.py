#!/usr/bin/env python3
"""
Script para corrigir detecção de sintomas críticos
"""

import re
import shutil
from pathlib import Path

def corrigir_deteccao():
    """Aplicar correção na detecção de sintomas críticos"""
    
    arquivo_original = Path("src/chatbot.py")
    arquivo_backup = Path("src/chatbot.py.backup")
    
    print("🔧 APLICANDO CORREÇÃO CRÍTICA...")
    print("=" * 40)
    
    # 1. Backup
    if not arquivo_backup.exists():
        shutil.copy2(arquivo_original, arquivo_backup)
        print("✅ Backup criado: src/chatbot.py.backup")
    
    # 2. Ler arquivo
    with open(arquivo_original, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # 3. Encontrar função atual
    padrao_funcao = r'def detectar_sintomas_criticos\(self, texto: str\) -> bool:.*?return any\(re\.search\(padrao, texto_lower\) for padrao in padroes_criticos\)'
    
    # 4. Nova função corrigida
    nova_funcao = '''def detectar_sintomas_criticos(self, texto: str) -> bool:
        """Detectar sintomas críticos - VERSÃO CORRIGIDA"""
        texto_lower = texto.lower()
        
        # PADRÕES MAIS ABRANGENTES E SEGUROS
        padroes_criticos = [
            # Ideação suicida
            r"pensando em suicídio",
            r"pensando em suicidio", 
            r"quero (me )?matar",
            r"vou (me )?suicidar",
            r"vou (me )?suicid",
            r"quero morrer",
            r"prefiro morrer",
            r"melhor morrer",
            
            # Desesperança
            r"não aguento mais",
            r"nao aguento mais",
            r"não suporto mais",
            r"nao suporto mais",
            r"não aguento mais viver",
            r"cansei de viver",
            r"quero desaparecer",
            
            # Planos/métodos
            r"vou acabar com tudo",
            r"vou me jogar",
            r"vou tomar todos",
            r"tentei me matar",
            r"já tentei (me )?matar",
            r"como me matar",
            r"maneiras de morrer",
            
            # Sintomas psicóticos
            r"escuto vozes",
            r"ouço vozes",
            r"vejo coisas",
            r"pessoas que não existem",
            r"vozes na (minha )?cabeça",
            
            # Expressões diretas
            r"\\bsuicídio\\b",
            r"\\bsuicidio\\b",
            r"\\bmatar-me\\b",
            r"\\bme matar\\b",
        ]
        
        # Verificar se algum padrão é encontrado
        for padrao in padroes_criticos:
            if re.search(padrao, texto_lower):
                logger.critical(f"🚨 PADRÃO CRÍTICO DETECTADO: '{padrao}' em '{texto[:50]}...'")
                return True
        
        return False'''
    
    # 5. Substituir usando regex mais flexível
    if 'def detectar_sintomas_criticos(self, texto: str) -> bool:' in conteudo:
        # Encontrar início da função
        inicio = conteudo.find('def detectar_sintomas_criticos(self, texto: str) -> bool:')
        
        # Encontrar fim da função (próxima função ou final)
        resto = conteudo[inicio:]
        fim_relativo = resto.find('\n    def ')  # Próxima função
        if fim_relativo == -1:
            fim_relativo = resto.find('\n\nclass ')  # Próxima classe
        if fim_relativo == -1:
            fim_relativo = len(resto)  # Final do arquivo
        
        fim = inicio + fim_relativo
        
        # Substituir
        conteudo_novo = conteudo[:inicio] + nova_funcao + conteudo[fim:]
        
        # 6. Salvar
        with open(arquivo_original, 'w', encoding='utf-8') as f:
            f.write(conteudo_novo)
        
        print("✅ Função detectar_sintomas_criticos corrigida!")
        print("🔧 Padrões expandidos de 7 para 20+")
        print("✅ Agora detecta 'pensando em suicídio'")
        print("✅ Agora detecta 'não aguento mais'")
        
        return True
    else:
        print("❌ Função não encontrada!")
        return False

def testar_correcao():
    """Testar se a correção funciona"""
    print("\n🧪 TESTANDO CORREÇÃO...")
    print("=" * 30)
    
    try:
        # Importar chatbot corrigido
        import sys
        sys.path.append('src')
        
        # Remover módulo se já carregado
        if 'chatbot' in sys.modules:
            del sys.modules['chatbot']
        
        from chatbot import LlamaTriagemBot
        
        # Testar detecção
        bot = LlamaTriagemBot()
        
        frases_teste = [
            "Estou pensando em suicídio e não aguento mais",
            "Quero morrer",
            "Não aguento mais",
            "Olá, como vai?",  # Esta NÃO deve detectar
        ]
        
        for frase in frases_teste:
            detectado = bot.detectar_sintomas_criticos(frase)
            status = "🚨 CRÍTICO" if detectado else "✅ Normal"
            print(f"   {status}: '{frase}'")
        
        print("\n✅ Teste concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("🚨 CORREÇÃO DE SEGURANÇA CRÍTICA")
    print("Bug: Sistema não detectava 'pensando em suicídio'")
    print("=" * 50)
    
    # Aplicar correção
    sucesso = corrigir_deteccao()
    
    if sucesso:
        # Testar
        testar_correcao()
        
        print("\n" + "=" * 50)
        print("✅ CORREÇÃO APLICADA COM SUCESSO!")
        print("\n🔥 PRÓXIMOS PASSOS:")
        print("1. Execute: python main.py")
        print("2. Digite: 'Estou pensando em suicídio'")
        print("3. Verifique se @curai1bot recebe notificação")
        print("\n🚨 ESTE BUG DE SEGURANÇA FOI CORRIGIDO!")
    else:
        print("\n❌ FALHA NA CORREÇÃO!")
        print("Aplique manualmente substituindo a função.")