/*
 * Shared API transport helpers.
 *
 * Responsibilities:
 * - Store frontend API transport configuration.
 * - Build complete backend request URLs.
 * - Send JSON-based HTTP requests from frontend controllers.
 * - Parse backend JSON responses consistently.
 * - Normalize network, HTTP, and malformed-response errors.
 *
 * Architectural rule:
 * - Page controllers must not call fetch directly.
 * - Page controllers must use these helpers together with api-endpoints.js.
 */

const LLA_API_CONFIG = {
    baseUrl: "http://127.0.0.1:8000"
};

function buildApiUrl(endpoint) {
    return `${LLA_API_CONFIG.baseUrl}${endpoint}`;
}


function createJsonRequestOptions(method, data = null) {
    const options = {
        method: method
    };

    if (data !== null) {
        options.headers = {
            "Content-Type": "application/json"
        };

        options.body = JSON.stringify(data);
    }

    return options;
}


async function parseJsonResponse(response) {
    try {
        return await response.json();
    } catch (error) {
        throw new Error("The server returned an invalid response.");
    }
}

async function requestJson(endpoint, options) {
    let response;

    try {
        response =
            await fetch(buildApiUrl(endpoint), options);
    } catch (error) {
        throw new Error("Could not connect to the backend server.");
    }

    const data =
        await parseJsonResponse(response);

    if (!response.ok) {
        throw new Error(data.error || "The server rejected the request.");
    }

    return data;
}

async function getJson(endpoint) {
    return await requestJson(
        endpoint,
        createJsonRequestOptions("GET")
    );
}

async function postJson(endpoint, data) {
    return await requestJson(
        endpoint,
        createJsonRequestOptions("POST", data)
    );
}

async function putJson(endpoint, data) {
    return await requestJson(
        endpoint,
        createJsonRequestOptions("PUT", data)
    );
}

async function deleteJson(endpoint) {
    return await requestJson(
        endpoint,
        createJsonRequestOptions("DELETE")
    );
}