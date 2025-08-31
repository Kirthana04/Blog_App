import os
from dotenv import load_dotenv
import groq

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

# Check if API key exists
if not api_key:
    print("ERROR: GROQ_API_KEY not found in environment variables")
    print("Make sure your .env file contains a valid GROQ_API_KEY")
    exit(1)

# Create Groq client
client = groq.Client(api_key=api_key)

try:
    # List available models
    print("Fetching available models from Groq...")
    models = client.models.list()
    
    print("\nAVAILABLE MODELS:")
    print("================")
    
    for model in models.data:
        print(f"- {model.id}")
        
    print("\nRecommended model to use: mixtral-8x7b-32768")
    
except Exception as e:
    print(f"ERROR: Could not fetch models: {str(e)}")
    print("\nTry one of these common models:")
    print("- mixtral-8x7b-32768")
    print("- gemma-7b-it")
    print("- claude-3-haiku-20240307")
