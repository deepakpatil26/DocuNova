# DocuNova 🚀

### Intelligent RAG-Powered Knowledge Assistant

DocuNova is a high-performance, enterprise-ready RAG (Retrieval-Augmented Generation) assistant that transforms your static documents into an interactive knowledge base. Ask questions, get grounded answers with citations, and manage your usage with a sleek, modern interface.

---

## ✨ Features

- **🎯 Precision RAG**: Accurate answers derived directly from your documents using Llama 3.3 (Groq).
- **📝 Source Citations**: Every claim is backed by a citation from the uploaded documents.
- **📁 Multi-Doc Workspace**: Query multiple documents simultaneously with semantic understanding.
- **🔐 Secure Auth**: Robust authentication via Firebase & Google OAuth for isolated data.
- **📊 Token Quotas**: Integrated token tracking with a professional usage dashboard.
- **🛡️ Enterprise Rate Limiting**: Secured endpoints with tiered usage controls.
- **🌓 Claude-style UI**: Minimalist, premium design with full Dark Mode support and smooth micro-animations.

---

## 🖼️ Screenshots

|              Light Mode Workspace               |              Dark Mode Workspace              |
| :---------------------------------------------: | :-------------------------------------------: |
| ![Light Mode](./screenshots/HomePage-Light.png) | ![Dark Mode](./screenshots/HomePage-Dark.png) |

|           Document Library            |            Interactive Chat            |
| :-----------------------------------: | :------------------------------------: |
| ![Library](./screenshots/Library.png) | ![Chat](./screenshots/Recent-Chat.png) |

---

## 🌐 Deployment

DocuNova is currently deployed and live at:
**[👉 View Live Demo](https://docunova.example.com)** _(Replace this with your actual URL)_

### Backend Infrastructure

- **API**: FastAPI hosted on [Your Provider]
- **Vector DB**: Qdrant Cloud
- **Auth**: Firebase

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python), SQLAlchemy, Slowapi (Rate Limiting).
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons.
- **Vector Engine**: Qdrant (High-performance vector similarity search).
- **LLM**: Groq Llama 3.3 (Blazing fast inference).
- **Auth/Storage**: Firebase Authentication & SQL-based metadata management.

---

## 🚀 Quick Start (Development)

### 1. Requirements

- Python 3.10+
- Node.js 18+
- Qdrant (Docker or Cloud instance)

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
# Configure .env with GROQ_API_KEY and QDRANT_URL
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 📄 License

MIT © 2026 DocuNova Team
