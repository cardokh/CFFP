const STUDENT_LESSON_DETAILS_MESSAGE_ID =
    "studentLessonDetailsMessage";

const START_LESSON_BUTTON_ID =
    "startLessonButton";

const SIGN_UP_LESSON_BUTTON_ID =
    "signUpLessonButton";

const WITHDRAW_LESSON_BUTTON_ID =
    "withdrawLessonButton";

const BACKEND_API_BASE_URL =
    "http://localhost:8000";


function getLessonIdFromUrl() {
    const params =
        new URLSearchParams(window.location.search);

    return Number(params.get("lessonId"));
}


function getAuthenticatedUserId() {
    const authenticatedUser =
        requireAuthentication();

    if (!authenticatedUser || !authenticatedUser.userId) {
        throw new Error(
            "Authenticated user ID is missing."
        );
    }

    return authenticatedUser.userId;
}


function navigateBackToLessons() {
    window.location.href =
        LLA_PATHS.mobile.protected.availableLessons;
}


function startLesson(lessonId) {
    window.location.href =
        `/mobile/protected/start-lesson.html?lessonId=${lessonId}`;
}


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function findLookupName(items, id) {
    const safeItems =
        items || [];

    const matchingItem =
        safeItems.find((item) =>
            Number(item.id) === Number(id)
        );

    if (!matchingItem) {
        return "";
    }

    return matchingItem.name;
}


function findAssignedLesson(userLessons, lessonId) {
    return (userLessons || []).find((lesson) =>
        Number(lesson.lessonId) === Number(lessonId) &&
        lesson.isActive === true
    );
}


function buildLessonReferenceLabels(lesson, formOptions) {
    return {
        categoryName: findLookupName(
            formOptions.lesson_categories,
            lesson.categoryId
        )
    };
}


function setButtonEnabled(buttonId, enabled) {
    document
        .getElementById(buttonId)
        .disabled = !enabled;
}


function getLessonActionLabel(assignedLesson) {
    if (!assignedLesson) {
        return "Start lesson";
    }

    const lessonStatus =
        assignedLesson.lessonStatusName || "";

    if (
        lessonStatus === "In Progress" ||
        lessonStatus === "Completed"
    ) {
        return "Review lesson";
    }

    return "Start lesson";
}


function setToolbarState(assignedLesson) {
    const isAssigned =
        Boolean(assignedLesson);

    const startLessonButton =
        document.getElementById(
            START_LESSON_BUTTON_ID
        );

    setButtonEnabled(
        SIGN_UP_LESSON_BUTTON_ID,
        !isAssigned
    );

    setButtonEnabled(
        WITHDRAW_LESSON_BUTTON_ID,
        isAssigned
    );

    setButtonEnabled(
        START_LESSON_BUTTON_ID,
        isAssigned
    );

    startLessonButton.textContent =
        getLessonActionLabel(
            assignedLesson
        );
}


function renderLessonDetails(
    lesson,
    lessonLabels,
    assignedLesson
) {
    const detailsCard =
        document.getElementById(
            "studentLessonDetailsCard"
        );

    detailsCard.innerHTML = `
        <div class="student-lesson-details-list">

            <div class="student-lesson-detail-row">
                <span class="student-lesson-detail-label">
                    Title:
                </span>

                <span class="student-lesson-detail-value">
                    ${escapeHtml(
        lesson.title || ""
    )}
                </span>
            </div>

            <div class="student-lesson-detail-row">
                <span class="student-lesson-detail-label">
                    Category:
                </span>

                <span class="student-lesson-detail-value">
                    ${escapeHtml(
        lessonLabels.categoryName || ""
    )}
                </span>
            </div>

            <div class="student-lesson-detail-row">
                <span class="student-lesson-detail-label">
                    Status:
                </span>

                <span class="student-lesson-detail-value">
                    ${escapeHtml(
        assignedLesson
            ? assignedLesson.lessonStatusName || "Signed up"
            : "Not signed up"
    )}
                </span>
            </div>

            <div class="student-lesson-detail-row">
                <span class="student-lesson-detail-label">
                    Description:
                </span>

                <span class="student-lesson-detail-value">
                    ${escapeHtml(
        lesson.description || ""
    )}
                </span>
            </div>

        </div>
    `;
}


function showPageError(error) {
    const messageElement =
        document.getElementById(
            STUDENT_LESSON_DETAILS_MESSAGE_ID
        );

    messageElement.textContent =
        error.message ||
        "Failed to load lesson details.";

    messageElement.classList.remove(
        "hidden"
    );
}


async function signupForLesson(lessonId) {
    const userId =
        getAuthenticatedUserId();

    const data =
        await postJson(
            `/api/student/lessons/signup/${userId}`,
            {
                lesson_id: lessonId
            }
        );

    if (!data.success) {
        throw new Error(
            data.error || "Failed to sign up for lesson."
        );
    }
}


async function withdrawFromLesson(lessonId) {
    const userId =
        getAuthenticatedUserId();

    const response =
        await fetch(
            `${BACKEND_API_BASE_URL}/api/student/lessons/remove/${userId}`,
            {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    lesson_id: lessonId
                })
            }
        );

    const data =
        await response.json();

    if (!data.success) {
        throw new Error(
            data.error || "Failed to withdraw from lesson."
        );
    }
}


async function loadStudentLessonDetails() {
    try {
        setToolbarState(null);

        const lessonId =
            getLessonIdFromUrl();

        if (!lessonId) {
            throw new Error(
                "Lesson ID is missing."
            );
        }

        const userId =
            getAuthenticatedUserId();

        const [
            lessonDetailsResponse,
            referenceDataResponse,
            userLessonsResponse
        ] = await Promise.all([
            getJson(
                LLA_API_ENDPOINTS.admin.lessons.byId(
                    lessonId
                )
            ),

            getJson(
                LLA_API_ENDPOINTS.admin
                    .referenceData
                    .lessonFormOptions
            ),

            getJson(
                `/api/student/lessons/${userId}`
            )
        ]);

        if (
            !lessonDetailsResponse.success ||
            !lessonDetailsResponse.lesson
        ) {
            throw new Error(
                lessonDetailsResponse.error ||
                "Failed to load lesson details."
            );
        }

        if (!referenceDataResponse.success) {
            throw new Error(
                "Failed to load lesson reference data."
            );
        }

        const assignedLesson =
            userLessonsResponse.success
                ? findAssignedLesson(
                    userLessonsResponse.userLessons,
                    lessonId
                )
                : null;

        const lessonLabels =
            buildLessonReferenceLabels(
                lessonDetailsResponse.lesson,
                referenceDataResponse.form_options
            );

        renderLessonDetails(
            lessonDetailsResponse.lesson,
            lessonLabels,
            assignedLesson
        );

        setToolbarState(
            assignedLesson
        );

    } catch (error) {
        console.error(error);

        setToolbarState(null);

        showPageError(error);
    }
}


document
    .getElementById(
        "backToMyLessonsButton"
    )
    .addEventListener(
        "click",
        navigateBackToLessons
    );


document
    .getElementById(
        SIGN_UP_LESSON_BUTTON_ID
    )
    .addEventListener(
        "click",
        async () => {
            try {
                const lessonId =
                    getLessonIdFromUrl();

                await signupForLesson(
                    lessonId
                );

                await loadStudentLessonDetails();

            } catch (error) {
                console.error(error);

                showPageError(error);
            }
        }
    );


document
    .getElementById(
        WITHDRAW_LESSON_BUTTON_ID
    )
    .addEventListener(
        "click",
        async () => {
            try {
                const lessonId =
                    getLessonIdFromUrl();

                await withdrawFromLesson(
                    lessonId
                );

                await loadStudentLessonDetails();

            } catch (error) {
                console.error(error);

                showPageError(error);
            }
        }
    );


document
    .getElementById(
        START_LESSON_BUTTON_ID
    )
    .addEventListener(
        "click",
        () => {
            const lessonId =
                getLessonIdFromUrl();

            startLesson(lessonId);
        }
    );


loadStudentLessonDetails();