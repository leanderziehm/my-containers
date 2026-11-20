run:
	uv run uvicorn main:app --host 0.0.0.0 

c bc build_container:
	podman build -t container1 . && podman run --rm -it --name container1 -p 8002:8000 container1
