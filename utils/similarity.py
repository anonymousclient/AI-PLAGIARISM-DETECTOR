from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(text1, text2):
    """
    Calculate similarity between two texts using TF-IDF and cosine similarity.
    Returns a percentage (0-100).
    """
    if not text1 or not text2:
        return 0.0

    try:
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])

        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = round(similarity[0][0] * 100, 2)
        return score
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0


def get_status(score):
    """
    Return plagiarism status based on similarity score.
    0-30  → Safe
    30-60 → Suspicious
    60-100 → High Plagiarism
    """
    if score < 30:
        return "Safe"
    elif score < 60:
        return "Suspicious"
    else:
        return "High Plagiarism"


def get_status_color(score):
    """Return Bootstrap color class based on similarity score."""
    if score < 30:
        return "success"     # Green
    elif score < 60:
        return "warning"     # Yellow
    else:
        return "danger"      # Red
