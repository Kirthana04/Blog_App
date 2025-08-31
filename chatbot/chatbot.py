import os
import groq
import sys
from dotenv import load_dotenv

load_dotenv()

class Chatbot:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("ERROR: GROQ_API_KEY not found in environment variables. Please add it to your .env file.")
            
        
        self.groq_client = groq.Client(api_key=self.api_key)
    
    def groq_api_key_format(self):
        """Return a masked version of the API key for debugging"""
        if not self.api_key:
            return "No API key found"
        if len(self.api_key) < 10:
            return f"API key too short: {len(self.api_key)} chars (should be ~40+ chars)"
        # Only show first 4 and last 4 characters
        return f"{self.api_key[:4]}...{self.api_key[-4:]} (length: {len(self.api_key)})"
        
    async def get_answer(self, query, blogs):
        """Get answer from Groq LLM based on relevant blog content"""
        if not blogs:
            return {"answer": "I don't have enough information to answer that question.", "has_answer": False}
        
        # Create context from blogs with safer field access
        context_parts = []
        for blog in blogs:
            title = blog.get('title', 'No title')
            contents = blog.get('contents', 'No content available')
            context_parts.append(f"Title: {title}\nContent: {contents}")
        
        context = "\n\n".join(context_parts)
        
        # Prepare prompt for the LLM
        prompt = f"""
        You are an AI assistant for a blog website. Answer the user's question based only on the following blog content:
        
        {context}
        
        User question: {query}
        
        If the blog content doesn't contain information to answer the question, respond with "I don't have enough information to answer that question."
        
        Answer:
        """
        
        try:
            # Call Groq LLM with a more recent model
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Updated to a more recent model
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for a blog website."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content
            has_answer = "I don't have enough information" not in answer
            
            return {"answer": answer, "has_answer": has_answer}
        
        except groq.AuthenticationError as auth_error:
            print(f"ERROR: Invalid Groq API Key: {str(auth_error)}")
            print(f"Current key format: {self.groq_api_key_format()}")
            print("You can get a Groq API key from https://console.groq.com/keys")
            print("Make sure to restart the server after updating the .env file")
            return {
                "answer": "Sorry, there was an authentication error with the AI service. Please check the server logs and ensure you have a valid Groq API key.", 
                "has_answer": False
            }
        except groq.error.BadRequestError as model_error:
            error_str = str(model_error)
            print(f"ERROR with Groq model: {error_str}")
            
            if "model_decommissioned" in error_str:
                print("The model has been decommissioned! Updating to a newer model...")
                # Try with an alternate model next time
                print("Please update your code to use a current model. Try running list_groq_models.py to see available models.")
            
            return {
                "answer": "Sorry, there was an error with the AI model. The team has been notified.",
                "has_answer": False
            }
        except Exception as e:
            print(f"ERROR calling Groq API: {str(e)}")
            return {
                "answer": "Sorry, there was an error processing your request.",
                "has_answer": False
            }