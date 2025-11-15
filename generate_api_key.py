"""
Script helper para gerar API Keys seguras
Usage: python generate_api_key.py [prefix]
"""
import sys
import secrets
def generate_api_key(prefix="sk"):
    """Gera uma API key aleatória e segura"""
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"
if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else "sk"
    print("🔑 API Key Generator")
    print("=" * 60)
    print(f"\nAPI Key gerada ({prefix}):")
    print(f"  {generate_api_key(prefix)}")
    print("\n💡 Adicione no seu .env:")
    print(f"  API_KEYS={generate_api_key(prefix)}")
    print("\n📝 Para múltiplas keys, separe por vírgula:")
    print(f"  API_KEYS={generate_api_key('dev')},{generate_api_key('prod')}")
    print("=" * 60)
