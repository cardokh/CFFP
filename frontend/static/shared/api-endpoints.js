/*
 * Shared frontend API endpoint definitions.
 *
 * Responsibilities:
 * - Centralize frontend API endpoint strings.
 * - Keep page controllers free from hardcoded backend paths.
 * - Preserve the endpoint object shapes expected by existing desktop/mobile pages.
 * - Provide small endpoint builders for identifier-based resources.
 */

const CCORE_API_ENDPOINTS = {
    auth: {
        login: "/api/auth/login",
        register: "/api/auth/register",
        forgotPassword: "/api/auth/forgot-password"
    },

    ai: {
        speechGenerate: "/api/ai/speech/generate"
    },

    admin: {
        users: {
            list: "/api/admin/users",
            create: "/api/admin/users",

            byId(userId) {
                return `/api/admin/users/${encodeURIComponent(userId)}`;
            }
        },

        lessonCategories: {
            list: "/api/admin/lesson-categories",
            create: "/api/admin/lesson-categories",

            byId(categoryId) {
                return `/api/admin/lesson-categories/${encodeURIComponent(categoryId)}`;
            }
        },

        learningItems: {
            list: "/api/admin/learning-items",
            create: "/api/admin/learning-items",

            byId(learningItemId) {
                return `/api/admin/learning-items/${encodeURIComponent(learningItemId)}`;
            },

            examples(learningItemId) {
                return `/api/admin/learning-items/examples/${encodeURIComponent(learningItemId)}`;
            }
        },

        quizQuestions: {
            list: "/api/admin/quiz-questions",
            create: "/api/admin/quiz-questions",

            byId(quizQuestionId) {
                return `/api/admin/quiz-questions/${encodeURIComponent(quizQuestionId)}`;
            }
        },

        quizQuestionOptions: {
            list: "/api/admin/quiz-question-options",
            create: "/api/admin/quiz-question-options",

            byId(optionId) {
                return `/api/admin/quiz-question-options/${encodeURIComponent(optionId)}`;
            },

            byQuestionId(questionId) {
                return `/api/admin/quiz-questions-options/${encodeURIComponent(questionId)}`;
            }
        },

        lessons: {
            list: "/api/admin/lessons",
            create: "/api/admin/lessons",

            byId(lessonId) {
                return `/api/admin/lessons/${encodeURIComponent(lessonId)}`;
            },

            learningItems(lessonId) {
                return `/api/admin/lessons-learning-items/${encodeURIComponent(lessonId)}`;
            },

            quizQuestions(lessonId) {
                return `/api/admin/lessons-quiz-questions/${encodeURIComponent(lessonId)}`;
            }
        },

        referenceData: {
            lessonFormOptions: "/api/admin/reference-data/lesson-form-options"
        },

        userLessons: {
            list: "/api/admin/user-lessons",
            create: "/api/admin/user-lessons",

            byId(userLessonId) {
                return `/api/admin/user-lessons/${encodeURIComponent(userLessonId)}`;
            },

            byUserId(userId) {
                return `/api/admin/user-lessons/${encodeURIComponent(userId)}`;
            },

            markInProgress(userLessonId) {
                return `/api/admin/user-lessons/in-progress/${encodeURIComponent(userLessonId)}`;
            },

            markCompleted(userLessonId) {
                return `/api/admin/user-lessons/completed/${encodeURIComponent(userLessonId)}`;
            }
        },

        // Backward-compatible aliases used by older page controllers.
        userById(userId) {
            return this.users.byId(userId);
        }
    },

    student: {
        lessons: {
            byUserId(userId) {
                return `/api/student/lessons/${encodeURIComponent(userId)}`;
            },

            signup(lessonId) {
                return `/api/student/lessons/signup/${encodeURIComponent(lessonId)}`;
            },

            remove(lessonId) {
                return `/api/student/lessons/remove/${encodeURIComponent(lessonId)}`;
            }
        },

        progress: {
            byUserId(userId) {
                return `/api/student/progress/${encodeURIComponent(userId)}`;
            }
        }
    },

    lesson: {
        interaction: "/api/lesson"
    },

    tts: {
        base: "/api/tts",

        byText(text) {
            return `/api/tts/${encodeURIComponent(text)}`;
        }
    },

    tasks: {
        list: "/api/ccore/tasks",
        create: "/api/ccore/tasks",
        statuses: "/api/ccore/task-statuses",
        executionProviders: "/api/ccore/execution-providers",
        executionImplementerTypes: "/api/ccore/execution-implementer-types",
        executionTargets: "/api/ccore/execution-targets",
        executionConfigurations: "/api/ccore/execution-configurations",

        byId(taskId) {
            return `/api/ccore/tasks/${encodeURIComponent(taskId)}`;
        },

        execute(taskId) {
            return `/api/ccore/tasks/${encodeURIComponent(taskId)}/execute`;
        },

        executions(taskId) {
            return `/api/ccore/tasks/${encodeURIComponent(taskId)}/executions`;
        }
    },

    metrics: {
        list: "/api/ccore/metrics",
        create: "/api/ccore/metrics",
        types: "/api/ccore/metric-types",

        byId(metricId) {
            return `/api/ccore/metrics/${encodeURIComponent(metricId)}`;
        }
    },

    automation: {
        tasks: {
            list: "/api/automation/tasks",

            byId(taskId) {
                return `/api/automation/tasks/${encodeURIComponent(taskId)}`;
            },

            configuration(taskId) {
                return `/api/automation/tasks/${encodeURIComponent(taskId)}/configuration`;
            },

            validate(taskId) {
                return `/api/automation/tasks/${encodeURIComponent(taskId)}/validate`;
            },

            execute(taskId) {
                return `/api/automation/tasks/${encodeURIComponent(taskId)}/execute`;
            },

            executions(taskId) {
                return `/api/automation/tasks/${encodeURIComponent(taskId)}/executions`;
            },

            executionReport(taskId, executionId) {
                return `/api/automation/tasks/${encodeURIComponent(taskId)}/executions/${encodeURIComponent(executionId)}`;
            }
        },

        pipelines: {
            list: "/api/automation/pipelines",

            byId(pipelineId) {
                return `/api/automation/pipelines/${encodeURIComponent(pipelineId)}`;
            }
        }
    }
};

const LLA_API_ENDPOINTS = CCORE_API_ENDPOINTS;
