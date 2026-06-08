"""
User lesson assignment messages.

Responsibilities:
- Centralize reusable user lesson assignment success/error messages.
- Avoid hardcoded messages across routes and services.
- Keep LLA assignment messaging consistent.

Architecture:
routes/services -> user_lesson_assignment_messages
"""

USER_LESSON_ASSIGNMENTS_FETCHED_SUCCESSFULLY = (
    "User lesson assignments fetched successfully."
)

USER_LESSON_ASSIGNMENTS_UPDATED_SUCCESSFULLY = (
    "User lesson assignments updated successfully."
)

STUDENT_LESSONS_FETCHED_SUCCESSFULLY = "Student lessons fetched successfully."

STUDENT_LESSON_SIGNUP_SUCCESSFUL = "Student lesson signup completed successfully."

STUDENT_LESSON_REMOVED_SUCCESSFULLY = "Student lesson removed successfully."

USER_ID_IS_REQUIRED = "User ID is required."

INVALID_USER_ID = "Invalid user ID."

INVALID_REQUEST_BODY = "Invalid request body."

LESSONS_FIELD_IS_REQUIRED = "Lessons field is required."

LESSONS_MUST_BE_A_LIST = "Lessons must be a list."

LESSON_ID_REQUIRED = "lesson_id is required."

LESSON_ID_MUST_BE_INTEGER = "lesson_id must be an integer."

USER_LESSON_ASSIGNMENT_UPDATE_FAILED = "Failed to update user lesson assignments."

USER_LESSON_ASSIGNMENT_FETCH_FAILED = "Failed to fetch user lesson assignments."

STUDENT_LESSON_SIGNUP_FAILED = "Failed to sign student up for lesson."

STUDENT_LESSON_REMOVE_FAILED = "Failed to remove student lesson."
