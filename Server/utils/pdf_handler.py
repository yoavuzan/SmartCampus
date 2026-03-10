import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from config import settings

# Configure Google API Key
os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
PDF_PATH = os.path.join(BASE_DIR, "PDF_Files", "regulations.pdf")

# Initialize Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def initialize_rag():
    """Load PDF, split text, and create/load vector store."""
    if not os.path.exists(PDF_PATH):
        print(
            f"Warning: PDF file not found at {PDF_PATH}. Please place the regulations PDF there."
        )
        return None

    # Load and split
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    # Create or load vector store
    vector_store = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=DB_DIR
    )
    return vector_store


# Global variable to hold the vector store
_vector_store = None


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        if os.path.exists(DB_DIR):
            _vector_store = Chroma(
                persist_directory=DB_DIR, embedding_function=embeddings
            )
        else:
            _vector_store = initialize_rag()
    return _vector_store


def get_rag_chain():
    """Returns the LCEL RAG chain for streaming or invocation."""
    vs = get_vector_store()
    if vs is None:
        return None

    # Initialize LLM

    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)
    # Hebrew Prompt Template
    template = """
    Use the following information to answer the question at the end. 
    If you don't know the answer, just say that you don't know; do not try to make up an answer.
    Always answer in Hebrew only.

    CRITICAL: Mention the section number (e.g., "לפי סעיף X").
    {context}

    Question: {question}
    Detailed answer in Hebrew:"""

    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    rag_chain = (
        {"context": vs.as_retriever() | format_docs, "question": RunnablePassthrough()}
        | QA_CHAIN_PROMPT
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_regulations(question: str):
    """Query the RAG pipeline in Hebrew using the modern LCEL chain (Blocking)."""
    chain = get_rag_chain()
    if chain is None:
        return "שגיאה: לא נמצא קובץ תקנון לניתוח."
    return chain.invoke(question)


if __name__ == "__main__":
    # Example usage (ensure PDF exists)
    response = ask_regulations("מה הם תנאי המעבר לשנה ב'?")
    print(response)
    pass
