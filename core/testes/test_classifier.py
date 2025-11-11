#!/usr/bin/env python3
"""
Script para testar a classificação de emails localmente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from classifier.views import EmailClassifierView

def test_email_classification():
    """Testa a classificação com alguns exemplos"""
    
    # Criar instância da view
    classifier_view = EmailClassifierView()
    
    # Emails de teste
    test_emails = [
        {
            'text': 'Olá, estou com um problema no sistema. Não consigo fazer login e preciso urgentemente acessar minha conta.',
            'expected': 'Suporte Técnico'
        },
        {
            'text': 'Muito obrigado pelo excelente atendimento! Vocês são incríveis e estou muito satisfeito.',
            'expected': 'Agradecimento'
        },
        {
            'text': 'Gostaria de saber como funciona o processo de devolução de produtos.',
            'expected': 'Dúvida'
        },
        {
            'text': 'GANHE DINHEIRO FÁCIL! CLIQUE AQUI AGORA! OFERTA LIMITADA!!!',
            'expected': 'Spam'
        },
        {
            'text': 'Estou muito insatisfeito com o serviço. O produto chegou quebrado e ninguém me ajuda.',
            'expected': 'Reclamação'
        }
    ]
    
    print("🧪 Testando classificação de emails...\n")
    
    for i, test_case in enumerate(test_emails, 1):
        print(f"📧 Teste {i}:")
        print(f"   Texto: {test_case['text'][:60]}...")
        print(f"   Esperado: {test_case['expected']}")
        
        try:
            # Executar classificação
            result = classifier_view.classify_with_keywords(test_case['text'])
            
            print(f"   ✅ Resultado:")
            print(f"      Subcategoria: {result['subcategoria']}")
            print(f"      Categoria: {result['categoria']}")
            print(f"      Tom: {result['tom']}")
            print(f"      Urgência: {result['urgencia']}")
            
            # Verificar se o resultado está correto
            if result['subcategoria'] == test_case['expected']:
                print(f"   ✅ SUCESSO!")
            else:
                print(f"   ⚠️  Diferente do esperado")
                
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
        
        print("-" * 60)

if __name__ == '__main__':
    test_email_classification()