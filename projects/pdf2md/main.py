from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymupdf4llm
import tempfile
import os

app = FastAPI(title="PDF to Markdown API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    temp_path = None

    try:
        # Read uploaded PDF
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        # Save temporarily because pymupdf4llm accepts file paths
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        # Convert PDF to Markdown
        md_text = pymupdf4llm.to_markdown(temp_path)

        return {
            "filename": file.filename,
            "markdown": md_text
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF conversion failed: {str(e)}"
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await file.close()
