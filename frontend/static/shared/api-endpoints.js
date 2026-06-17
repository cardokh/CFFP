/*
 * Shared API endpoint definitions.
 *
 * Responsibilities:
 * - Centralize backend API endpoint paths.
 * - Avoid hardcoded API route strings in page controllers.
 * - Provide reusable endpoint builders for entity-specific routes.
 * - Keep frontend API usage aligned with backend routing.
 */

const LLA_API_ENDPOINTS = {
    auth: {
        login: "/api/auth/login",
        register: "/api/auth/register",
        forgotPassword: "/api/auth/forgot-password"
    },

    student: {
        lessons: {
            byUserId(userId) {
                return `/api/student/lessons/${userId}`;
            }
        },

        progress: {
            byUserId(userId) {
                return `/api/student/progress/${userId}`;
            }
        }
    },

    admin: {
        referenceData: {
            lessonFormOptions: "/api/admin/reference-data/lesson-form-options"
        },

        users: {
            list: "/api/admin/users",
            create: "/api/admin/users",

            byId(userId) {
                return `/api/admin/users/${userId}`;
            }
        },

        lessonCategories: {
            list: "/api/admin/lesson-categories",
            create: "/api/admin/lesson-categories",

            byId(categoryId) {
                return `/api/admin/lesson-categories/${categoryId}`;
            }
        },

        learningItems: {
            list: "/api/admin/learning-items",
            create: "/api/admin/learning-items",

            byId(learningItemId) {
                return `/api/admin/learning-items/${learningItemId}`;
            },

            examples(learningItemId) {
                return `/api/admin/learning-items/examples/${learningItemId}`;
            }
        },

        quizQuestions: {
            list: "/api/admin/quiz-questions",
            create: "/api/admin/quiz-questions",

            byId(questionId) {
                return `/api/admin/quiz-questions/${questionId}`;
            }
        },

        quizQuestionOptions: {
            byQuestionId(questionId) {
                return `/api/admin/quiz-questions-options/${questionId}`;
            },

            byId(optionId) {
                return `/api/admin/quiz-question-options/${optionId}`;
            }
        },

        lessons: {
            list: "/api/admin/lessons",
            create: "/api/admin/lessons",

            byId(lessonId) {
                return `/api/admin/lessons/${lessonId}`;
            },

            learningItems(lessonId) {
                return `/api/admin/lessons-learning-items/${lessonId}`;
            },

            quizQuestions(lessonId) {
                return `/api/admin/lessons-quiz-questions/${lessonId}`;
            }
        },

        userLessons: {
            byUserId(userId) {
                return `/api/admin/user-lessons/${userId}`;
            },

            markInProgress(userId) {
                return `/api/admin/user-lessons/in-progress/${userId}`;
            },

            markCompleted(userId) {
                return `/api/admin/user-lessons/completed/${userId}`;
            }
        }
    }
};


const CCORE_API_ENDPOINTS = {
    automation: {
        tasks: {
            list: "/api/automation/tasks"
        }
    }
};
