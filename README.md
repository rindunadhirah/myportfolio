# Rindu Maharani Nadhirah - Personal Portfolio

A personal portfolio website created for Individual Assignment 1 of the Platform-Based Programming course at the Faculty of Computer Science, Universitas Indonesia.

This website introduces my background, developing skills, selected projects, and educational journey. It is built as a static portfolio page using Django templates, semantic HTML5, and CSS3.

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
- **Education:** Shows my educational journey from senior high school to university.

## Technologies Used

- **Python and Django:** Run the web application and render the portfolio template.
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

### AI Limitations and My Manual Fixes

The AI was useful, but its answers were not always correct or suitable for my assignment.

- It suggested using JavaScript for a scroll animation. I remembered that Assignment 1 focused on plain HTML5 and CSS3, so I asked the AI to read the PDF again. I did not add the JavaScript.
- Some first CSS suggestions did not match the layout I wanted. I changed the portrait ratio, card alignment, project-image frame, colors, and animation speed after testing them.
- The navigation looked correct on regular mobile screens but became clipped at 320 pixels. I fixed it after testing a narrower screen.
- I checked the website and ran Django checks before commits instead of assuming that every generated suggestion would work.

In conclusion, AI helped me with ideas and explanations, but I still check the original assignment, confirm facts, understand the code, and test the result myself.
