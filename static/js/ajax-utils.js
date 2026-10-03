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

    // Expose one object without adding duplicate global names
    window.ajaxUtils = Object.freeze({
        escapeHtml,
        fillUrl,
        getCookie,
    });
})();
