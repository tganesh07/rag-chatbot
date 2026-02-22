import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.settings import settings
import shutil
import os

class VectorDatabase:
    def __init__(self):
        self.persist_dir = str(settings.CHROMA_PERSIST_DIR)
        
        # Initialize Embeddings (Local Sentence Transformers)
        print(f"Initializing Embeddings: {settings.EMBEDDING_MODEL}")
        self.embedding_function = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        
        # Initialize Vector Store
        self.vector_store = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embedding_function,
            collection_name="rag_documents"
        )
        
    def add_documents(self, documents):
        """Adds documents to the vector store."""
        if not documents:
            return
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
