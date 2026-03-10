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
# Using gemini-1.5-flash for stability and better rate limits
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# 1. Routing Chain (Analysis)
router_prompt = ChatPromptTemplate.from_template("""
נתח את השאלה של המשתמש וקבע אילו מקורות מידע דרושים כדי לענות עליה.
המקורות הזמינים:
- SQL: מידע אישי על הסטודנט, ציונים, קורסים, מרצים, כיתות ומבחנים.
- PDF: תקנון האקדמי, חוקים ונהלים של האוניברסיטה.

ענה בפורמט JSON בלבד עם המפתחות "sql" ו-"pdf" וערכים בוליאניים (true/false).

שאלה: {question}
""")

router_chain = router_prompt | llm | JsonOutputParser()

# 2. SQL Chain (Manual LCEL)
db = SQLDatabase.from_uri(sqlite_url)

sql_gen_prompt = ChatPromptTemplate.from_template("""
בהתבסס על סכימת הנתונים הבאה, כתוב שאילתת SQLite שתענה על שאלת המשתמש. 
כתוב רק את השאילתה עצמה, ללא גרשיים או מילות הסבר.

סכימת נתונים:
{schema}

שאלה: {question}
שאילתת SQL:""")

def get_schema(_):
    return db.get_table_info()

def run_query(query):
    return db.run(query)

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
אתה עוזר אקדמי אינטליגנטי במערכת SmartCampus. 
השתמש במידע הבא כדי לענות על שאלת המשתמש בצורה מנומסת ומקצועית בעברית.

מידע מהמערכת (SQL):
{sql_context}

מידע מהתקנון (PDF):
{pdf_context}

שאלה: {question}

הוראות:
- אם אין מידע רלוונטי באף אחד מהמקורות, ענה תשובה כללית בנימוס.
- השתמש בבולד (**) להדגשת דברים חשובים.
- ענה בעברית בלבד.
""")

async def orchestrator(question: str) -> AsyncGenerator[str, None]:
    if len(question) < 4 or any(word in question for word in ["היי", "שלום", "בוקר טוב"]):
        async for chunk in llm.astream(f"ענה בנימוס ובקצרה בעברית לסטודנט: {question}"):
            yield chunk.content
        return
    # Phase 1: Analyze Route
    try:
        route = await router_chain.ainvoke({"question": question})
    except Exception as e:
        print(f"Routing Error: {e}")
        route = {"sql": True, "pdf": True} # Fallback to both
    
    sql_context = "לא נדרש מידע מהמערכת."
    pdf_context = "לא נדרש מידע מהתקנון."
    
    # Phase 2: Fetch Data
    if route.get("sql"):
        try:
            sql_context = sql_chain.invoke({"question": question})
        except Exception as e:
            sql_context = f"שגיאה בשליפת נתונים מה-SQL: {e}"
            
    if route.get("pdf"):
        try:
            # pdf_chain (from pdf_handler) is an LCEL chain
            pdf_context = pdf_chain.invoke(question)
        except Exception as e:
            pdf_context = f"שגיאה בשליפת נתונים מהתקנון: {e}"

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
