/*
 * Desktop login page controller.
 *
 * Responsibilities:
 * - Handle login form submission
 * - Validate communication with the backend authentication API
 * - Store authenticated user data using shared session utilities
 * - Navigate to register, forgot-password, demo, and protected welcome pages
 * - Display login and registration feedback messages
 */

const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");
const goToRegisterButton = document.getElementById("goToRegisterButton");
const forgotPasswordLink = document.getElementById("forgotPasswordLink");
const tryDemoButton = document.getElementById("tryDemoButton");

const REGISTER_SUCCESS_MESSAGE_KEY = "registerSuccessMessage";

function showLoginMessage(message, isSuccess = false) {
    loginMessage.textContent = message;
    loginMessage.style.color = isSuccess ? "#1f7a3f" : "#b00020";
}

function showRedirectMessageOnce() {
    const message =
        sessionStorage.getItem(REGISTER_SUCCESS_MESSAGE_KEY);

    if (!message) {
        return;
    }

    showLoginMessage(message, true);

    sessionStorage.removeItem(
        REGISTER_SUCCESS_MESSAGE_KEY
    );
}

function goToRegister() {
    window.location.href =
        window.LLA_PATHS.desktop.public.register;
}

function goToForgotPassword() {
    window.location.href =
        window.LLA_PATHS.desktop.public.forgotPassword;
}

function goToTryDemo() {
    window.location.href =
        window.LLA_PATHS.desktop.public.tryDemo;
}

function goToProtectedWelcome() {
    window.location.href =
        window.LLA_PATHS.desktop.protected.welcome;
}

async function handleLoginSubmit(event) {
    event.preventDefault();

    showLoginMessage("");

    const email =
        document.getElementById("email").value.trim();

    const password =
        document.getElementById("password").value;

    try {
        const result =
            await login(email, password);

        if (result.success) {
            saveAuthenticatedUser(result.user);

            goToProtectedWelcome();

            return;
        }

        showLoginMessage(
            mapLoginError(result.error)
        );
    } catch (error) {
        showLoginMessage(
            error.message || "Could not connect to the server."
        );

        console.error(error);
    }
}

showRedirectMessageOnce();

loginForm.addEventListener(
    "submit",
    handleLoginSubmit
);

goToRegisterButton.addEventListener(
    "click",
    goToRegister
);

forgotPasswordLink.addEventListener(
    "click",
    goToForgotPassword
);

tryDemoButton.addEventListener(
    "click",
    goToTryDemo
);