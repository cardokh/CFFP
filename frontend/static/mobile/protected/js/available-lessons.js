const MOBILE_LESSONS_CONTAINER_ID =
    "mobileLessonsContainer";

let currentLessons =
    [];


function getAuthenticatedUserId() {

    const authenticatedUser =
        requireAuthentication();

    if (
        !authenticatedUser ||
        !authenticatedUser.userId
    ) {
        throw new Error(
            "Authenticated user ID is missing."
        );
    }

    return authenticatedUser.userId;
}


function navigateToStudentLessonDetails(
    lessonId
) {
    window.location.href =
        `/mobile/protected/student-lesson-details.html?lessonId=${lessonId}`;
}


function renderEmptyLessons() {

    const container =
        document.getElementById(
            MOBILE_LESSONS_CONTAINER_ID
        );

    container.innerHTML = `
        <div class="empty-card">
            No lessons available.
        </div>
    `;
}


function renderLessonRow(
    lesson
) {

    return `
        <tr
            class="lesson-row"
            data-lesson-id="${lesson.lessonId}"
        >

            <td class="lesson-title-cell">
                ${escapeHtml(
        lesson.lessonTitle || "-"
    )}
            </td>

            <td>
                ${escapeHtml(
        lesson.categoryName || "-"
    )}
            </td>

            <td class="lesson-status-cell">
                ${escapeHtml(
        lesson.lessonStatusName || "-"
    )}
            </td>

        </tr>
    `;
}


function renderLessons(
    lessons
) {

    const container =
        document.getElementById(
            MOBILE_LESSONS_CONTAINER_ID
        );

    currentLessons =
        lessons || [];

    if (
        !currentLessons ||
        currentLessons.length === 0
    ) {
        renderEmptyLessons();
        return;
    }

    container.innerHTML = `
        <table class="mobile-lessons-table">

            <thead>
                <tr>
                    <th>Lesson</th>
                    <th>Category</th>
                    <th>Status</th>
                </tr>
            </thead>

            <tbody>
                ${currentLessons
            .map((lesson) =>
                renderLessonRow(
                    lesson
                )
            )
            .join("")}
            </tbody>

        </table>
    `;
}


async function handleLessonsClick(
    event
) {

    const lessonRow =
        event.target.closest(
            "[data-lesson-id]"
        );

    if (!lessonRow) {
        return;
    }

    const lessonId =
        Number(
            lessonRow.dataset.lessonId
        );

    navigateToStudentLessonDetails(
        lessonId
    );
}


async function loadLessonLibrary() {

    const container =
        document.getElementById(
            MOBILE_LESSONS_CONTAINER_ID
        );

    try {

        const userId =
            getAuthenticatedUserId();

        const data =
            await getJson(
                `/api/student/lessons/${userId}`
            );

        if (!data.success) {

            throw new Error(
                data.error ||
                "Failed to load lessons."
            );
        }

        renderLessons(
            data.userLessons || []
        );

    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <div class="error-card">
                ${escapeHtml(
            error.message ||
            "Failed to load lessons."
        )}
            </div>
        `;
    }
}


document
    .getElementById(
        MOBILE_LESSONS_CONTAINER_ID
    )
    .addEventListener(
        "click",
        handleLessonsClick
    );


loadLessonLibrary();