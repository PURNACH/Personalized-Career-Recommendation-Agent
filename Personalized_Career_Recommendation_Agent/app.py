import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from src.database import (
    initialize_db,
    save_profile,
    save_recommendations,
    get_profiles,
    get_profile_count,
)
from src.career_engine import recommend_careers
from src.career_data import CAREERS
from src.ai_coach import career_answer

load_dotenv()
initialize_db()

st.set_page_config(
    page_title="CareerCompass AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CUSTOM DESIGN ----------------


st.markdown("""
<style>
/* Main application background */
.stApp {
    background: #000000;
    color: #FFFFFF;
}

/* Main headings and text */
h1, h2, h3, h4, h5, h6, p, label {
    color: #FFFFFF;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #000000;
    border-right: 2px solid #00FF00;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF;
}

/* Hero section */
.hero {
    background: #000000;
    border: 2px solid #00FF00;
    border-radius: 16px;
    padding: 24px;
    color: #FFFFFF;
    margin-bottom: 18px;
}

.hero h1 {
    color: #00FF00;
}

/* Metric cards */
.metric {
    background: #000000;
    border: 1px solid #00FF00;
    padding: 18px;
    border-radius: 14px;
    min-height: 115px;
    margin-bottom: 10px;
}

.metric h2 {
    color: #00FF00;
    margin: 5px 0;
}

/* Content cards */
.card {
    background: #000000;
    color: #FFFFFF;
    border: 1px solid #00FF00;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #000000;
    color: #FFFFFF;
    border: 1px solid #00FF00;
    border-radius: 6px;
}

/* Placeholder text */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #FFFFFF;
}

/* Select boxes */
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background: #000000;
    color: #FFFFFF;
}

/* Buttons */
.stButton button {
    background: #000000;
    color: #00FF00;
    border: 2px solid #00FF00;
    border-radius: 8px;
    font-weight: bold;
    transition: 0.2s;
}

/* Button hover */
.stButton button:hover {
    background: #00FF00;
    color: #000000;
    border: 2px solid #00FF00;
}

/* Links */
a {
    color: #00FF00 !important;
}

/* Success messages */
[data-testid="stAlert"][kind="success"] {
    background: #000000;
    border: 1px solid #00FF00;
    color: #FFFFFF;
}

/* Error and warning messages */
[data-testid="stAlert"][kind="error"],
[data-testid="stAlert"][kind="warning"] {
    background: #000000;
    border: 1px solid #FF0000;
    color: #FFFFFF;
}

/* Error text */
.stException,
[data-testid="stError"] {
    color: #FF0000;
}

/* Progress bar */
.stProgress > div > div > div {
    background: #00FF00;
}

/* Dividers */
hr {
    border-color: #00FF00;
}

/* Checkbox and radio labels */
.stCheckbox label,
.stRadio label {
    color: #FFFFFF;
}

/* Dataframes and tables */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid #00FF00;
}

/* Remove extra decoration */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("# 🎯 CareerCompass AI")
    st.caption("PERSONALIZED CAREER GUIDANCE")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Home",
            "Profile",
            "Recommendations",
            "Learning Roadmap",
            "Skill Gap Analysis",
            "Job Opportunities",
            "Chat Assistant",
        ],
        key="navigation",
    )

    st.divider()
    st.markdown("**Developed by Purnachandar**")
    st.caption("AI • Machine Learning • NLP")

# ---------------- SESSION STATE ----------------

if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "Purnachandar",
        "education": "MCA",
        "experience": 0.0,
        "skills": "",
        "interests": "",
        "goal": "Get my first job",
    }

if "results" not in st.session_state:
    st.session_state.results = []

if "chat" not in st.session_state:
    st.session_state.chat = []

if "roadmap_role" not in st.session_state:
    st.session_state.roadmap_role = "Software Developer"

# ---------------- PROFILE INPUT ----------------

def profile_form():
    p = st.session_state.profile

    with st.form("profile_form"):
        name = st.text_input("Full name", value=p["name"])

        education = st.selectbox(
            "Education",
            ["MCA", "B.Tech / B.E.", "BCA", "B.Sc",
             "M.Sc", "B.Com", "Other"],
            index=["MCA", "B.Tech / B.E.", "BCA", "B.Sc",
                   "M.Sc", "B.Com", "Other"].index(p["education"])
            if p["education"] in [
                "MCA", "B.Tech / B.E.", "BCA", "B.Sc",
                "M.Sc", "B.Com", "Other"
            ] else 0,
        )

        experience = st.number_input(
            "Experience (years)",
            min_value=0.0,
            max_value=50.0,
            value=float(p["experience"]),
            step=0.5,
        )

        skills = st.text_area(
            "Skills (comma-separated)",
            value=p["skills"],
            placeholder="Python, SQL, Excel, Machine Learning",
        )

        interests = st.text_area(
            "Career interests",
            value=p["interests"],
            placeholder="AI, data analysis, software development",
        )

        goal = st.selectbox(
            "Career goal",
            [
                "Get my first job",
                "Change my career",
                "Improve my technical skills",
                "Get an internship",
                "Prepare for a promotion",
            ],
            index=[
                "Get my first job",
                "Change my career",
                "Improve my technical skills",
                "Get an internship",
                "Prepare for a promotion",
            ].index(p["goal"])
            if p["goal"] in [
                "Get my first job",
                "Change my career",
                "Improve my technical skills",
                "Get an internship",
                "Prepare for a promotion",
            ] else 0,
        )

        submitted = st.form_submit_button(
            "Save Profile and Find Careers",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not name.strip() or not skills.strip():
            st.error("Enter your name and at least one skill.")
            return

        st.session_state.profile = {
            "name": name.strip(),
            "education": education,
            "experience": experience,
            "skills": skills,
            "interests": interests,
            "goal": goal,
        }

        p = st.session_state.profile

        profile_id = save_profile(
            p["name"], p["education"], p["experience"],
            p["skills"], p["interests"], p["goal"],
        )

        results = recommend_careers(
            p["skills"], p["interests"],
            p["education"], p["goal"],
        )

        save_recommendations(profile_id, results)
        st.session_state.results = results

        st.success("Profile saved and recommendations generated!")

# ---------------- RECOMMENDATION CARDS ----------------

def show_recommendations(limit=None):
    results = st.session_state.results

    if not results:
        st.info(
            "Complete your profile first to generate personalized "
            "career recommendations."
        )
        if st.button("Open Profile", key="open_profile"):
            st.session_state.navigation = "Profile"
            st.rerun()
        return

    shown = results if limit is None else results[:limit]

    for item in shown:
        with st.container(border=True):
            left, right = st.columns([5, 1])

            with left:
                st.markdown(f"### {item['role']}")
                st.write(item["description"])
                st.caption(
                    "Matching skills: "
                    + (", ".join(item["matched"]) or "None detected")
                )

            with right:
                st.metric("Match score", f"{item['score']}%")

            with st.expander("View career details"):
                st.write("**Skills to develop**")
                st.write(", ".join(item["missing"]) or "No listed gaps.")

                st.write("**Suggested courses**")
                for course in item["courses"]:
                    st.write(f"• {course}")

                st.write("**Portfolio project**")
                st.write(item["project"])

# ---------------- HOME DASHBOARD ----------------

if page == "Home":
    p = st.session_state.profile

    st.markdown(f"""
    <div class="hero">
      <h1>👋 Hello, {p['name']}!</h1>
      <p>Here are your personalized career recommendations based on
      your profile. Build skills, discover opportunities, and plan
      your future.</p>
      <b>Better Skills · Better Opportunities · A Brighter Future</b>
    </div>
    """, unsafe_allow_html=True)

    results = st.session_state.results

    career_count = len(results) if results else 5
    job_count = 8
    resource_count = sum(
        len(c["courses"]) for c in results[:3]
    ) if results else 12
    gap_count = len(results[0]["missing"]) if results else 4

    a, b, c, d = st.columns(4)

    with a:
        st.markdown(
            f'<div class="metric blue"><b>💼 Recommended Career Paths</b>'
            f'<h2>{career_count}</h2><small>Career options</small></div>',
            unsafe_allow_html=True,
        )

    with b:
        st.markdown(
            f'<div class="metric green"><b>👤 Recommended Job Roles</b>'
            f'<h2>{job_count}</h2><small>Example role categories</small></div>',
            unsafe_allow_html=True,
        )

    with c:
        st.markdown(
            f'<div class="metric purple"><b>📚 Learning Resources</b>'
            f'<h2>{resource_count}</h2><small>Course suggestions</small></div>',
            unsafe_allow_html=True,
        )

    with d:
        st.markdown(
            f'<div class="metric orange"><b>🎯 Skill Gaps Identified</b>'
            f'<h2>{gap_count}</h2><small>Skills to improve</small></div>',
            unsafe_allow_html=True,
        )

    left, right = st.columns([1.25, 1])

    with left:
        st.subheader("⭐ Top Career Recommendations")
        show_recommendations(limit=4)

    with right:
        st.subheader("📘 Your Learning Roadmap")

        stages = [
            ("1", "Build Strong Fundamentals",
             "Python, SQL and programming basics"),
            ("2", "Learn Core Technologies",
             "Tools and frameworks for your career"),
            ("3", "Gain Practical Experience",
             "Projects, portfolio and practical exercises"),
            ("4", "Get Career Ready",
             "Interview practice and relevant certifications"),
        ]

        for number, title, description in stages:
            with st.container(border=True):
                st.markdown(f"**{number}. {title}**")
                st.caption(description)

        st.subheader("🤖 Career Guidance Assistant")
        st.write(
            "Ask about career options, learning plans, "
            "technical skills and interviews."
        )

        question = st.text_input(
            "Your career question",
            key="home_question",
        )

        if st.button("Ask Career Coach", type="primary"):
            if question.strip():
                answer = career_answer(
                    question, st.session_state.profile
                )
                st.write(answer)
            else:
                st.warning("Enter a question first.")

# ---------------- PROFILE PAGE ----------------

elif page == "Profile":
    st.title("👤 Student Profile")
    st.write("Enter your qualifications, skills and career goals.")
    profile_form()

# ---------------- RECOMMENDATIONS PAGE ----------------

elif page == "Recommendations":
    st.title("⭐ Career Recommendations")
    st.write("Career matches generated from your profile.")
    show_recommendations()

# ---------------- LEARNING ROADMAP ----------------

elif page == "Learning Roadmap":
    st.title("📚 Personalized Learning Roadmap")

    role_names = [c["role"] for c in CAREERS]

    selected = st.selectbox(
        "Select your target career",
        role_names,
        index=role_names.index(st.session_state.roadmap_role)
        if st.session_state.roadmap_role in role_names else 0,
    )

    st.session_state.roadmap_role = selected

    career = next(c for c in CAREERS if c["role"] == selected)

    roadmap = [
        ("Weeks 1–2", career["courses"][0]),
        ("Weeks 3–4", career["courses"][1]),
        ("Weeks 5–6", career["courses"][2]),
        ("Weeks 7–8", career["courses"][3]),
        ("Weeks 9–10", "Build " + career["project"]),
        ("Weeks 11–12", "Portfolio and interview preparation"),
    ]

    st.progress(0.0, text="Complete the milestones below.")

    for period, task in roadmap:
        with st.container(border=True):
            st.checkbox(
                f"{period}: {task}",
                key=f"roadmap_{selected}_{period}",
            )

    st.caption(
        "Roadmap completion is tracked in the current browser session. "
        "It is not yet saved to the database."
    )

# ---------------- SKILL GAP ANALYSIS ----------------

elif page == "Skill Gap Analysis":
    st.title("🎯 Skill Gap Analysis")

    selected = st.selectbox(
        "Target career",
        [c["role"] for c in CAREERS],
    )

    career = next(c for c in CAREERS if c["role"] == selected)

    user_skills = {
        s.strip().lower()
        for s in st.session_state.profile["skills"].split(",")
        if s.strip()
    }

    required = set(career["skills"])
    matched = sorted(user_skills.intersection(required))
    missing = sorted(required - user_skills)

    st.subheader(selected)

    first, second = st.columns(2)

    with first:
        st.metric("Skills matched", len(matched))
        if matched:
            for skill in matched:
                st.success(skill)
        else:
            st.info("No matching skills entered yet.")

    with second:
        st.metric("Skills to develop", len(missing))
        if missing:
            for skill in missing:
                st.warning(skill)
        else:
            st.success("All listed skills match.")

    completion = len(matched) / max(len(required), 1)
    st.progress(completion, text=f"Listed skill coverage: {completion:.0%}")

    st.caption(
        "Skill coverage is based only on the selected role's "
        "starter skill list. It does not measure real-world proficiency."
    )

# ---------------- JOB OPPORTUNITIES ----------------

elif page == "Job Opportunities":
    st.title("💼 Job Opportunities")
    st.write(
        "Explore example job-role categories that correspond to "
        "the career paths in this project."
    )

    job_rows = [
        {
            "Role": c["role"],
            "Example level": "Entry level / Junior",
            "Key skills": ", ".join(c["skills"][:4]),
            "Source": "Illustrative role, not a live vacancy",
        }
        for c in CAREERS
    ]

