#!/usr/bin/env python3
"""
Educational Assistant - Flask Web Application
RAG-powered lesson plan generator for K-12 teachers.
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Flask and web components
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge

# ML/AI libraries
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

# Utilities
from functools import lru_cache
import gc
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EducationalAssistant:
    """Main class for the educational assistant with RAG functionality."""

    def __init__(self):
        """Initialize the educational assistant."""
        self.index = None
        self.documents = []
        self.embedding_model = None
        self.llm_pipeline = None
        self.tokenizer = None

        # Configuration
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 300))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 50))
        self.max_chunks = int(os.getenv('MAX_CHUNKS', 4))
        self.embedding_model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.llm_model_name = os.getenv('LLM_MODEL', 'microsoft/DialoGPT-medium')

        # Load components
        self.load_components()

    def load_components(self) -> bool:
        """Load all required components (index, documents, models)."""
        try:
            logger.info("🚀 Loading Educational Assistant components...")

            # Load FAISS index
            if not self.load_faiss_index():
                logger.warning("⚠️ FAISS index not found - running in fallback mode")

            # Load documents
            if not self.load_documents():
                logger.warning("⚠️ Documents not found - running in fallback mode")

            # Load embedding model
            if not self.load_embedding_model():
                logger.error("❌ Failed to load embedding model")
                return False

            # Load LLM (optional for fallback)
            self.load_llm()

            logger.info("✅ Educational Assistant components loaded successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load components: {e}")
            return False

    def load_faiss_index(self) -> bool:
        """Load the FAISS vector index."""
        try:
            if os.path.exists('document.index'):
                self.index = faiss.read_index('document.index')
                logger.info(f"✅ Loaded FAISS index with {self.index.ntotal} vectors")
                return True
            else:
                logger.warning("⚠️ document.index not found")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to load FAISS index: {e}")
            return False

    def load_documents(self) -> bool:
        """Load document chunks metadata."""
        try:
            if os.path.exists('documents.json'):
                with open('documents.json', 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                logger.info(f"✅ Loaded {len(self.documents)} document chunks")
                return True
            else:
                logger.warning("⚠️ documents.json not found")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to load documents: {e}")
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

    def load_llm(self) -> bool:
        """Load the language model for text generation."""
        try:
            logger.info(f"Loading LLM: {self.llm_model_name}")

            # Use CPU-only for better compatibility
            device = "cpu"

            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model_name)
            model = AutoModelForCausalLM.from_pretrained(
                self.llm_model_name,
                torch_dtype=torch.float32,
                device_map=device,
                low_cpu_mem_usage=True
            )

            # Create pipeline
            self.llm_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=self.tokenizer,
                device=device,
                max_length=1024,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )

            logger.info("✅ LLM loaded successfully")
            return True

        except Exception as e:
            logger.warning(f"⚠️ Failed to load LLM (will use fallback): {e}")
            return False

    @lru_cache(maxsize=1000)
    def get_cached_embedding(self, text: str) -> np.ndarray:
        """Get cached embedding for text."""
        return self.embedding_model.encode([text])[0]

    def retrieve_context(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant context using RAG."""
        try:
            if not self.index or not self.documents:
                logger.warning("⚠️ No index or documents available for retrieval")
                return []

            # Create query embedding
            query_embedding = self.get_cached_embedding(query)
            query_embedding = query_embedding.reshape(1, -1).astype('float32')

            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)

            # Search for similar chunks
            scores, indices = self.index.search(query_embedding, self.max_chunks)

            # Get relevant documents
            relevant_docs = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.documents) and score > 0.1:  # Similarity threshold
                    doc = self.documents[idx].copy()
                    doc['similarity_score'] = float(score)
                    doc['rank'] = i + 1
                    relevant_docs.append(doc)

            logger.info(f"Retrieved {len(relevant_docs)} relevant document chunks")
            return relevant_docs

        except Exception as e:
            logger.error(f"❌ Failed to retrieve context: {e}")
            return []

    def detect_elementary_music(self, query: str) -> bool:
        """Detect if query is for elementary general music."""
        music_keywords = [
            'music', 'musical', 'song', 'singing', 'rhythm', 'melody', 'beat',
            'instrument', 'piano', 'guitar', 'drum', 'orchestra', 'choir',
            'note', 'scale', 'tempo', 'dynamics', 'pitch'
        ]

        elementary_keywords = [
            'elementary', 'primary', 'kindergarten', 'k-5', 'grade 1', 'grade 2',
            'grade 3', 'grade 4', 'grade 5', 'young', 'children'
        ]

        query_lower = query.lower()

        has_music = any(keyword in query_lower for keyword in music_keywords)
        has_elementary = any(keyword in query_lower for keyword in elementary_keywords)

        return has_music and has_elementary

    def detect_external_knowledge_request(self, query: str) -> bool:
        """Detect if user wants external knowledge beyond documents."""
        external_triggers = [
            'search the web', 'best practices', 'include external ideas',
            'go beyond the documents', 'latest research', 'current trends',
            'what else', 'additional ideas', 'more information',
            'external sources', 'beyond curriculum'
        ]

        query_lower = query.lower()
        return any(trigger in query_lower for trigger in external_triggers)

    def extract_duration(self, query: str) -> Optional[int]:
        """Extract lesson duration from query."""
        # Look for duration patterns
        duration_patterns = [
            r'(\d+)\s*(?:minute|min)s?',
            r'(\d+)\s*(?:hour|hr)s?',
            r'(\d+)\s*(?:period|class)s?'
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, query.lower())
            if match:
                duration = int(match.group(1))
                # Convert hours to minutes
                if 'hour' in pattern or 'hr' in pattern:
                    duration *= 60
                # Assume class periods are 45 minutes
                elif 'period' in pattern or 'class' in pattern:
                    duration *= 45
                return duration

        return None

    def format_elementary_music_lesson(self, content: str, duration: int) -> str:
        """Format lesson plan for elementary music (12-section format)."""
        extended_duration = duration + 5  # Add 5 minutes for extension

        template = f"""# Elementary General Music Lesson Plan

## Overview
**Grade Level:** Elementary (K-5) | **Duration:** {extended_duration} minutes | **Lesson Theme:** {content[:100]}...

## Florida Standards (MU)
- MU.K.C.1.1: Respond to music from various sound sources
- MU.1.C.2.1: Identify the difference between beat and rhythm
- MU.2.S.3.1: Sing simple songs in a group setting

## Learning Goals (I can…)
- I can identify different musical elements in songs
- I can participate in group musical activities
- I can express myself through music and movement

## Learning Targets (I will…)
- I will listen actively to musical examples
- I will participate respectfully in group activities
- I will demonstrate understanding through movement or singing

## Materials & Resources
- Audio system/speakers
- Musical instruments (rhythm sticks, shakers)
- Visual aids (musical notation charts)
- Movement scarves or props

## Activities Timeline
| Time | Activity | Differentiation | Marzano Element Tag |
|------|----------|----------------|-------------------|
| 5 min | Opening Circle & Warm-up | Visual/auditory cues | Setting Objectives |
| 10 min | Main Musical Activity | Multiple learning styles | Providing Feedback |
| 15 min | Guided Practice | Peer support | Practicing Skills |
| 10 min | Creative Expression | Choice in expression | Generating Hypotheses |
| 5 min | Extension & Differentiation | Advanced/remedial options | Extending Learning |

## Life-Skills Competencies
This lesson integrates CASEL SEL competencies with NCAS Artistic Processes by fostering **self-awareness** through musical expression, **social awareness** through ensemble participation, and **responsible decision-making** in creative choices.

## Assessment
**Formative:** Observation of student participation and engagement during activities
**Summative:** Student demonstration of musical concepts through performance or movement

## Teacher Reflection Prompts
1. How effectively did students engage with the musical concepts presented?
2. What adjustments could improve student understanding and participation?
3. How can I better differentiate instruction for diverse learners in future lessons?

## Optional Tech/AI Enhancements
- Use music apps for rhythm practice
- Incorporate digital audio tools for sound exploration
- Virtual instrument apps for extended learning

## Alignment Summary
**Marzano Elements Used:** Setting Objectives, Providing Feedback, Practicing Skills, Generating Hypotheses, Extending Learning

## SELARTS Framework
**CASEL x NCAS Connections:** Self-Awareness + Creating, Social Awareness + Performing, Responsible Decision-Making + Responding
"""
        return template

    def format_general_lesson(self, content: str, duration: int, subject: str = "General") -> str:
        """Format lesson plan for general subjects (6-section format)."""
        extended_duration = duration + 5  # Add 5 minutes for extension

        template = f"""# Lesson Plan

## Overview
**Grade Level:** K-12 | **Subject:** {subject} | **Duration:** {extended_duration} minutes

## Standards
Relevant state and national standards will be addressed based on the specific content and grade level.

## Learning Objectives
Students will be able to understand and apply the key concepts presented in this lesson through various learning activities and assessments.

## Instructional Steps
1. **Opening (5 minutes):** Introduction and objective setting
2. **Direct Instruction (15 minutes):** Core content delivery
3. **Guided Practice (15 minutes):** Structured practice activities
4. **Independent Practice (10 minutes):** Individual application
5. **Extension & Differentiation (5 minutes):** Advanced activities and support for diverse learners
6. **Closure (5 minutes):** Summary and assessment

## Assessment
**Formative Assessment:** Ongoing observation and questioning during activities
**Summative Assessment:** End-of-lesson evaluation of student understanding and skill demonstration

## Differentiation
- **For Advanced Learners:** Extended activities and deeper exploration
- **For Struggling Learners:** Additional support, visual aids, and modified expectations
- **For English Language Learners:** Visual supports, peer partnerships, and vocabulary scaffolding
- **For Special Needs:** Accommodations based on individual learning plans
"""
        return template

    def generate_response(self, query: str, context: List[Dict], use_external: bool = False) -> str:
        """Generate response using LLM or fallback method."""
        try:
            # Extract duration
            duration = self.extract_duration(query)
            if duration is None:
                return "How long should the lesson be? Please specify the duration (e.g., 30 minutes, 1 hour)."

            # Detect lesson type
            is_elementary_music = self.detect_elementary_music(query)

            # Prepare context
            context_text = ""
            if context:
                context_text = "\n\n".join([doc['text'] for doc in context[:self.max_chunks]])

            # Generate response based on available context
            if context_text and not use_external:
                # Document-grounded response
                if is_elementary_music:
                    response = self.format_elementary_music_lesson(context_text, duration)
                    return f"### 📚 Based on District Documents:\n\n{response}"
                else:
                    response = self.format_general_lesson(context_text, duration)
                    return f"### 📚 Based on District Documents:\n\n{response}"

            elif use_external or not context_text:
                # External knowledge or fallback response
                if self.llm_pipeline:
                    # Use LLM for generation
                    prompt = f"Create a lesson plan for: {query}"
                    generated = self.llm_pipeline(prompt, max_length=512, num_return_sequences=1)
                    content = generated[0]['generated_text']
                else:
                    # Fallback content
                    content = f"Lesson plan content for: {query}"

                if is_elementary_music:
                    response = self.format_elementary_music_lesson(content, duration)
                else:
                    response = self.format_general_lesson(content, duration)

                if use_external:
                    return f"### 🌐 Supplemented from General Knowledge:\n\n{response}"
                else:
                    return f"### 📚 Based on Available Resources:\n\n{response}"

            else:
                return "This information does not appear in the uploaded curriculum documents."

        except Exception as e:
            logger.error(f"❌ Failed to generate response: {e}")
            return "I apologize, but I encountered an error while generating your lesson plan. Please try again."

    def process_query(self, query: str, duration: str = None) -> Dict[str, Any]:
        """Process a user query and return structured response."""
        try:
            logger.info(f"Processing query: {query[:100]}...")

            # Add duration to query if provided separately
            if duration and duration != "":
                query = f"{query} Duration: {duration}"

            # Check for external knowledge request
            use_external = self.detect_external_knowledge_request(query)

            # Retrieve context
            context = self.retrieve_context(query) if not use_external else []

            # Generate response
            response = self.generate_response(query, context, use_external)

            # Prepare result
            result = {
                'response': response,
                'context_used': len(context),
                'sources': [doc['source'] for doc in context] if context else [],
                'timestamp': datetime.now().isoformat(),
                'query_type': 'elementary_music' if self.detect_elementary_music(query) else 'general',
                'external_knowledge': use_external
            }

            # Force garbage collection
            gc.collect()

            return result

        except Exception as e:
            logger.error(f"❌ Failed to process query: {e}")
            return {
                'response': "I apologize, but I encountered an error while processing your request. Please try again.",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize educational assistant
assistant = EducationalAssistant()

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        memory_usage = psutil.virtual_memory().percent
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'memory_usage': f"{memory_usage}%",
            'components': {
                'faiss_index': assistant.index is not None,
                'documents': len(assistant.documents) > 0,
                'embedding_model': assistant.embedding_model is not None,
                'llm_pipeline': assistant.llm_pipeline is not None
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/ask', methods=['POST'])
def ask():
    """Handle lesson plan generation requests."""
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400

        query = data['query'].strip()
        duration = data.get('duration', '').strip()

        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400

        # Process the query
        result = assistant.process_query(query, duration)

        return jsonify(result)

    except RequestEntityTooLarge:
        return jsonify({'error': 'Request too large'}), 413
    except Exception as e:
        logger.error(f"❌ Error in /ask endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Please try again later'
        }), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get('PORT', 5000))

    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
