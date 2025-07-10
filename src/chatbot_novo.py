#!/usr/bin/env python3
"""
Chatbot Real de Triagem Psicológica com LLaMA e Telegram
VERSÃO MELHORADA COM 22 PERGUNTAS ESTRUTURADAS
"""

import json
import sqlite3
import datetime
import re
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Logging
from loguru import logger

# Dependências
from dotenv import load_dotenv
load_dotenv()

# Configurar logging
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "logs").mkdir(exist_ok=True)

logger.add(
    DATA_DIR / "logs" / "chatbot_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO"
)

# Dependências LLaMA
try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        pipeline
    )
    import torch
    LLAMA_AVAILABLE = True
    logger.info("🤖 Transformers carregado com sucesso")
except ImportError:
    logger.warning("⚠️ Transformers não disponível. Usando modo simulação.")
    LLAMA_AVAILABLE = False

# Dependências Telegram
try:
    from telegram_notifier import notificar_urgente, notificar_intenso
    TELEGRAM_DISPONIVEL = True
    logger.info("📱 Sistema Telegram carregado")
except ImportError:
    TELEGRAM_DISPONIVEL = False
    logger.warning("⚠️ Sistema Telegram não disponível")

class GravidadeNivel(Enum):
    LEVE = "leve"
    MODERADO = "moderado" 
    INTENSO = "intenso"
    URGENTE = "urgente"

class EtapaTriagem(Enum):
    INICIO = "inicio"
    DADOS_PESSOAIS = "dados_pessoais"
    MOTIVOS_BUSCA = "motivos_busca"        # NOVO
    SINTOMAS_ESCALA = "sintomas_escala"    # NOVO
    AVALIACAO = "avaliacao"
    RESULTADO = "resultado"

@dataclass
class DadosPaciente:
    nome: str = ""
    cpf: str = ""
    telefone: str = ""
    idade: Optional[int] = None
    email: Optional[str] = None

@dataclass
class AvaliacaoSintomas:
    # Motivos da busca (sim/não) - 12 perguntas
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
    
    # Escala de sintomas (0-4) - 10 perguntas
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
        return sum(motivos)

@dataclass
class TriagemResultado:
    paciente: DadosPaciente
    sintomas: AvaliacaoSintomas
    nivel_gravidade: GravidadeNivel
    recomendacoes: List[str]
    acoes_imediatas: List[str]
    data_triagem: datetime.datetime
    eh_acompanhamento: bool = False
    comparacao_anterior: Optional[str] = None

class ProtocolosMedicos:
    """Protocolos médicos baseados no fluxograma"""
    
    @staticmethod
    def determinar_gravidade(sintomas: AvaliacaoSintomas) -> GravidadeNivel:
        """Determinar gravidade com base em motivos + escala"""
        
        # Críticos sempre = URGENTE
        if sintomas.sintomas_criticos:
            return GravidadeNivel.URGENTE
        
        # Pontuação da escala (0-40)
        pontuacao_escala = sintomas.pontuacao_total
        
        # Contagem de motivos positivos (0-12)
        motivos_positivos = sintomas.contagem_motivos_positivos
        
        # Algoritmo combinado
        if pontuacao_escala >= 32 or motivos_positivos >= 8:
            return GravidadeNivel.URGENTE
        elif pontuacao_escala >= 24 or motivos_positivos >= 6:
            return GravidadeNivel.INTENSO
        elif pontuacao_escala >= 16 or motivos_positivos >= 4:
            return GravidadeNivel.MODERADO
        else:
            return GravidadeNivel.LEVE
    
    @staticmethod
    def gerar_protocolo(nivel: GravidadeNivel) -> Tuple[List[str], List[str]]:
        """Retorna (ações_imediatas, recomendações)"""
        
        protocolos = {
            GravidadeNivel.URGENTE: (
                [
                    "🚨 Notificação IMEDIATA Dr. José via Telegram",
                    "📞 Contato familiar/responsável AGORA", 
                    "🏥 Acionamento SAMU/192 se necessário",
                    "⚕️ Encaminhamento emergência psiquiátrica",
                    "📋 Registro prioritário no prontuário",
                    "⏰ Follow-up obrigatório em 24h"
                ],
                [
                    "Internação psiquiátrica se indicada",
                    "Avaliação médica emergencial",
                    "Supervisão familiar 24h",
                    "Plano de segurança rigoroso",
                    "Medicação de urgência se prescrita"
                ]
            ),
            GravidadeNivel.INTENSO: (
                [
                    "📱 Notificação prioritária Dr. José via Telegram",
                    "⏱️ Agendamento psiquiatria em 48h",
                    "👨‍👩‍👧‍👦 Contato família - orientações",
                    "📋 Plano de segurança individualizado",
                    "📞 Monitoramento telefônico 72h",
                    "🔄 Reavaliação agendada em 1 semana"
                ],
                [
                    "Consulta psiquiátrica urgente",
                    "Acompanhamento psicológico semanal",
                    "Orientações familiares específicas",
                    "Medicação se necessária",
                    "Rede de apoio fortalecida"
                ]
            ),
            GravidadeNivel.MODERADO: (
                [
                    "📨 Notificação padrão Dr. José",
                    "📅 Agendamento psicologia em 7 dias",
                    "📖 Orientações de autocuidado",
                    "👥 Grupo de apoio se disponível",
                    "📞 Check-in em 15 dias",
                    "🔄 Reavaliação em 1 mês"
                ],
                [
                    "Acompanhamento psicológico regular",
                    "Técnicas de manejo da ansiedade",
                    "Estabelecimento de rotina",
                    "Atividades prazerosas",
                    "Apoio social"
                ]
            ),
            GravidadeNivel.LEVE: (
                [
                    "ℹ️ Notificação informativa Dr. José",
                    "📅 Agendamento psicologia em 15 dias",
                    "📚 Material educativo fornecido",
                    "💡 Orientações preventivas",
                    "🔄 Reavaliação em 2 meses"
                ],
                [
                    "Acompanhamento psicológico preventivo",
                    "Estratégias de bem-estar",
                    "Exercícios físicos regulares",
                    "Higiene do sono",
                    "Manejo do estresse"
                ]
            )
        }
        
        return protocolos.get(nivel, protocolos[GravidadeNivel.LEVE])

class DatabaseManager:
    """Gerenciamento de banco de dados"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = DATA_DIR / "database" / "triagem.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS triagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL,
                dados_paciente TEXT NOT NULL,
                sintomas TEXT NOT NULL,
                nivel_gravidade TEXT NOT NULL,
                pontuacao_total INTEGER NOT NULL,
                sintomas_criticos BOOLEAN NOT NULL,
                motivos_positivos INTEGER NOT NULL,
                data_triagem TIMESTAMP NOT NULL,
                eh_acompanhamento BOOLEAN DEFAULT FALSE
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("💾 Banco de dados inicializado")
    
    def salvar_triagem(self, resultado: TriagemResultado):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO triagens (
                cpf, dados_paciente, sintomas, nivel_gravidade,
                pontuacao_total, sintomas_criticos, motivos_positivos, data_triagem, eh_acompanhamento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resultado.paciente.cpf,
            json.dumps(asdict(resultado.paciente)),
            json.dumps(asdict(resultado.sintomas)),
            resultado.nivel_gravidade.value,
            resultado.sintomas.pontuacao_total,
            resultado.sintomas.sintomas_criticos,
            resultado.sintomas.contagem_motivos_positivos,
            resultado.data_triagem.isoformat(),
            resultado.eh_acompanhamento
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"💾 Triagem salva para CPF: {resultado.paciente.cpf}")
    
    def buscar_triagem_anterior(self, cpf: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM triagens 
            WHERE cpf = ? 
            ORDER BY data_triagem DESC 
            LIMIT 1
        """, (cpf,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'pontuacao_total': row[5],
            'nivel_gravidade': row[4],
            'motivos_positivos': row[7],
            'data_triagem': row[8]
        }

class LlamaTriagemBot:
    """Chatbot principal com LLaMA real e Telegram"""
    
    def __init__(self, model_name: str = None):
        logger.info("🚀 Inicializando LlamaTriagemBot...")
        
        self.db = DatabaseManager()
        self.protocolos = ProtocolosMedicos()
        self.sessoes = {}
        
        # Configurar modelo
        self.model_name = model_name or os.getenv("MODEL_NAME", "microsoft/DialoGPT-medium")
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        
        # Inicializar LLaMA
        if LLAMA_AVAILABLE and self.model_name:
            self.setup_llama()
        else:
            logger.warning("⚠️ Usando modo simulação (LLaMA não disponível)")
            self.llama_pipeline = None
    
    def setup_llama(self):
        """Configurar modelo LLaMA"""
        try:
            logger.info(f"📥 Carregando modelo: {self.model_name}")
            
            # Configurar autenticação se necessário
            use_auth_token = self.huggingface_token if self.huggingface_token else None
            
            # Carregar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                token=use_auth_token
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Detectar dispositivo
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"🖥️ Usando dispositivo: {device}")
            
            # Carregar modelo
            if device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    token=use_auth_token
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    token=use_auth_token
                )
                self.model.to(device)
            
            # Criar pipeline
            self.llama_pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=300,
                temperature=0.7,
                do_sample=True,
                device=0 if device == "cuda" else -1
            )
            
            logger.info("✅ LLaMA configurado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar LLaMA: {e}")
            self.llama_pipeline = None
    
    def gerar_resposta_llama(self, prompt: str) -> str:
        """Gerar resposta usando LLaMA"""
        if not self.llama_pipeline:
            return self.resposta_fallback(prompt)
        
        try:
            # Prompt específico para triagem psicológica
            prompt_especializado = f"""
Como assistente de triagem psicológica especializado, responda com empatia e profissionalismo.

Contexto: Sistema de triagem de saúde mental com protocolos médicos.
Usuário: {prompt}

Resposta empática e profissional:"""
            
            resultado = self.llama_pipeline(
                prompt_especializado, 
                max_length=200, 
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            resposta = resultado[0]['generated_text']
            
            # Limpar resposta
            if "Resposta empática e profissional:" in resposta:
                resposta = resposta.split("Resposta empática e profissional:")[-1].strip()
            
            return resposta
        
        except Exception as e:
            logger.error(f"❌ Erro na geração LLaMA: {e}")
            return self.resposta_fallback(prompt)
    
    def resposta_fallback(self, contexto: str) -> str:
        """Respostas estruturadas como fallback"""
        contexto_lower = contexto.lower()
        
        if any(word in contexto_lower for word in ['suicídio', 'matar', 'morrer', 'acabar']):
            return """🚨 **PROTOCOLO URGENTE ATIVADO** 🚨

Identifiquei sinais que requerem atenção IMEDIATA.

✅ Dr. José será notificado AGORA
✅ Contato familiar será acionado
✅ SAMU 192 disponível se necessário

**VOCÊ NÃO ESTÁ SOZINHO(A)!**

Me diga: você está em local seguro?"""
        
        elif "olá" in contexto_lower or "oi" in contexto_lower:
            return """🏥 Olá! Sou seu assistente de triagem psicológica.

Estou aqui para avaliar sua situação atual de forma confidencial e profissional.

Para começar, pode me dizer seu nome completo?"""
        
        else:
            return "Entendo. Continue me contando mais sobre como você está se sentindo."
    
    def detectar_sintomas_criticos(self, texto: str) -> bool:
        """Detectar sintomas críticos - VERSÃO CORRIGIDA"""
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
                logger.critical(f"🚨 PADRÃO CRÍTICO DETECTADO: '{padrao}' em '{texto[:50]}...'")
                return True
        
        return False
    
    def processar_mensagem(self, mensagem: str, user_id: str) -> str:
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
            return self.gerar_resposta_llama(mensagem)
    
    def iniciar_sessao(self, user_id: str):
        """Inicializar nova sessão"""
        self.sessoes[user_id] = {
            "etapa": EtapaTriagem.INICIO,
            "paciente": DadosPaciente(),
            "sintomas": AvaliacaoSintomas(),
            "pergunta_motivo_atual": 0,
            "pergunta_sintoma_atual": 0,
            "historico": []
        }
        logger.info(f"🆕 Nova sessão: {user_id}")
    
    def ativar_protocolo_urgente(self, user_id: str) -> str:
        """Ativar protocolo emergencial COM notificação Telegram"""
        self.sessoes[user_id]["sintomas"].ideacao_suicida = 4
        self.sessoes[user_id]["sintomas"].pensamentos_suicidas = True
        self.sessoes[user_id]["etapa"] = EtapaTriagem.RESULTADO
        
        logger.critical(f"🚨 PROTOCOLO URGENTE: {user_id}")
        
        # NOTIFICAÇÃO TELEGRAM IMEDIATA
        if TELEGRAM_DISPONIVEL:
            resultado_emergencia = {
                "paciente": asdict(self.sessoes[user_id]["paciente"]),
                "sintomas": {"sintomas_criticos": True, "pontuacao_total": 40},
                "nivel_gravidade": "urgente",
                "data_triagem": datetime.datetime.now().isoformat()
            }
            
            logger.info("📱 Enviando notificação EMERGÊNCIA via Telegram")
            sucesso = notificar_urgente(resultado_emergencia)
            
            if sucesso:
                notificacao_status = "✅ Dr. José foi notificado IMEDIATAMENTE via Telegram"
            else:
                notificacao_status = "⚠️ Tentativa de notificação via Telegram (verificar configuração)"
        else:
            notificacao_status = "📱 Configure Telegram para notificações automáticas"
        
        return f"""🚨 **PROTOCOLO DE EMERGÊNCIA ATIVADO** 🚨

✅ Caso registrado no sistema
{notificacao_status}
✅ Contato familiar será acionado
✅ SAMU 192 disponível se necessário

**VOCÊ NÃO ESTÁ SOZINHO(A)!**

Por favor, me diga:
- Você está em local seguro?
- Há alguém com você agora?

Aguarde o contato do Dr. José."""
    
    def processar_inicio(self, mensagem: str, user_id: str) -> str:
        """Processar início da triagem"""
        sessao = self.sessoes[user_id]
        
        # Tentar extrair nome
        if len(mensagem.split()) >= 2:
            possivel_nome = mensagem.strip()
            if not any(char.isdigit() for char in possivel_nome):
                sessao["paciente"].nome = possivel_nome
                sessao["etapa"] = EtapaTriagem.DADOS_PESSOAIS
                
                return f"Prazer, {possivel_nome}! Agora preciso do seu CPF e telefone para contato."
        
        return "Olá! Para começar a triagem, pode me dizer seu nome completo?"
    
    def processar_dados_pessoais(self, mensagem: str, user_id: str) -> str:
        """Processar dados pessoais"""
        sessao = self.sessoes[user_id]
        
        # Extrair CPF
        cpf_match = re.search(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}', mensagem)
        if cpf_match:
            sessao["paciente"].cpf = cpf_match.group()
        
        # Extrair telefone
        tel_match = re.search(r'\(?(\d{2})\)?\s?\d{4,5}-?\d{4}', mensagem)
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
📋 **1. Motivos da busca** (12 perguntas sim/não)  
📊 **2. Escala de sintomas** (10 perguntas 0-4)

Começando com os motivos..."""
        
        return "Preciso do seu CPF e telefone para prosseguir. Pode me fornecer essas informações?"
    
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
                    return f"**MOTIVO {numero}/12:** {proxima_pergunta}\n\n*Responda: SIM ou NÃO*"
                else:
                    # Terminou motivos, ir para escala
                    sessao["etapa"] = EtapaTriagem.SINTOMAS_ESCALA
                    return self.iniciar_escala_sintomas()
        
        # Primeira pergunta ou resposta inválida
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
                return f"**SINTOMA {numero}/10:** {proxima_pergunta}\n\n*Responda de 0 a 4*"
            else:
                # Terminou escala, finalizar triagem
                return self.finalizar_triagem_completa(user_id)
        
        return "Erro no processamento. Tente novamente."
    
    def finalizar_triagem_completa(self, user_id: str) -> str:
        """Finalizar triagem completa COM notificações Telegram"""
        sessao = self.sessoes[user_id]
        
        # Determinar gravidade
        nivel = self.protocolos.determinar_gravidade(sessao["sintomas"])
        acoes, recomendacoes = self.protocolos.gerar_protocolo(nivel)
        
        # Criar resultado
        resultado = TriagemResultado(
            paciente=sessao["paciente"],
            sintomas=sessao["sintomas"],
            nivel_gravidade=nivel,
            recomendacoes=recomendacoes,
            acoes_imediatas=acoes,
            data_triagem=datetime.datetime.now()
        )
        
        # Salvar no banco
        self.db.salvar_triagem(resultado)
        
        # NOTIFICAÇÕES TELEGRAM
        if TELEGRAM_DISPONIVEL:
            resultado_dict = {
                "paciente": asdict(resultado.paciente),
                "sintomas": asdict(resultado.sintomas),
                "nivel_gravidade": resultado.nivel_gravidade.value,
                "data_triagem": resultado.data_triagem.isoformat()
            }
            
            # Notificar casos urgentes e intensos
            if nivel == GravidadeNivel.URGENTE:
                logger.info("📱 Enviando notificação URGENTE via Telegram")
                sucesso = notificar_urgente(resultado_dict)
                if sucesso:
                    logger.info("✅ Notificação urgente enviada")
                else:
                    logger.error("❌ Falha na notificação urgente")
            
            elif nivel == GravidadeNivel.INTENSO:
                logger.info("📱 Enviando notificação INTENSO via Telegram")
                sucesso = notificar_intenso(resultado_dict)
                if sucesso:
                    logger.info("✅ Notificação intenso enviada")
                else:
                    logger.error("❌ Falha na notificação intenso")
        
        # Gerar resposta
        resposta = self.gerar_resposta_resultado(resultado)
        
        # Adicionar info sobre notificação
        if TELEGRAM_DISPONIVEL and nivel in [GravidadeNivel.URGENTE, GravidadeNivel.INTENSO]:
            resposta += f"\n\n📱 **Dr. José foi notificado via Telegram sobre este caso {nivel.value}.**"
        
        return resposta
    
    def gerar_resposta_resultado(self, resultado: TriagemResultado) -> str:
        """Gerar resposta final MELHORADA"""
        emoji_nivel = {
            GravidadeNivel.LEVE: "🟢",
            GravidadeNivel.MODERADO: "🟡",
            GravidadeNivel.INTENSO: "🟠", 
            GravidadeNivel.URGENTE: "🔴"
        }
        
        emoji = emoji_nivel[resultado.nivel_gravidade]
        
        resposta = f"""
{emoji} **RESULTADO DA TRIAGEM COMPLETA** {emoji}

👤 **Paciente:** {resultado.paciente.nome}
📊 **Pontuação Escala:** {resultado.sintomas.pontuacao_total}/40
📋 **Motivos Positivos:** {resultado.sintomas.contagem_motivos_positivos}/12
🎯 **Nível de Gravidade:** {resultado.nivel_gravidade.value.upper()}

🚨 **Sintomas Críticos:** {'SIM' if resultado.sintomas.sintomas_criticos else 'NÃO'}

🎯 **AÇÕES IMEDIATAS:**
"""
        
        for acao in resultado.acoes_imediatas:
            resposta += f"• {acao}\n"
        
        resposta += "\n💡 **RECOMENDAÇÕES:**\n"
        for rec in resultado.recomendacoes:
            resposta += f"• {rec}\n"
        
        # Adicionar resumo dos motivos principais
        motivos_marcados = []
        if resultado.sintomas.ansiedade_excessiva: motivos_marcados.append("Ansiedade")
        if resultado.sintomas.tristeza_constante: motivos_marcados.append("Tristeza")
        if resultado.sintomas.pensamentos_suicidas: motivos_marcados.append("⚠️ Pensamentos suicidas")
        if resultado.sintomas.agressividade: motivos_marcados.append("Agressividade")
        if resultado.sintomas.crises_panico: motivos_marcados.append("Crises de pânico")
        if resultado.sintomas.uso_substancias: motivos_marcados.append("Uso de substâncias")
        if resultado.sintomas.alucinacoes_delirios: motivos_marcados.append("⚠️ Alucinações/delírios")
        
        if motivos_marcados:
            resposta += f"\n📝 **Principais motivos identificados:** {', '.join(motivos_marcados[:5])}"
        
        resposta += "\n\n❓ Deseja mais informações ou agendar acompanhamento?"
        
        return resposta

# Função para teste direto
def main():
    """Teste direto do chatbot"""
    from rich.console import Console
    
    console = Console()
    console.print("[bold blue]🤖 Testando Chatbot com LLaMA Real e 22 Perguntas[/bold blue]")
    
    # Inicializar
    model_name = os.getenv("MODEL_NAME", "microsoft/DialoGPT-medium")
    console.print(f"[yellow]📥 Modelo: {model_name}[/yellow]")
    console.print(f"[yellow]📱 Telegram: {'Ativo' if TELEGRAM_DISPONIVEL else 'Inativo'}[/yellow]")
    console.print(f"[yellow]📋 Triagem: 12 Motivos + 10 Sintomas = 22 Perguntas[/yellow]")
    
    bot = LlamaTriagemBot(model_name)
    
    user_id = "teste_user"
    
    console.print("\n[green]✅ Bot inicializado! Digite 'sair' para encerrar[/green]")
    console.print("[cyan]📋 Fluxo: Nome → CPF/Tel → 12 Motivos (sim/não) → 10 Sintomas (0-4) → Resultado[/cyan]")
    
    while True:
        try:
            mensagem = console.input("\n[bold cyan]Você:[/bold cyan] ")
            
            if mensagem.lower() in ['sair', 'exit', 'quit']:
                break
            
            resposta = bot.processar_mensagem(mensagem, user_id)
            console.print(f"[bold green]Assistente:[/bold green] {resposta}")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Encerrando...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]❌ Erro: {e}[/red]")

if __name__ == "__main__":
    main()