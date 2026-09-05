# Rindu Maharani Nadhirah - Personal Portfolio

A personal portfolio website created for Individual Assignment 1 of the Platform-Based Programming course at the Faculty of Computer Science, Universitas Indonesia.

This website introduces my background, developing skills, selected projects, and educational journey. It is built as a static portfolio page using Django templates, semantic HTML5, and CSS3.

## Student Information

- **Name:** Rindu Maharani Nadhirah
- **Nickname:** Nadhirah
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
- **Git and GitHub:** Track the project’s development and commit history.

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
