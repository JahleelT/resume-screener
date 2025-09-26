[![Unified App CI/CD](https://github.com/JahleelT/jahleelt-resume-screener/actions/workflows/app.yml/badge.svg)](https://github.com/JahleelT/jahleelt-resume-screener/actions/workflows/app.yml)

# Resume Screener

*** ⚠️ This project is being completely reworked and continued by [Jahleel](https;github.com/JahleelT) ⚠️ ***

## Quick Note
- This project was originally a group project, which can be found [here](https://github.com/software-students-spring2025/5-final-finalone), but because I have completely overhauled the backend (and currently working on the frontend), their names have been removed. The original proof-of-concept project will remain at the aforementioned link.

## Current Version
- ***Frontend:***
  - **TypeScript:** Enforces type-safety and stronger development than plain JS
  - **React:** Creates a rich and interactive UI for an enhanced UX.
  - **Flask-CORS:** Just for routing
  - 
  
- ***Backend:***
  - **Python:** Base language for the backend to handle endpoints, JWT auth, and orchestration of AI workflows, as well as both database interactions.
  - **Flask:** Framework used to build the API.
  - **LangChain:** Used to orchestrate OpenAI with various APIs
  - **OpenAI:** Cloud-based API to access GPT 4o Mini
  - **Vector Database (Pinecone):** Used for embedding the unstructured data (resume and job descriptions), enabling efficient similarity search and retrieval, allowing the LLM to analyze and compare content more efficiently.
  - **SQLAlchemy:** Pythonic SQL for object relational mapping (between User, Resume, and Analysis types)
  - **Flask-JWT-Extended:** Managing JWT auth

## Former Version
- An AI-powered application that compares your resume against a job posting and provides actionable feedback. Built with Flask, MongoDB, Playwright, and OpenAI's API. All logic now lives in a unified backend structure.

## Table of Contents

- [Resume Screener](#resume-screener)
  - [Quick Note](#quick-note)
  - [Current Version](#current-version)
  - [Former Version](#former-version)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Setup \& Run Locally](#setup--run-locally)
  - [Docker Compose](#docker-compose)
  - [Running Tests](#running-tests)
- [For app.py](#for-apppy)
  - [Container Images](#container-images)
  - [Deployment](#deployment)
  - [License](#license)

## Prerequisites

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- [Python 3.10+ ](https://www.python.org/downloads/)
- [Node.js 18.20+]()
- [PostgreSQL]()
- [OpenAI API]()
- [Pinecone API]()

## Environment Variables

1. Create a `.env` file in the `app/` directory based on the provided `.env.example`.
2. Include the following variables:


```env
MONGO_URI = mongodb://mongo:27017/resume_db
SECRET_KEY = your_secret_key
OPENAI_API_KEY = sk-xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

1. After copying, rename to `.env` and replace dummy values, including the OpenAI Key, with your own.

## Setup & Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/JahleelT/jahleelt-resume-screener.git
   cd jahleelt-resume-screener
   ```
2. Copy `env.example` to `.env` in `app/`, then update values.
3. Build and start services with Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. Visit `http://localhost:5050` to access the Web App.

## Docker Compose

The `docker-compose.yml` file defines:

- **mongo**: MongoDB service on port 27017
- **app**: Unified on port 5050

## Running Tests
 
*** ⚠️ Tests are currently on hold until further notice as I migrate the repository from two subsystems to one unified system ⚠️ ***

```bash
# For app.py
cd app
pytest --disable-warnings -q


## Container Images

- [gbs4189/web-app](https://hub.docker.com/r/gbs4189/web-app)
- [gbs4189/ml-client](https://hub.docker.com/r/gbs4189/ml-client)

## Deployment

We deploy to DigitalOcean via GitHub Actions. Configuration is defined in `spec.yaml`. Ensure your DigitalOcean App ID and required secrets are set in GitHub repository settings under **Secrets and variables**.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
