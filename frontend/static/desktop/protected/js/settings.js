const SETTINGS_MESSAGE_ID =
    "settingsMessage";

const SETTINGS_STORAGE_KEY =
    "studentLearningSettings";

const LEGACY_SETTINGS_STORAGE_KEY =
    "studentLearningPreferences";

const ROWS_PER_PAGE_STORAGE_KEY =
    "adminTableRowsPerPage";

const DEFAULT_SETTINGS = {
    learningLanguage: "spanish",
    nativeLanguage: "english",
    speechSpeed: "normal",
    rowsPerPage: "10",
    interactionStyle: "encouraging",
    embodimentType: "robot",
    pronunciationHints: "enabled",
    autoPlayPronunciation: "enabled",
    themePreview: "hejSanDark",
    preferredDevice: "desktop"
};

let originalSettings =
    { ...DEFAULT_SETTINGS };

function getElement(id) {
    return document.getElementById(id);
}

function getSavedSettings() {
    const savedSettingsText =
        localStorage.getItem(SETTINGS_STORAGE_KEY) ||
        localStorage.getItem(LEGACY_SETTINGS_STORAGE_KEY);

    if (!savedSettingsText) {
        return { ...DEFAULT_SETTINGS };
    }

    try {
        return {
            ...DEFAULT_SETTINGS,
            ...JSON.parse(savedSettingsText)
        };
    } catch (error) {
        return { ...DEFAULT_SETTINGS };
    }
}

function getCurrentSettingsFromForm() {
    return {
        learningLanguage: getElement("learningLanguageSelect").value,
        nativeLanguage: getElement("nativeLanguageSelect").value,
        speechSpeed: getElement("speechSpeedSelect").value,
        rowsPerPage: getElement("rowsPerPageSelect").value,
        interactionStyle: getElement("interactionStyleSelect").value,
        embodimentType: getElement("embodimentTypeSelect").value,
        pronunciationHints: getElement("pronunciationHintsSelect").value,
        autoPlayPronunciation: getElement("autoPlayPronunciationSelect").value,
        themePreview: getElement("themePreviewSelect").value,
        preferredDevice: getElement("preferredDeviceSelect").value
    };
}

function applySettingsToForm(settings) {
    getElement("learningLanguageSelect").value =
        settings.learningLanguage;

    getElement("nativeLanguageSelect").value =
        settings.nativeLanguage;

    getElement("speechSpeedSelect").value =
        settings.speechSpeed;

    getElement("rowsPerPageSelect").value =
        settings.rowsPerPage;

    getElement("interactionStyleSelect").value =
        settings.interactionStyle;

    getElement("embodimentTypeSelect").value =
        settings.embodimentType;

    getElement("pronunciationHintsSelect").value =
        settings.pronunciationHints;

    getElement("autoPlayPronunciationSelect").value =
        settings.autoPlayPronunciation;

    getElement("themePreviewSelect").value =
        settings.themePreview;

    getElement("preferredDeviceSelect").value =
        settings.preferredDevice;
}

function areSettingsEqual(firstSettings, secondSettings) {
    return JSON.stringify(firstSettings) ===
        JSON.stringify(secondSettings);
}

function saveSettings() {
    const selectedSettings =
        getCurrentSettingsFromForm();

    if (areSettingsEqual(selectedSettings, originalSettings)) {
        showInfoMessage(
            SETTINGS_MESSAGE_ID,
            "No changes detected."
        );

        return;
    }

    localStorage.setItem(
        SETTINGS_STORAGE_KEY,
        JSON.stringify(selectedSettings)
    );

    localStorage.setItem(
        LEGACY_SETTINGS_STORAGE_KEY,
        JSON.stringify(selectedSettings)
    );

    localStorage.setItem(
        ROWS_PER_PAGE_STORAGE_KEY,
        selectedSettings.rowsPerPage
    );

    originalSettings =
        { ...selectedSettings };

    showSuccessMessage(
        SETTINGS_MESSAGE_ID,
        "Settings saved successfully."
    );
}

function resetSettings() {
    const selectedSettings =
        getCurrentSettingsFromForm();

    if (areSettingsEqual(selectedSettings, DEFAULT_SETTINGS)) {
        showInfoMessage(
            SETTINGS_MESSAGE_ID,
            "No changes detected."
        );

        return;
    }

    applySettingsToForm(DEFAULT_SETTINGS);

    showInfoMessage(
        SETTINGS_MESSAGE_ID,
        "Settings reset. Click Save Settings to keep these changes."
    );
}

function loadSettings() {
    originalSettings =
        getSavedSettings();

    applySettingsToForm(originalSettings);
}

function initializeSettingsPage() {
    getElement("saveSettingsButton")
        .addEventListener(
            "click",
            saveSettings
        );

    getElement("resetSettingsButton")
        .addEventListener(
            "click",
            resetSettings
        );

    loadSettings();
}

initializeSettingsPage();