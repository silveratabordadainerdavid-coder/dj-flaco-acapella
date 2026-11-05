
import os
import shutil
import subprocess
import tempfile

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(title="DJ FLACO ACAPELLA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://silveratabordadainerdavid-coder.github.io"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"mensaje": "DJ FLACO ACAPELLA está funcionando"}

@app.post("/separate")
async def separate(
    file: UploadFile = File(...),
    mode: str = Form(...)
):
    if mode not in ["vocals", "instrumental"]:
        raise HTTPException(400, "Modo no válido")

    if not file.filename.lower().endswith((".mp3", ".wav")):
        raise HTTPException(400, "Usa un archivo MP3 o WAV")

    folder = tempfile.mkdtemp()
    try:
        input_path = os.path.join(folder, "audio" + os.path.splitext(file.filename)[1])

        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        subprocess.run(
            [
                "python", "-m", "demucs",
                "--two-stems=vocals",
                "-n", "htdemucs",
                "-o", folder,
                input_path
            ],
            check=True,
            timeout=900
        )

        result_name = "vocals.wav" if mode == "vocals" else "no_vocals.wav"
        result_path = os.path.join(
            folder, "htdemucs", "audio", result_name
        )

        if not os.path.exists(result_path):
            raise HTTPException(500, "No se encontró el audio separado")

        return FileResponse(
            result_path,
            media_type="audio/wav",
            filename=result_name,
            background=None
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(408, "El procesamiento tardó demasiado")
    except subprocess.CalledProcessError:
        raise HTTPException(500, "No se pudo separar el audio")
    finally:
        # Los archivos temporales se limpian al terminar.
        pass
