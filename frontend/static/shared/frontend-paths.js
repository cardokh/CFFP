/*
 * Shared frontend navigation and path definitions.
 *
 * Responsibilities:
 * - Centralize reusable frontend URL paths.
 * - Avoid hardcoded navigation paths in controllers and components.
 * - Provide one shared frontend routing/path registry.
 *
 * Architectural rules:
 * - Frontend pages and controllers must not hardcode application paths.
 * - Shared navigation paths must be defined here.
 */

window.LLA_PATHS = {
   root: {
      index: "/index.html"
   },

   desktop: {
      root: "/desktop",

      public: {
         root: "/desktop/public",

         login: "/desktop/public/login.html",
         register: "/desktop/public/register.html",
         forgotPassword: "/desktop/public/forgot-password.html",
         tryDemo: "/desktop/public/try-demo.html"
      },

      protected: {
         root: "/desktop/protected",

         welcome: "/desktop/protected/welcome.html",
         availableLessons: "/desktop/protected/available-lessons.html",
         studentLessonDetails:
            "/desktop/protected/student-lesson-details.html",
         lessonPlayer: "/desktop/protected/lesson-player/lesson-player.html",
         progress: "/desktop/protected/progress.html",
         contact: "/desktop/protected/contact.html",
         settings: "/desktop/protected/settings.html",
         projectGuide: "/desktop/protected/project-guide/project-guide.html",
         automation: {
            tasks: "/desktop/protected/automation/tasks.html"
         },
         presentation: "/desktop/protected/presentation.html",
         about: "/desktop/protected/about.html",

         admin: {
            root: "/desktop/protected/admin",

            dashboard:
               "/desktop/protected/admin/admin.html",

            users: {
               root:
                  "/desktop/protected/admin/users",

               list:
                  "/desktop/protected/admin/users/users.html",

               edit: (userId) =>
                  `/desktop/protected/admin/users/user-edit.html?userId=${userId}`,

               create:
                  "/desktop/protected/admin/users/user-create.html"
            },

            lessonCategories: {
               root:
                  "/desktop/protected/admin/lesson-categories",

               list:
                  "/desktop/protected/admin/lesson-categories/lesson-categories.html",

               details: (categoryId) =>
                  `/desktop/protected/admin/lesson-categories/lesson-category-details.html?categoryId=${categoryId}`,

               edit: (categoryId) =>
                  `/desktop/protected/admin/lesson-categories/lesson-category-edit.html?categoryId=${categoryId}`,

               create:
                  "/desktop/protected/admin/lesson-categories/lesson-category-create.html"
            },

            learningItems: {
               root:
                  "/desktop/protected/admin/learning-items",

               list:
                  "/desktop/protected/admin/learning-items/learning-items.html",

               details: (learningItemId) =>
                  `/desktop/protected/admin/learning-items/learning-item-details.html?learningItemId=${learningItemId}`,

               edit: (learningItemId) =>
                  `/desktop/protected/admin/learning-items/learning-item-edit.html?learningItemId=${learningItemId}`,

               create:
                  "/desktop/protected/admin/learning-items/learning-item-create.html"
            },

            quizQuestions: {
               root:
                  "/desktop/protected/admin/quiz-questions",

               list:
                  "/desktop/protected/admin/quiz-questions/quiz-questions.html",

               edit: (questionId) =>
                  `/desktop/protected/admin/quiz-questions/quiz-question-edit.html?questionId=${questionId}`,

               create:
                  "/desktop/protected/admin/quiz-questions/quiz-question-create.html"
            },

            lessons: {
               root:
                  "/desktop/protected/admin/lessons",

               list:
                  "/desktop/protected/admin/lessons/lessons.html",

               edit: (lessonId) =>
                  `/desktop/protected/admin/lessons/lesson-edit.html?lessonId=${lessonId}`,

               create:
                  "/desktop/protected/admin/lessons/lesson-create.html"
            }
         }
      },

      shared: {
         root: "/desktop/shared"
      }
   },

   mobile: {
      root: "/mobile",

      public: {
         root: "/mobile/public",

         login: "/mobile/public/login.html",
         register: "/mobile/public/register.html",
         forgotPassword: "/mobile/public/forgot-password.html",
         tryDemo: "/mobile/public/try-demo.html"
      },

      protected: {
         root: "/mobile/protected",

         welcome:
            "/mobile/protected/welcome.html",

         availableLessons:
            "/mobile/protected/available-lessons.html",

         progress:
            "/mobile/protected/progress.html",

         projectGuide:
            "/mobile/protected/project-guide.html",

         contact:
            "/mobile/protected/contact.html",

         settings:
            "/mobile/protected/settings.html"
      },

      shared: {
         root: "/mobile/shared"
      }
   },

   shared: {
      root: "/shared"
   }
};