
BASE_URL="http://localhost:8000"

echo "🔍 Verificando endpoints da API..."
echo ""


echo "1. Testing Health Check..."
curl -s "$BASE_URL/api/classifier/health/" | python3 -m json.tool
echo ""
echo "---"
echo ""


echo "2. Testing Email Classification..."
curl -s -X POST "$BASE_URL/api/classifier/classify/" \
  -H "Content-Type: application/json" \
  -d '{"email_text": "Olá, preciso de ajuda urgente com o login do sistema. Não consigo acessar há 2 horas."}' \
  | python3 -m json.tool
echo ""
echo "---"
echo ""

echo "3. Testing Dashboard Overview..."
curl -s "$BASE_URL/api/analytics/dashboard/overview/?days=30" | python3 -m json.tool
echo ""
echo "---"
echo ""


echo "4. Testing Executive Summary..."
curl -s -X POST "$BASE_URL/api/classifier/summary/" \
  -H "Content-Type: application/json" \
  -d '{"email_text": "Prezados, gostaria de informar que o projeto está atrasado devido a problemas técnicos. Precisamos de mais 2 semanas para conclusão. O orçamento de R$ 15.000 está aprovado. Por favor, revisem os documentos antes da reunião de sexta-feira às 14h.", "max_sentences": 3}' \
  | python3 -m json.tool
echo ""
echo "---"
echo ""


echo "5. Testing Batch Email Processing..."
curl -s -X POST "$BASE_URL/api/classifier/batch/" \
  -H "Content-Type: application/json" \
  -d '{"emails": ["Olá, preciso de ajuda com o sistema.", "Obrigado pela ajuda!", "Quando teremos a reunião?"]}' \
  | python3 -m json.tool
echo ""

echo "✅ Testes concluídos!"
