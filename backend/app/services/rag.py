from typing import List, Dict, Any
from .embeddings import embedding_service
from .vector_store import vector_store
from .llm import llm_service

class RAGService:

    async def query(
        self,
        question: str,
        document_ids: List[str] = None,
        conversation_history: List[Dict] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve context across multiple documents and generate answer
        """

        # Step 1: Embed the question
        question_embedding = embedding_service.embed_text(question)

        # Step 2: Retrieve relevant chunks
        print(f"DEBUG: RAG query for question: '{question}' (doc_ids: {document_ids})")
        relevant_chunks = vector_store.search(
            query_embedding=question_embedding,
            document_ids=document_ids,
            user_id=user_id
        )
        print(f"DEBUG: Found {len(relevant_chunks)} relevant chunks")

        if not relevant_chunks:
            return {
                "answer": "I couldn't find any relevant information in the documents to answer your question.",
                "sources": [],
                "context_used": ""
            }

        # Step 3: Construct context
        context_parts = []
        for idx, chunk in enumerate(relevant_chunks, 1):
            metadata = chunk["metadata"]
            source_info = f"[Document: {metadata.get('filename', 'Unknown')}"
            if metadata.get('page'):
                source_info += f", Page {metadata['page']}"
            source_info += "]"

            context_parts.append(f"{source_info}\n{chunk['text']}\n")

        context = "\n---\n".join(context_parts)

        # Step 4: Generate answer using LLM
        answer = await llm_service.generate_answer(
            context=context,
            question=question,
            conversation_history=conversation_history
        )

        # Step 5: Format sources
        sources = []
        for chunk in relevant_chunks:
            metadata = chunk["metadata"]
            sources.append({
                "document_id": metadata.get("document_id"),
                "filename": metadata.get("filename"),
                "page": metadata.get("page"),
                "chunk_text": chunk["text"][:200] + "...",  # Preview
                "relevance_score": round(chunk["score"], 3)
            })

        return {
            "answer": answer,
            "sources": sources,
            "context_used": context
        }

    async def query_stream(
        self,
        question: str,
        document_ids: List[str] = None,
        conversation_history: List[Dict] = None,
        user_id: str = None
    ):
        """
        Streaming RAG pipeline: retrieve context and yield streaming LLM response
        """
        try:
            # Step 1: Embed the question
            print(f"DEBUG: Embedding question: '{question[:30]}...'")
            question_embedding = embedding_service.embed_text(question)
            print("DEBUG: Question embedded successfully.")

            # Step 2: Retrieve relevant chunks
            print(f"DEBUG: Searching vector store (docs: {document_ids}, user: {user_id})...")
            relevant_chunks = vector_store.search(
                query_embedding=question_embedding,
                document_ids=document_ids,
                user_id=user_id
            )
            print(f"DEBUG: Found {len(relevant_chunks)} relevant chunks.")

            if not relevant_chunks:
                print("DEBUG: No relevant chunks found. Yielding default message.")
                yield "I couldn't find any relevant information in the documents to answer your question."
                return

            # Step 3: Construct context
            context_parts = []
            for idx, chunk in enumerate(relevant_chunks, 1):
                metadata = chunk["metadata"]
                source_info = f"[Document: {metadata.get('filename', 'Unknown')}"
                if metadata.get('page'):
                    source_info += f", Page {metadata['page']}"
                source_info += "]"
                context_parts.append(f"{source_info}\n{chunk['text']}\n")

            context = "\n---\n".join(context_parts)
            print(f"DEBUG: Context constructed (length: {len(context)}). Starting LLM stream...")

            # Step 4 & 5: Stream answer
            async for chunk in llm_service.generate_stream(
                context=context,
                question=question,
                conversation_history=conversation_history
            ):
                yield chunk
            print("DEBUG: RAG streaming complete.")
        except Exception as e:
            print(f"ERROR in RAG query_stream: {e}")
            import traceback
            traceback.print_exc()
            yield f"Error in RAG service: {str(e)}"

# Singleton instance
rag_service = RAGService()
