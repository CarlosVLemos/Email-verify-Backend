#!/usr/bin/env python3
"""
Validação rápida das correções implementadas
"""
import os
import sys
import django

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from classifier.views import EmailClassifierView

def quick_validation():
    # Usa as novas classes diretamente da pasta email_scripts
    from classifier.email_scripts import EmailClassifier, EmailResponseGenerator
    
    classifier = EmailClassifier()
    response_generator = EmailResponseGenerator()
    
    # Casos críticos para validar as correções
    test_cases = [
        {
            'text': '''🚨 URGENTE: Parabéns, Você é Nosso Vencedor Sortudo! 🎉 Confirme Sua Recompensa AGORA!
            
            Prezado(a) Cliente, Temos uma notícia FANTÁSTICA para você! O seu endereço de e-mail foi sorteado entre milhares de participantes em nossa Promoção Anual de Fidelidade! Você foi o contemplado(a) com o GRANDE PRÊMIO de R$ 50.000,00 (Cinquenta Mil Reais) e um iPhone 15 Pro! Isso mesmo! Sua sorte mudou de vida! Para reivindicar esta recompensa incrível, você precisa confirmar os seus dados no prazo máximo de 24 HORAS. Esta é uma oportunidade ÚNICA e com prazo LIMITADO. Não deixe essa chance passar! 👉 CLIQUE AQUI PARA RESGATAR SEU PRÊMIO AGORA MESMO! 👈 https://www.sitefake-promoções-seguras.com/claim/prize789 ATENÇÃO: Devido ao alto valor do prêmio, é necessário uma pequena taxa de liberação de apenas R$ 49,90.''',
            'description': 'SPAM COMPLEXO (email real do usuário)',
            'expected_category': 'Improdutivo',
            'expected_subcategory': 'Spam'
        },
        {
            'text': 'GANHE MILHÕES! Clique aqui agora! Oferta limitada!!! $$$',
            'description': 'Spam simples',
            'expected_category': 'Improdutivo', 
            'expected_subcategory': 'Spam'
        },
        {
            'text': 'Parabéns pelo sucesso do projeto! Ficamos muito orgulhosos do trabalho da equipe.',
            'description': 'Felicitações legítimas',
            'expected_category': 'Produtivo',
            'expected_subcategory': 'Felicitações'
        },
        {
            'text': 'Muito obrigado pela ajuda de ontem. O problema foi resolvido.',
            'description': 'Agradecimento simples',
            'expected_category': 'Improdutivo',
            'expected_subcategory': 'Agradecimento'
        },
        {
            'text': 'URGENTE! Sistema fora do ar! Preciso de suporte imediato!',
            'description': 'Suporte técnico urgente',
            'expected_category': 'Produtivo',
            'expected_subcategory': 'Suporte Técnico'
        },
        {
            'text': 'Confira nossa nova promoção de produtos tecnológicos com desconto especial.',
            'description': 'Marketing legítimo',
            'expected_category': 'Improdutivo',
            'expected_subcategory': 'Marketing'
        }
    ]
    
    print("🔍 VALIDAÇÃO DA NOVA CLASSIFICAÇÃO HIERÁRQUICA")
    print("=" * 60)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        result = classifier.classify(case['text'])
        response = response_generator.generate_response(
            result['categoria'], 
            result['subcategoria'], 
            result['tom'], 
            result['urgencia']
        )
        
        # Verificações de acerto
        category_correct = result['categoria'] == case['expected_category']
        subcategory_correct = result['subcategoria'] == case['expected_subcategory'] 
        
        if category_correct and subcategory_correct:
            status = "✅ CORRETO"
            success_count += 1
        else:
            status = "❌ ERRO"
        
        print(f"\n{i}. {status} - {case['description']}")
        print(f"   📝 Texto: {case['text'][:70]}...")
        print(f"   📂 Categoria: {result['categoria']} (esperado: {case['expected_category']})")
        print(f"   🏷️  Subcategoria: {result['subcategoria']} (esperado: {case['expected_subcategory']})")
        print(f"   😊 Tom: {result['tom']} | ⚡ Urgência: {result['urgencia']}")
        
        if 'spam_score' in result:
            print(f"   🚨 Spam Score: {result['spam_score']}")
        if 'reasoning' in result:
            print(f"   🧠 Raciocínio: {result['reasoning']}")
            
        print(f"   💬 Resposta: {response[:100]}...")
    
    print(f"\n{'='*60}")
    print(f"🎯 RESULTADO: {success_count}/{total_count} casos corretos ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🚀 PERFEITO! Todos os casos foram classificados corretamente!")
        print("✨ A nova lógica hierárquica está funcionando como esperado.")
    else:
        print("⚠️  Alguns casos precisam de ajuste.")
    
    print("\n📋 RESUMO DA NOVA LÓGICA:")
    print("   1️⃣ PRIORIDADE: Detecta SPAM primeiro (evita falsos positivos)")  
    print("   2️⃣ MARKETING: Identifica conteúdo comercial como Improdutivo")
    print("   3️⃣ HIERARQUIA: Produtivo > Social > Improdutivo")
    print("   4️⃣ VALIDAÇÃO: Anti-spam em felicitações e agradecimentos")

if __name__ == '__main__':
    quick_validation()