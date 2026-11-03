(() => {
    const AJAX_URL_PLACEHOLDER =
        "00000000-0000-0000-0000-000000000000";

    // Read a cookie value, including Django's CSRF token
    function getCookie(name) {
        const cookies = document.cookie
            ? document.cookie.split(";")
            : [];

        for (const item of cookies) {
            const cookie = item.trim();

            if (cookie.startsWith(`${name}=`)) {
                return decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
            }
        }

        return null;
    }

    // Escape text before inserting it through innerHTML
    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    // Insert an object UUID into a Django URL template
    function fillUrl(template, objectId) {
        return template.replace(AJAX_URL_PLACEHOLDER, objectId);
    }

    // Turn DRF error responses into one readable message
    function apiErrorMessage(data, status) {
        const messages = [];

        function collect(value) {
            if (Array.isArray(value)) {
                value.forEach(collect);
            } else if (value && typeof value === "object") {
                Object.values(value).forEach(collect);
            } else if (typeof value === "string") {
                messages.push(value);
            }
        }

        collect(data);
        return messages.join(" ")
            || `Request failed with status ${status}.`;
    }

    // Send a JSON write request with Django's CSRF token
    async function writeJson(url, method, payload) {
        const response = await fetch(url, {
            method,
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken") || "",
            },
            body: payload === undefined
                ? undefined
                : JSON.stringify(payload),
        });

        if (response.status === 204) {
            return null;
        }

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            const error = new Error(
                apiErrorMessage(data, response.status)
            );
            error.data = data;
            error.status = response.status;
            throw error;
        }

        return data;
    }

    // Expose one object without adding duplicate global names
    window.ajaxUtils = Object.freeze({
        apiErrorMessage,
        escapeHtml,
        fillUrl,
        getCookie,
        writeJson,
    });
})();
