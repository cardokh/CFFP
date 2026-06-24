const ORGANIZATIONS_ENDPOINT = "/api/ccore/organizations";

async function loadOrganizations() {
    const statusElement = document.getElementById("organizations-status");
    const tableBody = document.querySelector("#organizations-table tbody");

    try {
        const response = await fetch(ORGANIZATIONS_ENDPOINT);
        const payload = await response.json();
        const items = payload.items || [];

        tableBody.innerHTML = items.map((organization) => `
            <tr data-organization-id="${organization.organization_id}">
                <td>${organization.organization_name || ""}</td>
                <td>${organization.organization_code || ""}</td>
                <td>${organization.organization_type_name || ""}</td>
                <td>${organization.is_active ? "Yes" : "No"}</td>
                <td>${organization.updated_at || ""}</td>
            </tr>
        `).join("");

        statusElement.textContent = `${items.length} organization(s) loaded.`;
    } catch (error) {
        statusElement.textContent = "Could not load organizations.";
    }
}

document.addEventListener("DOMContentLoaded", loadOrganizations);
