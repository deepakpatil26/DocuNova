import PyPDF2
import pdfplumber
from typing import List, Dict, Any
from pathlib import Path
import re
from ..core.config import settings

class Chunk:
    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        self.metadata = metadata

class DocumentProcessor:

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> tuple[str, Dict[str, Any]]:
        """Extract text and metadata from PDF"""
        text = ""
        metadata = {
            "total_pages": 0,
            "page_texts": {}
        }

        try:
            # Try pdfplumber first (better for complex PDFs)
            with pdfplumber.open(file_path) as pdf:
                metadata["total_pages"] = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text() or ""
                    text += f"\n\n--- Page {page_num} ---\n\n{page_text}"
                    metadata["page_texts"][page_num] = page_text

        except Exception as e:
            # Fallback to PyPDF2
            print(f"pdfplumber failed, using PyPDF2: {e}")
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata["total_pages"] = len(pdf_reader.pages)

                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    page_text = page.extract_text() or ""
                    text += f"\n\n--- Page {page_num} ---\n\n{page_text}"
                    metadata["page_texts"][page_num] = page_text

        return text.strip(), metadata

    @staticmethod
    def extract_text_from_txt(file_path: str) -> tuple[str, Dict[str, Any]]:
        """Extract text from plain text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        metadata = {
            "total_pages": 1,
            "line_count": len(text.split('\n'))
        }

        return text, metadata

    @staticmethod
    def smart_chunk(text: str, document_id: str, filename: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Intelligent chunking that preserves context
        """
        chunks = []

        # Clean text
        text = re.sub(r'\n{3,}', '\n\n', text)  # Remove excessive newlines

        # Split by pages if available
        if "page_texts" in metadata:
            for page_num, page_text in metadata["page_texts"].items():
                page_chunks = DocumentProcessor._chunk_text(
                    page_text,
                    {
                        "document_id": document_id,
                        "filename": filename,
                        "page": page_num,
                        "total_pages": metadata.get("total_pages", 1)
                    }
                )
                chunks.extend(page_chunks)
        else:
            # No page info, chunk the whole text
            chunks = DocumentProcessor._chunk_text(
                text,
                {
                    "document_id": document_id,
                    "filename": filename,
                    "page": 1
                }
            )

        return chunks

    @staticmethod
    def _chunk_text(text: str, base_metadata: Dict[str, Any]) -> List[Chunk]:
        """Helper function to chunk text with overlap"""
        chunks = []

        # Split by sentences (rough)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        current_chunk = ""
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length < settings.CHUNK_SIZE:
                current_chunk += sentence + " "
                current_length += sentence_length
            else:
                # Save current chunk
                if current_chunk.strip():
                    chunks.append(Chunk(
                        text=current_chunk.strip(),
                        metadata={
                            **base_metadata,
                            "chunk_index": len(chunks),
                            "chunk_length": len(current_chunk)
                        }
                    ))

                # Start new chunk with overlap
                overlap_size = settings.CHUNK_OVERLAP
                overlap_text = current_chunk[-overlap_size:] if len(current_chunk) > overlap_size else current_chunk
                current_chunk = overlap_text + sentence + " "
                current_length = len(current_chunk)

        # Add last chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                text=current_chunk.strip(),
                metadata={
                    **base_metadata,
                    "chunk_index": len(chunks),
                    "chunk_length": len(current_chunk)
                }
            ))

        return chunks

# Singleton instance
document_processor = DocumentProcessor()
