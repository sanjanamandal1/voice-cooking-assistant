import streamlit as st
import speech_recognition as sr
import pyttsx3
import json
import time
from PIL import Image
import pygame
import threading
import os

# -----------------------------
# Initialization
# -----------------------------
if "engine" not in st.session_state:
    st.session_state.engine = pyttsx3.init()
engine = st.session_state.engine

if "step_index" not in st.session_state:
    st.session_state.step_index = 0

if "timers" not in st.session_state:
    st.session_state.timers = []

if "music_playing" not in st.session_state:
    st.session_state.music_playing = False

recognizer = sr.Recognizer()

# -----------------------------
# Load Recipes
# -----------------------------
with open("recipes.json") as file:
    recipes = json.load(file)

selected_recipe = st.selectbox("🍳 Choose a recipe", list(recipes.keys()))
steps = recipes[selected_recipe]["steps"]
images = recipes[selected_recipe]["images"]
ingredients = recipes[selected_recipe].get("ingredients", [])
base_servings = recipes[selected_recipe].get("servings", 1)

# -----------------------------
# Static Layout (non-flickering)
# -----------------------------
st.title("🎤 Advanced Voice-Controlled Cooking Assistant")
st.write("Cook hands-free with images, timers, voice commands, and smart ingredient scaling!")

col1, col2 = st.columns([1, 1])
with col1:
    try:
        img = Image.open(images[st.session_state.step_index])
        img = img.resize((400, 350))
        col1.image(img)
    except:
        col1.warning("Image not found")
with col2:
    step_placeholder = col2.empty()
    step_placeholder.write(f"### Step {st.session_state.step_index+1} / {len(steps)}")
    step_placeholder.write(steps[st.session_state.step_index])

timer_placeholder = st.empty()
ingredient_placeholder = st.empty()

# -----------------------------
# Non-blocking TTS
# -----------------------------
def speak(text):
    def run_speech():
        try:
            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            pass
    threading.Thread(target=run_speech, daemon=True).start()

# -----------------------------
# Recipe Step Functions
# -----------------------------
def show_step(idx):
    try:
        img = Image.open(images[idx]).resize((400, 350))
        col1.image(img)
    except:
        col1.warning("Image not found")
    step_placeholder.write(f"### Step {idx+1} / {len(steps)}")
    step_placeholder.write(steps[idx])
    speak(f"Step {idx+1}: {steps[idx]}")

def next_step():
    if st.session_state.step_index + 1 < len(steps):
        st.session_state.step_index += 1
        show_step(st.session_state.step_index)
    else:
        speak("No more steps available")

def repeat_step():
    show_step(st.session_state.step_index)

def go_to_step(command):
    numbers = [int(s) for s in command.split() if s.isdigit()]
    if numbers and 1 <= numbers[0] <= len(steps):
        st.session_state.step_index = numbers[0]-1
        show_step(st.session_state.step_index)
    else:
        speak("Invalid step number")

# -----------------------------
# Ingredient Scaling
# -----------------------------
def scale_ingredients(desired_servings):
    scale_factor = desired_servings / base_servings
    scaled_ingredients = []
    for ing in ingredients:
        try:
            qty, rest = ing.split(" ",1)
            scaled_qty = float(qty.replace("g","").replace("ml","")) * scale_factor
            unit = "g" if "g" in qty else "ml"
            scaled_ingredients.append(f"{int(scaled_qty)}{unit} {rest}")
        except:
            scaled_ingredients.append(ing)
    ingredient_placeholder.write("### Adjusted Ingredients:")
    for ing in scaled_ingredients:
        ingredient_placeholder.write(f"• {ing}")
    speak(f"Ingredients scaled for {desired_servings} servings")

# -----------------------------
# Timer Functions (non-flickering)
# -----------------------------
def set_timer(command):
    numbers = [int(s) for s in command.split() if s.isdigit()]
    if numbers:
        minutes = numbers[0]
        st.session_state.timers.append({
            "name": f"Timer {len(st.session_state.timers)+1}",
            "minutes": minutes,
            "start_time": time.time()
        })
        speak(f"Timer set for {minutes} minutes")
    else:
        speak("Please specify a valid number for timer")

def update_timers():
    to_remove = []
    for idx, t in enumerate(st.session_state.timers):
        elapsed = (time.time() - t["start_time"]) / 60
        remaining = max(0, int(t["minutes"] - elapsed))
        if remaining > 0:
            timer_placeholder.markdown(f"⏳ **{t['name']}**: {remaining} min left")
        else:
            timer_placeholder.markdown(f"⏱ **{t['name']} completed!**")
            speak(f"{t['name']} completed!")
            to_remove.append(idx)
    for idx in reversed(to_remove):
        st.session_state.timers.pop(idx)

# -----------------------------
# Background Music
# -----------------------------
def play_background_music():
    try:
        if not st.session_state.music_playing:
            st.session_state.music_playing = True
            pygame.mixer.init()
            music_file = "background_music.mp3"
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play(-1)
            else:
                st.warning("Background music file not found")
    except Exception as e:
        st.warning(f"Could not play background music: {e}")

play_background_music()

# -----------------------------
# NLP Voice Commands
# -----------------------------
def process_command(command):
    cmd = command.lower()
    if any(word in cmd for word in ["next", "proceed", "continue"]):
        next_step()
    elif any(word in cmd for word in ["repeat", "again", "replay"]):
        repeat_step()
    elif "go to step" in cmd:
        go_to_step(cmd)
    elif "timer" in cmd:
        set_timer(cmd)
    elif "make" in cmd and "servings" in cmd:
        numbers = [int(s) for s in cmd.split() if s.isdigit()]
        if numbers:
            scale_ingredients(numbers[0])
        else:
            speak("Please specify the number of servings")
    elif any(word in cmd for word in ["stop", "exit", "quit"]):
        speak("Stopping assistant. Goodbye!")
        st.stop()
    else:
        speak("Command not recognized. Try Next Step, Repeat, Set Timer, or Make servings.")

# -----------------------------
# Voice Recognition
# -----------------------------
if st.button("🎙 Start Listening"):
    with sr.Microphone() as source:
        speak("Listening for your command...")
        audio = recognizer.listen(source, phrase_time_limit=8)
        try:
            user_cmd = recognizer.recognize_google(audio)
            st.write(f"You said: {user_cmd}")
            process_command(user_cmd)
        except:
            speak("Sorry, I did not understand. Please repeat.")

# -----------------------------
# Update timers every run (non-flickering)
# -----------------------------
update_timers()


