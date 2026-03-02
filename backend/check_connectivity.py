import os
import requests
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

def check():
    print("--- Connectivity Check ---")
    
    # 1. Check Qdrant
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    print(f"Checking Qdrant: {url}...")
    try:
        client = QdrantClient(url=url, api_key=api_key, timeout=10)
        collections = client.get_collections()
        print(f"✅ Qdrant Connected! Found {len(collections.collections)} collections.")
    except Exception as e:
        print(f"❌ Qdrant Connection Failed: {e}")

    # 2. Check Groq
    groq_key = os.getenv("GROQ_API_KEY")
    print("\nChecking Groq API...")
    if not groq_key:
        print("❌ Groq API Key missing in .env")
    else:
        try:
            resp = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {groq_key}"},
                timeout=10
            )
            if resp.status_code == 200:
                print("✅ Groq API Key is valid!")
            else:
                print(f"❌ Groq API Check failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Groq Connection Failed: {e}")

if __name__ == "__main__":
    check()
