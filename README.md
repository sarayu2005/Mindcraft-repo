Here's a README for the MindCraft GitHub repo:

---

# 🧠 MindCraft

> An AI-driven, gamified platform for personalized Python programming education.


---

## 🚀 What is MindCraft?

MindCraft is a full-stack web application that transforms Python education from passive video-watching into an interactive, gamified journey. It combines **Reinforcement Learning-driven personalization**, **AI-assisted feedback**, and **game mechanics** to keep learners engaged from their first `print("Hello, World!")` to advanced DSA problems.

**Selected for KSCST SPP 2025–26 (49th series)** — government-funded under IISc Bangalore.

---

## ✨ Features

- **Adventure Skill Quest** — Diagnostic survey that uses K-means clustering to place users on a personalized learning roadmap (Beginner / Intermediate / Advanced)
- **Topic Maps** — Visual, node-based curriculum where every concept follows a Theory → Syntax → Quiz loop with XP gating
- **Escape Room** — 4-level narrative coding challenges that test logic in a low-stakes, story-driven environment
- **AI Coding Exam** — Timed DSA exam with an in-browser Python editor and Gemini-powered code review (efficiency, style, edge cases)
- **Debug Section** — Pre-broken code challenges that train analytical thinking and resilience
- **Gamification Engine** — XP, progress bars, and badges that reward every milestone
- **AI Feedback Portal** — Detailed performance analysis identifying weak areas and conceptual gaps

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, HTML5, CSS3 (Flexbox, CSS Variables) |
| Backend Gateway | Node.js + Express |
| Compiler Service | Python 3.8+, Flask |
| AI Integration | Google Gemini API |
| ML Clustering | Scikit-learn (K-means) |
| Database | SQLite |
| Auth | bcrypt, JWT |
| Notifications | Nodemailer / Gmail SMTP |

---

## 🏗 Architecture

MindCraft uses a **Hybrid Microservices (Polyglot) Architecture** with three decoupled tiers:

```
React Frontend (SPA)
       ↕
Node.js API Gateway  ←→  Gemini AI API
       ↕
Flask Compiler Microservice (sandboxed subprocess execution)
```

User code runs in isolated OS subprocesses with CPU/memory limits and ephemeral file management — no persistent storage of user scripts.

---

## ⚙️ Getting Started

### Prerequisites
- Node.js v16+
- Python 3.8+
- npm & pip

### Installation

```bash
# Clone the repo
git clone https://github.com/sarayu2005/mindcraft.git
cd mindcraft

# Install frontend & backend dependencies
npm install

# Install Python dependencies
pip install flask google-generativeai scikit-learn joblib bcrypt

# Set up environment variables
cp .env.example .env
# Add your GEMINI_API_KEY, JWT_SECRET, SMTP credentials
```

### Running Locally

```bash
# Start Node.js gateway
npm start

# Start Flask compiler service (separate terminal)
cd compiler
python app.py
```

Visit `http://localhost:3000`

---

## 📄 Publication

**MINDCRAFT: An AI-Driven Gamified Platform for Personalized Python Programming Education**
*IRE Journals, Vol. 9, Issue 6, Dec 2025, pp. 1056–1063*
DOI: [10.64388/IREV9I6-1712649](https://doi.org/10.64388/IREV9I6-1712649)

Also presented at **IEEE Conference** on Agentic AI systems.

---

## 👩‍💻 Author

**Sarayu Valteti** — [LinkedIn](https://linkedin.com/in/sarayu-valteti) · [GitHub](https://github.com/sarayu2005)

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.
