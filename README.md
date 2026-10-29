# 🌌 Astrobase

**Your gateway to opportunities, resources, and pathways in astronomy, astrophysics, physics, and space science.**

Astrobase is a student-focused platform designed to bring educational resources, opportunities, and university information related to space science into one place.

The project aims to make it easier for students to discover competitions, research programmes, scholarships, educational material, and potential academic pathways without having to search across countless separate websites.

> *The universe is vast. Your path is yours.*

---

## 🎯 Why Astrobase?

Students interested in astronomy and space science often struggle to find reliable, relevant information about opportunities and educational pathways. Useful information is scattered across university websites, competition announcements, research organisations, and educational platforms.

Astrobase aims to simplify this process through a central platform where students can explore opportunities, discover learning resources, and investigate universities and programmes.

The long-term vision is to develop Astrobase into a broader space-science discovery and guidance platform.

## ✨ Current Development

Astrobase is under active development. The project currently includes website pages and administrative functionality, with further platform features planned for future development.

### Implemented website and administration features

- A multi-page website with a consistent visual identity.
- Dedicated sections for opportunities, resources, and universities.
- An Explore section for discovering Astrobase's content.
- Login and registration interface pages.
- An administrative dashboard for managing platform content.
- A Feedback Management page for reviewing user reports.
- Report summary cards showing total reports and status counts.
- Search and status filtering for submitted reports.
- A full-report viewer.
- Administrative controls for updating report statuses.
- Responsive styling and a consistent dark-themed interface.

**Note:** The presence of a page or interface does not necessarily mean its complete backend workflow is finished. Database integration, authentication, and individual features are being developed and verified as the project progresses.

## 🧭 Main Sections

### Opportunities

A dedicated section for discovering opportunities related to astronomy, astrophysics, physics, and space science, including competitions, internships, scholarships, research programmes, and workshops.

### Resources

A planned resource library covering books, courses, research papers, educational websites, videos, tools, articles, notes, and podcasts.

### Universities

A section intended to help students explore universities and academic programmes relevant to physics, astronomy, astrophysics, and related fields.

### Explore

A central discovery hub connecting the different sections of Astrobase and helping students investigate possible pathways into space science.

### Feedback Management

An administrative interface for viewing submitted reports, searching and filtering submissions, viewing full report details, and updating report statuses.

### Community

A future feature intended to provide a space for students, researchers, and space enthusiasts to exchange knowledge, discuss ideas, and collaborate.

---

## 🏗️ Planned Platform Architecture

Astrobase is being designed around three primary account roles.

| Role | Intended purpose |
|---|---|
| Student | Discover content and access personal features |
| Organisation | Contribute and manage approved content |
| Admin | Verify organisations, review submissions, and manage the platform |

The intended platform will include organisation verification, content submission and approval workflows, student profiles, saved items, and role-based permissions.

### Content workflow

The planned opportunity workflow is:

`Draft → Pending → Published → Expired / Closed → Archived`

Organisation applications will follow a separate verification process:

`Application → Admin Review → Verified / Rejected`

These workflows are part of the platform's design and will be implemented progressively.

## 🤖 Future AI Systems

Astrobase's long-term roadmap includes three distinct AI systems:

- **Astrobase AI:** Personalised guidance and discovery across the platform.
- **Chatbot AI:** Quick answers about Astrobase and general science or space-related questions.
- **University Advisor AI:** Guidance for exploring universities and academic programmes based on a student's interests and preferences.

These systems are planned features and are not presented as completed functionality.

## 🛠️ Technology Stack

The project uses or is being developed around the following technologies:

- **Python** for backend programming.
- **Flask** for web application routing and backend functionality.
- **MySQL** for structured data storage.
- **HTML** for page structure.
- **CSS** for styling and responsive layouts.
- **JavaScript** for frontend interactions.
- **mysql-connector-python** for Python–MySQL connectivity.
- **python-dotenv** for environment-based configuration.

The frontend, backend, and database are intended to work together as the platform develops.

## 👨‍🚀 Development & Contributions

Astrobase is a personal project developed by **Akil**, with AI assistance from ChatGPT.

### My contributions

I lead the project and make the decisions that shape Astrobase's direction and functionality. My work includes:

- Defining the project's purpose, goals, and long-term vision.
- Designing the platform's architecture, account roles, and content workflows.
- Building and refining the website's HTML and CSS.
- Working on the frontend interface and JavaScript interactions.
- Developing the Python and Flask backend.
- Planning database structures and MySQL integration.
- Testing features, identifying issues, and refining the user experience.
- Deciding which features to implement and prioritising future development.

### AI assistance

ChatGPT has assisted during development by:

- Explaining programming concepts and technical decisions.
- Suggesting and generating code for selected features.
- Helping debug errors and troubleshoot implementation issues.
- Recommending interface and CSS improvements.
- Assisting with architecture planning and documentation.
- Helping organise the project roadmap.

AI-generated suggestions are reviewed and adapted as part of the development process. The project direction, feature decisions, testing, and final implementation choices remain under my responsibility.

This distinction reflects the collaborative nature of the development process without presenting AI-assisted work as exclusively human-written.

## 🚀 Development Roadmap

The next stages of development include:

- Completing and refining the MySQL database architecture.
- Developing backend routes and database integration.
- Implementing and strengthening authentication and role-based permissions.
- Connecting website sections to real database records.
- Developing student, organisation, and admin dashboards.
- Expanding content moderation and management workflows.
- Implementing notification and audit systems.
- Developing the three planned AI systems.
- Exploring community functionality in a future version.

Planned features will be marked as such until they are implemented and tested.

## 🔒 Configuration & Security

Configuration and database credentials should be stored in environment variables rather than hardcoded into the source code.

A local `.env` file should not be committed to the repository. A `.env.example` file can be provided with placeholder values to document the required configuration.

Authentication, permissions, database security, and deployment practices will continue to be developed as Astrobase moves toward a more complete platform.

## 🌠 Project Vision

Astrobase is more than a directory of links. Its long-term goal is to help students navigate the many possible routes into astronomy, astrophysics, physics, and space science.

By bringing opportunities, educational resources, universities, and future guidance tools together, Astrobase aims to make exploring these fields more accessible.

**Built step by step, with curiosity, code, and a long-term vision for space science.**

---

*Developed by Akil, with AI assistance from ChatGPT.*
