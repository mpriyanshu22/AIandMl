# AI & ML Repository

A consolidated workspace repository containing artificial intelligence, generative AI, and machine learning projects and practice modules.

## Structure

```
AIandML/
├── AIALL/              # Generative AI, LLM applications, Agents, and RAG projects
│   ├── practice/       # LangGraph, RAG pipelines, Minicursor, Ollama, Vector search
│   ├── Practice-19-09-26/
│   ├── Practice-20-09-26/
│   └── (Standalone repositories tracked independently):
│       ├── cursor_vibe_talker/app/ -> mpriyanshu22/Vibe-talker
│       ├── Gen-Ai-practice/        -> mpriyanshu22/Full-Rag
│       └── minicursor/             -> mpriyanshu22/Minicursor
│
└── MLALL/              # Core Machine Learning concepts, libraries, and foundational exercises
    ├── day1/ ... day3/ # Foundational Python & environments
    ├── filesystem/
    ├── Logging/
    ├── Matplotlib/
    ├── Memorymanagement/
    ├── MultiThreading&Multiprocessing/
    ├── numpy/
    ├── pandas/
    ├── Seaborn/
    └── Sqlite/
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js (for web client modules where applicable)

### Setup
1. Clone the repository:
   ```bash
   git clone <YOUR_REPOSITORY_URL>
   cd AIandML
   ```

2. Create and activate a virtual environment for the subproject you want to run:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. Configure environment variables:
   - For subprojects requiring API keys, copy `.env.example` to `.env` and fill in your keys.

---
> **Security Note:** Sensitive files (`.env`, secrets, API keys) and virtual environments are ignored via `.gitignore` and should never be committed to Git.
