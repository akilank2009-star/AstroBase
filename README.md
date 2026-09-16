# Astrobase

Astrobase is a platform designed to help students explore opportunities, resources, universities and pathways related to astronomy, astrophysics, physics and space science.

The goal of Astrobase is to bring useful information for students interested in space science into one place, making it easier to discover opportunities, learn through resources, explore universities and understand different pathways into the field.

## Why Astrobase?

Students interested in astronomy and space science often have to search across many different websites to find competitions, research programmes, internships, educational resources and university programmes.

Astrobase aims to make this process simpler by bringing these different types of information together into a single platform.

The universe is vast. There isn't just one path through it.

## Features

### Students

- Student registration and authentication
- Personal student profiles
- Explore opportunities
- Explore educational resources
- Explore universities and programmes
- Search and discovery features
- Save relevant opportunities and resources
- Personal reports and information
- Access to community features

### Organisations

- Organisation registration and application
- Organisation verification workflow
- Organisation profiles
- Organisation dashboard
- Submit resources
- Submit opportunities
- Manage submitted content
- Contribute university information
- Track organisation submissions

### Admin

- Admin authentication
- Organisation verification
- Review organisation applications
- Review submitted opportunities
- Review submitted resources
- Manage university information
- Edit submitted content
- Approve or reject submissions
- Archive content
- Content moderation and management

## Content Workflows

Astrobase uses structured workflows to help keep contributed content organised.

### Organisation Verification

Organisation applications follow a verification process:

`Application → Admin Review → Verified / Rejected`

### Content Submission

Content submitted by organisations can go through an approval process:

`Draft → Pending → Published → Expired / Closed → Archived`

This allows organisations to contribute information while keeping final publishing under administrative review.

## Main Sections

### Opportunities

A collection of opportunities related to astronomy, astrophysics, physics and space science, including competitions, internships, programmes, scholarships, research opportunities and other activities.

### Resources

Educational material intended to help students learn and explore different areas of space science.

### Universities

Information about universities and programmes relevant to students interested in physics, astronomy, astrophysics and related fields.

### Explore

A broader discovery area designed to help students explore different pathways and areas of interest rather than following a single predefined route.

### Community

A planned space for students and space enthusiasts to interact, share knowledge and build a wider community around space science.

## User Roles

Astrobase currently uses three primary roles:

| Role | Purpose |
| --- | --- |
| Student | Explore opportunities, resources, universities and personal features |
| Organisation | Contribute and manage approved content |
| Admin | Verify organisations and manage platform content |

Each account has one primary role, with access controlled through role-based permissions.

## Tech Stack

- Python
- Flask
- MySQL
- HTML
- CSS
- JavaScript
- mysql-connector-python
- python-dotenv

## Project Structure

```text
AstroBase
├── README.md
├── requirements.txt
└── Website
    ├── app.py
    ├── HTML
    │   ├── index.html
    │   ├── login.html
    │   ├── register.html
    │   ├── opportunities.html
    │   ├── resources.html
    │   ├── universities.html
    │   └── ...
    ├── Images
    ├── script.js
    ├── style.css
    └── astrobase_schema.sql