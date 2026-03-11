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
Analyze the user's question and determine the data source.

Available sources:
- SQL: Information about students, courses enrollment, lecturers details, exam dates, and classroom locations (building, room number, capacity).
- PDF: Academic regulations, university laws, attendance policies, and general procedures.

Note: This system does NOT store student grades in the SQL database. Questions about grades should be handled by PDF (general rules) or a polite refusal.

Answer ONLY in JSON: {{"sql": boolean, "pdf": boolean}}

Question: {question}
""")

router_chain = router_prompt | llm | JsonOutputParser()

# 2. SQL Chain (Manual LCEL)
db = SQLDatabase.from_uri(sqlite_url)

sql_gen_prompt = ChatPromptTemplate.from_template("""
You are a SQLite expert. Based on the schema below, write a query to answer the user's question.

Database Schema:
- Student: (id, first_name, last_name, email, major, is_active)
- Course: (id, name, code, credits, lecturer_id, classroom_id)
- StudentCourseLink: (student_id, course_id) -> Link table for Students and Courses
- Lecturer: (id, first_name, last_name, email, department)
- Exam: (id, subject, date, classroom_id, lecturer_id, course_id)
- Classroom: (id, building, room_number, capacity, has_projector)

Relationships:
- To find a student's courses: Student JOIN StudentCourseLink JOIN Course.
- To find a course's lecturer: Course JOIN Lecturer on Course.lecturer_id = Lecturer.id.
- To find where an exam takes place: Exam JOIN Classroom on Exam.classroom_id = Classroom.id.

Instructions:
1. Use ONLY the columns listed above.
2. For dates, use SQLite syntax.
3. Return ONLY the raw SQL query.

Question: {question}
SQL Query:""")


def get_schema(_):
    return db.get_table_info()


def run_query(query):
    # Removing potential formatting noise if the LLM adds it
    clean_query = query.replace("```sql", "").replace("```", "").strip()
    return db.run(clean_query)


fixed_schema = """
- Student(id, first_name, last_name, email, major)
- Course(id, name, code, lecturer_id, classroom_id)
- StudentCourseLink(student_id, course_id)
- Exam(id, subject, date, classroom_id, course_id)
- Classroom(id, building, room_number)
- Lecturer(id, first_name, last_name, email, department)
"""

sql_chain = (
    RunnablePassthrough.assign(schema=lambda _: fixed_schema)
    | sql_gen_prompt
    | llm
    | StrOutputParser()
    | run_query
)

# 3. PDF Chain (Imported from pdf_handler)
pdf_chain = get_rag_chain()

# 4. Final Answer Chain
final_prompt = ChatPromptTemplate.from_template("""
You are an academic assistant for the SmartCampus system. 
Your goal is to provide professional, polite, and accurate responses in Hebrew based on the provided context.

Context from SQL (Personal/Specific Data):
{sql_context}

Context from PDF (Regulations/Procedures):
{pdf_context}

User Question: {question}

Instructions:
1. LANGUAGE: Your entire response MUST be in Hebrew.
2. GRADES: If the user asks about grades, explicitly state that the system currently does not have access to personal grades, but can assist with exam dates or course registration.
3. FORMATTING: Use bold (**) for course names, lecturer names, locations (building/room), and dates.
4. TONE: Be helpful and academic. If a lecturer's name is found in the SQL context, refer to them as "המרצה [Name]".
5. ACCURACY: If no information is found in either context, politely inform the user that you don't have that specific information.
""")


async def orchestrator(question: str) -> AsyncGenerator[str, None]:
    # Quick response for greetings to save tokens and time
    if len(question) < 4 or any(
        word in question for word in ["היי", "שלום", "בוקר טוב"]
    ):
        async for chunk in llm.astream(
            f"Answer politely and briefly in Hebrew: {question}"
        ):
            content = chunk.content
            if isinstance(content, str):
                yield content
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        yield part["text"]
                    elif isinstance(part, str):
                        yield part
        return

    # Phase 1: Analyze Route
    try:
        route = await router_chain.ainvoke({"question": question})
    except Exception as e:
        print(f"Routing Error: {e}")
        route = {"sql": True, "pdf": True}  # Fallback to both sources

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
        "question": question,
    }

    final_chain = final_prompt | llm | StrOutputParser()

    async for chunk in final_chain.astream(inputs):
        if chunk:
            yield str(chunk)


def get_orchestrator_chain():
    return orchestrator
