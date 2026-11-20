import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
# import uvicorn

app = FastAPI()

global_MEMORY = ""

clients = set()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SSE Notepad</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 20px auto;
        }

        textarea {
            width: 100%;
            height: 500px;
            font-size: 16px;
            padding: 10px;
            box-sizing: border-box;
        }
    </style>
</head>
<body>
    <h2>Live Notepad (SSE)</h2>

    <textarea id="editor"></textarea>

    <script>
const editor = document.getElementById("editor");

let suppressSend = false;
let timer;

fetch("/content")
    .then(r => r.text())
    .then(text => {
        editor.value = text;
    });

const events = new EventSource("/events");

events.onmessage = (event) => {
    const incoming = event.data;

    if (editor.value !== incoming) {
        const start = editor.selectionStart;
        const end = editor.selectionEnd;

        suppressSend = true;

        editor.value = incoming;

        editor.setSelectionRange(
            Math.min(start, incoming.length),
            Math.min(end, incoming.length)
        );

        suppressSend = false;
    }
};

editor.addEventListener("input", () => {
    if (suppressSend) return;

    clearTimeout(timer);

    timer = setTimeout(() => {
        fetch("/update", {
            method: "POST",
            headers: {
                "Content-Type": "text/plain"
            },
            body: editor.value
        });
    }, 150);
});
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML


@app.get("/content")
async def content():
    return global_MEMORY


@app.post("/update")
async def update(request: Request):
    text = (await request.body()).decode("utf-8")

    global global_MEMORY
    global_MEMORY = text

    for queue in list(clients):
        await queue.put(text)

    return {"status": "ok"}


@app.get("/events")
async def events():
    queue = asyncio.Queue()
    clients.add(queue)

    async def event_stream():
        try:
            yield f"data: {global_MEMORY.replace(chr(10), chr(10) + 'data: ')}\n\n"

            while True:
                data = await queue.get()

                data = data.replace("\r\n", "\n").replace("\r", "\n")

                for line in data.split("\n"):
                    yield f"data: {line}\n"

                yield "\n"

        finally:
            clients.discard(queue)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
# if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)