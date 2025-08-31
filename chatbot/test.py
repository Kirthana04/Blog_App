from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()
 
 
api_key = os.getenv("GROQ_API_KEY")
 
print(api_key)