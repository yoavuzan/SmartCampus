import asyncio
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.orchestrator import orchestrator

async def test_question(q):
    print(f"\nQuestion: {q}")
    print("Response: ", end="", flush=True)
    async for chunk in orchestrator(q):
        print(chunk, end="", flush=True)
    print("\n---")

async def main():
    questions = [
        "מה הם תנאי המעבר לשנה ב?", # PDF
        "אילו קורסים יש במחלקה למדעי המחשב?", # SQL
        "האם יש לי מבחנים בקרוב?" # SQL
    ]
    for q in questions:
        await test_question(q)

if __name__ == "__main__":
    asyncio.run(main())
