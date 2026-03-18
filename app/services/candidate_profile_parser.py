from typing import List


COMMON_PROFILE_SKILLS = [
    "python",
    "sql",
    "machine learning",
    "deep learning",
    "nlp",
    "llm",
    "rag",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "pytorch",
    "tensorflow",
    "scikit-learn",
    "pandas",
    "numpy",
    "spark",
    "fastapi",
    "django",
    "flask",
    "postgresql",
    "mysql",
    "git",
    "linux",
    "airflow",
    "mlops",
    "data science",
    "statistics",
    "computer vision",
    "langchain",
]


def extract_profile_skills(*texts: str) -> List[str]:
    combined_text = " ".join([text for text in texts if text]).lower()
    found_skills = [skill for skill in COMMON_PROFILE_SKILLS if skill in combined_text]
    return sorted(list(set(found_skills)))