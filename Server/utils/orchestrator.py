import os
from typing import AsyncGenerator

from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

from .pdf_handler import get_rag_chain
from DB.database import sqlite_url

# Model Configuration
# Gemini 2.0 Flash is recommended for its speed and logic capabilities
llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)

# 1. Routing Chain (Analysis)
router_prompt = ChatPromptTemplate.from_template("""
Analyze the user's question and determine which data sources are needed to answer it.
Available sources:
- SQL: Personal student information, grades, courses, lecturers, classrooms, and exams.
- PDF: Academic regulations, university laws, and procedures.

Answer ONLY in JSON format with the keys "sql" and "pdf" and boolean values (true/false).

Question: {question}
""")

router_chain = router_prompt | llm | JsonOutputParser()

# 2. SQL Chain (Manual LCEL)
db = SQLDatabase.from_uri(sqlite_url)

sql_gen_prompt = ChatPromptTemplate.from_template("""
Based on the following database schema, write a SQLite query to answer the user's question.
Output ONLY the raw SQL query without any backticks, markdown formatting, or explanations.

Database Schema:
{schema}

Question: {question}
SQL Query:""")

def get_schema(_):
    return db.get_table_info()

def run_query(query):
    # Removing potential formatting noise if the LLM adds it
    clean_query = query.replace("```sql", "").replace("```", "").strip()
    return db.run(clean_query)

sql_chain = (
    RunnablePassthrough.assign(schema=get_schema)
    | sql_gen_prompt
    | llm
    | StrOutputParser()
    | run_query
)

# 3. PDF Chain (Imported from pdf_handler)
pdf_chain = get_rag_chain()

# 4. Final Answer Chain
final_prompt = ChatPromptTemplate.from_template("""
You are an intelligent academic assistant for the SmartCampus system.
Use the provided context information to answer the user's question professionally and politely in Hebrew.

System Information (SQL Context):
{sql_context}

Regulations Information (PDF Context):
{pdf_context}

User Question: {question}

Instructions:
- If no relevant information is found in either source, provide a polite general response in Hebrew.
- Use bold (**) to emphasize important details like dates, grades, or section numbers.
- Your entire response MUST be in Hebrew only.
- If regulations are used, mention the section number as provided in the context.
""")

async def orchestrator(question: str) -> AsyncGenerator[str, None]:
    # Quick response for greetings to save tokens and time
    if len(question) < 4 or any(word in question for word in ["היי", "שלום", "בוקר טוב"]):
        async for chunk in llm.astream(f"ענה בנימוס ובקצרה בעברית לסטודנט: {question}"):
            yield chunk.content
        return

    # Phase 1: Analyze Route
    try:
        route = await router_chain.ainvoke({"question": question})
    except Exception as e:
        print(f"Routing Error: {e}")
        route = {"sql": True, "pdf": True} # Fallback to both sources
    
    sql_context = "No system data retrieved."
    pdf_context = "No regulation data retrieved."
    
    # Phase 2: Fetch Data
    if route.get("sql"):
        try:
            sql_context = sql_chain.invoke({"question": question})
        except Exception as e:
            sql_context = f"SQL Retrieval Error: {e}"
            
    if route.get("pdf"):
        try:
            pdf_context = pdf_chain.invoke(question)
        except Exception as e:
            pdf_context = f"PDF Retrieval Error: {e}"

    # Phase 3: Final Streamed Answer
    inputs = {
        "sql_context": sql_context,
        "pdf_context": pdf_context,
        "question": question
    }
    
    final_chain = final_prompt | llm | StrOutputParser()
    
    async for chunk in final_chain.astream(inputs):
        yield chunk

def get_orchestrator_chain():
    return orchestrator