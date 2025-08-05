import spacy
import logging
from typing import List, Dict
from app.exceptions.spacy_error import SpacyModelLoadError, SpacyProcessingError

class SpacyProcessor:
    def __init__(self, modelo="pt_core_news_sm"):
        """
        Inicializa o processador spaCy com modelo robusto e vocabulário otimizado para múltiplos setores.
        """
        try:
            self.nlp = spacy.load(modelo)
            logging.info(f"SPACY >>> Modelo spaCy '{modelo}' carregado com sucesso.")
        except OSError as e:
            logging.error(f"SPACY >>> Erro ao carregar o modelo spaCy: {e}")
            raise SpacyModelLoadError(f"Não foi possível carregar o modelo spaCy '{modelo}': {e}")

        # Dicionário expandido de sinônimos para múltiplos setores
        self.SINONIMOS = {
            # Tecnologia
            "celular": "smartphone", "telefone": "smartphone", "móvel": "smartphone",
            "computador": "notebook", "laptop": "notebook", "pc": "notebook",
            "tv": "televisão", "monitor": "televisão",
            "fone": "headphone", "headset": "headphone", "auscultador": "headphone",
            "app": "aplicativo", "software": "aplicativo", "programa": "aplicativo",
            
            # Saúde
            "médico": "doutor", "dr": "doutor", "doutora": "doutor", "dr": "profissional de saúde", "doutor": "profissional de saúde",
            "hospital": "clínica", "posto": "clínica", "consultório": "clínica",
            "remedio": "medicamento", "remédio": "medicamento",
            "psicologo": "profissional de saúde", "psicóloga": "profissional de saúde", "terapeuta": "profissional de saúde",
            "fisio": "fisioterapeuta", "fisioterapia": "fisioterapeuta", 
            "dentista": "odontólogo", "odonto": "odontólogo",
            "enfermeiro": "profissional de saúde", "enfermagem": "profissional de saúde",
            "nutricionista": "profissional de saúde", "nutri": "profissional de saúde",
            "consulta": "atendimento médico", "sessão": "atendimento médico", "exame": "procedimento médico",
            "posto de saúde": "unidade básica", "ubs": "unidade básica", "hospitalar": "internação",
            
            # Finanças
            "banco": "instituição financeira", "financiamento": "empréstimo",
            "crédito": "empréstimo", "dinheiro": "capital", "valor": "montante",
            
            # Varejo
            "loja": "estabelecimento", "mercado": "supermercado", "comercio": "comércio",
            "produto": "item", "mercadoria": "item",
            
            # RH
            "funcionário": "colaborador", "empregado": "colaborador", "trabalhador": "colaborador",
            "contratação": "admissão", "demissão": "rescisão",
            
            # Construção
            "obra": "construção", "casa": "residência", "prédio": "edifício",
            
            # Educação
            "escola": "instituição de ensino", "universidade": "faculdade", "professor": "docente",
            
            # Serviços
            "conserto": "reparo", "consertar": "reparo", "arrumar": "reparo",
            "manutenção": "reparo", "troca": "substituição", "substituir": "substituição",
            
            # Atendimento
            "falar": "contato", "conversar": "contato", "atendimento": "suporte",
            "ajuda": "suporte", "dúvida": "suporte", "problema": "suporte",
            
            # Geral
            "preço": "valor", "custo": "valor", "comprar": "venda", "adquirir": "venda"
        }

        # Palavras irrelevantes expandidas
        self.PALAVRAS_IRRELEVANTES = {
            "preciso", "quero", "gostaria", "de", "estou", "vou", "em", "para", 
            "a", "o", "na", "nao", "com", "por", "que", "como", "qual", "quando",
            "onde", "porque", "meu", "minha", "isso", "aquele", "algum", "todo"
        }

        # Substantivos irrelevantes expandidos
        self.SUBSTANTIVOS_IRRELEVANTES = {
            "casa", "ontem", "hoje", "amanhã", "dia", "semana", "mês", "ano",
            "lugar", "coisa", "pessoa", "momento", "vez", "tipo", "parte"
        }

        # Termos de negação importantes
        self.TERMOS_NEGACAO = {
            "não", "nem", "nunca", "jamais", "tampouco"
        }

    def process_message(self, mensagem: str) -> List[str]:
        """
        Processa a mensagem para extrair palavras-chave relevantes com técnicas avançadas.
        
        Args:
            mensagem (str): Mensagem a ser processada.

        Returns:
            List[str]: Lista de palavras-chave extraídas e normalizadas.
        """
        if self.nlp is None:
            logging.error("Modelo spaCy não carregado. Não é possível processar a mensagem.")
            raise SpacyModelLoadError("Modelo spaCy não carregado.")

        try:
            doc = self.nlp(mensagem.lower())
            palavras_chave = []
            
            # Primeiro verifica termos de negação
            tem_negacao = any(token.text in self.TERMOS_NEGACAO for token in doc)
            
            for token in doc:
                # Considera substantivos, verbos, adjetivos e entidades nomeadas
                if (token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"] or token.ent_type_) and not token.is_stop:
                    lemma = token.lemma_.lower()
                    
                    # Normaliza usando sinônimos ou mantém o lemma
                    palavra_normalizada = self.SINONIMOS.get(lemma, lemma)
                    
                    # Filtra palavras irrelevantes
                    if (palavra_normalizada not in self.PALAVRAS_IRRELEVANTES and
                        palavra_normalizada not in self.SUBSTANTIVOS_IRRELEVANTES):
                        
                        # Adiciona contexto de negação se necessário
                        if tem_negacao:
                            palavra_normalizada = f"não_{palavra_normalizada}"
                        
                        palavras_chave.append(palavra_normalizada)

            # Remove duplicatas mantendo a ordem
            palavras_chave = list(dict.fromkeys(palavras_chave))
            
            logging.debug(f"Palavras-chave extraídas: {palavras_chave}")
            return palavras_chave

        except Exception as e:
            logging.error(f"Erro ao processar a mensagem com spaCy: {e}")
            raise SpacyProcessingError(f"Erro ao processar a mensagem: {e}")

    def extrair_entidades(self, mensagem: str) -> Dict[str, List[str]]:
        """
        Extrai entidades nomeadas da mensagem com suporte para múltiplos setores.
        
        Args:
            mensagem (str): Mensagem a ser processada.
            
        Returns:
            Dict[str, List[str]]: Dicionário com tipos de entidades e seus valores.
        """
        try:
            doc = self.nlp(mensagem)
            entidades = {}
            
            for ent in doc.ents:
                if ent.label_ not in entidades:
                    entidades[ent.label_] = []
                
                # Normaliza o texto da entidade
                texto_entidade = self.SINONIMOS.get(ent.text.lower(), ent.text)
                entidades[ent.label_].append(texto_entidade)
            
            return entidades
        except Exception as e:
            logging.error(f"Erro ao extrair entidades: {e}")
            return {}

    def identificar_setor(self, mensagem: str) -> str:
        """
        Tenta identificar o setor/indústria mais relevante com base na mensagem.
        
        Args:
            mensagem (str): Mensagem a ser analisada.
            
        Returns:
            str: Setor identificado ou 'Outros' se não identificado.
        """
        palavras_chave = self.process_message(mensagem)
        entidades = self.extrair_entidades(mensagem)
        
        # Mapeamento de palavras-chave para setores
        setores = {
            'Tecnologia': ['smartphone', 'notebook', 'aplicativo', 'tecnologia', 'software'],
            'Saúde': ['doutor', 'medicamento', 'clínica', 'saúde', 'hospital'],
            'Finanças': ['banco', 'empréstimo', 'capital', 'finanças', 'pagamento'],
            'Varejo': ['loja', 'produto', 'venda', 'comércio', 'supermercado'],
            'RH': ['colaborador', 'admissão', 'rescisão', 'recrutamento'],
            'Construção': ['obra', 'construção', 'edifício', 'residência'],
            'Educação': ['escola', 'faculdade', 'docente', 'ensino']
        }
        
        # Contagem de ocorrências por setor
        contagem_setores = {setor: 0 for setor in setores}
        
        for palavra in palavras_chave:
            for setor, termos in setores.items():
                if palavra in termos:
                    contagem_setores[setor] += 1
        
        # Verifica o setor com maior contagem
        setor_identificado = max(contagem_setores.items(), key=lambda x: x[1])
        
        return setor_identificado[0] if setor_identificado[1] > 0 else 'Outros'