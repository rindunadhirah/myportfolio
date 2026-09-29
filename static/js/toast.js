let toastHideTimer;
let toastCloseTimer;

function showToast(
    title,
    message,
    type = "normal",
    duration = 3000
) {
    const toast = document.getElementById("toast-component");
    const toastTitle = document.getElementById("toast-title");
    const toastMessage = document.getElementById("toast-message");

    // Stop if the toast component is unavailable
    if (!toast || !toastTitle || !toastMessage) {
        return;
    }

    // Cancel timers from the previous notification
    clearTimeout(toastHideTimer);
    clearTimeout(toastCloseTimer);

    toast.classList.remove(
        "toast-success",
        "toast-error",
        "toast-normal"
    );
    toast.classList.add(`toast-${type}`);

    // textContent prevents messages from being treated as HTML
    toastTitle.textContent = title;
    toastMessage.textContent = message;

    if (!toast.matches(":popover-open")) {
        toast.showPopover();
    }

    toast.classList.remove("toast-hidden");
    toast.classList.add("toast-show");

    // Hide the notification after the selected duration
    toastHideTimer = setTimeout(() => {
        toast.classList.remove("toast-show");
        toast.classList.add("toast-hidden");

        toastCloseTimer = setTimeout(() => {
            if (toast.matches(":popover-open")) {
                toast.hidePopover();
            }
        }, 250);
    }, duration);
}

// Make the function available to other page scripts
window.showToast = showToast;

// Display messages created by Django
document.addEventListener("DOMContentLoaded", () => {
    const djangoMessages = document.querySelectorAll(
        ".django-toast-message"
    );

    djangoMessages.forEach((item, index) => {
        // Show multiple messages one after another
        setTimeout(() => {
            showToast(
                item.dataset.toastTitle,
                item.dataset.toastMessage,
                item.dataset.toastType
            );
        }, index * 3500);
    });
});