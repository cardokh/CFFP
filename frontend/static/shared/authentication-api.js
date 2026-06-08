/*
 * Shared authentication API helpers.
 *
 * Responsibilities:
 * - Provide reusable frontend authentication API operations.
 * - Delegate HTTP communication to shared api.js helpers.
 * - Centralize authentication-related backend requests.
 * - Keep page-specific authentication controllers thin.
 *
 * Dependencies:
 * - api.js must be loaded before this file.
 * - api-endpoints.js must be loaded before this file.
 *
 * Architectural rules:
 * - Authentication page controllers must not call postJson() directly.
 * - Authentication endpoint paths must come from api-endpoints.js.
 */

async function login(email, password) {
    return await postJson(
        LLA_API_ENDPOINTS.auth.login,
        {
            email: email,
            password: password
        }
    );
}

async function registerUser(registerData) {
    return await postJson(
        LLA_API_ENDPOINTS.auth.register,
        registerData
    );
}

async function requestPasswordReset(email) {
    return await postJson(
        LLA_API_ENDPOINTS.auth.forgotPassword,
        {
            email: email
        }
    );
}