import sys
import threading
import queue
import builtins
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# Import your multiagent conversation function.
from services.chatbot.multiagent_assistant import initiate_chat

app = FastAPI()
templates = Jinja2Templates(directory="services/chatbot/api_test/templates")


# Global dictionaries to keep track of each session's input queue and WebSocket.
session_input_queues = {}
session_websockets = {}

# Global variable to hold the main event loop.
main_loop = None

def send_to_websocket(session_id: str, message: str):
    """
    Send a text message to the websocket associated with the given session_id.
    This function schedules the send_text coroutine on the main event loop.
    """
    websocket = session_websockets.get(session_id)
    if websocket and main_loop:
        asyncio.run_coroutine_threadsafe(websocket.send_text(message), main_loop)


class WebSocketStream:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.buffer = ""
        self.suppress_initial_output = True  # Still suppress early output

    def write(self, msg):
        if self.suppress_initial_output:
            return

        self.buffer += msg
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            if line.strip():
                # If the line contains the unwanted markers, skip sending it.
                if "Next speaker:" in line or "(to chat_manager):" in line:
                    continue
                # Otherwise, print to console and send to the WebSocket.
                sys.__stdout__.write(f"[stdout][{self.session_id}]: {line}\n")
                send_to_websocket(self.session_id, line)

    def flush(self):
        if not self.suppress_initial_output and self.buffer.strip():
            leftover = self.buffer.strip()
            if not ("Next speaker:" in leftover or "(to chat_manager):" in leftover):
                sys.__stdout__.write(f"[stdout][{self.session_id}]: {leftover}\n")
                send_to_websocket(self.session_id, leftover)
        self.buffer = ""
        sys.__stdout__.flush()


def custom_input(prompt=""):
    """
    Custom input function that sends a prompt via the WebSocket and waits for the user response.
    On the very first call, it sends a custom greeting and disables early output suppression.
    """
    session_id = threading.current_thread().session_id
    # Retrieve the stream instance from the current thread.
    ws_stream = getattr(threading.current_thread(), "ws_stream", None)
    if ws_stream and ws_stream.suppress_initial_output:
        # Disable suppression and send a custom greeting.
        ws_stream.suppress_initial_output = False
        send_to_websocket(session_id, "Hello, how may I help you?")
    sys.__stdout__.write(f"[custom_input][{session_id}]: Sending prompt: {prompt.strip()}\n")
    send_to_websocket(session_id, prompt)
    # Block until a response is received from the client.
    user_response = session_input_queues[session_id].get()
    sys.__stdout__.write(f"[custom_input][{session_id}]: Received response: {user_response}\n")
    return user_response

def run_conversation(session_id: str):
    """
    Runs the multiagent conversation for a given session.
    Overrides stdout and input() so that output is sent via WebSocket
    and input is received from the client.
    """
    sys.__stdout__.write(f"[run_conversation]: Starting conversation for session {session_id}\n")
    # Create an input queue for this session.
    session_input_queues[session_id] = queue.Queue()
    threading.current_thread().session_id = session_id

    # Create our custom stream and attach it to the thread for later access.
    ws_stream = WebSocketStream(session_id)
    threading.current_thread().ws_stream = ws_stream

    # Redirect stdout and override input.
    original_stdout = sys.stdout
    sys.stdout = ws_stream
    original_input = builtins.input
    builtins.input = custom_input

    try:
        # Start the multiagent conversation (blocking call).
        initiate_chat()
    except Exception as e:
        sys.__stdout__.write(f"[run_conversation][{session_id}]: Error: {str(e)}\n")
        send_to_websocket(session_id, f"Error: {str(e)}")
    finally:
        # Restore original stdout and input.
        builtins.input = original_input
        sys.stdout = original_stdout
        sys.__stdout__.write(f"[run_conversation][{session_id}]: Conversation ended.\n")
        send_to_websocket(session_id, "Conversation ended.")
        # Clean up session data.
        session_input_queues.pop(session_id, None)
        session_websockets.pop(session_id, None)


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    """
    Serves the index.html page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for a given session.
    The conversation starts automatically when a client connects.
    """
    await websocket.accept()
    global main_loop
    main_loop = asyncio.get_running_loop()  # Set the event loop here.
    session_websockets[session_id] = websocket

    # Automatically start the conversation in a new thread.
    threading.Thread(target=run_conversation, args=(session_id,), daemon=True).start()


    try:
        while True:
            data = await websocket.receive_text()
            # Put client input into the corresponding input queue.
            if session_id in session_input_queues:
                session_input_queues[session_id].put(data)
            else:
                sys.__stdout__.write(f"[websocket] No input queue for session {session_id}\n")
    except WebSocketDisconnect:
        sys.__stdout__.write(f"[websocket] Client disconnected: {session_id}\n")
        session_websockets.pop(session_id, None)

if __name__ == "__main__":
    uvicorn.run(
        "services.chatbot.api_test.app:app",
        host="127.0.0.1",
        port=5000,
        reload=True
    )


