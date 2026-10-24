
import os


def career_answer(question, profile=None):
    api_key = os.getenv("GROQ_API_KEY", "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").strip()

    if not api_key:
        return (
            "Welcome to CareerCompass AI! To begin, learn Python "
            "fundamentals, practice SQL, build a portfolio project, "
            "and prepare for interviews in your target role. "
            "Add a Groq API key to enable AI-powered responses."
        )

    try:
        from groq import Groq

        client = Groq(api_key=api_key)

        context = ""
        if profile:
            context = (
                f"\nStudent profile: {profile}\n"
            )

        response = client.chat.completions.create(
            model=os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-120b",
            ),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CareerCompass AI, a practical career "
                        "guidance assistant. Help with career choices, "
                        "technical skills, projects, learning roadmaps "
                        "and interview preparation. Do not guarantee "
                        "jobs or invent live vacancies."
                    ),
                },
                {
                    "role": "user",
                    "content": context + question,
                },
            ],
            temperature=0.4,
        )

        return response.choices[0].message.content

    except Exception as exc:
        return (
            "The AI service could not respond. Check the API key, "
            "model access and internet connection. "
            f"Error: {exc}"
        )
