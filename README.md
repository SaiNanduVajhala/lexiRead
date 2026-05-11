# 📖 lexiRead: The Dyslexia-Friendly Reading Companion

<div align="center">
  <em>An AI-powered reading companion designed to instantly transform complex, dense texts into clear, digestible, and visually stress-free formats using Google Gemma 4.</em>
</div>

<br/>

> [!CAUTION]
> **Important Prerequisites & Notes:**
> - **Google Gemini API Key:** You MUST have a valid Google Gemini API key to use the AI features. The app will gracefully fall back to mock data if no key is provided.
> - **Privacy First:** Your API key is stored locally in your browser's `localStorage` and is only transmitted in the request header to the backend. It is **never** saved on the server or logged.
> - **Python 3.10+:** Ensure you are running Python 3.10 or higher for the FastAPI backend to function correctly.

---

## 🎯 Why lexiRead?

The modern web is full of walls of text, complex jargon, and visually dense layouts. For neurodivergent readers (Dyslexia, ADHD, Irlen Syndrome), this creates a massive barrier to information. 

**lexiRead solves this through "Digital Equity."** It doesn't just summarize text; it reconstructs it using cognitive load-reducing patterns, bionic typography, and interactive Socratic learning.

---

## 🚀 Quick Start

Get the application running locally in under 2 minutes.

### 1. Installation

```bash
# Enter the backend directory
cd backend

# Install the Python dependencies
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# Start the FastAPI server
python -m uvicorn main:app --reload --port 8000
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

### 3. Add Your API Key
1. Click the **Settings** icon (⚙️) in the top navigation bar.
2. Scroll down to **API Configuration**.
3. Paste your Google Gemini API Key and click **Save**.

---

## 🧠 AI-Powered Features (Gemma 4)

lexiRead leverages the reasoning capabilities of **Gemma 4** to make text cognitively accessible.

### 📝 Smart Simplification
Instead of one massive summary, lexiRead breaks text into manageable chunks:
- **Summary:** A simple 2-3 sentence overview.
- **Key Facts:** Core, actionable bullet points.
- **Relatable Analogy:** Generates a real-world analogy to map abstract concepts to everyday understanding.
- **Custom Prompts:** Set permanent instructions in Settings (e.g., *"Keep sentences under 10 words"*).

### 💬 Socratic "Deep Dive"
We use **Progressive Disclosure**. Instead of overwhelming the user with text, every section has a **"Tell Me More"** button. Clicking it acts as a patient tutor, explaining that specific concept in even simpler terms.

---

## ♿ Accessibility Suite (Zero Latency)

These features run entirely in the browser, instantly transforming the visual experience.

<details>
<summary><b>1. Bionic Typography</b></summary>
Artificially thickens the first half of every word (e.g., <b>wel</b>come). This creates an artificial fixation point, guiding the eyes across the page and significantly improving reading speed and focus.
</details>

<details>
<summary><b>2. Reading Ruler Overlay</b></summary>
A horizontal, tinted bar that follows the user's mouse cursor. It masks out surrounding text to prevent "line jumping" and visual crowding.
</details>

<details>
<summary><b>3. Interactive Context Toolbar</b></summary>
Highlight any text on the screen to summon a floating toolbar:
<ul>
  <li><b>Read Aloud (TTS):</b> Uses the native browser SpeechSynthesis API to read text aloud at a slightly reduced, dyslexia-optimized pacing.</li>
  <li><b>Instant Dictionary:</b> Instantly looks up the highlighted word without losing your place on the page.</li>
</ul>
</details>

<details>
<summary><b>4. Dyslexia-Optimized UI</b></summary>
<ul>
  <li><b>OpenDyslexic Font:</b> Research-backed typography designed with heavy bottoms to prevent letter swapping (b/d, p/q).</li>
  <li><b>Pastel Color Palette:</b> Soft cream and pastel green backgrounds reduce visual stress and glare (Irlen Syndrome friendly).</li>
</ul>
</details>

---

## 🛠 Technical Architecture

lexiRead uses a decoupled, server-rendered approach to ensure maximum compatibility.

*   **Frontend (Browser):** Vanilla HTML5, JavaScript, and Tailwind CSS.
    *   *State Management:* Heavy use of `localStorage` and `sessionStorage`. The API Key, Library history, and accessibility settings never leave the user's device unless explicitly sent in a secure request header.
*   **Backend (FastAPI):**
    *   *Model Routing:* Uses `gemma-4-31b-it` for heavy reasoning tasks (Summaries, Deep Dives) and the faster `gemma-4-26b-a4b-it` for low-latency tasks (Dictionary lookups).
    *   *Client-Side Auth:* The backend acts as a stateless proxy. It extracts the `X-API-Key` from the HTTP Header (sent by the frontend) and dynamically configures the LLM per request.

---

## 🔌 API Reference

<details>
<summary><b><code>POST /process-text</code></b></summary>
Simplifies a block of text into a structured JSON format.

- **Headers:** `X-API-Key: <Google Gemini Key>`
- **Body:**
  ```json
  {
    "text": "The complex text to simplify...",
    "custom_prompt": "Optional user instructions"
  }
  ```
</details>

<details>
<summary><b><code>POST /deep-dive</code></b></summary>
Provides a deeper, Socratic explanation for a specific section.

- **Headers:** `X-API-Key: <Google Gemini Key>`
- **Body:**
  ```json
  {
    "section_type": "summary",
    "section_content": "The text to expand upon",
    "original_text": "The original context"
  }
  ```
</details>

<details>
<summary><b><code>POST /define-word</code></b></summary>
Gets a 10-year-old level definition of a word. Checks the local `dictionary_seed.json` first for zero-latency, offline-capable results before falling back to the LLM.

- **Headers:** `X-API-Key: <Google Gemini Key>`
- **Body:**
  ```json
  {
    "word": "Obfuscate",
    "context_sentence": "The lawyer tried to obfuscate the truth."
  }
  ```
</details>

---

## 🚀 Future Roadmap
*   **Local AI Execution:** Future support for running Gemma locally via WebAssembly or Ollama for users requiring 100% offline privacy.
*   **Document Parsing:** Advanced PDF and image OCR integration directly in the browser.

---

<div align="center">
  <em>Developed for the Gemma 4 Good Hackathon</em>
</div>
