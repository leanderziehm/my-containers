from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil

app = FastAPI()

# Create files directory next to this Python script
UPLOAD_DIR = Path(__file__).parent / "uploadedfiles"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        # Prevent directory traversal attacks
        filename = Path(file.filename).name

        if not filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        file_path = UPLOAD_DIR / filename

        # Save uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": "File uploaded successfully",
            "filename": filename,
            "path": str(file_path)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()