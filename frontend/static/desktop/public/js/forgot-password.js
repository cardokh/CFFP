/*
 * Desktop forgot-password page controller.
 *
 * Responsibilities:
 * - Handle password recovery form submission
 * - Validate email input
 * - Simulate recovery-link feedback for the prototype
 * - Navigate back to the login page
 */

const forgotPasswordForm = document.getElementById("forgotPasswordForm");
const forgotPasswordMessage = document.getElementById("forgotPasswordMessage");
const sendResetButton = document.getElementById("sendResetButton");
const goToLoginButton = document.getElementById("goToLoginButton");

function showForgotPasswordMessage(message, isSuccess = false) {
    forgotPasswordMessage.textContent = message;
    forgotPasswordMessage.style.color = isSuccess ? "#1f7a3f" : "#b00020";
}

function goToLogin() {
    window.location.href = "./login.html";
}

function validateEmail(email) {
    if (!email) {
        return "Please enter your email address.";
    }

    if (!email.includes("@")) {
        return "Please enter a valid email address.";
    }

    return null;
}

function setRecoveryButtonState(disabled, text) {
    sendResetButton.disabled = disabled;
    sendResetButton.textContent = text;
}

function handleForgotPasswordSubmit(event) {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();

    const validationError = validateEmail(email);

    if (validationError) {
        showForgotPasswordMessage(validationError);
        return;
    }

    setRecoveryButtonState(true, "Sending...");

    showForgotPasswordMessage(
        "If this email exists in our system, a recovery link has been sent.",
        true
    );

    setRecoveryButtonState(true, "Recovery link sent");
}

forgotPasswordForm.addEventListener("submit", handleForgotPasswordSubmit);
goToLoginButton.addEventListener("click", goToLogin);