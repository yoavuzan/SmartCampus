# Project Context: SmartCampus (University Management System)
**Last Updated:** March 10, 2026

I am developing a full-stack university management system called **SmartCampus**.
The entire system, including the AI logic and User Interface, is designed for **Hebrew-speaking users**.

## Root Structure (C:\Users\yoav5\CyberPro\SmartCampus):
- `Server/`: Backend (FastAPI + SQLModel + LangChain).
- `Frontend/`: Frontend (React).
- `.venv/`: Python environment.
- `Gemini.md`: This context file.

## Backend Detailed Structure (Server/):
- `main.py`: Entry point and API Routes.
- `config.py` & `.env`: Environment and settings management.
- `database.db`: Local SQLite database.
- `PDF_Files/`: Contains `regulations.pdf` (The source for RAG).
- `chroma_db/`: Persistent vector store for AI context.
- `utils/`:
    - `security.py`: JWT & Password Hashing (SHA-256 + Bcrypt).
    - `pdf_handler.py`: RAG logic using Gemini 1.5 Flash.
- `DB/`:
    - `Engine.py`: SQLModel engine configuration.
    - `database.py`: Session management.
    - `schemas/`: `Student.py`, `Course.py`, `Classroom.py`, `Lecturer.py`, `Exam.py`, `StudentCourseLink.py`.

## AI & Data Strategy:
- **Language Support:** **Full Native Hebrew Support.** The AI must understand and respond in professional, academic Hebrew.
- **LLM:** Google Gemini 1.5 Flash (Excellent for Hebrew NLU).
- **RAG:** Implementing **LCEL** (LangChain Expression Language).
- **Embeddings:** `models/embedding-001`.
- **Vector Store:** ChromaDB (`langchain-chroma`).

## Core Features:
1. **Authentication:** Secure login with role-based redirection (Admin/User).
2. **Hebrew AI Assistant:** A specialized bot that retrieves information from the university regulations PDF and answers students in clear, natural Hebrew.
3. **Campus Management:** Full CRUD operations for all academic entities.

---
**Instruction for Gemini:** - All code comments and documentation should be in English.
- **All AI-generated content for the end-user MUST be in Hebrew.**
- Use the specific schema paths in `Server/DB/schemas/`. 
- For AI tasks, use `Server/utils/pdf_handler.py`. 
- Always use **LCEL** syntax to avoid legacy `RetrievalQA` errors.