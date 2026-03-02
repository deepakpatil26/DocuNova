from groq import AsyncGroq
from typing import List, Dict, Any, Optional, AsyncGenerator
from ..core.config import settings

class LLMService:
    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.DEFAULT_LLM_MODEL

    async def generate_answer(self, context: str, question: str, conversation_history: List[Dict] = None) -> str:
        """
        Generate answer using LLM with context
        """
        if not self.client:
             return "LLM API Key not configured. Please set GROQ_API_KEY in .env file."

        # Build system prompt
        system_prompt = """You are a helpful AI assistant that answers questions based ONLY on the provided context from documents.

Key instructions:
1. ONLY use information from the given context
2. If the answer is not in the context, say "I don't have enough information to answer this question based on the provided documents."
3. Cite sources for every major claim using the format: [Source: {filename}, Page {page}]
4. Be concise but comprehensive
5. If multiple sources provide information, synthesize them
6. Never make up information not in the context

Response format:
- Provide a direct answer first
- Support with details from the context
- Include source citations inline"""

        # Build user prompt
        user_prompt = f"""Context from documents:

{context}

Question: {question}

Please provide a well-sourced answer based on the context above."""

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Add conversation history if provided
        if conversation_history:
            # Filter and format history to ensure it matches expected format
            valid_history = []
            for msg in conversation_history[-6:]: # Last 3 exchanges
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                     valid_history.append({"role": msg['role'], "content": msg['content']})
            messages.extend(valid_history)

        # Add current query
        messages.append({"role": "user", "content": user_prompt})

        # Call LLM
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=1000,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"LLM error: {e}")
            return f"Error generating response: {str(e)}"

    async def generate_stream(self, context: str, question: str, conversation_history: List[Dict] = None) -> AsyncGenerator[str, None]:
        """
        Generate streaming answer using LLM with context
        """
        if not self.client:
             yield "LLM API Key not configured."
             return

        # Build prompts (same as generate_answer)
        system_prompt = """You are a helpful AI assistant that answers questions based ONLY on the provided context from documents.

Key instructions:
1. ONLY use information from the given context
2. If the answer is not in the context, say "I don't have enough information to answer this question based on the provided documents."
3. Cite sources for every major claim using the format: [Source: {filename}, Page {page}]
4. Be concise but comprehensive
5. If multiple sources provide information, synthesize them
6. Never make up information not in the context

Response format:
- Provide a direct answer first
- Support with details from the context
- Include source citations inline"""

        user_prompt = f"""Context from documents:

{context}

Question: {question}

Please provide a well-sourced answer based on the context above."""

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            valid_history = []
            for msg in conversation_history[-6:]:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                     valid_history.append({"role": msg['role'], "content": msg['content']})
            messages.extend(valid_history)

        messages.append({"role": "user", "content": user_prompt})

        try:
            print(f"DEBUG: Calling Groq API (model: {self.model})...")
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
                stream=True,
            )

            chunk_count = 0
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    chunk_count += 1
                    if chunk_count == 1:
                        print(f"DEBUG: Received FIRST chunk from Groq: '{content[:10]}...'")
                    yield content
            
            print(f"DEBUG: Groq internal stream finished. Total chunks from Groq: {chunk_count}")

        except Exception as e:
            print(f"LLM streaming error: {e}")
            import traceback
            traceback.print_exc()
            yield f"Error generating response: {str(e)}"

# Singleton instance
llm_service = LLMService()
