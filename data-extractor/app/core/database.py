import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.settings import settings
import shutil
import os
import time

class VectorDatabase:
    def __init__(self):
        self.persist_dir = str(settings.CHROMA_PERSIST_DIR)
        
        # Determine the collection name based on RAG mode to avoid dimension mismatch conflicts
        self.collection_name = f"rag_documents_{settings.RAG_MODE}"
        
        # Initialize Embeddings dynamically
        self.embedding_function = self._initialize_embeddings()
        
        # Initialize Vector Store
        self.vector_store = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embedding_function,
            collection_name=self.collection_name
        )

    def _initialize_embeddings(self):
        if settings.RAG_MODE in ["local", "hybrid"]:
            print(f"Initializing Local Embeddings: {settings.EMBEDDING_MODEL}")
            return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        
        elif settings.RAG_MODE == "cloud":
            if settings.LLM_PROVIDER == "gemini":
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                print("Initializing Cloud Embeddings: Google Gemini")
                return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            elif settings.LLM_PROVIDER == "openai":
                from langchain_openai import OpenAIEmbeddings
                print("Initializing Cloud Embeddings: OpenAI")
                return OpenAIEmbeddings()
            else:
                raise ValueError(f"Unsupported CLOUD LLM Provider for embeddings: {settings.LLM_PROVIDER}")
        else:
            raise ValueError(f"Unsupported RAG_MODE: {settings.RAG_MODE}")

    def add_documents(self, documents):
        """Adds documents to the vector store with custom logic for API heavy modes."""
        if not documents:
            return
            
        if settings.RAG_MODE == "cloud" and settings.LLM_PROVIDER == "gemini":
            # Gemini has strict rate limits, process in small batches
            batch_size = 1
            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]
                try:
                    self.vector_store.add_documents(batch)
                    time.sleep(5)  # Sleep to respect API rate limits
                except Exception as e:
                    if "429" in str(e):
                        print("Rate limit hit. Waiting 60 seconds before retrying...")
                        time.sleep(60)
                        self.vector_store.add_documents(batch)
                    else:
                        raise e
            print(f"Added {len(documents)} chunks to vector store via batching.")
        else:
            # Standard local fast add
            self.vector_store.add_documents(documents)
            print(f"Added {len(documents)} chunks to vector store.")

    def delete_file_documents(self, file_path: str):
        """Removes all documents associated with a specific file path."""
        # ChromaDB doesn't support complex metadata filtering for deletion easily in LangChain wrapper
        # Implementation via underlying client or by re-indexing might be safer.
        # For this version, we will perform a get to find IDs and then delete.
        try:
            # This is a naive implementation; production might need better ID management
            # Retaining simple logic: Get IDs where source == file_path
            # Note: ChromaDB basic filtering in LangChain is limited.
            # Using the underlying client for more control
             
            client = self.vector_store._client
            collection = self.vector_store._collection
            
            # Simple metadata filter
            result = collection.get(where={"source": file_path})
            ids_to_delete = result['ids']
            
            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                print(f"Deleted {len(ids_to_delete)} chunks for {file_path}")
        except Exception as e:
            print(f"Error deleting documents for {file_path}: {e}")

    def update_file(self, file_path: str, new_documents):
        """Deletes old documents for the file and adds new ones."""
        self.delete_file_documents(file_path)
        self.add_documents(new_documents)

    def as_retriever(self):
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )

# Global instance
vector_db = VectorDatabase()
