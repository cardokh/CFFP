/*
 * Desktop demo access controller.
 *
 * Responsibilities:
 * - Authenticate using the shared demo account.
 * - Store demo user session data using shared session utilities.
 * - Redirect successful demo sessions to the protected welcome page.
 * - Display demo login feedback messages.
 */

const startDemoButton =
    document.getElementById("startDemoButton");

const demoMessage =
    document.getElementById("demoMessage");

const DEMO_ACCOUNT = {
    email: "demo@hejsan.local",
    password: "DemoPassword123"
};

function showDemoMessage(message, isSuccess = false) {
    demoMessage.textContent = message;
    demoMessage.style.color = isSuccess ? "#1f7a3f" : "#b00020";
}

function resetDemoButton() {
    startDemoButton.disabled = false;
    startDemoButton.textContent = "Start demo";
}

function goToProtectedWelcome() {
    window.location.href =
        window.LLA_PATHS.desktop.protected.welcome;
}

async function startDemo() {
    startDemoButton.disabled = true;
    startDemoButton.textContent = "Starting demo...";

    showDemoMessage("");

    try {
        const result =
            await login(
                DEMO_ACCOUNT.email,
                DEMO_ACCOUNT.password
            );

        if (result.success) {
            saveAuthenticatedUser(result.user);

            goToProtectedWelcome();

            return;
        }

        showDemoMessage("Could not start demo. Please try again.");

        resetDemoButton();

    } catch (error) {
        showDemoMessage("Could not connect to the server.");

        resetDemoButton();

        console.error(error);
    }
}

startDemoButton.addEventListener(
    "click",
    startDemo
);