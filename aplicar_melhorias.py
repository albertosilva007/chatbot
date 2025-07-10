#!/usr/bin/env python3
"""
Script para aplicar melhorias na triagem:
- Motivos da busca (12 perguntas sim/não)
- Escala de sintomas (10 perguntas 0-4)
- Mantém detecção de emergência funcionando
"""

import shutil
import re
from pathlib import Path
from datetime import datetime

def fazer_backup():
    """Fazer backup do arquivo atual"""
    arquivo_original = Path("src/chatbot.py")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_backup = Path(f"src/chatbot_backup_{timestamp}.py")
    
    shutil.copy2(arquivo_original, arquivo_backup)
    print(f"✅ Backup criado: {arquivo_backup}")
    return arquivo_backup

def aplicar_melhorias():
    """Aplicar todas as melhorias"""
    
    print("🚀 APLICANDO MELHORIAS NA TRIAGEM")
    print("=" * 50)
    print("📋 Adicionando:")
    print("   • Motivos da busca (12 perguntas sim/não)")
    print("   • Escala de sintomas (10 perguntas 0-4)")
    print("   • Detecção crítica aprimorada")
    print("=" * 50)
    
    # 1. Backup
    backup_file = fazer_backup()
    
    # 2. Ler arquivo atual
    with open("src/chatbot.py", 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # 3. Substituições
    print("\n🔧 Aplicando modificações...")
    
    # 3.1 Atualizar EtapaTriagem
    conteudo = re.sub(
        r'class EtapaTriagem\(Enum\):.*?RESULTADO = "resultado"',
        '''class EtapaTriagem(Enum):
    INICIO = "inicio"
    DADOS_PESSOAIS = "dados_pessoais"
    MOTIVOS_BUSCA = "motivos_busca"        # NOVO
    SINTOMAS_ESCALA = "sintomas_escala"    # NOVO
    AVALIACAO = "avaliacao"
    RESULTADO = "resultado"''',
        conteudo,
        flags=re.DOTALL
    )
    print("   ✅ EtapaTriagem atualizada")
    
    # 3.2 Atualizar AvaliacaoSintomas
    nova_classe_sintomas = '''@dataclass
class AvaliacaoSintomas:
    # Motivos da busca (sim/não)
    ansiedade_excessiva: bool = False
    tristeza_constante: bool = False
    pensamentos_suicidas: bool = False      # ⚠️ CRÍTICO
    agressividade: bool = False
    crises_panico: bool = False
    uso_substancias: bool = False
    alucinacoes_delirios: bool = False      # ⚠️ CRÍTICO
    problemas_sono: bool = False
    problemas_alimentares: bool = False
    luto_recente: bool = False
    violencia_domestica: bool = False       # ⚠️ CRÍTICO
    dificuldade_relacionamentos: bool = False
    
    # Escala de sintomas (0-4)
    ansiedade: int = 0
    tristeza: int = 0
    irritabilidade: int = 0
    insonia: int = 0
    ideacao_suicida: int = 0               # ⚠️ CRÍTICO
    tentativa_suicidio: int = 0            # ⚠️ CRÍTICO
    alucinacoes: int = 0                   # ⚠️ CRÍTICO
    choro: int = 0
    isolamento: int = 0
    abuso_substancias: int = 0
    
    @property
    def pontuacao_total(self) -> int:
        """Pontuação total da escala (0-40)"""
        return (self.ansiedade + self.tristeza + self.irritabilidade + 
                self.insonia + self.ideacao_suicida + self.tentativa_suicidio +
                self.alucinacoes + self.choro + self.isolamento + self.abuso_substancias)
    
    @property
    def sintomas_criticos(self) -> bool:
        """Verifica sintomas críticos"""
        return (self.pensamentos_suicidas or 
                self.alucinacoes_delirios or 
                self.violencia_domestica or
                self.ideacao_suicida > 2 or
                self.tentativa_suicidio > 0 or
                self.alucinacoes > 2)
    
    @property
    def contagem_motivos_positivos(self) -> int:
        """Conta motivos marcados como sim"""
        motivos = [
            self.ansiedade_excessiva, self.tristeza_constante, 
            self.pensamentos_suicidas, self.agressividade,
            self.crises_panico, self.uso_substancias,
            self.alucinacoes_delirios, self.problemas_sono,
            self.problemas_alimentares, self.luto_recente,
            self.violencia_domestica, self.dificuldade_relacionamentos
        ]
        return sum(motivos)'''
    
    # Encontrar e substituir classe AvaliacaoSintomas
    padrao_classe = r'@dataclass\s*class AvaliacaoSintomas:.*?(?=@dataclass|class [A-Z])'
    conteudo = re.sub(padrao_classe, nova_classe_sintomas + '\n\n', conteudo, flags=re.DOTALL)
    print("   ✅ AvaliacaoSintomas expandida")
    
    # 3.3 Adicionar novas funções antes da classe LlamaTriagemBot
    novas_funcoes = '''
    def processar_motivos_busca(self, mensagem: str, user_id: str) -> str:
        """Processar motivos da busca (12 perguntas sim/não)"""
        sessao = self.sessoes[user_id]
        
        # Lista de perguntas
        perguntas_motivos = [
            ("ansiedade_excessiva", "Você tem sentido ansiedade excessiva?"),
            ("tristeza_constante", "Você tem sentido tristeza constante?"),
            ("pensamentos_suicidas", "⚠️ Você tem tido pensamentos suicidas?"),
            ("agressividade", "Você tem sentido agressividade?"),
            ("crises_panico", "Você tem tido crises de pânico?"),
            ("uso_substancias", "Você tem feito uso de substâncias (álcool/drogas)?"),
            ("alucinacoes_delirios", "⚠️ Você tem tido alucinações ou delírios?"),
            ("problemas_sono", "Você tem problemas de sono?"),
            ("problemas_alimentares", "Você tem problemas alimentares?"),
            ("luto_recente", "Você passou por um luto recente?"),
            ("violencia_domestica", "⚠️ Você sofreu violência doméstica?"),
            ("dificuldade_relacionamentos", "Você tem dificuldades nos relacionamentos?")
        ]
        
        # Verificar resposta sim/não
        resposta_lower = mensagem.lower().strip()
        resposta_bool = None
        
        if resposta_lower in ['sim', 's', 'yes', 'y', '1']:
            resposta_bool = True
        elif resposta_lower in ['não', 'nao', 'n', 'no', '0']:
            resposta_bool = False
        
        if resposta_bool is not None:
            # Salvar resposta
            if 'pergunta_motivo_atual' not in sessao:
                sessao['pergunta_motivo_atual'] = 0
            
            if sessao['pergunta_motivo_atual'] < len(perguntas_motivos):
                campo, _ = perguntas_motivos[sessao['pergunta_motivo_atual']]
                setattr(sessao["sintomas"], campo, resposta_bool)
                sessao['pergunta_motivo_atual'] += 1
                
                # Verificar emergência em tempo real
                if resposta_bool and campo in ['pensamentos_suicidas', 'alucinacoes_delirios', 'violencia_domestica']:
                    logger.critical(f"🚨 MOTIVO CRÍTICO DETECTADO: {campo}")
                    return self.ativar_protocolo_urgente(user_id)
                
                # Próxima pergunta ou avançar
                if sessao['pergunta_motivo_atual'] < len(perguntas_motivos):
                    proxima_pergunta = perguntas_motivos[sessao['pergunta_motivo_atual']][1]
                    numero = sessao['pergunta_motivo_atual'] + 1
                    return f"**MOTIVO {numero}/12:** {proxima_pergunta}\\n\\n*Responda: SIM ou NÃO*"
                else:
                    # Terminou motivos, ir para escala
                    sessao["etapa"] = EtapaTriagem.SINTOMAS_ESCALA
                    sessao['pergunta_sintoma_atual'] = 0
                    return self.iniciar_escala_sintomas()
        
        # Primeira pergunta ou resposta inválida
        if 'pergunta_motivo_atual' not in sessao:
            sessao['pergunta_motivo_atual'] = 0
        
        pergunta_atual = perguntas_motivos[sessao['pergunta_motivo_atual']][1]
        numero = sessao['pergunta_motivo_atual'] + 1
        
        return f"""📋 **MOTIVOS DA BUSCA**

Vou fazer 12 perguntas sobre o que te trouxe aqui.
Responda apenas **SIM** ou **NÃO** para cada uma.

**MOTIVO {numero}/12:** {pergunta_atual}

*Responda: SIM ou NÃO*"""

    def iniciar_escala_sintomas(self) -> str:
        """Iniciar escala de sintomas"""
        return """📊 **ESCALA DE SINTOMAS**

Agora vou avaliar a intensidade dos seus sintomas.
Para cada pergunta, responda de **0 a 4**:

• **0** = Nada/Nunca
• **1** = Pouco/Raramente  
• **2** = Moderado/Às vezes
• **3** = Bastante/Frequentemente
• **4** = Muito/Sempre

**SINTOMA 1/10:** Qual o nível da sua ansiedade nas últimas 2 semanas?

*Responda de 0 a 4*"""

    def processar_sintomas_escala(self, mensagem: str, user_id: str) -> str:
        """Processar escala de sintomas (10 perguntas 0-4)"""
        sessao = self.sessoes[user_id]
        
        # Lista de perguntas da escala
        perguntas_escala = [
            ("ansiedade", "Qual o nível da sua ansiedade nas últimas 2 semanas?"),
            ("tristeza", "Qual o nível da sua tristeza/depressão?"),
            ("irritabilidade", "Qual o nível da sua irritabilidade?"),
            ("insonia", "Qual o nível dos seus problemas de sono?"),
            ("ideacao_suicida", "⚠️ Qual a intensidade de pensamentos sobre morte/suicídio?"),
            ("tentativa_suicidio", "⚠️ Já tentou se machucar ou se matar? (0=nunca, 4=recentemente)"),
            ("alucinacoes", "⚠️ Qual a frequência de ver/ouvir coisas que outros não veem?"),
            ("choro", "Qual a frequência de episódios de choro?"),
            ("isolamento", "Qual o nível do seu isolamento social?"),
            ("abuso_substancias", "Qual o nível do uso de álcool/drogas?")
        ]
        
        # Verificar resposta 0-4
        try:
            pontuacao = int(mensagem.strip())
            if pontuacao < 0 or pontuacao > 4:
                raise ValueError
        except (ValueError, TypeError):
            return "Por favor, responda apenas com um número de **0 a 4**."
        
        # Salvar resposta
        if 'pergunta_sintoma_atual' not in sessao:
            sessao['pergunta_sintoma_atual'] = 0
        
        if sessao['pergunta_sintoma_atual'] < len(perguntas_escala):
            campo, _ = perguntas_escala[sessao['pergunta_sintoma_atual']]
            setattr(sessao["sintomas"], campo, pontuacao)
            sessao['pergunta_sintoma_atual'] += 1
            
            # Verificar emergência em tempo real
            if campo in ['ideacao_suicida', 'tentativa_suicidio', 'alucinacoes'] and pontuacao >= 3:
                logger.critical(f"🚨 SINTOMA CRÍTICO DETECTADO: {campo} = {pontuacao}")
                return self.ativar_protocolo_urgente(user_id)
            
            # Próxima pergunta ou finalizar
            if sessao['pergunta_sintoma_atual'] < len(perguntas_escala):
                proxima_pergunta = perguntas_escala[sessao['pergunta_sintoma_atual']][1]
                numero = sessao['pergunta_sintoma_atual'] + 1
                return f"**SINTOMA {numero}/10:** {proxima_pergunta}\\n\\n*Responda de 0 a 4*"
            else:
                # Terminou escala, finalizar triagem
                return self.finalizar_triagem_completa(user_id)
        
        return "Erro no processamento. Tente novamente."
'''
    
    # Adicionar as novas funções antes de finalizar_triagem_completa
    conteudo = conteudo.replace(
        '    def finalizar_triagem_completa(self, user_id: str) -> str:',
        novas_funcoes + '\n    def finalizar_triagem_completa(self, user_id: str) -> str:'
    )
    print("   ✅ Novas funções adicionadas")
    
    # 3.4 Atualizar processar_mensagem para incluir novas etapas
    novo_processar_mensagem = '''    def processar_mensagem(self, mensagem: str, user_id: str) -> str:
        """Processar mensagem seguindo o fluxograma MELHORADO"""
        
        # Inicializar sessão
        if user_id not in self.sessoes:
            self.iniciar_sessao(user_id)
        
        sessao = self.sessoes[user_id]
        
        # Log da mensagem
        logger.info(f"📨 Mensagem de {user_id}: {mensagem[:50]}...")
        
        # Verificar sintomas críticos SEMPRE
        if self.detectar_sintomas_criticos(mensagem):
            return self.ativar_protocolo_urgente(user_id)
        
        # Processar baseado na etapa
        etapa = sessao["etapa"]
        
        if etapa == EtapaTriagem.INICIO:
            return self.processar_inicio(mensagem, user_id)
        elif etapa == EtapaTriagem.DADOS_PESSOAIS:
            return self.processar_dados_pessoais(mensagem, user_id)
        elif etapa == EtapaTriagem.MOTIVOS_BUSCA:          # NOVO
            return self.processar_motivos_busca(mensagem, user_id)
        elif etapa == EtapaTriagem.SINTOMAS_ESCALA:        # NOVO
            return self.processar_sintomas_escala(mensagem, user_id)
        else:
            # Usar LLaMA para resposta geral
            return self.gerar_resposta_llama(mensagem)'''
    
    # Substituir processar_mensagem
    conteudo = re.sub(
        r'    def processar_mensagem\(self, mensagem: str, user_id: str\) -> str:.*?return self\.gerar_resposta_llama\(mensagem\)',
        novo_processar_mensagem,
        conteudo,
        flags=re.DOTALL
    )
    print("   ✅ processar_mensagem atualizada")
    
    # 3.5 Atualizar processar_dados_pessoais
    novo_processar_dados = '''    def processar_dados_pessoais(self, mensagem: str, user_id: str) -> str:
        """Processar dados pessoais"""
        sessao = self.sessoes[user_id]
        
        # Extrair CPF
        cpf_match = re.search(r'\\d{3}\\.?\\d{3}\\.?\\d{3}-?\\d{2}', mensagem)
        if cpf_match:
            sessao["paciente"].cpf = cpf_match.group()
        
        # Extrair telefone
        tel_match = re.search(r'\\(?\\(\\d{2}\\)\\)?\\s?\\d{4,5}-?\\d{4}', mensagem)
        if tel_match:
            sessao["paciente"].telefone = tel_match.group()
        
        if sessao["paciente"].cpf and sessao["paciente"].telefone:
            sessao["etapa"] = EtapaTriagem.MOTIVOS_BUSCA  # MUDANÇA: ir para motivos
            
            # Verificar acompanhamento
            triagem_anterior = self.db.buscar_triagem_anterior(sessao["paciente"].cpf)
            if triagem_anterior:
                sessao["eh_acompanhamento"] = True
                return """Vejo que você já fez triagem conosco. 

Vou fazer uma nova avaliação para acompanhar sua evolução.

Começando com os motivos que te trouxeram aqui hoje..."""
            
            return """Obrigado pelos dados!

Agora vou fazer uma avaliação completa em 2 etapas:
1. **Motivos da busca** (12 perguntas sim/não)  
2. **Escala de sintomas** (10 perguntas 0-4)

Começando com os motivos..."""
        
        return "Preciso do seu CPF e telefone para prosseguir. Pode me fornecer essas informações?"'''
    
    # Substituir processar_dados_pessoais
    conteudo = re.sub(
        r'    def processar_dados_pessoais\(self, mensagem: str, user_id: str\) -> str:.*?return "Preciso do seu CPF.*?"',
        novo_processar_dados,
        conteudo,
        flags=re.DOTALL
    )
    print("   ✅ processar_dados_pessoais atualizada")
    
    # 4. Salvar arquivo modificado
    with open("src/chatbot.py", 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("\n✅ MELHORIAS APLICADAS COM SUCESSO!")
    return True

def verificar_aplicacao():
    """Verificar se aplicação foi bem-sucedida"""
    print("\n🔍 VERIFICANDO APLICAÇÃO...")
    print("-" * 30)
    
    try:
        with open("src/chatbot.py", 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        verificacoes = [
            ("MOTIVOS_BUSCA", "MOTIVOS_BUSCA" in conteudo),
            ("SINTOMAS_ESCALA", "SINTOMAS_ESCALA" in conteudo),
            ("processar_motivos_busca", "def processar_motivos_busca" in conteudo),
            ("processar_sintomas_escala", "def processar_sintomas_escala" in conteudo),
            ("ansiedade_excessiva", "ansiedade_excessiva" in conteudo),
            ("contagem_motivos_positivos", "contagem_motivos_positivos" in conteudo)
        ]
        
        todas_ok = True
        for nome, check in verificacoes:
            status = "✅" if check else "❌"
            print(f"   {status} {nome}")
            if not check:
                todas_ok = False
        
        return todas_ok
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def testar_sintaxe():
    """Testar se arquivo tem sintaxe válida"""
    print("\n🧪 TESTANDO SINTAXE...")
    print("-" * 20)
    
    try:
        import py_compile
        py_compile.compile('src/chatbot.py', doraise=True)
        print("✅ Sintaxe válida!")
        return True
    except Exception as e:
        print(f"❌ Erro de sintaxe: {e}")
        return False

if __name__ == "__main__":
    print("🚀 APLICANDO MELHORIAS NA TRIAGEM PSICOLÓGICA")
    print("=" * 60)
    print("📋 NOVAS FUNCIONALIDADES:")
    print("   • 12 Motivos da busca (sim/não)")
    print("   • 10 Escalas de sintomas (0-4)")
    print("   • Detecção crítica aprimorada")
    print("   • Algoritmo de gravidade melhorado")
    print("=" * 60)
    
    # Aplicar melhorias
    sucesso = aplicar_melhorias()
    
    if sucesso:
        # Verificar aplicação
        verificacao_ok = verificar_aplicacao()
        
        if verificacao_ok:
            # Testar sintaxe
            sintaxe_ok = testar_sintaxe()
            
            if sintaxe_ok:
                print("\n🎉 MELHORIAS APLICADAS COM SUCESSO!")
                print("=" * 40)
                print("✅ Backup criado")
                print("✅ Código modificado")
                print("✅ Verificação passou")
                print("✅ Sintaxe válida")
                print("\n🚀 PRÓXIMOS PASSOS:")
                print("1. python main.py")
                print("2. Testar triagem completa")
                print("3. Verificar @curai1bot")
                print("\n📋 NOVA TRIAGEM:")
                print("   Nome → CPF/Tel → 12 Motivos → 10 Sintomas → Resultado")
            else:
                print("\n❌ Erro de sintaxe detectado")
                print("Verifique o arquivo manualmente")
        else:
            print("\n❌ Verificação falhou")
            print("Algumas funcionalidades podem não ter sido aplicadas")
    else:
        print("\n❌ Falha na aplicação das melhorias")
        print("Tente aplicar manualmente")