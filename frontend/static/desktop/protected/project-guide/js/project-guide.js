function initializeProjectGuideTabs() {

    const tabs = document.querySelectorAll(".project-guide-tab[data-guide-section]");
    const sections = document.querySelectorAll(".project-guide-section");

    if (!tabs.length || !sections.length) {
        return;
    }

    tabs.forEach((tab) => {

        tab.addEventListener("click", () => {

            const targetSection = tab.dataset.guideSection;

            tabs.forEach((currentTab) => {
                currentTab.classList.remove("is-active");
            });

            sections.forEach((section) => {
                section.classList.remove("is-active");
            });

            tab.classList.add("is-active");

            const matchingSection = document.querySelector(
                `[data-guide-panel="${targetSection}"]`
            );

            if (matchingSection) {
                matchingSection.classList.add("is-active");
            }

        });

    });

}

function initializeEvaluationTabs() {

    const tabs = document.querySelectorAll(".project-guide-tab[data-evaluation-section]");
    const panels = document.querySelectorAll(".project-guide-evaluation-panel");

    if (!tabs.length || !panels.length) {
        return;
    }

    tabs.forEach((tab) => {

        tab.addEventListener("click", () => {

            const targetPanel = tab.dataset.evaluationSection;

            tabs.forEach((currentTab) => {
                currentTab.classList.remove("is-active");
            });

            panels.forEach((panel) => {
                panel.classList.remove("is-active");
            });

            tab.classList.add("is-active");

            const matchingPanel = document.querySelector(
                `[data-evaluation-panel="${targetPanel}"]`
            );

            if (matchingPanel) {
                matchingPanel.classList.add("is-active");
            }

        });

    });

}

function getEvaluationFiles() {

    return [
        "./data/evaluations/evaluation-student-01.json",
        "./data/evaluations/evaluation-student-02.json",
        "./data/evaluations/evaluation-student-03.json",
        "./data/evaluations/evaluation-demo-user.json",
        "./data/evaluations/evaluation-admin-user.json"
    ];

}

function formatParticipantName(participantId) {

    if (!participantId) {
        return "Unknown Participant";
    }

    return participantId
        .split("-")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ");

}

function formatStatus(status) {

    if (!status) {
        return "Unknown";
    }

    return status;

}

function formatRating(rating) {

    if (!rating || rating <= 0) {
        return "N/A";
    }

    return `${rating}/5`;

}

function getTasks(evaluation) {

    if (!evaluation || !Array.isArray(evaluation.tasks)) {
        return [];
    }

    return evaluation.tasks;

}

function getPostTestQuestions(evaluation) {

    if (!evaluation || !Array.isArray(evaluation.postTestQuestions)) {
        return [];
    }

    return evaluation.postTestQuestions;

}

function getOpenEndedQuestions(evaluation) {

    if (!evaluation || !Array.isArray(evaluation.openEndedQuestions)) {
        return [];
    }

    return evaluation.openEndedQuestions;

}

function getCompletedTaskCount(evaluation) {

    return getTasks(evaluation).filter((task) => task.completed).length;

}

function getTotalTaskCount(evaluation) {

    return getTasks(evaluation).length;

}

function getAnsweredRatingQuestions(evaluation) {

    return getPostTestQuestions(evaluation).filter((question) => {
        return question.rating && question.rating > 0;
    });

}

function getAverageRating(evaluation) {

    const answeredQuestions = getAnsweredRatingQuestions(evaluation);

    if (!answeredQuestions.length) {
        return 0;
    }

    const total = answeredQuestions.reduce((sum, question) => {
        return sum + question.rating;
    }, 0);

    return total / answeredQuestions.length;

}

function getCompletedEvaluationCount(evaluations) {

    return evaluations.filter((evaluation) => {
        return evaluation.status && evaluation.status.toLowerCase() === "complete";
    }).length;

}

function getOverallAverageRating(evaluations) {

    const ratings = evaluations
        .map((evaluation) => getAverageRating(evaluation))
        .filter((rating) => rating > 0);

    if (!ratings.length) {
        return 0;
    }

    const total = ratings.reduce((sum, rating) => {
        return sum + rating;
    }, 0);

    return total / ratings.length;

}

function createElement(tagName, className, textContent) {

    const element = document.createElement(tagName);

    if (className) {
        element.className = className;
    }

    if (textContent !== undefined && textContent !== null) {
        element.textContent = textContent;
    }

    return element;

}

function clearElement(element) {

    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }

}

function createSummaryMetric(label, value) {

    const card = createElement("div", "evaluation-summary-metric");

    card.appendChild(createElement("span", "evaluation-summary-value", value));
    card.appendChild(createElement("span", "evaluation-summary-label", label));

    return card;

}

function renderSummaryPanel(evaluations) {

    const panel = document.querySelector("[data-evaluation-summary-panel]");

    if (!panel) {
        return;
    }

    clearElement(panel);

    const legend = createElement("legend", null, "Summary Analysis");
    panel.appendChild(legend);

    const completedEvaluations = getCompletedEvaluationCount(evaluations);
    const overallAverage = getOverallAverageRating(evaluations);

    const totalTasks = evaluations.reduce((sum, evaluation) => {
        return sum + getTotalTaskCount(evaluation);
    }, 0);

    const completedTasks = evaluations.reduce((sum, evaluation) => {
        return sum + getCompletedTaskCount(evaluation);
    }, 0);

    const totalRatingQuestions = evaluations.reduce((sum, evaluation) => {
        return sum + getPostTestQuestions(evaluation).length;
    }, 0);

    const answeredRatingQuestions = evaluations.reduce((sum, evaluation) => {
        return sum + getAnsweredRatingQuestions(evaluation).length;
    }, 0);

    const grid = createElement("div", "evaluation-summary-grid");

    grid.appendChild(createSummaryMetric("Evaluations", `${completedEvaluations}/${evaluations.length}`));
    grid.appendChild(createSummaryMetric("Tasks", `${completedTasks}/${totalTasks}`));
    grid.appendChild(createSummaryMetric("Rating Responses", `${answeredRatingQuestions}/${totalRatingQuestions}`));
    grid.appendChild(createSummaryMetric("Avg Rating", overallAverage > 0 ? `${overallAverage.toFixed(1)}/5` : "N/A"));

    panel.appendChild(grid);

}

function createParticipantCell(textContent) {

    return createElement("td", null, textContent);

}

function renderParticipantList(evaluations, selectedParticipantId) {

    const tableBody = document.querySelector("[data-evaluation-participant-table-body]");

    if (!tableBody) {
        return;
    }

    clearElement(tableBody);

    evaluations.forEach((evaluation) => {

        const row = document.createElement("tr");
        row.className = "evaluation-participant-row";
        row.tabIndex = 0;
        row.dataset.participantId = evaluation.participantId;

        if (evaluation.participantId === selectedParticipantId) {
            row.classList.add("is-active");
        }

        const completedTasks = getCompletedTaskCount(evaluation);
        const totalTasks = getTotalTaskCount(evaluation);
        const averageRating = getAverageRating(evaluation);

        row.appendChild(createParticipantCell(formatParticipantName(evaluation.participantId)));
        row.appendChild(createParticipantCell(evaluation.participantType || "Unknown"));
        row.appendChild(createParticipantCell(formatStatus(evaluation.status)));
        row.appendChild(createParticipantCell(`${completedTasks}/${totalTasks}`));
        row.appendChild(createParticipantCell(averageRating > 0 ? `${averageRating.toFixed(1)}/5` : "N/A"));

        row.addEventListener("click", () => {
            renderEvaluationDetails(evaluation);
            renderParticipantList(evaluations, evaluation.participantId);
        });

        row.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                renderEvaluationDetails(evaluation);
                renderParticipantList(evaluations, evaluation.participantId);
            }
        });

        tableBody.appendChild(row);

    });

}

function createDetailSection(titleText) {

    const section = createElement("section", "evaluation-detail-section");

    const title = createElement("h4", null, titleText);
    section.appendChild(title);

    return section;

}

function renderTaskDetails(parent, evaluation) {

    const section = createDetailSection("Tasks");

    const tasks = getTasks(evaluation);

    if (!tasks.length) {
        section.appendChild(createElement("p", null, "No task data available."));
        parent.appendChild(section);
        return;
    }

    tasks.forEach((task) => {

        const text = task.task || "Unnamed task";
        const status = task.completed ? "Completed" : "Not Completed";

        const row = createElement("div", "evaluation-task-row");

        row.appendChild(createElement("span", "evaluation-heading-label", text));
        row.appendChild(createElement("span", "evaluation-heading-value", status));

        section.appendChild(row);

    });

    parent.appendChild(section);

}

function renderRatingDetails(parent, evaluation) {

    const section = createDetailSection("Post-Test Questions");

    const questions = getPostTestQuestions(evaluation);

    if (!questions.length) {
        section.appendChild(createElement("p", null, "No post-test question data available."));
        parent.appendChild(section);
        return;
    }

    questions.forEach((question) => {

        const questionText = question.question || "Unnamed question";
        const rating = formatRating(question.rating);

        const row = createElement("div", "evaluation-task-row");

        row.appendChild(
            createElement("span", "evaluation-heading-label", questionText)
        );

        row.appendChild(
            createElement("span", "evaluation-heading-value", rating)
        );

        section.appendChild(row);

    });
    parent.appendChild(section);

}

function renderOpenAnswerDetails(parent, evaluation) {

    const section = createDetailSection("Open-Ended Questions");

    const questions = getOpenEndedQuestions(evaluation);

    if (!questions.length) {
        section.appendChild(createElement("p", null, "No open-ended question data available."));
        parent.appendChild(section);
        return;
    }

    questions.forEach((question) => {

        const item = createElement("div", "evaluation-open-answer");

        const questionText = question.question || "Unnamed question";
        const answer = question.answer || "Pending evaluation";


        item.appendChild(
            createElement(
                "p",
                "evaluation-heading-label evaluation-open-question",
                questionText
            )
        );

        item.appendChild(
            createElement(
                "p",
                "evaluation-heading-value evaluation-open-response",
                answer
            )
        );

        section.appendChild(item);

    });

    parent.appendChild(section);

}

function renderEvaluationDetails(evaluation) {

    const panel = document.querySelector("[data-evaluation-details-panel]");

    if (!panel) {
        return;
    }

    clearElement(panel);

    panel.appendChild(createElement("legend", null, "Evaluation Details"));

    const participantHeading = createElement("h3", "evaluation-participant-heading");

    participantHeading.appendChild(createElement("span", "evaluation-heading-label", "Participant: "));
    participantHeading.appendChild(createElement("span", "evaluation-heading-value", formatParticipantName(evaluation.participantId)));

    panel.appendChild(participantHeading);

    renderTaskDetails(panel, evaluation);
    renderRatingDetails(panel, evaluation);
    renderOpenAnswerDetails(panel, evaluation);

}

function renderEvaluationLoadError() {

    const summaryPanel = document.querySelector("[data-evaluation-summary-panel]");
    const participantList = document.querySelector("[data-evaluation-participant-table-body]");
    const detailsPanel = document.querySelector("[data-evaluation-details-panel]");

    if (summaryPanel) {
        clearElement(summaryPanel);
        summaryPanel.appendChild(createElement("legend", null, "Summary Analysis"));
        summaryPanel.appendChild(createElement("p", null, "Evaluation data could not be loaded."));
    }

    if (participantList) {
        clearElement(participantList);
    }

    if (detailsPanel) {
        clearElement(detailsPanel);
        detailsPanel.appendChild(createElement("legend", null, "Selected Participant Details"));
        detailsPanel.appendChild(createElement("p", null, "Please check that the JSON files exist in /desktop/protected/data/evaluations/."));
    }

}

function renderEvaluationResults(evaluations) {

    if (!evaluations.length) {
        renderEvaluationLoadError();
        return;
    }

    const selectedEvaluation = evaluations[0];

    renderSummaryPanel(evaluations);
    renderParticipantList(evaluations, selectedEvaluation.participantId);
    renderEvaluationDetails(selectedEvaluation);

}

async function loadEvaluationResults() {

    const files = getEvaluationFiles();

    try {

        const evaluations = await Promise.all(
            files.map(async (file) => {

                const response = await fetch(file);

                if (!response.ok) {
                    throw new Error(`Could not load ${file}`);
                }

                return response.json();

            })
        );

        renderEvaluationResults(evaluations);

    } catch (error) {

        console.error(error);
        renderEvaluationLoadError();

    }

}

document.addEventListener("DOMContentLoaded", () => {
    initializeProjectGuideTabs();
    initializeEvaluationTabs();
    loadEvaluationResults();
});