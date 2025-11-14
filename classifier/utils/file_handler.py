"""
Utilitário para extração de texto de arquivos
"""
import logging
import pdfplumber
import docx

logger = logging.getLogger(__name__)


class FileTextExtractor:
    """Extrai texto de diferentes formatos de arquivo"""
    
    SUPPORTED_FORMATS = {
        '.pdf': 'PDF',
        '.txt': 'Text',
        '.docx': 'Word Document',
        '.doc': 'Word Document'
    }
    
    @classmethod
    def extract_text(cls, uploaded_file):
        """
        Extrai texto de arquivo enviado
        
        Args:
            uploaded_file: Arquivo do request.FILES
            
        Returns:
            tuple: (texto_extraído, erro)
        """
        try:
            filename = uploaded_file.name.lower()
            
            if filename.endswith('.pdf'):
                return cls._extract_from_pdf(uploaded_file)
            elif filename.endswith('.txt'):
                return cls._extract_from_txt(uploaded_file)
            elif filename.endswith(('.docx', '.doc')):
                return cls._extract_from_docx(uploaded_file)
            else:
                supported = ', '.join(cls.SUPPORTED_FORMATS.keys())
                return None, f'Formato não suportado. Use: {supported}'
                
        except Exception as e:
            logger.error(f"Erro ao processar {uploaded_file.name}: {e}")
            return None, f'Erro ao ler arquivo: {str(e)}'
    
    @staticmethod
    def _extract_from_pdf(uploaded_file):
        """Extrai texto de PDF"""
        text = ''
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        
        text = text.strip()
        if not text:
            return None, 'PDF vazio ou sem texto extraível'
        return text, None
    
    @staticmethod
    def _extract_from_txt(uploaded_file):
        """Extrai texto de TXT"""
        try:
            text = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            text = uploaded_file.read().decode('latin-1')
        
        text = text.strip()
        if not text:
            return None, 'Arquivo TXT vazio'
        return text, None
    
    @staticmethod
    def _extract_from_docx(uploaded_file):
        """Extrai texto de DOCX"""
        doc = docx.Document(uploaded_file)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        
        text = text.strip()
        if not text:
            return None, 'Documento Word vazio'
        return text, None
    
    @classmethod
    def is_supported(cls, filename):
        """Verifica se o formato é suportado"""
        return any(filename.lower().endswith(ext) for ext in cls.SUPPORTED_FORMATS.keys())
