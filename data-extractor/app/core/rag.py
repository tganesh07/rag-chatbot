from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from app.settings import settings
from app.core.database import vector_db

class RAGPipeline:
    def __init__(self):
        self.llm = self._initialize_llm()
        self.retriever = vector_db.as_retriever()
        
        # Define Prompt Template
        self.template = """You are a helpful assistant for Question-Answering tasks.
        Use the following pieces of retrieved context to answer the question.
        If you don't know the answer, just say that you don't know.
        
        Context:
        {context}
        
        Question:
        {question}
        
        Answer:"""
        
        self.prompt = ChatPromptTemplate.from_template(self.template)
        
        # Setup Chain
        self.chain = (
            RunnableParallel({"context": self.retriever, "question": RunnablePassthrough()})
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _initialize_llm(self):
        if settings.RAG_MODE == "local":
            try:
                from langchain_community.chat_models import ChatOllama
                return ChatOllama(model=settings.OLLAMA_MODEL, temperature=0.0)
            except ImportError:
                raise ImportError("Could not import ChatOllama. Ensure langchain-community is installed.")
                pass

        elif settings.RAG_MODE in ["hybrid", "cloud"]:
            if settings.LLM_PROVIDER == "gemini":
                if not settings.GOOGLE_API_KEY:
                    raise ValueError("Google API Key not set.")
                return ChatGoogleGenerativeAI(
                    model=settings.LLM_MODEL,
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=0,
                    convert_system_message_to_human=True # Sometimes needed for older Gemini versions
                )
            elif settings.LLM_PROVIDER == "openai":
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OpenAI API Key not set.")
                return ChatOpenAI(
                    model=settings.LLM_MODEL,
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0
                )
            else:
                raise ValueError(f"Unsupported LLM Provider: {settings.LLM_PROVIDER}")
        else:
             raise ValueError(f"Unsupported RAG Mode: {settings.RAG_MODE}")

    def query(self, question: str):
        return self.chain.invoke(question)

# Global instance
# We initialize this lazily in main app usually, but for now:
try:
    rag_pipeline = RAGPipeline()
except Exception as e:
    print(f"RAG Pipeline Warning: {e}")
    rag_pipeline = None
