const experienceApp = document.getElementById("experience-app");

if (experienceApp) {
    const PLACEHOLDER_ID =
        "00000000-0000-0000-0000-000000000000";
    const SEARCH_DELAY = 300;

    const config = {
        endpoint: experienceApp.dataset.experiencesEndpoint,
        loginUrl: experienceApp.dataset.loginUrl,
        starUrlTemplate: experienceApp.dataset.starUrlTemplate,
        updateUrlTemplate: experienceApp.dataset.updateUrlTemplate,
        deleteUrlTemplate: experienceApp.dataset.deleteUrlTemplate,
        isAuthenticated:
            experienceApp.dataset.isAuthenticated === "true",
        isSuperuser: experienceApp.dataset.isSuperuser === "true",
        isEditor: experienceApp.dataset.isEditor === "true",
    };

    const filterForm = document.getElementById(
        "experience-filter-form"
    );
    const searchInput = document.getElementById(
        "experience-search"
    );
    const categoryFilter = document.getElementById(
        "experience-category"
    );
    const loadingState = document.getElementById(
        "experience-loading"
    );
    const errorState = document.getElementById(
        "experience-error"
    );
    const emptyState = document.getElementById(
        "experience-empty"
    );
    const retryButton = document.getElementById(
        "experience-retry"
    );
    const experienceGrid = document.getElementById(
        "experience-grid"
    );

    let searchTimer;
    let experienceController;

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

    // Insert an Experience UUID into a Django URL
    function createExperienceUrl(template, experienceId) {
        return template.replace(PLACEHOLDER_ID, experienceId);
    }

    // Format a stored date for the card
    function formatMonthYear(dateValue) {
        const date = new Date(`${dateValue}T00:00:00Z`);

        return new Intl.DateTimeFormat("en", {
            month: "short",
            year: "numeric",
            timeZone: "UTC",
        }).format(date);
    }

    // Display only the requested Experience page state
    function displayPageState({
        showLoading = false,
        showError = false,
        showEmpty = false,
        showGrid = false,
    }) {
        loadingState.classList.toggle("hide", !showLoading);
        errorState.classList.toggle("hide", !showError);
        emptyState.classList.toggle("hide", !showEmpty);
        experienceGrid.classList.toggle("hide", !showGrid);
        experienceGrid.setAttribute(
            "aria-busy",
            showLoading ? "true" : "false"
        );
    }

    // Create a button with consistent classes
    function createButton(text, className = "button") {
        const button = document.createElement("button");
        button.type = "button";
        button.className = className;
        button.textContent = text;
        return button;
    }

    function buildStarControl(experience, experienceId) {
        const starCount = Number(experience.star_count) || 0;

        if (!config.isAuthenticated) {
            const loginLink = document.createElement("a");
            const starIcon = document.createElement("span");
            const count = document.createElement("span");

            loginLink.href = config.loginUrl;
            loginLink.className = "button button-star";
            starIcon.setAttribute("aria-hidden", "true");
            starIcon.textContent = "★";
            count.className = "star-count";
            count.textContent = starCount;

            loginLink.append(
                starIcon,
                document.createTextNode(" Log in to star "),
                count
            );
            return loginLink;
        }

        const form = document.createElement("form");
        const csrfInput = document.createElement("input");
        const button = document.createElement("button");
        const starIcon = document.createElement("span");
        const count = document.createElement("span");
        const starText = experience.is_starred
            ? "Unstar"
            : "Star";

        form.method = "post";
        form.action = createExperienceUrl(
            config.starUrlTemplate,
            experienceId
        );
        form.className = "star-form";

        csrfInput.type = "hidden";
        csrfInput.name = "csrfmiddlewaretoken";
        csrfInput.value = getCookie("csrftoken") || "";

        button.type = "submit";
        button.className = experience.is_starred
            ? "button button-star is-starred"
            : "button button-star";
        button.setAttribute(
            "aria-pressed",
            experience.is_starred ? "true" : "false"
        );
        button.setAttribute(
            "aria-label",
            experience.is_starred
                ? `Remove star from ${experience.title}`
                : `Star ${experience.title}`
        );

        starIcon.setAttribute("aria-hidden", "true");
        starIcon.textContent = "★";
        count.className = "star-count";
        count.textContent = starCount;

        button.append(
            starIcon,
            document.createTextNode(` ${starText} `),
            count
        );
        form.append(csrfInput, button);
        return form;
    }

    function buildEditControl(experienceId) {
        if (!config.isSuperuser && !config.isEditor) {
            return null;
        }

        const editLink = document.createElement("a");
        editLink.href = createExperienceUrl(
            config.updateUrlTemplate,
            experienceId
        );
        editLink.className = "button";
        editLink.textContent = "Edit Experience";
        return editLink;
    }

    function buildDeleteControl(experience, experienceId) {
        if (!config.isSuperuser) {
            return null;
        }

        const wrapper = document.createElement("div");
        const openButton = createButton(
            "Delete Experience",
            "button button-danger"
        );
        const modal = document.createElement("div");
        const backdrop = createButton("");
        const content = document.createElement("div");
        const closeButton = createButton("×");
        const title = document.createElement("h2");
        const message = document.createElement("p");
        const strongTitle = document.createElement("strong");
        const modalActions = document.createElement("div");
        const cancelButton = createButton(
            "Cancel",
            "button button-secondary"
        );
        const deleteForm = document.createElement("form");
        const csrfInput = document.createElement("input");
        const confirmButton = document.createElement("button");
        const modalId = `delete-experience-${experienceId}`;
        const titleId = `${modalId}-title`;

        wrapper.className = "experience-delete-action";
        openButton.setAttribute("popovertarget", modalId);
        openButton.setAttribute(
            "aria-label",
            `Delete ${experience.title}`
        );

        modal.id = modalId;
        modal.className = "project-delete-modal";
        modal.setAttribute("popover", "auto");
        modal.setAttribute("role", "dialog");
        modal.setAttribute("aria-modal", "true");
        modal.setAttribute("aria-labelledby", titleId);

        backdrop.className = "project-delete-modal__backdrop";
        backdrop.setAttribute("popovertarget", modalId);
        backdrop.setAttribute("popovertargetaction", "hide");
        backdrop.setAttribute(
            "aria-label",
            "Close delete confirmation"
        );

        content.className = "project-delete-modal__content";
        closeButton.className = "project-delete-modal__close";
        closeButton.setAttribute("popovertarget", modalId);
        closeButton.setAttribute("popovertargetaction", "hide");
        closeButton.setAttribute(
            "aria-label",
            "Close delete confirmation"
        );

        title.id = titleId;
        title.textContent = "Delete Experience?";
        strongTitle.textContent = experience.title;
        message.append(
            document.createTextNode(
                "Are you sure you want to delete "
            ),
            strongTitle,
            document.createTextNode("?")
        );

        modalActions.className = "project-delete-modal__actions";
        cancelButton.setAttribute("popovertarget", modalId);
        cancelButton.setAttribute("popovertargetaction", "hide");

        deleteForm.method = "post";
        deleteForm.action = createExperienceUrl(
            config.deleteUrlTemplate,
            experienceId
        );
        csrfInput.type = "hidden";
        csrfInput.name = "csrfmiddlewaretoken";
        csrfInput.value = getCookie("csrftoken") || "";
        confirmButton.type = "submit";
        confirmButton.className = "button button-danger";
        confirmButton.textContent = "Yes, Delete";

        deleteForm.append(csrfInput, confirmButton);
        modalActions.append(cancelButton, deleteForm);
        content.append(
            closeButton,
            title,
            message,
            modalActions
        );
        modal.append(backdrop, content);
        wrapper.append(openButton, modal);
        return wrapper;
    }

    // Build one card without interpreting user data as HTML
    function buildExperienceCard(item) {
        const experience = item.fields;
        const experienceId = item.pk;
        const card = document.createElement("article");
        const header = document.createElement("div");
        const category = document.createElement("span");
        const date = document.createElement("p");
        const startTime = document.createElement("time");
        const title = document.createElement("h2");
        const organization = document.createElement("p");
        const status = document.createElement("p");
        const actions = document.createElement("div");

        card.className = "experience-card";
        header.className = "experience-card-header";
        category.className = "experience-category";
        category.textContent = experience.category_label;

        date.className = "experience-date";
        startTime.dateTime = experience.started_on;
        startTime.textContent = formatMonthYear(
            experience.started_on
        );
        date.append(startTime, document.createTextNode(" - "));

        if (experience.ended_on) {
            const endTime = document.createElement("time");
            endTime.dateTime = experience.ended_on;
            endTime.textContent = formatMonthYear(
                experience.ended_on
            );
            date.appendChild(endTime);
        } else {
            date.appendChild(document.createTextNode("Present"));
        }

        header.append(category, date);
        title.textContent = experience.title;
        organization.className = "experience-organization";
        organization.textContent = experience.organization;

        const responsibilities = Array.isArray(
            experience.responsibilities
        )
            ? experience.responsibilities
            : [];

        if (responsibilities.length > 0) {
            const list = document.createElement("ul");
            list.className = "experience-responsibilities";

            for (const responsibility of responsibilities) {
                const itemElement = document.createElement("li");
                itemElement.textContent = responsibility;
                list.appendChild(itemElement);
            }

            card.append(header, title, organization, list);
        } else {
            const description = document.createElement("p");
            description.className = "experience-description";
            description.textContent = experience.description;
            card.append(header, title, organization, description);
        }

        status.className = "experience-status";
        status.textContent = experience.is_ongoing
            ? "Ongoing"
            : "Completed";
        actions.className = "experience-card-actions";
        actions.appendChild(
            buildStarControl(experience, experienceId)
        );

        const editControl = buildEditControl(experienceId);
        const deleteControl = buildDeleteControl(
            experience,
            experienceId
        );

        if (editControl) {
            actions.appendChild(editControl);
        }

        if (deleteControl) {
            actions.appendChild(deleteControl);
        }

        card.append(status, actions);
        return card;
    }

    // Keep the visible URL synchronized with the active filters
    function updateBrowserUrl(search, category) {
        const url = new URL(window.location.href);

        if (search) {
            url.searchParams.set("search", search);
        } else {
            url.searchParams.delete("search");
        }

        if (category) {
            url.searchParams.set("category", category);
        } else {
            url.searchParams.delete("category");
        }

        window.history.replaceState({}, "", url);
    }

    // Request filtered experiences and update the page
    async function fetchExperiences() {
        if (experienceController) {
            experienceController.abort();
        }

        experienceController = new AbortController();
        displayPageState({ showLoading: true });

        const endpoint = new URL(
            config.endpoint,
            window.location.origin
        );
        const search = searchInput.value.trim();
        const category = categoryFilter.value;

        if (search) {
            endpoint.searchParams.set("search", search);
        }

        if (category) {
            endpoint.searchParams.set("category", category);
        }

        try {
            const response = await fetch(endpoint, {
                headers: {
                    Accept: "application/json",
                },
                signal: experienceController.signal,
            });

            if (!response.ok) {
                throw new Error(
                    `Request failed with status ${response.status}`
                );
            }

            const experiences = await response.json();
            experienceGrid.replaceChildren();
            updateBrowserUrl(search, category);

            if (experiences.length === 0) {
                displayPageState({ showEmpty: true });
                return;
            }

            for (const experience of experiences) {
                experienceGrid.appendChild(
                    buildExperienceCard(experience)
                );
            }

            displayPageState({ showGrid: true });
        } catch (error) {
            if (error.name === "AbortError") {
                return;
            }

            console.error("Unable to load experiences:", error);
            displayPageState({ showError: true });
        }
    }

    // Wait briefly after typing before sending a request
    searchInput.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(
            fetchExperiences,
            SEARCH_DELAY
        );
    });

    categoryFilter.addEventListener(
        "change",
        fetchExperiences
    );

    filterForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(searchTimer);
        fetchExperiences();
    });

    retryButton.addEventListener("click", fetchExperiences);
    fetchExperiences();
}
