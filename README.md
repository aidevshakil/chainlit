# 🚀 Chainlit Conversational AI & Gemini Image Generator

A conversational AI application built using **Chainlit** and **Google Gemini API** (`google-genai` SDK), featuring real-time chat streaming, AI image generation with **Imagen 3**, interactive action buttons, and visual step indicators.

---

## 🎯 Task Objectives & Decorator Overview

This application showcases the core architecture of Chainlit, specifically how **Python Decorators (`@`)** create an event-driven conversational web UI:

1. **`@cl.on_chat_start`**: 
   - Fires once when a user opens the chat UI session.
   - Used for setting up the Gemini client, initializing session variables (`cl.user_session`), and rendering the welcome message & quick action buttons.

2. **`@cl.on_message`**: 
   - Fires every time a user submits a message in the chat input.
   - Routes request between streaming conversational text (`gemini-2.5-flash`) and image generation (`imagen-3.0-generate-002`).

3. **`@cl.action_callback`**: 
   - Handles clicks on custom UI buttons (`cl.Action`).
   - Enables interactive elements like preset prompts and aspect-ratio toggles.

4. **`async with cl.step`**: 
   - Context manager for visually rendering workflow steps, tool execution, or long-running tasks in the UI.

---

## 🛠️ Step-by-Step Setup Guide

### 1. Prerequisites
- Python 3.10 or higher.
- A free **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Install Dependencies
In your terminal, navigate to this project folder and run:
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the root directory (or copy `.env.example`):
```bash
cp .env.example .env
```
Open `.env` and insert your Gemini API Key:
```env
GEMINI_API_KEY=AIzaSy...your_actual_key_here
```

### 4. Launch the Chainlit App
Run Chainlit with auto-reload (`-w`):
```bash
chainlit run app.py -w
```
Chainlit will automatically launch your default browser at: `http://localhost:8000`.

---

## 🎨 How to Use the App

- **Chat**: Type any prompt (e.g., *"Explain quantum computing in simple terms"*).
- **Generate Images**:
  - Type `/image <prompt>` (e.g., `/image a majestic lion wearing a golden crown in a lush forest`)
  - Or type prompts containing keywords like *"generate an image of..."* or *"draw..."*
  - Or click any of the preset buttons (**Cyberpunk City**, **AI Robot**, **Watercolor Sunset**).
- **Toggle Aspect Ratio**: Click the `📐 Aspect Ratio` button to switch between `1:1` square images and `16:9` widescreen images.

---

## 📁 Repository Structure
```
chainlit/
├── app.py                 # Main Chainlit application code
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── README.md              # Project setup & documentation
└── STREAMLIT_VS_CHAINLIT.md # Assignment writeup comparing Streamlit & Chainlit
```
