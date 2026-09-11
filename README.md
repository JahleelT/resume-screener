# Resume Screener

Resume Screener is an AI-assisted resume analysis platform designed to compare candidate resumes against job descriptions using semantic retrieval and large language models.

The project was built to explore document ingestion pipelines, vector search, retrieval-augmented analysis, and full-stack application architecture.

---

## Project Status

This project is no longer under active development.

The primary objective of the project was to explore and implement an AI-powered resume analysis workflow using modern retrieval and LLM tooling. The backend architecture, document-processing pipeline, vector retrieval workflow, and analysis logic were completed as part of those goals.

The repository is maintained as a portfolio project and reference implementation.

---

## Background

This repository originated as a university group project. The original proof-of-concept version can be found here:

https://github.com/software-students-spring2025/5-final-finalone

Following completion of the course project, the backend architecture was extensively redesigned and expanded to explore more advanced document processing, vector retrieval, and AI-assisted analysis workflows.

---

## Features

- User registration and authentication
- Resume upload and storage
- Resume management APIs
- Job description ingestion from URLs
- Resume and job description chunking
- Embedding generation and vector retrieval
- AI-powered resume analysis
- Analysis history tracking
- RESTful API architecture

---

## Tech Stack

### Backend

- Python
- Flask
- SQLAlchemy
- PostgreSQL
- OpenAI API
- LangChain
- Pinecone
- Flask-JWT-Extended
- bcrypt

### Frontend

- React
- TypeScript
- Axios
- React Router

### Infrastructure

- Docker
- Docker Compose
- GitHub Actions

---

## Architecture

```text
Resume
   ↓
Document Loader
   ↓
Text Chunking
   ↓
Embedding Generation
   ↓
Pinecone Vector Store
   ↓
Retrieval Pipeline
   ↓
OpenAI Analysis
   ↓
Stored Analysis Results
```

---

## Key Areas of Exploration

This project focused on:

- REST API design
- Authentication and user management
- Database modeling and CRUD operations
- Retrieval-augmented generation (RAG) workflows
- Vector search systems
- Semantic document analysis
- Document processing pipelines
- Full-stack application architecture
- AI application development

---

## Repository Structure

```text
backend/
├── routes.py
├── db/
├── chains/
├── embeddings/
├── loaders/
├── schemas/
└── utils/

frontend/
├── src/
├── public/
└── configuration files

archives/
└── original project materials
```

---

## Technologies Explored

- Resume parsing and ingestion
- Job description extraction
- Embedding generation
- Semantic search
- Vector databases
- JWT authentication
- PostgreSQL data modeling
- AI-assisted content analysis
- Containerized development workflows

---

## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.