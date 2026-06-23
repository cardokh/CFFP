/*
 * Shared frontend API endpoint definitions.
 *
 * Responsibilities:
 * - Centralize frontend API endpoint strings.
 * - Keep page controllers free from hardcoded backend paths.
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
        users: "/api/admin/users",

        userById(userId) {
            return `/api/admin/users/${encodeURIComponent(userId)}`;
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
