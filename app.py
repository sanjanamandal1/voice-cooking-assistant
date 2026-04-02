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

timer_placeholder = st.empty()
ingredient_placeholder = st.empty()
progress_placeholder = st.empty()

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
    progress = (idx + 1) / len(steps)
    progress_placeholder.progress(progress)
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
def scale_ingredients(desired_servings, speak=True):
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
    if speak:
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
            "start_time": time.time(),
            "last_announce": time.time()
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
            # Announce every minute
            if time.time() - t["last_announce"] >= 60:
                speak(f"{remaining} minutes left on {t['name']}")
                t["last_announce"] = time.time()
        else:
            timer_placeholder.markdown(f"⏱ **{t['name']} completed!**")
            speak(f"{t['name']} completed!")
            to_remove.append(idx)
    for idx in reversed(to_remove):
        st.session_state.timers.pop(idx)

# -----------------------------
# Background Music
# -----------------------------
def toggle_background_music():
    try:
        if st.session_state.music_playing:
            pygame.mixer.music.stop()
            st.session_state.music_playing = False
            speak("Background music stopped")
        else:
            pygame.mixer.init()
            music_file = "background_music.mp3"
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play(-1)
                st.session_state.music_playing = True
                speak("Background music started")
            else:
                st.warning("Background music file not found")
    except Exception as e:
        st.warning(f"Could not toggle background music: {e}")

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
    elif any(word in cmd for word in ["music", "play music", "background music"]):
        toggle_background_music()
    elif any(word in cmd for word in ["stop", "exit", "quit"]):
        speak("Stopping assistant. Goodbye!")
        st.stop()
    else:
        speak("Command not recognized. Try Next Step, Repeat, Set Timer, Make servings, or Music.")

# -----------------------------
# Load Recipes
# -----------------------------
with open("recipes.json") as file:
    recipes = json.load(file)

categories = list(set(recipe.get("category", "Other") for recipe in recipes.values()))
selected_category = st.selectbox("🍽 Choose a category", categories)

filtered_recipes = {k: v for k, v in recipes.items() if v.get("category", "Other") == selected_category}
selected_recipe = st.selectbox("🍳 Choose a recipe", list(filtered_recipes.keys()))
recipe_data = filtered_recipes[selected_recipe]
steps = recipe_data["steps"]
images = recipe_data["images"]
ingredients = recipe_data.get("ingredients", [])
base_servings = recipe_data.get("servings", 1)

desired_servings = st.number_input("🍽 Desired servings", min_value=1, value=base_servings)
if desired_servings != base_servings:
    scale_ingredients(desired_servings, speak=False)

# -----------------------------
# Static Layout (non-flickering)
# -----------------------------
st.title("🎤 You")
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
    
    # Progress bar
    progress = (st.session_state.step_index + 1) / len(steps)
    progress_placeholder.progress(progress)

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
    progress = (idx + 1) / len(steps)
    progress_placeholder.progress(progress)
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
# Voice Recognition
# -----------------------------
col3, col4, col5 = st.columns(3)
with col3:
    if st.button("➡️ Next Step"):
        next_step()
with col4:
    if st.button("🔄 Repeat Step"):
        repeat_step()
with col5:
    if st.button("🎵 Toggle Music"):
        toggle_background_music()

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


