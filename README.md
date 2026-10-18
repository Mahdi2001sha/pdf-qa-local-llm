# PDF Q&A (typed PDFs)

Upload a typed PDF, ask questions, get answers from a local LLM.
Every question and answer is saved to a CSV, and every uploaded PDF is saved as a version.

## Run
1. Install **Python 3.10+** (tick "Add to PATH") and **Ollama** (https://ollama.com/download).
2. Double-click `Start.bat`.
   First run creates a virtual environment, installs packages and downloads the models
   (several GB), so it takes a while. The browser opens automatically.

## Folders
| Folder      | Purpose |
|-------------|---------|
| `models/`   | Local models (Ollama stores them here) |
| `logs/`     | `pdfs/` = saved version of each uploaded PDF, `qa_log.csv` = questions + answers |
| `frontend/` | Plain HTML / CSS / JS page |
| `backend/`  | Python (FastAPI). One file per task |

## Backend files
| File | Task |
|------|------|
| `config.py` | All settings (paths, model names, chunk size) |
| `pdf_loader.py` | Receive + validate the upload, save a versioned copy |
| `pdf_reader.py` | Extract text page by page (PyMuPDF) |
| `text_chunker.py` | Split text into overlapping chunks |
| `retriever.py` | Find the chunks relevant to the question |
| `llm_client.py` | Talk to the LLM (Ollama) |
| `qa_service.py` | Build the prompt and get the answer |
| `qa_logger.py` | Write the Q&A CSV |
| `main.py` | API + serves the frontend; connects all of the above |

## Notes
- Scanned (image-only) PDFs are rejected with a clear message. OCR can be added later as a new step.
- `Start.bat` runs its own Ollama on port 21434 (not the default 11434, which Windows can block). By default it reuses the models already installed in `%USERPROFILE%\.ollama\models`; see the top of `Start.bat` to store models in `models/` instead.
- Downloads need access to registry.ollama.ai (a VPN may be needed on some networks). Without `bge-m3` the app still works using keyword search.
- To use a smaller/faster model, change `LLM_MODEL` in `Start.bat` (e.g. `qwen2.5:3b`) and in `backend/config.py`.
