run:
	uv run uvicorn main:app --reload

req:
	uv pip freeze > requirements.txt

bc build_container:
	podman build -t container1 . && podman run --network=host --rm -it --name container1 -p 8900:8900 container1
