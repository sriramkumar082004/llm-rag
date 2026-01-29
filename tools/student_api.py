"""
Student API Tool - Natural Language Interface to Student Database

Provides CRUD operations and natural language query capabilities
for the Student PostgreSQL database.
"""

import logging
from typing import List, Dict, Optional, Any
from db import DatabaseConnection
from rag import query_ollama

logger = logging.getLogger(__name__)


# ========================================
# CRUD Operations
# ========================================


def get_all_students(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Fetch all student records with pagination.

    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        List of student dictionaries
    """
    query = """
    SELECT user_id, name, age, course 
    FROM students 
    ORDER BY user_id 
    LIMIT %s OFFSET %s;
    """

    try:
        with DatabaseConnection() as cursor:
            cursor.execute(query, (limit, offset))
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            students = [dict(zip(columns, row)) for row in results]
            logger.info(f"✅ Retrieved {len(students)} students")
            return students
    except Exception as e:
        logger.error(f"❌ Error fetching students: {e}")
        return []


def get_student_by_id(student_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a specific student by ID.

    Args:
        student_id: Student ID

    Returns:
        Student dictionary or None if not found
    """
    query = """
    SELECT user_id, name, age, course 
    FROM students 
    WHERE user_id = %s;
    """

    try:
        with DatabaseConnection() as cursor:
            cursor.execute(query, (student_id,))
            result = cursor.fetchone()

            if result:
                columns = [desc[0] for desc in cursor.description]
                student = dict(zip(columns, result))
                logger.info(f"✅ Retrieved student ID {student_id}")
                return student
            else:
                logger.warning(f"⚠️  Student ID {student_id} not found")
                return None
    except Exception as e:
        logger.error(f"❌ Error fetching student {student_id}: {e}")
        return None


def search_students(name: str) -> List[Dict[str, Any]]:
    """
    Search students by name (case-insensitive partial match).

    Args:
        name: Name or partial name to search for

    Returns:
        List of matching student dictionaries
    """
    query = """
    SELECT user_id, name, age, course 
    FROM students 
    WHERE LOWER(name) LIKE LOWER(%s)
    ORDER BY name;
    """

    try:
        with DatabaseConnection() as cursor:
            cursor.execute(query, (f"%{name}%",))
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            students = [dict(zip(columns, row)) for row in results]
            logger.info(f"✅ Found {len(students)} students matching '{name}'")
            return students
    except Exception as e:
        logger.error(f"❌ Error searching students: {e}")
        return []


def get_students_by_course(course: str) -> List[Dict[str, Any]]:
    """
    Get all students enrolled in a specific course.

    Args:
        course: Course name (case-insensitive partial match)

    Returns:
        List of student dictionaries
    """
    query = """
    SELECT user_id, name, age, course 
    FROM students 
    WHERE LOWER(course) LIKE LOWER(%s)
    ORDER BY name;
    """

    try:
        with DatabaseConnection() as cursor:
            cursor.execute(query, (f"%{course}%",))
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            students = [dict(zip(columns, row)) for row in results]
            logger.info(f"✅ Found {len(students)} students in course '{course}'")
            return students
    except Exception as e:
        logger.error(f"❌ Error fetching students by course: {e}")
        return []


def add_student(
    name: str,
    age: int,
    course: str,
) -> Optional[int]:
    """
    Add a new student to the database.

    Args:
        name: Student name
        age: Student age
        course: Course name

    Returns:
        New student ID or None if failed
    """
    query = """
    INSERT INTO students (name, age, course)
    VALUES (%s, %s, %s)
    RETURNING user_id;
    """

    try:
        with DatabaseConnection() as cursor:
            cursor.execute(query, (name, age, course))
            student_id = cursor.fetchone()[0]
            logger.info(f"✅ Added new student: {name} (ID: {student_id})")
            return student_id
    except Exception as e:
        logger.error(f"❌ Error adding student: {e}")
        return None


def update_student(student_id: int, **kwargs) -> bool:
    """
    Update student information.

    Args:
        student_id: Student ID
        **kwargs: Fields to update (name, age, course)

    Returns:
        True if successful, False otherwise
    """
    allowed_fields = {"name", "age", "course"}
    update_fields = {
        k: v for k, v in kwargs.items() if k in allowed_fields and v is not None
    }

    if not update_fields:
        logger.warning("⚠️  No valid fields to update")
        return False

    set_clause = ", ".join([f"{field} = %s" for field in update_fields.keys()])
    query = f"""
    UPDATE students 
    SET {set_clause}
    WHERE user_id = %s;
    """

    try:
        with DatabaseConnection() as cursor:
            values = list(update_fields.values()) + [student_id]
            cursor.execute(query, values)

            if cursor.rowcount > 0:
                logger.info(f"✅ Updated student ID {student_id}")
                return True
            else:
                logger.warning(f"⚠️  Student ID {student_id} not found")
                return False
    except Exception as e:
        logger.error(f"❌ Error updating student: {e}")
        return False


def delete_student(student_id: int) -> bool:
    """
    Delete a student from the database.

    Args:
        student_id: Student ID

    Returns:
        True if successful, False otherwise
    """
    query = "DELETE FROM students WHERE user_id = %s;"

    try:
        with DatabaseConnection() as cursor:
            cursor.execute(query, (student_id,))

            if cursor.rowcount > 0:
                logger.info(f"✅ Deleted student ID {student_id}")
                return True
            else:
                logger.warning(f"⚠️  Student ID {student_id} not found")
                return False
    except Exception as e:
        logger.error(f"❌ Error deleting student: {e}")
        return False


# ========================================
# Natural Language Query Interface
# ========================================


def execute_sql_query(sql_query: str) -> str:
    """
    Execute a SQL query and return formatted results.

    Args:
        sql_query: SQL query to execute

    Returns:
        Formatted string with query results
    """
    try:
        with DatabaseConnection() as cursor:
            cursor.execute(sql_query)

            # Check if it's a SELECT query
            if sql_query.strip().upper().startswith("SELECT"):
                columns = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()

                if not results:
                    return "No results found."

                # Format results as a readable string
                formatted_results = []
                for row in results:
                    row_dict = dict(zip(columns, row))
                    formatted_results.append(str(row_dict))

                return "\n".join(formatted_results)
            else:
                return f"Query executed successfully. Rows affected: {cursor.rowcount}"

    except Exception as e:
        logger.error(f"❌ SQL execution error: {e}")
        return f"Error executing query: {str(e)}"


def query_students_natural(question: str) -> str:
    """
    Answer natural language questions about students using the database.

    This is the main entry point for the Student API tool in the hybrid agent.
    It converts natural language questions to SQL queries and returns formatted answers.

    Args:
        question: Natural language question about students

    Returns:
        Formatted answer based on database query
    """
    # First, get some sample data to help the LLM understand the schema
    schema_info = """
    Database Schema:
    Table: students
    Columns:
    - user_id (INTEGER, PRIMARY KEY)
    - name (VARCHAR)
    - age (INTEGER)
    - course (VARCHAR)
    """

    # Use LLM to convert natural language to SQL
    prompt = f"""You are a SQL expert. Convert the following natural language question into a PostgreSQL query.

{schema_info}

Rules:
1. Return ONLY the SQL query, nothing else
2. Use proper PostgreSQL syntax
3. For counting, use COUNT(*)
4. For filtering by course, use ILIKE for case-insensitive matching
5. Always use safe queries (SELECT only, no DELETE/DROP/etc.)
6. If asking for "students", select: user_id, name, age, course

Question: {question}

SQL Query:"""

    try:
        # Get SQL query from LLM
        sql_query = query_ollama(prompt).strip()

        # Clean up the response (remove markdown code blocks if present)
        if sql_query.startswith("```"):
            lines = sql_query.split("\n")
            sql_query = "\n".join(
                [line for line in lines if not line.startswith("```")]
            )
            sql_query = sql_query.strip()

        # Remove "sql" or "SQL" prefix if present
        if sql_query.lower().startswith("sql"):
            sql_query = sql_query[3:].strip()

        logger.info(f"Generated SQL: {sql_query}")

        # Execute the query
        raw_results = execute_sql_query(sql_query)

        # Use LLM to format the results into a natural language answer
        answer_prompt = f"""Based on the database query results below, provide a clear, natural language answer to the question.

Question: {question}

Query Results:
{raw_results}

Provide a concise, helpful answer:"""

        answer = query_ollama(answer_prompt)
        return answer

    except Exception as e:
        logger.error(f"❌ Error in natural language query: {e}")
        return f"I encountered an error processing your question: {str(e)}"


# ========================================
# Helper Functions
# ========================================


def get_students_count() -> int:
    """Get total number of students in the database."""
    query = "SELECT COUNT(*) FROM students;"

    try:
        with DatabaseConnection() as cursor:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        logger.error(f"❌ Error counting students: {e}")
        return 0


def get_course_statistics() -> Dict[str, Any]:
    """Get statistics about course enrollment."""
    query = """
    SELECT 
        course, 
        COUNT(*) as student_count, 
        AVG(age) as avg_age
    FROM students 
    GROUP BY course 
    ORDER BY student_count DESC;
    """

    try:
        with DatabaseConnection() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            stats = [dict(zip(columns, row)) for row in results]
            return {"courses": stats}
    except Exception as e:
        logger.error(f"❌ Error fetching course statistics: {e}")
        return {"courses": []}


if __name__ == "__main__":
    # Test the Student API
    logging.basicConfig(level=logging.INFO)

    print("\n📊 Student API Test\n" + "=" * 50)

    # Test: Get all students
    print("\n1. All Students:")
    students = get_all_students(limit=5)
    for s in students:
        print(f"  - {s['name']}, {s['age']}, {s['course']}")

    # Test: Search by name
    print("\n2. Search for 'Alice':")
    results = search_students("Alice")
    for s in results:
        print(f"  - {s['name']}, {s['course']}")

    # Test: Get by course
    print("\n3. Python Course Students:")
    python_students = get_students_by_course("Python")
    for s in python_students:
        print(f"  - {s['name']}")

    # Test: Statistics
    print("\n4. Student Count:", get_students_count())

    print("\n✅ Student API tests complete!")
