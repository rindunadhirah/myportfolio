const experienceApp = document.getElementById("experience-app");

if (experienceApp) {
    const SEARCH_DELAY = 300;
    const { fillUrl, readJson, writeJson } = window.ajaxUtils;

    const config = {
        endpoint: experienceApp.dataset.experiencesEndpoint,
        createEndpoint:
            experienceApp.dataset.createExperienceEndpoint,
        loginUrl: experienceApp.dataset.loginUrl,
        starUrlTemplate: experienceApp.dataset.starUrlTemplate,
        detailUrlTemplate: experienceApp.dataset.detailUrlTemplate,
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
    const experienceForm = document.getElementById(
        "experience-form"
    );
    const experienceModal = document.getElementById(
        "add-experience-modal"
    );
    const experienceModalTitle = document.getElementById(
        "add-experience-modal-title"
    );
    const experienceSubmitButton = document.getElementById(
        "experience-form-submit"
    );
    const addExperienceButton = document.getElementById(
        "add-experience-button"
    );

    let searchTimer;
    let experienceController;
    let editingExperienceId = null;

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

        const button = document.createElement("button");
        const starIcon = document.createElement("span");
        const count = document.createElement("span");
        const starText = experience.is_starred
            ? "Unstar"
            : "Star";

        button.type = "button";
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
        button.dataset.action = "star";
        button.dataset.id = experienceId;
        button.title = experience.starred_by_names || "";

        starIcon.setAttribute("aria-hidden", "true");
        starIcon.textContent = "★";
        count.className = "star-count";
        count.textContent = starCount;

        button.append(
            starIcon,
            document.createTextNode(` ${starText} `),
            count
        );
        return button;
    }

    function buildEditControl(experienceId) {
        if (!config.isSuperuser && !config.isEditor) {
            return null;
        }

        const editButton = createButton("Edit Experience");
        editButton.dataset.action = "edit";
        editButton.dataset.id = experienceId;
        return editButton;
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

        confirmButton.type = "button";
        confirmButton.className = "button button-danger";
        confirmButton.textContent = "Yes, Delete";
        confirmButton.dataset.action = "delete";
        confirmButton.dataset.id = experienceId;

        modalActions.append(cancelButton, confirmButton);
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
    function buildExperienceCard(experience) {
        const experienceId = experience.id;
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
            const experiences = await readJson(endpoint, {
                signal: experienceController.signal,
            });
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

    function closeExperienceModal() {
        if (experienceModal?.matches(":popover-open")) {
            experienceModal.hidePopover();
        }
    }

    // Prepare the shared form for adding or editing
    function setExperienceFormMode(experience = null) {
        if (!experienceForm) {
            return;
        }

        clearExperienceErrors();
        experienceForm.reset();
        editingExperienceId = experience?.id || null;

        if (editingExperienceId) {
            experienceModalTitle.textContent = "Edit Experience";
            experienceSubmitButton.textContent = "Save Changes";

            const values = {
                title: experience.title,
                organization: experience.organization,
                description: experience.description,
                responsibilities: Array.isArray(
                    experience.responsibilities
                )
                    ? experience.responsibilities.join("\n")
                    : "",
                category: experience.category,
                thumbnail: experience.thumbnail || "",
                started_on: experience.started_on,
                ended_on: experience.ended_on || "",
            };

            for (const [name, value] of Object.entries(values)) {
                const field = experienceForm.elements.namedItem(name);

                if (field) {
                    field.value = value;
                }
            }
        } else {
            experienceModalTitle.textContent = "Add Experience";
            experienceSubmitButton.textContent = "Add Experience";
        }

        syncExperienceDates();
    }

    // Load one record before opening the edit form
    async function openExperienceEditor(experienceId, button) {
        const originalText = button.textContent;
        button.disabled = true;
        button.textContent = "Loading...";

        try {
            const endpoint = fillUrl(
                config.detailUrlTemplate,
                experienceId
            );
            const experience = await readJson(endpoint);
            setExperienceFormMode(experience);
            experienceModal.showPopover();
        } catch (error) {
            window.showToast(
                "Experience could not be opened",
                error.message,
                "error",
                5000
            );
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }

    // Keep the end date on or after the start date
    function syncExperienceDates() {
        if (!experienceForm) {
            return;
        }

        const startInput = experienceForm.querySelector(
            '[name="started_on"]'
        );
        const endInput = experienceForm.querySelector(
            '[name="ended_on"]'
        );

        if (!startInput || !endInput) {
            return;
        }

        endInput.min = startInput.value;

        if (
            startInput.value
            && endInput.value
            && endInput.value < startInput.value
        ) {
            endInput.setCustomValidity(
                "End date cannot be earlier than start date."
            );
        } else {
            endInput.setCustomValidity("");
        }
    }

    function clearExperienceErrors() {
        experienceForm
            .querySelectorAll("[data-ajax-error]")
            .forEach((error) => error.remove());
        experienceForm
            .querySelectorAll('[aria-invalid="true"]')
            .forEach((field) => {
                field.removeAttribute("aria-invalid");
            });
    }

    // Show each server error below the related field
    function displayExperienceErrors(errors) {
        const messages = [];
        let firstInvalidField = null;

        for (const [fieldName, fieldErrors] of Object.entries(errors)) {
            const field = experienceForm.elements.namedItem(fieldName);
            const fieldGroup = field?.closest(".form-group");
            const fieldLabel = fieldGroup
                ?.querySelector("label")
                ?.textContent.trim() || "Form";
            const errorList = Array.isArray(fieldErrors)
                ? fieldErrors
                : [fieldErrors];

            for (const error of errorList) {
                const message = typeof error === "string"
                    ? error
                    : error.message;
                messages.push(`${fieldLabel}: ${message}`);

                if (fieldGroup) {
                    const errorElement = document.createElement("p");
                    errorElement.className = "form-error";
                    errorElement.dataset.ajaxError = "true";
                    errorElement.textContent = message;
                    fieldGroup.appendChild(errorElement);
                }
            }

            if (field) {
                field.setAttribute("aria-invalid", "true");
                firstInvalidField ||= field;
            }
        }

        firstInvalidField?.focus();
        return messages;
    }

    function buildExperiencePayload() {
        const fields = new FormData(experienceForm);
        const responsibilities = String(
            fields.get("responsibilities") || ""
        )
            .split(/\r?\n/)
            .map((item) => item.trim())
            .filter(Boolean);

        return {
            title: fields.get("title"),
            organization: fields.get("organization"),
            description: fields.get("description"),
            responsibilities,
            category: fields.get("category"),
            thumbnail: fields.get("thumbnail") || null,
            started_on: fields.get("started_on"),
            ended_on: fields.get("ended_on") || null,
        };
    }

    // Create or update an experience through the DRF API
    async function saveExperience(event) {
        event.preventDefault();
        clearExperienceErrors();

        const isEditing = Boolean(editingExperienceId);
        const endpoint = isEditing
            ? fillUrl(
                config.detailUrlTemplate,
                editingExperienceId
            )
            : config.createEndpoint;
        experienceSubmitButton.disabled = true;

        try {
            await writeJson(
                endpoint,
                isEditing ? "PATCH" : "POST",
                buildExperiencePayload()
            );
            experienceForm.reset();
            editingExperienceId = null;
            syncExperienceDates();
            closeExperienceModal();
            window.showToast(
                isEditing
                    ? "Experience updated"
                    : "Experience added",
                isEditing
                    ? "The experience was updated successfully."
                    : "The new experience was added successfully.",
                "success"
            );
            await fetchExperiences();
        } catch (error) {
            console.error("Unable to add experience:", error);
            const messages = error.data
                ? displayExperienceErrors(error.data)
                : [error.message];
            window.showToast(
                isEditing
                    ? "Experience could not be updated"
                    : "Experience could not be added",
                messages.join("\n"),
                "error",
                5000
            );
        } finally {
            experienceSubmitButton.disabled = false;
        }
    }

    // Handle star and delete buttons without page navigation
    experienceGrid.addEventListener("click", async (event) => {
        const button = event.target.closest(
            "button[data-action]"
        );

        if (!button || button.disabled) {
            return;
        }

        const action = button.dataset.action;

        if (action === "edit") {
            await openExperienceEditor(
                button.dataset.id,
                button
            );
            return;
        }

        const endpoint = fillUrl(
            action === "star"
                ? config.starUrlTemplate
                : config.detailUrlTemplate,
            button.dataset.id
        );
        button.disabled = true;

        try {
            await writeJson(
                endpoint,
                action === "star" ? "POST" : "DELETE"
            );
            window.showToast(
                "Success",
                action === "star"
                    ? "Experience star updated."
                    : "Experience deleted successfully.",
                "success"
            );
            await fetchExperiences();
        } catch (error) {
            window.showToast(
                "Request failed",
                error.message,
                "error",
                5000
            );
        } finally {
            button.disabled = false;
        }
    });

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

    if (experienceForm) {
        const startInput = experienceForm.querySelector(
            '[name="started_on"]'
        );
        const endInput = experienceForm.querySelector(
            '[name="ended_on"]'
        );

        startInput?.addEventListener(
            "change",
            syncExperienceDates
        );
        endInput?.addEventListener(
            "change",
            syncExperienceDates
        );
        experienceForm.addEventListener(
            "submit",
            saveExperience
        );
        experienceForm.addEventListener("input", (event) => {
            const fieldGroup = event.target.closest(".form-group");

            event.target.removeAttribute("aria-invalid");
            fieldGroup
                ?.querySelectorAll("[data-ajax-error]")
                .forEach((error) => error.remove());
        });
        syncExperienceDates();
    }

    addExperienceButton?.addEventListener("click", () => {
        setExperienceFormMode();
    });

    fetchExperiences();
}
