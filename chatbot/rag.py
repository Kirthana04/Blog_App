# import os
# import groq
# from dotenv import load_dotenv

# load_dotenv()

# class RAGSystem:
#     def __init__(self, embedding_manager):
#         self.embedding_manager = embedding_manager
#         self.groq_client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        
#     async def get_answer(self, query):
#         """Get answer using RAG approach"""
#         # Find relevant chunks
#         relevant_chunks = self.embedding_manager.find_similar_chunks(query)
        
#         if not relevant_chunks:
#             return {
#                 "answer": "I'm sorry, but I don't have information about that topic.",
#                 "sources": [],
#                 "has_answer": False
#             }
        
#         # Extract relevant contexts
#         contexts = [chunk["text"] for chunk in relevant_chunks]
#         sources = [{"blog_id": chunk["blog_id"], "chunk_id": chunk["chunk_id"]} for chunk in relevant_chunks]
        
#         # Combine contexts
#         combined_context = "\n\n".join(contexts)
        
#         # Construct prompt for LLM
#         prompt = f"""
#         You are a helpful assistant for a blog website. Answer the user's question based ONLY on the provided context.
#         If the answer cannot be determined from the context, respond with "I don't have enough information about that topic."
        
#         Context:
#         {combined_context}
        
#         User Question: {query}
        
#         Answer:
#         """
        
#         # Get response from Groq
#         try:
#             response = self.groq_client.chat.completions.create(
#                 model="llama3-8b-8192",  # Using a smaller model available on free tier
#                 messages=[
#                     {"role": "system", "content": "You are a helpful assistant who answers questions based only on the provided context."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.2,  # Low temperature for more factual responses
#                 max_tokens=800
#             )
            
#             answer = response.choices[0].message.content
            
#             # Check if the answer indicates insufficient information
#             has_answer = "I don't have enough information" not in answer
            
#             return {
#                 "answer": answer,
#                 "sources": sources,
#                 "has_answer": has_answer
#             }
#         except Exception as e:
#             print(f"Error calling Groq API: {e}")
#             return {
#                 "answer": "I'm having trouble connecting to my knowledge base. Please try again later.",
#                 "sources": [],
#                 "has_answer": False
#             }