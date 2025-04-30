<!-- # E Buddy: AI Chatbot Development and Integration Platform

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
 -->


<!-- Banner -->
<p align="center">
  <img src="docs/media/banner.png" alt="E-Buddy – AI Chatbot Platform" width="800"/>
</p>

<h1 align="center">🛍️  E-Buddy &nbsp;|&nbsp; 10-Minute AI Chatbots for E-commerce</h1>
<p align="center">
  <i>Turn your store into a 24 × 7 sales & support powerhouse – no code, no hassle.</i>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-blue.svg"/></a>
  <a href="https://github.com/our-org/e-buddy/actions"><img alt="CI" src="https://github.com/our-org/e-buddy/actions/workflows/ci.yml/badge.svg"/></a>
  <a href="https://sonarcloud.io"><img alt="Quality Gate" src="https://sonarcloud.io/api/project_badges/measure?project=e-buddy&metric=alert_status"/></a>
  <a href="https://hub.docker.com/r/e-buddy/platform"><img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/e-buddy/platform?logo=docker"/></a>
</p>

<p align="center">
  <!-- <a href="#-live-demo">Live Demo</a> • -->
  <a href="#-key-features">Features</a> •
  <a href="#-business-value">Business Value</a> •
  <a href="#-pricing--plans">Pricing</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-api-documentation">API Docs</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 🎯 Project Overview
E-Buddy is a SaaS platform that lets merchants create production-ready, AI-powered chatbots in **< 10 minutes**.  
Simply drop in a URL (or upload docs), copy the embed script, and watch an intelligent assistant handle product questions, recommend items, capture leads, and drive conversions — all while learning automatically from your website.

## ✨ Key Features
| Category | Highlights |
|----------|------------|
| ⚡ Rapid Setup | 1. Paste your store URL → auto-crawls pages <br>2. Upload PDFs, TXT, CSV, etc. <br>3. Copy-paste JS widget — done! |
| 🧠 Smart Knowledge Base | Multimodal ingestion, chunking & vector storage (PDF, text, HTML). Scheduled **auto-re-crawl** keeps answers fresh. |
| 🗣️ Multimodal Chat | Text, **voice search**, and **image-based product lookup** out of the box. |
| 🛒 Product Recommendations | Real-time suggestions that increase AOV and cross-sell opportunities. |
| 🎯 Lead Capture | Collect name, email, phone (fully configurable). Push leads to CRM via webhooks. |
| 📊 Conversion Analytics | Track total chats, crawled pages, leads, and **conversion rate** (anonymous visitor → order). |
| 🔄 Model Flexibility | Gemini 2, GPT-4, Claude 3, DeepSeek Coder, and more. Switch anytime. |
| 🖼️ Fully Brandable Widget | Colors, avatar, greetings, fallback messages, lead-form fields, button shapes… everything. |
| 🔔 Zero-Code Integrations | Stripe for billing, Google Tag Manager, and Webhooks for events. |
| ☁️ Scales With You | Serverless workers, sharded MongoDB, horizontal FastAPI workers. |

---

## 💡 Business Value

| Pain Point | How E-Buddy Helps | Impact |
|------------|------------------|--------|
| 24/7 Support Costs | AI handles 80 %+ of repetitive queries | ↓ Support tickets • ↓ Payroll |
| Cart Abandonment | Proactive product suggestions & FAQ answers | ↑ Checkout rate |
| Low Conversion on Mobile | Voice & image search for faster discovery | ↑ Mobile revenue |
| Anonymous Visitors | Built-in lead forms | Growth of email/SMS lists |
| Out-of-Date FAQs | Scheduled crawl + doc sync | Always accurate info |
| Dev Bandwidth | 10-minute, copy-paste deployment | No engineering backlog |

<!-- > Result: **+13 % average sales uplift** and **-46 % support workload** across pilot stores (see `docs/case-studies.md`). -->

---

## 💵 Pricing & Plans

| Plan | Monthly | Chatbots | Messages / mo | Training Chars | Models | Support |
|------|---------|----------|---------------|----------------|--------|---------|
| Free | $0 | 1 | 100 | 10 k | Gemini-Flash | Community |
| Starter | $19 | 3 | 3 k | 100 k | + GPT-3.5 | Email |
| Pro | $49 | 10 | 10 k | 500 k | + GPT-4, Claude 3 | Priority Email/Chat |
| Enterprise | $129 | Unlimited | Unlimited | Unlimited | All models | Dedicated AM |

➡️ Need more? Purchase **Add-Ons** straight from the dashboard (extra bots, message packs). Billing is handled via Stripe Checkout and webhooks.  
See `docs/pricing.md` for full details.

---

---

## ⚙️ Local Installation & Project Structure

### 1. Prerequisites  

| Purpose            | Tool / Version | Notes |
|--------------------|----------------|-------|
| Python runtime     | **Python 3.10 +** | Tested on 3.11 |
| JavaScript runtime | **Node 18 +**  | LTS recommended |
| Package managers   | `pip`, `npm` / `pnpm` / `yarn` | We use **pnpm** in examples |
| Database           | **MongoDB Atlas** | Free tier works fine. Create a cluster & grab the connection string |
| Misc. CLI          | `git`, `curl` (for testing) | — |

> You _don’t_ need MongoDB installed locally if you use Atlas.

---

### 2. Backend Setup (FastAPI)

1. Clone & enter the repo  
```bash
git clone https://github.com/Learnathon-By-Geeky-Solutions/tyrocoders.git
cd backend
```

2. Create & activate a virtual-env  
```bash
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
```

3. Install dependencies  
```bash
pip install -r requirements.txt
```

4. Environment variables  
```bash
cp .env.example .env
```
Create a  `.env` file under backend directory. Here is a sample: 
```
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.xxxxxx.mongodb.net/ebuddy
JWT_SECRET=ReplaceMe
STRIPE_KEY=sk_test_*******
OPENAI_KEY=sk-*******
GEMINI_KEY=*******
```
> See the settings class in app/core/config.py to see all the variales to be placed in the  `.env` file

5. Run the server 
```bash
cd app
uvicorn app.main:app             # first time run
uvicorn app.main:app --reload    # auto reloading for developemnt 
```
Access:
- **Swagger UI:** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 3. Folder Structure (high-level)

```
e-buddy/
├─ backend/
│  ├─ app/
│  │  ├─ api/             # REST endpoints
│  │  ├─ core/            # settings / auth / config
│  │  ├─ services/        # business logic
│  │  ├─ crud/            # db logic
│  │  ├─ utils/           # utility functions
│  │  ├─ procssing/       # vector embeddings, model processing, llm response
│  │  ├─ training/        # chatbot training, scrapping, knowledgebase from url
│  │  └─ main.py
│  ├─ tests/
│  ├─ scripts/
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ app/             # Next.js 14 “/app”
│  │  ├─ components/
│  │  └─ styles/
│  └─ package.json
└─ README.md
```

---

### 4. Frontend Setup (Next.js 14)

```bash
cd ../frontend
pnpm i              # or npm install / yarn
pnpm dev            # or npm run dev
# → http://localhost:3000
```

Fill `frontend/.env` (copy from `.env.example`) so the UI can reach the API:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
STRIPE_PUBLISHABLE_KEY=pk_test_*******
```

Hot-reload is enabled.

---

### 5. (Advanced) Dockerising the Project

We do not ship container files yet; the steps below create them from scratch so you can run **frontend + backend** in one command.

#### 5.1 Create `backend/Dockerfile`

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Install OS deps
RUN apt-get update && apt-get install -y build-essential

# Copy app
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# Expose & run
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 5.2 Create `frontend/Dockerfile`

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /web
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN npm i -g pnpm && pnpm i --frozen-lockfile
COPY frontend/ .
RUN pnpm build                   # generates .next

ENV PORT=3000
EXPOSE 3000
CMD ["pnpm", "start"]
```

#### 5.3 Create a root-level `docker-compose.yml`

```yaml
version: "3.9"
services:
  api:
    build: ./backend
    env_file: ./backend/.env
    ports:
      - "8000:8000"
  web:
    build: ./frontend
    env_file: ./frontend/.env
    depends_on:
      - api
    ports:
      - "3000:3000"
```

> MongoDB Atlas is cloud-hosted, so no local container is required. Your connection string in `backend/.env` should whitelist the Docker host’s IP or allow `0.0.0.0/0` while testing.

#### 5.4 Build & Run

```bash
docker compose build       # first time / when Dockerfiles change
docker compose up          # starts api + web
```

URLs  
• Frontend – http://localhost:3000  
• Swagger – http://localhost:8000/api/docs  

Stop with `docker compose down`.

---

### 6. Common Pitfalls

| Issue | Resolution |
|-------|------------|
| **Cannot connect to MongoDB Atlas** | Whitelist your current IP in Atlas → Network Access. |
| **CORS errors in browser** | Add `http://localhost:3000` to `ALLOWED_ORIGINS` in `backend/.env`. |
| **Docker: port already in use** | Change `ports` mapping in `docker-compose.yml`. |
| **Stripe webhook “No such application”** | Run `stripe login && stripe listen --forward-to localhost:8000/api/webhooks/stripe`. |

More fixes live in `docs/troubleshooting.md`.

You are now ready to hack on **E-Buddy** locally, or spin it up in containers for staging/production. Happy building! 🚀

Full reference & code snippets → `docs/api.md`.

---

## 🔍 Screenshots

<table>
<tr>
  <td align="center"><img src="docs/media/dashboard.png"  alt="Dashboard" width="300"/></td>
  <td align="center"><img src="docs/media/bot.png"     alt="Embeddable Widget" width="300"/></td>
  <td align="center"><img src="docs/media/analytics.png"  alt="Analytics" width="300"/></td>
</tr>
<tr>
  <td>Dashboard</td><td>Bot Creation</td><td>Conversion Analytics</td>
</tr>
</table>

More visuals → `docs/gallery.md`

---

## 🛠 Development Guidelines
• Backend follows **PEP 8**, is type-hinted, and linted by Ruff.  
• Frontend uses ESLint + Prettier (Airbnb config).  
• Conventional Commits apply (`feat:`, `fix:`…).  
• Unit tests: `pytest` & `vitest`. Coverage > 90 %.

Git branching: **GitFlow** (`main`, `develop`, `feature/*`, `hotfix/*`).

---

## 🤝 Contributing
We ♥ community input!  
1. Fork the repo & create a feature branch.  
2. Follow the [Contribution Guide](CONTRIBUTING.md).  
3. Open a pull request – we’ll review ASAP.  

Need help? Open an issue or join our Discord (`docs/community.md`).

---

## 📚 Resources
• Product Whitepaper – `docs/whitepaper.pdf`  
• Case Studies – `docs/case-studies.md`  
• Roadmap – `docs/roadmap.md`  

---

## 👨‍💻 Core Team

| Role | Name | GitHub |
|------|------|--------|
| Team Lead | **Mohtasim Hossain** | @mohtasim-tyro |
| Backend | **Fahim Sadik Rashad** | @fahim-rashad |
| Frontend | **Tanvir Hossen Shishir** | @tanvir-shishir |
| Mentor | **Minhazul Hasan** | @minhaz-mentor |

---

## 📄 License
Distributed under the **MIT License** – see [`LICENSE`](LICENSE) for details.

<p align="center"><sub>Made with ❤️ by Tyrocoders • © 2025</sub></p>