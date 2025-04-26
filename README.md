# E Buddy: AI Chatbot Development and Integration Platform

## Tyrocoders Team

**Team Members:**
- Mohtasim Hossain (Team Leader)
- Fahim Sadik Rashad
- Tanvir Hossen Shishir

**Mentor:**
- Minhazul Hasan

---

## Table of Contents
1. [Project Description](#project-description)
2. [Key Features](#key-features)
3. [Backend Setup](#backend-setup)
   - [Prerequisites](#prerequisites)
   - [Environment Variables](#environment-variables)
   - [Installation](#installation)
   - [Running the Backend](#running-the-backend)
   - [Folder Structure](#folder-structure)
4. [Frontend Setup](#frontend-setup)
5. [Resources](#resources)
6. [Contributing](#contributing)
7. [License](#license)

---

## Project Description

**E Buddy** is an advanced AI-powered chatbot platform designed to help businesses and developers quickly create, train, and deploy custom chatbots using their own knowledge bases. Through a user-friendly interface and seamless API integrations, E Buddy enables organizations to automate customer support, streamline information retrieval, and enhance user engagement across various digital channels.

E Buddy leverages FastAPI for a robust backend, MongoDB for scalable data storage, and provides embeddable scripts for easy integration with your web platforms. With built-in authentication, subscription management, and extensible training modules, E Buddy delivers a complete solution for intelligent conversational applications.

---

## Key Features

- **Custom chatbot creation for multiple business domains.**
- **Seamless knowledge base integration with structured and unstructured data.**
- **Secure user authentication and flexible role management with JWT.**
- **Built-in subscription and add-on management for flexible user plans.**
- **Integration with various AI language models for advanced conversations.**
- **Embeddable JavaScript widgets for easy website integration.**
- **Comprehensive, versioned REST API for full platform access.**
- **Modular, developer-friendly backend and clear data schemas.**

---



---

## Backend Setup

The backend is built with **FastAPI** and uses **MongoDB** for data persistence.

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or Atlas)
- `pip` (Python package manager)

### Environment Variables

Create a `.env` file in the `backend` directory and define all required variables as per `app/core/config.py` (such as database URI, secret keys, etc.).

### Installation

1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Backend
To run the backend, use the following commands:

1. Navigate to the `app` folder:
   ```bash
   cd app
   ```

2. Start the FastAPI server:
   ```bash
   uvicorn main:app
   ```

3. For development with auto-reload:
   ```bash
   uvicorn main:app --reload
   ```

Access:
- **Swagger UI:** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Folder Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── __init__.py
│   ├── core/
│   ├── crud/
│   ├── db/
│   ├── exceptions/
│   ├── knowledge_bases/
│   ├── middlewares/
│   ├── processing/
│   ├── schemas/
│   ├── services/
│   ├── training/
│   ├── utils/
│   └── __init__.py
├── scripts/
├── .env
├── requirements.txt
└── README.md
```

---

Certainly! Here’s a clear and professional way to present your **Frontend Setup** section, communicating both the technology used (Next.js) and the current status of the repository:

---

## Frontend Setup

**Currently, the main branch of this repository does not contain the frontend codebase.**  
The frontend, developed using [Next.js](https://nextjs.org/) and Node.js, will be added soon. This approach is in place to ensure that SonarQube analysis runs exclusively on the backend code, preventing unnecessary issues during code quality evaluations.

Once the frontend is merged into the repository, setup instructions will be as follows:

### Prerequisites

- Node.js (v18 or higher recommended)
- npm or yarn

### Installation

```bash
cd frontend
npm install
```
_or, if using yarn:_
```bash
cd frontend
yarn install
```

### Running the Frontend

```bash
npm run dev
```
_or, with yarn:_
```bash
yarn dev
```

By default, the frontend will be available at [http://localhost:3000](http://localhost:3000).

**Please check back soon for the fully integrated frontend in this repository.**

---

---

## Resources

- [Comprehensive Project Documentation](docs/index.md)
- [Contribution Guidelines](CONTRIBUTING.md)

---

## Contributing

We welcome your contributions! Please review our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get started, coding styles, and our pull request process.

---

## License

Distributed under the [MIT License](LICENSE). See the `LICENSE` file for more information.

