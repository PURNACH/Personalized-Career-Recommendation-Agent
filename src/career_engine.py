
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.career_data import CAREERS


def recommend_careers(skills, interests, education="", goal=""):
    user_skills = {
        item.strip().lower()
        for item in skills.split(",")
        if item.strip()
    }

    profile = " ".join([
        skills, interests, education, goal
    ]).lower()

    documents = [
        " ".join([
            career["role"],
            " ".join(career["skills"]),
            career["description"],
            career["interests"],
        ])
        for career in CAREERS
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
    )

    matrix = vectorizer.fit_transform(documents + [profile])

    similarities = cosine_similarity(
        matrix[-1], matrix[:-1]
    )[0]

    results = []

    for career, similarity in zip(CAREERS, similarities):
        required = set(career["skills"])
        matched = sorted(user_skills.intersection(required))
        missing = sorted(required - user_skills)

        skill_score = len(matched) / max(len(required), 1)

        score = (
            0.70 * float(similarity)
            + 0.30 * skill_score
        ) * 100

        results.append({
            **career,
            "score": round(min(score, 100), 1),
            "matched": matched,
            "missing": missing,
        })

    return sorted(
        results,
        key=lambda result: result["score"],
        reverse=True,
    )
