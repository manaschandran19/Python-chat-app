# Chat Application: Specifications and Architecture

This document provides an overview of the Python-based real-time chat application, detailing its features, architecture, and how it works.

## 1. Core Specifications

- **Real-Time Communication:** Messages are sent and received instantly without needing to refresh the page.
- **Public & Private Messaging:** Users can broadcast messages to everyone in the chat room or send private messages to specific users.
- **User Identification:** Each connected user is identified by a unique username.
- **Web-Based Interface:** The application is accessed through a web browser.

## 2. Technologies Used

- **Backend:**
    - **Python:** The core programming language.
    - **FastAPI:** A modern, high-performance web framework used to handle HTTP requests and WebSocket connections.
    - **Uvicorn:** An ASGI (Asynchronous Server Gateway Interface) server that runs the FastAPI application.
    - **WebSockets:** The technology that enables two-way, real-time communication between the client (browser) and the server.
- **Frontend:**
    - **HTML:** Provides the basic structure of the chat interface.
    - **CSS:** Styles the application for a clean, modern look.
    - **JavaScript:** Handles user interactions, WebSocket connections, and dynamic content updates.

## 3. Architecture

The application is divided into two main parts: a **FastAPI backend** (the server) and an **HTML/JavaScript frontend** (the client).

### Backend (`main.py`)

The backend is built around a central `ConnectionManager` class that tracks all active users.

#### Key Components:

1.  **FastAPI App (`app`)**:
    - The main instance of the FastAPI application.
    - It mounts a `/static` directory to serve CSS and JavaScript files directly.

2.  **`ConnectionManager` Class**:
    - This class is the heart of the chat's real-time functionality.
    - It uses a Python dictionary (`active_connections`) to store and manage all active WebSocket connections, mapping each `username` to their unique `WebSocket` object.
    - **`connect(username, websocket)`**: Accepts a new client connection and adds it to the dictionary.
    - **`disconnect(username)`**: Removes the client's connection when they leave the chat.
    - **`send_personal_message(message, username)`**: Looks up the recipient's username in the dictionary and sends them a message directly.
    - **`broadcast(message)`**: Iterates through all connections in the dictionary and sends a message to every connected client.

3.  **HTTP Endpoint (`GET /`)**:
    - When a user first navigates to the application's URL, this endpoint serves the `index.html` file, which contains the chat interface.

4.  **WebSocket Endpoint (`/ws/{username}`)**:
    - After the page loads, the frontend JavaScript opens a persistent WebSocket connection to this endpoint.
    - The server then enters a loop, continuously listening for messages from that specific client.
    - **Message Handling:**
        - It expects messages in a JSON format: `{"to": "recipient_username", "message": "your_message"}`.
        - If the `"to"` field is present, the server calls `send_personal_message` to deliver a private message. It also sends a confirmation echo back to the sender.
        - If the `"to"` field is missing, the server treats it as a public message and calls `broadcast`.
    - **Disconnection:** The server handles disconnections gracefully, ensuring the user is removed from the `ConnectionManager` and a "left the chat" message is broadcast to all users.

### Frontend (`index.html`, `main.js`)

The frontend provides the user interface and communicates with the backend.

1.  **User Interface (`index.html`)**:
    - A simple, card-based layout with a scrollable area for messages and an input field for typing.

2.  **Client-Side Logic (`main.js`)**:
    - **Connection:** Establishes and maintains the WebSocket connection with the `/ws/{username}` endpoint on the server.
    - **Sending Messages:** Captures text from the input field and sends it to the server over the WebSocket. The logic can be extended to create the JSON format for private messaging.
    - **Receiving Messages:** Listens for incoming messages from the server. When a message arrives, it dynamically creates a new element and appends it to the message display area.

## 4. How It Works (Data Flow)

1.  A user opens the application in their browser.
2.  The browser sends a `GET` request to the server, which returns the `index.html` page.
3.  The JavaScript on the page prompts the user for a username and establishes a WebSocket connection to the server's `/ws/{username}` endpoint.
4.  The server's `ConnectionManager` registers the new user.
5.  When the user types a message and hits "Send," the JavaScript sends the message text through the WebSocket.
6.  The server's WebSocket endpoint receives the text, determines if it's a private or broadcast message, and uses the `ConnectionManager` to distribute it to the correct recipient(s).
7.  The browsers of all receiving clients get the message through their WebSocket connections and display it in the chat window.
8.  When a user closes the browser tab, the WebSocket disconnects. The server detects this, removes the user from the `ConnectionManager`, and notifies the room that the user has left.
