"""
Parser de threads de email
Separa múltiplos emails contidos em um único texto/arquivo
"""
import re
from typing import List, Dict, Optional
from datetime import datetime


class EmailThreadParser:
    """
    Detecta e separa múltiplos emails em um texto
    Suporta diversos formatos e delimitadores
    """
    
    def __init__(self):
        self.header_patterns = {
            'from': [
                r'^From:\s*(.+)$',
                r'^De:\s*(.+)$',
                r'^Remetente:\s*(.+)$',
                r'^Sender:\s*(.+)$',
            ],
            'to': [
                r'^To:\s*(.+)$',
                r'^Para:\s*(.+)$',
                r'^Destinatário:\s*(.+)$',
                r'^Recipient:\s*(.+)$',
            ],
            'subject': [
                r'^Subject:\s*(.+)$',
                r'^Assunto:\s*(.+)$',
                r'^Título:\s*(.+)$',
            ],
            'date': [
                r'^Date:\s*(.+)$',
                r'^Data:\s*(.+)$',
                r'^Enviado em:\s*(.+)$',
                r'^Sent:\s*(.+)$',
            ]
        }
        
        self.separator_patterns = [
            r'^-{3,}$',           # --- (3 ou mais hífens)
            r'^={3,}$',           # === (3 ou mais iguais)
            r'^\*{3,}$',          # *** (3 ou mais asteriscos)
            r'^_{3,}$',           # ___ (3 ou mais underlines)
            r'^#{3,}$',           # ### (3 ou mais hashtags)
        ]
        
        self.reply_patterns = [
            r'^Re:\s*',
            r'^RE:\s*',
            r'^Fwd:\s*',
            r'^FWD:\s*',
            r'^Encaminhado:\s*',
            r'^Resposta:\s*',
            r'^Reply:\s*',
        ]
    
    def parse(self, text: str) -> List[Dict]:
        """
        Parse texto e retorna lista de emails separados
        
        Args:
            text: Texto completo contendo um ou mais emails
            
        Returns:
            Lista de dicionários, cada um representando um email
        """
        if not text or len(text.strip()) < 10:
            return []
        
        emails = self._split_by_headers(text)
        
        if len(emails) <= 1:
            emails = self._split_by_separators(text)
        
        if len(emails) <= 1:
            emails = self._split_by_blank_lines(text)
        
        if len(emails) <= 1:
            return [{
                'email_number': 1,
                'from': None,
                'to': None,
                'subject': None,
                'date': None,
                'body': text.strip(),
                'headers_found': False,
                'parsing_method': 'single_block'
            }]
        
        return emails
    
    def _split_by_headers(self, text: str) -> List[Dict]:
        """Separa emails baseado em cabeçalhos (From:, To:, Subject:, Date:)"""
        lines = text.split('\n')
        emails = []
        current_email = None
        current_body_lines = []
        in_body = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            from_match = self._match_header(line_stripped, 'from')
            if from_match:
                if current_email:
                    current_email['body'] = '\n'.join(current_body_lines).strip()
                    emails.append(current_email)
                
                current_email = {
                    'email_number': len(emails) + 1,
                    'from': from_match,
                    'to': None,
                    'subject': None,
                    'date': None,
                    'body': '',
                    'headers_found': True,
                    'parsing_method': 'header_detection'
                }
                current_body_lines = []
                in_body = False
                continue
            
            if not current_email:
                continue
            
            to_match = self._match_header(line_stripped, 'to')
            if to_match:
                current_email['to'] = to_match
                continue
            
            subject_match = self._match_header(line_stripped, 'subject')
            if subject_match:
                current_email['subject'] = subject_match
                continue
            
            date_match = self._match_header(line_stripped, 'date')
            if date_match:
                current_email['date'] = date_match
                continue
            
            if not line_stripped and not in_body:
                in_body = True
                continue
            
            if in_body or (current_email['from'] and not line_stripped.startswith(('From:', 'To:', 'Subject:', 'Date:', 'De:', 'Para:', 'Assunto:', 'Data:'))):
                in_body = True
                current_body_lines.append(line)
        
        if current_email:
            current_email['body'] = '\n'.join(current_body_lines).strip()
            emails.append(current_email)
        
        return emails
    
    def _split_by_separators(self, text: str) -> List[Dict]:
        """Separa emails baseado em separadores visuais (---, ===, etc)"""
        lines = text.split('\n')
        emails = []
        current_block = []
        
        for line in lines:
            line_stripped = line.strip()
            
            is_separator = any(
                re.match(pattern, line_stripped, re.MULTILINE)
                for pattern in self.separator_patterns
            )
            
            if is_separator and current_block:
                body = '\n'.join(current_block).strip()
                if body and len(body) > 10:
                    emails.append({
                        'email_number': len(emails) + 1,
                        'from': self._extract_from_body(body),
                        'to': None,
                        'subject': self._extract_subject_from_body(body),
                        'date': None,
                        'body': body,
                        'headers_found': False,
                        'parsing_method': 'separator_detection'
                    })
                current_block = []
            else:
                current_block.append(line)
        
        if current_block:
            body = '\n'.join(current_block).strip()
            if body and len(body) > 10:
                emails.append({
                    'email_number': len(emails) + 1,
                    'from': self._extract_from_body(body),
                    'to': None,
                    'subject': self._extract_subject_from_body(body),
                    'date': None,
                    'body': body,
                    'headers_found': False,
                    'parsing_method': 'separator_detection'
                })
        
        return emails
    
    def _split_by_blank_lines(self, text: str) -> List[Dict]:
        """Separa emails baseado em múltiplas linhas vazias (3+)"""
        blocks = re.split(r'\n\s*\n\s*\n+', text)
        
        emails = []
        for block in blocks:
            block = block.strip()
            if block and len(block) > 50:  # Mínimo de 50 caracteres para ser um email
                emails.append({
                    'email_number': len(emails) + 1,
                    'from': self._extract_from_body(block),
                    'to': None,
                    'subject': self._extract_subject_from_body(block),
                    'date': None,
                    'body': block,
                    'headers_found': False,
                    'parsing_method': 'blank_line_detection'
                })
        
        return emails
    
    def _match_header(self, line: str, header_type: str) -> Optional[str]:
        """Verifica se uma linha corresponde a um cabeçalho específico"""
        patterns = self.header_patterns.get(header_type, [])
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_from_body(self, body: str) -> Optional[str]:
        """Tenta extrair o remetente do corpo do email"""
        lines = body.split('\n')[:5]  # Primeiras 5 linhas
        for line in lines:
            for pattern in self.header_patterns['from']:
                match = re.match(pattern, line.strip(), re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        return None
    
    def _extract_subject_from_body(self, body: str) -> Optional[str]:
        """Tenta extrair o assunto do corpo do email"""
        lines = body.split('\n')[:10]  # Primeiras 10 linhas
        for line in lines:
            for pattern in self.header_patterns['subject']:
                match = re.match(pattern, line.strip(), re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 5 and len(line) < 100:
                return line
        
        return None
    
    def get_summary(self, emails: List[Dict]) -> Dict:
        """Retorna um resumo da thread"""
        if not emails:
            return {
                'total_emails': 0,
                'has_headers': False,
                'parsing_methods': [],
                'subjects': []
            }
        
        return {
            'total_emails': len(emails),
            'has_headers': any(email.get('headers_found', False) for email in emails),
            'parsing_methods': list(set(email.get('parsing_method', 'unknown') for email in emails)),
            'subjects': [email.get('subject') for email in emails if email.get('subject')],
            'senders': [email.get('from') for email in emails if email.get('from')],
            'first_email_preview': emails[0]['body'][:100] + '...' if emails[0]['body'] else None
        }
