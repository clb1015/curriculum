#!/usr/bin/env python3
"""
Educational Assistant - Document Ingestion Script
Processes PDF documents from Google Drive into a searchable FAISS index.
"""

import os
import json
import logging
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

# Core libraries
import fitz  # PyMuPDF
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Google Drive API
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentIngester:
    """Handles document ingestion from Google Drive to FAISS index."""

    def __init__(self, 
                 credentials_path: str = 'credentials.json',
                 token_path: str = 'token.json',
                 chunk_size: int = 300,
                 chunk_overlap: int = 50,
                 embedding_model: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the document ingester.

        Args:
            credentials_path: Path to Google API credentials
            token_path: Path to store OAuth token
            chunk_size: Size of text chunks in words
            chunk_overlap: Overlap between chunks in words
            embedding_model: Sentence transformer model name
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model_name = embedding_model

        # Google Drive API setup
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.service = None
        self.embedding_model = None

        # Storage
        self.documents = []
        self.embeddings = []

    def authenticate_google_drive(self) -> bool:
        """Authenticate with Google Drive API."""
        try:
            creds = None

            # Load existing token
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        logger.error(f"Credentials file not found: {self.credentials_path}")
                        logger.error("Please download credentials.json from Google Cloud Console")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save credentials for next run
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())

            self.service = build('drive', 'v3', credentials=creds)
            logger.info("✅ Google Drive authentication successful")
            return True

        except Exception as e:
            logger.error(f"❌ Google Drive authentication failed: {e}")
            return False

    def load_embedding_model(self) -> bool:
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info("✅ Embedding model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            return False

    def get_pdf_files_from_folder(self, folder_id: str) -> List[Dict[str, str]]:
        """Get all PDF files from a Google Drive folder."""
        try:
            query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, size, modifiedTime)"
            ).execute()

            files = results.get('files', [])
            logger.info(f"Found {len(files)} PDF files in folder")

            return files

        except Exception as e:
            logger.error(f"❌ Failed to get files from folder: {e}")
            return []

    def download_pdf(self, file_id: str, file_name: str) -> Optional[bytes]:
        """Download a PDF file from Google Drive."""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    logger.info(f"Download progress: {int(status.progress() * 100)}% - {file_name}")

            file_io.seek(0)
            return file_io.read()

        except Exception as e:
            logger.error(f"❌ Failed to download {file_name}: {e}")
            return None

    def extract_text_from_pdf(self, pdf_bytes: bytes, file_name: str) -> str:
        """Extract text from PDF bytes."""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()

            doc.close()

            # Clean the text
            text = self.clean_text(text)
            logger.info(f"Extracted {len(text)} characters from {file_name}")

            return text

        except Exception as e:
            logger.error(f"❌ Failed to extract text from {file_name}: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()-]', '', text)

        # Remove very short lines (likely artifacts)
        lines = text.split('\n')
        lines = [line.strip() for line in lines if len(line.strip()) > 10]

        return '\n'.join(lines)

    def chunk_text(self, text: str, source: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)

            if len(chunk_text.strip()) > 50:  # Skip very short chunks
                chunks.append({
                    'text': chunk_text,
                    'source': source,
                    'chunk_id': len(chunks),
                    'word_count': len(chunk_words),
                    'start_word': i,
                    'end_word': min(i + self.chunk_size, len(words))
                })

        return chunks

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for text chunks."""
        try:
            logger.info(f"Creating embeddings for {len(texts)} text chunks...")
            embeddings = self.embedding_model.encode(
                texts,
                show_progress_bar=True,
                batch_size=32
            )
            logger.info(f"✅ Created embeddings with shape: {embeddings.shape}")
            return embeddings

        except Exception as e:
            logger.error(f"❌ Failed to create embeddings: {e}")
            return np.array([])

    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build FAISS index from embeddings."""
        try:
            dimension = embeddings.shape[1]

            # Use IndexFlatIP for cosine similarity
            index = faiss.IndexFlatIP(dimension)

            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)

            # Add embeddings to index
            index.add(embeddings.astype('float32'))

            logger.info(f"✅ Built FAISS index with {index.ntotal} vectors")
            return index

        except Exception as e:
            logger.error(f"❌ Failed to build FAISS index: {e}")
            return None

    def save_index_and_documents(self, index: faiss.Index, documents: List[Dict]) -> bool:
        """Save FAISS index and document metadata."""
        try:
            # Save FAISS index
            faiss.write_index(index, 'document.index')
            logger.info("✅ Saved FAISS index to document.index")

            # Save document metadata
            with open('documents.json', 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved {len(documents)} document chunks to documents.json")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to save index and documents: {e}")
            return False

    def process_folder(self, folder_id: str) -> bool:
        """Process all PDFs in a Google Drive folder."""
        logger.info(f"Starting document ingestion from folder: {folder_id}")

        # Get PDF files
        pdf_files = self.get_pdf_files_from_folder(folder_id)
        if not pdf_files:
            logger.error("No PDF files found in folder")
            return False

        all_chunks = []

        # Process each PDF
        for file_info in pdf_files:
            file_id = file_info['id']
            file_name = file_info['name']

            logger.info(f"Processing: {file_name}")

            # Download PDF
            pdf_bytes = self.download_pdf(file_id, file_name)
            if not pdf_bytes:
                continue

            # Extract text
            text = self.extract_text_from_pdf(pdf_bytes, file_name)
            if not text:
                continue

            # Create chunks
            chunks = self.chunk_text(text, file_name)
            all_chunks.extend(chunks)

            logger.info(f"Created {len(chunks)} chunks from {file_name}")

        if not all_chunks:
            logger.error("No text chunks created from any documents")
            return False

        logger.info(f"Total chunks created: {len(all_chunks)}")

        # Create embeddings
        chunk_texts = [chunk['text'] for chunk in all_chunks]
        embeddings = self.create_embeddings(chunk_texts)

        if embeddings.size == 0:
            logger.error("Failed to create embeddings")
            return False

        # Build FAISS index
        index = self.build_faiss_index(embeddings)
        if index is None:
            return False

        # Save everything
        return self.save_index_and_documents(index, all_chunks)

    def run(self) -> bool:
        """Run the complete ingestion process."""
        logger.info("🚀 Starting Educational Assistant Document Ingestion")

        # Load embedding model
        if not self.load_embedding_model():
            return False

        # Authenticate with Google Drive
        if not self.authenticate_google_drive():
            return False

        # Get folder ID from user
        folder_id = input("\nEnter Google Drive folder ID: ").strip()
        if not folder_id:
            logger.error("No folder ID provided")
            return False

        # Process the folder
        success = self.process_folder(folder_id)

        if success:
            logger.info("🎉 Document ingestion completed successfully!")
            logger.info("Files created:")
            logger.info("  - document.index (FAISS vector index)")
            logger.info("  - documents.json (document chunks metadata)")
            logger.info("\nYou can now run the Flask application with: python app.py")
        else:
            logger.error("❌ Document ingestion failed")

        return success

def main():
    """Main function to run document ingestion."""
    # Load configuration from environment variables
    chunk_size = int(os.getenv('CHUNK_SIZE', 300))
    chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 50))
    embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

    # Create ingester
    ingester = DocumentIngester(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embedding_model=embedding_model
    )

    # Run ingestion
    success = ingester.run()

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
