# 🎤 Voice-Controlled Cooking Assistant

Cook hands-free with a voice-controlled assistant that guides you through recipes step by step!

---

## Features

- ✅ Voice commands for **next step**, **repeat step**, **set timer**, **ingredient scaling**, and **stop**.
- ✅ Displays **step-by-step images**.
- ✅ **Timers with voice feedback** every minute.
- ✅ **Smart ingredient scaling** for desired servings.
- ✅ Optional **background music** while cooking.
- 🎯 Basic version now, will scale up in future.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/sanjanamandal1/voice-cooking-assistant.git
cd voice-cooking-assistant
```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```
   
3. Install dependencies:
   
   ```bash
   pip install -r requirements.txt
   ```
   
5. Run the app:
   
     ```bash
   streamlit run app.py
   ```

## Usage

Choose a recipe from the dropdown.
Click Start Listening and say commands like:
“Next Step” / “What’s the next step?”
“Repeat”
“Set timer 5 minutes”
“Make 2 servings”
“Stop”


## 💻 Tech Stack:

Python
Streamlit
pyttsx3 (text-to-speech)
SpeechRecognition
pygame (background music)
Pillow (image display)
JSON (recipe storage)


## 🌐 Future Enhancements

Multi-timer support
More recipes and categories
Smarter NLP commands
Deploy on Streamlit Cloud for online demo
Improved UI and progress tracking
