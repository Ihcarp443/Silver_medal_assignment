# services/feedback_improver.py

from langchain_core.prompts import ChatPromptTemplate

from services.llm_service import model 


def improve_answer(
    question: str,
    answer: str,
    reason: str | None = None,
    comment: str | None = None
):
    
    prompt = ChatPromptTemplate.from_template(
        """
You are improving a previous response based on user feedback.

Original User Question:
{question}

Original Answer:
{answer}

User Feedback:
Feedback Type: {reason}

Additional User Comments:
{comment}

Instructions:
- Keep all factual information accurate.
- Do not invent government schemes or benefits.
- Address the user's feedback.
- Make the answer clearer and more useful.
- Use headings and bullet points when helpful.
- If the user says the answer is too long, shorten it.
- If the user says the answer is too short, provide more detail.
- If the user says the answer is unclear, simplify the language.
- Return only the improved answer.

Improved Answer:
"""
    )
    print("Improving answer with feedback:", reason, comment)

    chain = prompt | model

    response = chain.invoke(
        {
            "question": question,
            "answer": answer,
            "reason": reason or "Not specified",
            "comment": comment or "No additional comments"
        }
    )
    print("Improved answer:", response.content)

    return response.content