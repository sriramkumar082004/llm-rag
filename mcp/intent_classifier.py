import re
from datetime import datetime


def is_live_question(question: str) -> bool:
    """
    Determines if a question requires live/real-time data.

    Returns True if the question contains temporal indicators
    or topics that require current information.
    """
    question_lower = question.lower()

    # Temporal keywords
    temporal_keywords = [
        "today",
        "now",
        "current",
        "latest",
        "recent",
        "yesterday",
        "this week",
        "this month",
        "this year",
        "trending",
        "breaking",
        "live",
        "real-time",
        datetime.now().strftime("%Y"),  # Current year
        datetime.now().strftime("%B"),  # Current month
    ]

    # Topics that typically need live data
    live_topics = [
        "news",
        "weather",
        "stock",
        "price",
        "election",
        "covid",
        "pandemic",
        "sports score",
        "match result",
        "currency rate",
        "exchange rate",
        "update",
    ]

    # Check for temporal keywords
    for keyword in temporal_keywords:
        if keyword in question_lower:
            return True

    # Check for live topics
    for topic in live_topics:
        if topic in question_lower:
            return True

    # Check for future tense (predictions)
    future_patterns = [
        r"\bwill\b",
        r"\bgoing to\b",
        r"\bforecast\b",
        r"\bpredict\b",
        r"\bexpect\b",
    ]
    for pattern in future_patterns:
        if re.search(pattern, question_lower):
            return True

    return False


def is_student_question(question: str) -> bool:
    """
    Determines if a question is about student data from the database.

    Returns True if the question contains student-related keywords
    or patterns that suggest querying the student database.
    """
    question_lower = question.lower()

    # Keywords that indicate student database queries
    student_keywords = [
        "student",
        "students",
        "enrollment",
        "enrolled",
        "course",
        "courses",
        "class",
        "classes",
        "grade",
        "grades",
        "gpa",
        "learner",
        "learners",
        "pupil",
        "pupils",
        "undergraduate",
        "graduate",
        "major",
        "minor",
    ]

    # Check for student-specific keywords
    for keyword in student_keywords:
        if keyword in question_lower:
            return True

    # Check for operations on student data
    student_operations = [
        "add student",
        "create student",
        "new student",
        "register student",
        "enroll student",
        "delete student",
        "remove student",
        "update student",
        "modify student",
        "edit student",
        "list student",
        "show student",
        "find student",
        "search student",
        "get student",
        "how many student",
        "count student",
        "average age",
        "who is enrolled",
        "who is taking",
        "who studies",
    ]

    for operation in student_operations:
        if operation in question_lower:
            return True

    return False


def is_domain_question(question: str) -> bool:
    """
    Determines if a question is about the domain-specific data (crime database).

    Returns True if the question is asking about crimes, incidents, or related data
    from the database.
    """
    question_lower = question.lower()

    # Keywords that indicate crime database queries
    domain_keywords = [
        "crime",
        "criminal",
        "incident",
        "offense",
        "arrest",
        "robbery",
        "theft",
        "assault",
        "burglary",
        "homicide",
        "violation",
        "suspect",
        "victim",
        "report",
        "police",
        "investigation",
        "felony",
        "misdemeanor",
        "los angeles",
        # "la" is too short/generic on its own, better to rely on longer context or specific crime terms
        # "location", "area", "district" are too generic unless combined with crime terms
    ]

    # Check if question contains domain-specific keywords
    for keyword in domain_keywords:
        if keyword in question_lower:
            return True

    # Check for queries about specific data patterns ONLY if they likely relate to the domain
    # We remove generic patterns like "how many" or "list" as they apply to anything.
    # Instead, we can look for "crime" related patterns or just rely on the keywords above.

    # If the user asks specifically about "records" or "stats" WITHOUT a crime keyword,
    # it's usually general. So we rely heavily on the explicit domain keywords.

    return False


def classify_intent(question: str) -> str:
    """
    Classifies the intent of a question into one of four categories:
    - 'student': Requires student data from PostgreSQL database
    - 'web': Requires live/current data from the web
    - 'rag': Requires domain-specific data from the crime database
    - 'general': General knowledge question for Ollama

    Returns the intent type as a string.
    """

    # Priority 1: Student data questions go to Student API
    if is_student_question(question):
        return "student"

    # Priority 2: Live data questions go to web
    if is_live_question(question):
        return "web"

    # Priority 3: Domain-specific questions go to RAG database
    if is_domain_question(question):
        return "rag"

    # Priority 4: Everything else is general knowledge
    return "general"
