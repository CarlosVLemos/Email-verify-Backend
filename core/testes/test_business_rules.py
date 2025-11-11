#!/usr/bin/env python3
"""
Script de teste para validar as regras de negócio do classificador de emails
"""
import os
import sys
import django

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from classifier.email_scripts import EmailClassifier, EmailResponseGenerator

def test_hybrid_classification():
    """
    Testa a classificação híbrida (regras de negócio + categorias detalhadas + tom + urgência)
    """
    classifier = EmailClassifier()
    response_generator = EmailResponseGenerator()
    
    # Casos de teste com análise completa
    test_emails = [
        {
            'text': 'URGENTE! Estou com um erro crítico no sistema. O servidor não responde!',
            'expected_category': 'Produtivo',
            'expected_tone': 'Negativo',
            'expected_urgency': 'Alta'
        },
        {
            'text': 'Gostaria de saber como atualizar meus dados no sistema. Poderia me ajudar?',
            'expected_category': 'Produtivo',
            'expected_tone': 'Neutro',
            'expected_urgency': 'Baixa'
        },
        {
            'text': 'Muito obrigado pela excelente ajuda de ontem! Resolveu completamente meu problema.',
            'expected_category': 'Improdutivo',
            'expected_tone': 'Positivo',
            'expected_urgency': 'Baixa'
        },
        {
            'text': 'Parabéns pelo sucesso do projeto! Ficamos muito satisfeitos com os resultados.',
            'expected_category': 'Improdutivo',
            'expected_tone': 'Positivo',
            'expected_urgency': 'Baixa'
        },
        {
            'text': 'Estou insatisfeito com o péssimo atendimento. Preciso de uma solução imediata!',
            'expected_category': 'Produtivo',
            'expected_tone': 'Negativo',
            'expected_urgency': 'Alta'
        },
        {
            'text': 'Qual o status do meu chamado #12345? Estou aguardando há uma semana.',
            'expected_category': 'Produtivo',
            'expected_tone': 'Neutro',
            'expected_urgency': 'Média'
        }
    ]
    
    print("🧪 TESTE HÍBRIDO - CLASSIFICADOR DE EMAILS")
    print("📋 Regras de Negócio + Categorias Detalhadas + Tom + Urgência")
    print("=" * 70)
    
    for i, email in enumerate(test_emails, 1):
        result = classifier.classify(email['text'])
        response = response_generator.generate_response(
            result['categoria'], 
            result['subcategoria'], 
            result['tom'], 
            result['urgencia']
        )
        
        # Verificações
        category_ok = "✅" if result['categoria'] == email['expected_category'] else "❌"
        tone_ok = "✅" if result['tom'] == email['expected_tone'] else "❌"
        urgency_ok = "✅" if result['urgencia'] == email['expected_urgency'] else "❌"
        
        print(f"\n{i}. TESTE: {email['text'][:60]}...")
        print(f"   📂 Categoria: {category_ok} {result['categoria']} (esperado: {email['expected_category']})")
        print(f"   🏷️  Subcategoria: {result['subcategoria']} | Business: {result['business_subcategory']}")
        print(f"   😊 Tom: {tone_ok} {result['tom']} (esperado: {email['expected_tone']})")
        print(f"   ⚡ Urgência: {urgency_ok} {result['urgencia']} (esperado: {email['expected_urgency']})")
        print(f"   🧠 Reasoning: {result.get('reasoning', 'N/A')}")
        print(f"   💬 Resposta: {response[:100]}...")
    
    print("\n" + "=" * 70)
    print("🎯 TESTE HÍBRIDO CONCLUÍDO!")
    print("✨ Funcionalidades implementadas:")
    print("   📈 REGRAS DE NEGÓCIO: Produtivo (requer ação) vs Improdutivo (sem ação)")
    print("   🏷️  SUBCATEGORIAS: Suporte, Dúvida, Solicitação, Agradecimento, etc.")
    print("   😊 ANÁLISE DE TOM: Positivo, Negativo, Neutro")
    print("   ⚡ DETECÇÃO DE URGÊNCIA: Alta, Média, Baixa")
    print("   💬 RESPOSTAS PERSONALIZADAS: Baseadas em todos os fatores acima")

if __name__ == '__main__':
    test_hybrid_classification()