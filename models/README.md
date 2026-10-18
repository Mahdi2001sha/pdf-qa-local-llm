# models/

This folder holds the local AI models.

Optional: by default `Start.bat` reuses the normal Ollama models folder. To keep models here instead,
copy the `blobs` and `manifests` folders into this folder and change `OLLAMA_MODELS` in `Start.bat`.
Models used:

| Role        | Default model | Change it in             |
|-------------|---------------|--------------------------|
| Answers     | `qwen2.5:7b`  | `Start.bat` + `backend/config.py` |
| Embeddings  | `bge-m3`      | `Start.bat` + `backend/config.py` |

Do not delete the `blobs` / `manifests` folders that Ollama creates here.
