run:
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8002

c:
	podman build -t pdf2md . && podman run -d -p 8010:8010 --replace --name pdf2md pdf2md

