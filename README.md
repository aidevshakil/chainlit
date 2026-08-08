# ⚡ Chainlit FLUX.1-schnell Image Studio

A modern web application built using **Chainlit** and **Hugging Face Inference API** powered by **`black-forest-labs/FLUX.1-schnell`**, featuring high-speed AI image generation, interactive action buttons, aspect ratio toggles, and visual step indicators.

---

## 🛠️ Step-by-Step Setup Guide

### 1. Prerequisites
- Python 3.10 or higher.
- A free **Hugging Face User Access Token** (`HF_TOKEN`) from [Hugging Face Settings](https://huggingface.co/settings/tokens).

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
Open `.env` and insert your Hugging Face API token:
```env
HF_TOKEN=hf_your_actual_token_here
```

### 4. Launch the Chainlit App
Run Chainlit with auto-reload (`-w`):
```bash
chainlit run app.py -w
```
Chainlit will automatically launch your default browser at: `http://localhost:8000`.

---

## 🎨 How to Use the App

- **Generate Images**:
  - Type any prompt (e.g., *"A majestic lion wearing a golden crown in a lush forest"*)
  - Or type `/image <prompt>` or `/draw <prompt>`
  - Or click any preset button (**Cyberpunk City**, **3D AI Robot**, **Watercolor Sunset**, **Cosmic Nebula**).
- **Toggle Aspect Ratio**: Click the `📐 Aspect Ratio` button to switch between `1:1` square images and `16:9` widescreen images.

---

## 📁 Repository Structure
```
chainlit/
├── app.py                 # Main Chainlit application code
├── requirements.txt       # Python dependencies (chainlit, huggingface_hub, pillow, python-dotenv)
├── services/
│   └── flux.py            # FLUX.1-schnell image generation service wrapper
├── .env.example           # Environment template
├── chainlit.md            # App landing UI banner
├── public/                # Custom CSS styling
│   └── custom.css
└── README.md              # Project setup & documentation
```
