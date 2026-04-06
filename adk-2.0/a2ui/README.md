# A2UI Streaming Example

This folder contains the A2UI streaming example, isolated from other ADK 2.0 examples.

## Project Structure

- `a2ui_agent/`: The ADK agent server.
- `frontend/`: The React frontend application.
- `Makefile`: Helper commands to run the project.

## How to Run

To run the example, navigate to this directory and run the following commands:

### 1. Start the Agent Server
```bash
make run-agent
```
This will start the agent server on `http://localhost:8502`.

### 2. Start the Frontend
In a new terminal, run:
```bash
make run-frontend
```
This will start the Vite dev server on `http://localhost:5173`.

## Features

- **A2A Streaming**: Real-time communication between agent and frontend.
- **Dynamic UI**: Renders A2UI components based on agent responses.
- **Session Management**: Maintains session state across turns.
