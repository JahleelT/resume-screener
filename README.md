[![Web App CI/CD](https://github.com/software-students-spring2025/5-final-finalone/actions/workflows/web-app.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-finalone/actions/workflows/web-app.yml)
[![ML Client CI/CD](https://github.com/software-students-spring2025/5-final-finalone/actions/workflows/ml-client.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-finalone/actions/workflows/ml-client.yml)

# Resume Screener

A two-subsystem application that leverages AI to compare your resume against a job posting and provides actionable feedback. The system consists of:

- **Web App**: A Flask-based front end where users can upload resumes and job links.
- **ML Client**: A background service that fetches job descriptions, interfaces with OpenAI, and updates analysis results in MongoDB.

## Teammates

- [Gilad](https://github.com/giladspitzer)
- [Andly](https://github.com/andy-612)
- [Jahleel](https://github.com/JahleelT)
- [Matthew](https://github.com/bruhcolate)

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Setup & Run Locally](#setup--run-locally)
4. [Docker Compose](#docker-compose)
5. [Running Tests](#running-tests)
6. [Container Images](#container-images)
7. [Deployment](#deployment)
8. [License](#license)

## Prerequisites

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- A [MongoDB](https://www.mongodb.com/) instance (local or Atlas)
- [OpenAI API Key](https://platform.openai.com/)

## Environment Variables

Create a `.env` file in each subsystem directory (`web-app/` and `ml-client/`) based on the provided `.env.example`:

```env
# web-app/.env.example and ml-client/.env.example
OPENAI_API_KEY=sk-xxxxxx
MONGO_URI=mongodb://localhost:27017/resume_db
SECRET_KEY=your_secret_key
ML_CLIENT_HOST=http://ml-client:5001   # For web-app only
```

After copying, rename to `.env` and replace dummy values with your own.

## Setup & Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/software-students-spring2025/5-final-finalone.git
   cd resume-screener
   ```
2. Copy `env.example` to `.env` in both `web-app/` and `ml-client/`, then update values.
3. Build and start services with Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. Visit `http://localhost:5050` to access the Web App.

## Docker Compose

The `docker-compose.yml` file defines:

- **mongo**: MongoDB service on port 27017
- **ml-client**: Background worker on port 5001
- **web-app**: Front-end on port 5050 (mapped from 5000)

## Running Tests

Each subsystem includes Pytest tests. To run them:

```bash
# For web-app
cd web-app
pytest --disable-warnings -q

# For ml-client
cd ml-client
pytest --disable-warnings -q
```

## Container Images

- [gbs4189/web-app](https://hub.docker.com/r/gbs4189/web-app)
- [gbs4189/ml-client](https://hub.docker.com/r/gbs4189/ml-client)

## Deployment

We deploy to DigitalOcean via GitHub Actions. Configuration is defined in `spec.yaml`. Ensure your DigitalOcean App ID and required secrets are set in GitHub repository settings under **Secrets and variables**.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

