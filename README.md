# Rindu Maharani Nadhirah - Personal Portfolio

A personal portfolio website created for Individual Assignment of the Platform-Based Programming course at the Faculty of Computer Science, Universitas Indonesia.

This website introduces my background, skills, projects, experience, and education. It uses Django's Model-View-Template structure, with project and experience information stored in a database.

## Live Website

[View the deployed portfolio](https://rindu-maharani-myportofolio.pws.cs.ui.ac.id/)

## Student Information

- **Name:** Rindu Maharani Nadhirah
- **NPM:** 2506587131
- **Class:** PBP D

## Portfolio Sections

- **About Me:** Introduces my background, academic program, interests, and contact links.
- **Skills:** Organizes my technical, product management, and collaboration skills.
- **Projects:** Presents projects I have worked on, my contributions, and links to their deployed applications.
- **Experience:** Shows my roles, programs, responsibilities, and work history in chronological order.
- **Education:** Shows my educational journey from senior high school to university.

## Technologies Used

- **Python and Django:** Handle the website routes, views, models, templates, and data.
- **Django Template Language:** Displays database content dynamically inside HTML templates.
- **SQLite:** Stores project and experience information.
- **HTML5:** Provides the semantic structure of the portfolio.
- **CSS3:** Controls the colors, layouts, responsiveness, hover effects, and animations.
- **Git and GitHub:** Track the project's development and commit history.

## Running the Project Locally

### Prerequisites

Make sure Python 3 and Git are installed on your computer.

### Installation

1. Clone the repository and enter its directory.

    ```bash
    git clone https://github.com/rindunadhirah/myportfolio.git
    cd myportfolio
    ```

2. Create a virtual environment.

    ```bash
    python -m venv env
    ```

3. Activate the virtual environment.

    On Windows PowerShell:

    ```powershell
    .\env\Scripts\Activate.ps1
    ```

    On macOS or Linux:

    ```bash
    source env/bin/activate
    ```

4. Install the project dependencies.

    ```bash
    pip install -r requirements.txt
    ```

5. Prepare the local database.

    ```bash
    python manage.py migrate
    ```

6. Start the Django development server.

    ```bash
    python manage.py runserver
    ```

7. Open `http://127.0.0.1:8000/` in a browser.

## Running Checks and Tests

Activate the virtual environment, then run:

```powershell
python manage.py check
python manage.py test main
```

`check` verifies the Django configuration. `test main` runs the automated tests for the portfolio application.

## Main Routes

| Route | Purpose |
|---|---|
| `/` | Display the main portfolio page |
| `/projects/` | Display and search projects |
| `/projects/add/` | Create a project |
| `/api/projects/` | Return project data in JSON |
| `/experience/` | Display and filter experiences |
| `/experience/add/` | Create an experience |
| `/experience/<id>/edit/` | Update an experience |
| `/experience/<id>/delete/` | Delete an experience |
| `/api/experiences/` | Return experience data in JSON |

## Weekly Progress

### Week 1 - Tutorials 0 and 1

- Created the Git repository and connected it to GitHub.
- Created a Python virtual environment and installed the required packages.
- Created the Django project and prepared it for local development.
- Connected the main page using a Django view, URL, template, and static files.
- Built the first About Me page using HTML5 and CSS3.
- Replaced the sample content with my information, photo, biography, and contact links.
- Connected the project to PWS and added the deployment address to Django.

### Week 2 - Assignment 1

- Added Skills, Projects, and Education sections.
- Grouped my skills into three responsive cards.
- Added three projects with my contributions and deployed application links.
- Added my senior high school and university education.
- Made the website responsive on desktop, tablet, and mobile screens.
- Added CSS animations, hover effects, keyboard focus styles, and reduced motion support.
- Used a separate branch and made gradual Git commits.

### Week 3 - Tutorial 2 and Assignment 2

- Created Django models for Experience and Project data.
- Created and applied schema and data migrations.
- Displayed experience and project data from the database using Django templates.
- Created separate pages for Projects and Experience.
- Added named URL routes and connected the pages through the navigation bar.
- Added an Experience Journey card to the main page.
- Added empty states for pages that do not have data.
- Added tests for page access, templates, database content, and empty states.
- Kept the new pages responsive and consistent with the original portfolio design.

### Week 4 - Tutorial 3 and Assignment 3

- Refactored repeated HTML structures to use the shared `base.html` template.
- Added a `ProjectForm` and an `ExperienceForm` using Django ModelForm.
- Added pages for creating and updating experience data.
- Added delete confirmation buttons for projects and experiences.
- Added JSON endpoints for project and experience data.
- Serialized database objects into JSON and deserialized the data before displaying it.
- Added project search and experience category filtering.
- Added validation to prevent an experience from ending before it starts.
- Added success messages after creating, updating, or deleting data.
- Added tests for experience creation, updates, deletion, filtering, JSON delivery, and form validation.

## Reflective Questions

### Assignment 1

1. I used semantic HTML5 elements to give each part of my website a clear purpose. I used `<header>` for the navigation area, `<main>` for the main content, `<section>` for About Me, Skills, Projects, and Education, and `<footer>` for the closing information. I also used `<article>` for each skill card and project because each card contains information that can be understood on its own.

   I used `<nav>` for navigation and contact links, `<dl>`, `<dt>`, and `<dd>` for my student information, and `<time>` for project dates. These elements made the HTML easier to read and helped me understand the role of each part. They also help screen readers and search engines understand the page. I did not use `<aside>` because my portfolio does not have separate supporting content or a sidebar.

2. My main challenge was changing the wide desktop layout into a clear mobile layout. On desktop, the hero section and project cards use multiple columns. This layout did not have enough space on a phone, so I changed them into one-column layouts using media queries.

   I decided that my name should appear first on mobile, followed by my photo and personal information. For project cards, I placed the project information and image in a clear vertical order. I used CSS Grid areas to change the position of content without changing the HTML order. I also used flexible widths, `clamp()`, `minmax()`, and `aspect-ratio` to control text and image sizes.

   I tested the website at desktop, tablet, and mobile widths. During testing, I found that the navigation was slightly too wide on a 320-pixel screen. I added a smaller media query to reduce its spacing and font size. This showed me that responsive design needs testing at several screen widths, not only one desktop and one mobile size.

3. The current website is static, so I must edit the HTML whenever I want to add or change a project, skill, or education item. This can become difficult when the portfolio contains more information.

   The website also does not have a working contact form, project filters, or a private page for managing content. The email link can open an email application, but visitors cannot send a message directly through the website.

   In the next version, I would add project filters so recruiters could quickly find projects based on my role or the technologies I used. I would also add buttons that open more project details, such as the problem, my responsibilities, and the final result. Then, it would be good as well to have a downloadable CV and a contact form that would make it easier for recruiters to learn more about me and contact me.

### Assignment 2

1. When a user opens the Projects page, the browser sends a request to `/projects/`. The project-level `portofolio/urls.py` receives the request first. It uses `include()` to send the request to `main/urls.py`.

   The application-level `main/urls.py` matches `/projects/` with the named `show_projects` route. It then calls the `show_projects` view in `main/views.py`.

   The view asks the `Project` model for all project objects. The model represents the project data stored in the database. Django uses its Object-Relational Mapper to read the data without requiring a direct SQL query.

   The view places the result inside the `project_list` context and sends it to `projects.html`. The template uses a Django Template Language loop to display every project. If there are no projects, the `{% empty %}` block displays an empty message. Django renders the completed HTML and returns it to the browser.

2. I store project data in a model to keep the data separate from the page design. The model stores information such as the project title, role, summary, date, image, contributions, and technologies. The template is only responsible for deciding how that information appears on the page.

   This structure makes the website easier to maintain. I can add or update a project in the database without copying and editing a large HTML card. Every project also follows the same field structure, which reduces missing or inconsistent information.

   The same project data can be reused in different places. My main page displays a short project preview, while the Projects page displays the complete list. In the future, I can also add project filters, search, an admin page, or detail pages without rewriting all project content.

3. `makemigrations` creates a migration file based on changes made to a Django model. The migration file records what should change in the database, but it does not apply the change yet.

   `migrate` reads the migration file and applies the recorded change to the database. It creates or updates the required database tables and columns.

   For example, when I created the `Project` model, I ran `python manage.py makemigrations` to create its migration file. I then ran `python manage.py migrate` to create the project table in the database. Both commands are needed because the first command prepares the instructions and the second command applies them.

### Assignment 3

1. Django ModelForm connects a form directly to a Django model. It creates form fields and basic validation rules based on the model fields. This reduces repeated code because I do not need to write every HTML input, read every value from `request.POST`, or create the model object manually.

   ModelForm can still be customized. I added labels, placeholders, date inputs, and a validation rule that prevents the end date from being earlier than the start date.

   `{% csrf_token %}` protects forms that change data using a POST request. Django checks the token to confirm that the form came from my website. This prevents another website from sending an unwanted request using a visitor's active session.

2. JSON is often preferred because it is shorter and easier to process than XML. It represents data using objects, arrays, strings, numbers, Boolean values, and null values. These structures are easy to use in both Python and JavaScript.

   XML usually needs opening and closing tags, which makes the data longer. JSON uses less text and is widely supported by modern APIs and web frameworks. XML is still useful when a system needs features such as strict schemas or namespaces, but JSON is simpler for my portfolio data.

3. When the JSON endpoint receives a request, the view retrieves Experience objects from the database as a QuerySet. If a category is selected, the QuerySet is filtered first. Django then uses `serializers.serialize()` to convert the model objects into JSON text.

   The view returns the JSON using an `HttpResponse` with the `application/json` content type. The Experience page reads this response and uses `serializers.deserialize()` to convert the JSON back into Experience objects before sending them to the template.

   Serialization is required because Django model objects are Python objects and cannot be sent directly through an HTTP response. They must first be converted into a transferable data format such as JSON.

## AI Use and Prompt History

### AI Disclosure

I used OpenAI Codex as a guide while working on this assignment. It helped me understand the assignment rubric, plan the HTML sections, write readable CSS, and check responsive layouts.

I asked the AI to give code in small steps and explain where each block should be placed. I typed the changes into my project, tested them in the browser, and committed them myself. I also changed several AI suggestions when they did not match the assignment rules, my real project information, or my design preferences.

### Prompt Strategy

I worked on one small part at a time. I usually asked for one HTML or CSS section, tested it, and checked the code before committing. When I did not understand a CSS rule, I asked what it did before continuing.

When a suggestion seemed uncertain, I asked the AI to check the requirements and my request again. This helped me compare the AI response with the original source instead of accepting every suggestion immediately.

### Short Prompt Log

The following table contains shortened versions of the main prompts used during this assignment.

| Purpose | Prompt summary | My work after receiving the answer |
|---|---|---|
| Improve responsiveness | Help fix the portrait size, skill card alignment, project frames, and mobile navigation. | I tested different screen widths and changed the CSS where needed. |
| Add animation | Add CSS animation and reduced motion support without making the website distracting. | I tested the motion and increased the hero animation duration because it was too fast. |
| Check the assignment scope | Read the assignment PDF again and check whether JavaScript is suitable for Assignment 1. | I questioned the JavaScript suggestion and decided to keep the website within the HTML5 and CSS3 scope. |
| Check project information | Use my CV for the project descriptions and remove the SisPro SUS score because its source is unclear. | I checked the AI generated claims and kept only information supported by my CV. |
| Understand Django MVT | Explain how the project URL, application URL, view, model, and template work together. | I followed the request flow in my own code and used it to build the Projects page. |
| Question migration choices | Explain when I should create a new migration and whether every data change needs one. | I learned the difference between changing the database structure and changing existing data. |
| Check the assignment requirement | Show proof from the assignment about where the Experience section should appear. | I checked the original wording and used a Journey card that links to the full Experience page. |
| Correct experience information | Remove the PBP teaching assistant example because it is not in my CV. Use only my real experience. | I rejected the incorrect example, checked my CV, and kept only information that represents my experience. |
| Plan Assignment 3 | Create a roadmap for the required Experience form, JSON delivery, Git commits, tests, and documentation. | I compared the plan with the rubric and completed each feature in a separate step. |
| Build the Experience workflow | Guide me through creating, updating, deleting, filtering, serializing, and deserializing Experience data. | I entered the code myself, tested each action, and kept the interface consistent with my portfolio. |
| Debug automated tests | Explain why the JSON test found five records and why `self.experience` was missing. | I learned that data migrations also run in the test database and that each test needs an isolated setup. |
| Improve Git practice | Plan Conventional Commit messages and decide which small changes can be grouped together. | I grouped related changes into clear commits instead of creating one commit for every small edit. |

### AI Limitations and My Manual Fixes

The AI was useful, but its answers were not always correct or suitable for my assignment.

- It suggested using JavaScript for a scroll animation. I remembered that Assignment 1 focused on plain HTML5 and CSS3, so I asked the AI to read the PDF again. I did not add the JavaScript.
- Some first CSS suggestions did not match the layout I wanted. I changed the portrait ratio, card alignment, project-image frame, colors, and animation speed after testing them.
- The navigation looked correct on regular mobile screens but became clipped at 320 pixels. I fixed it after testing a narrower screen.
- I checked the website and ran Django checks before commits instead of assuming that every generated suggestion would work.
- The AI first used a PBP teaching assistant role as an example even though it was not in my CV. I noticed the mistake and replaced it with my real experience.
- The AI suggested an Experience preview before proving that the assignment required one. I rechecked the assignment instructions and chose a journey card that better matched my portfolio.
- Some project image styles made one of my project's image too tall or gave it the wrong frame size. I tested the page and adjusted the image container until all project cards had a consistent size.
- I checked every model, migration, template, and test before committing instead of accepting the generated code immediately.
- The AI initially suggested replacing complete files even when only a few lines needed to change. I asked for targeted additions and replacements to reduce unnecessary changes.
- A JSON endpoint test initially expected one Experience record, but the test database also loaded four records from a data migration. I corrected the test setup so each test starts with isolated data.
- While editing the test setup, a duplicated `setUp()` definition caused several tests to fail. I checked the traceback, corrected the indentation, and reran all tests.
- Some suggested Projects page styles changed too much of my original design. I kept the existing visual style and changed only the heading and card actions that needed improvement.

In conclusion, AI helped me with ideas and explanations, but I still check the original assignment, confirm facts, understand the code, and test the result myself.
