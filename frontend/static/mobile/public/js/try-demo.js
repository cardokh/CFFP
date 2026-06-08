/*
 * Mobile demo access controller.
 *
 * Responsibilities:
 * - Authenticate using the shared demo account.
 * - Store authenticated user session data using shared session utilities.
 * - Navigate to the mobile protected welcome page.
 * - Provide navigation back to the mobile login page.
 */

const startDemoButton =
    document.getElementById("startDemoButton");

const backToLoginButton =
    document.getElementById("backToLoginButton");

const demoMessage =
    document.getElementById("demoMessage");

const DEMO_ACCOUNT = {
    email: "demo@hejsan.local",
    password: "DemoPassword123"
};

function showDemoMessage(message, isSuccess = false) {
    demoMessage.textContent = message;
    demoMessage.style.color =
        isSuccess ? "#1f7a3f" : "#b00020";
}

function setDemoButtonState(disabled, text) {
    startDemoButton.disabled = disabled;
    startDemoButton.textContent = text;
}

function goToProtectedWelcome() {
    window.location.href =
        window.LLA_PATHS.mobile.protected.welcome;
}

function goBackToLogin() {
    window.location.href =
        window.LLA_PATHS.mobile.public.login;
}

async function startDemo() {
    setDemoButtonState(
        true,
        "Starting demo..."
    );

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

        showDemoMessage(
            "Could not start demo. Please try again."
        );

        setDemoButtonState(
            false,
            "Start demo"
        );

    } catch (error) {

        showDemoMessage(
            "Could not connect to the server."
        );

        setDemoButtonState(
            false,
            "Start demo"
        );

        console.error(error);
    }
}

startDemoButton.addEventListener(
    "click",
    startDemo
);

backToLoginButton.addEventListener(
    "click",
    goBackToLogin
);