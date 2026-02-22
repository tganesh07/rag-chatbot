import os
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredCSVLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def load_file(self, file_path: Path) -> List[Document]:
        """Loads a file and returns a list of Documents."""
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return []

        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.pdf':
                return self._load_pdf(file_path)
            elif suffix == '.txt':
                return self._load_txt(file_path)
            elif suffix == '.csv':
                return self._load_csv(file_path)
            elif suffix in ['.xlsx', '.xls']:
                return self._load_excel(file_path)
            else:
                print(f"Unsupported file type: {suffix}")
                return []
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return []

    def _load_pdf(self, path: Path) -> List[Document]:
        loader = PyPDFLoader(str(path))
        return loader.load()

    def _load_txt(self, path: Path) -> List[Document]:
        loader = TextLoader(str(path))
        return loader.load()

    def _load_csv(self, path: Path) -> List[Document]:
        # Using UnstructuredCSVLoader for better text representation
        loader = UnstructuredCSVLoader(str(path), mode="elements")
        return loader.load()

    def _load_excel(self, path: Path) -> List[Document]:
        # Convert Excel to meaningful text representation per row
        df = pd.read_excel(path)
        documents = []
        for index, row in df.iterrows():
            # Create a text representation of the row
            content = "\n".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            metadata = {"source": str(path), "row": index}
            documents.append(Document(page_content=content, metadata=metadata))
        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Splits documents into smaller chunks."""
        return self.text_splitter.split_documents(documents)

processor = DocumentProcessor()
