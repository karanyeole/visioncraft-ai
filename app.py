import streamlit as st
import asyncio
from g4f.client import Client
from PIL import Image
import requests
import io
from datetime import datetime
import json
import os

# Initialize g4f Client
client = Client()

# Streamlit Page Config
st.set_page_config(
    page_title="VisionCraft AI",
    layout="wide",
    page_icon="🌌",
    initial_sidebar_state="expanded"
)

HISTORY_FILE = "image_history.json"

# Load persistent history
def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                return [
                    (
                        item[0],  # prompt
                        item[1],  # url
                        item[2],  # timestamp
                        item[3] if len(item) > 3 else "Photorealistic",  # style
                        item[4] if len(item) > 4 else 0.5  # creativity
                    ) for item in data
                ]
        return []
    except (json.JSONDecodeError, IndexError):
        return []

# Save history to file
def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(st.session_state.history, f)

# Function to enhance prompt
def enhance_prompt(prompt, style, negative_prompt="", creativity=0.5):
    prefix = {
        "Photorealistic": "ultra high resolution, photorealistic, realistic lighting, detailed texture",
        "Cinematic": "cinematic lighting, depth of field, 8k, dramatic atmosphere",
        "Digital Art": "digital concept art, vibrant, colorful, clean design",
        "3D Render": "3D render, realistic materials, high detail, V-Ray",
        "Anime": "anime style, cel shading, vibrant colors, character portrait",
        "Oil Painting": "oil painting, textured brush strokes, classic style",
        "Sketch": "pencil sketch, monochrome, fine lines, hand-drawn"
    }
    enhanced = f"{prefix.get(style, '')}, {prompt}, creativity level: {creativity}"
    if negative_prompt:
        enhanced += f", negative prompt: {negative_prompt}"
    return enhanced

# Async image generation
async def generate_image(prompt, style, negative_prompt, creativity):
    final_prompt = enhance_prompt(prompt, style, negative_prompt, creativity)
    response = await client.images.async_generate(
        model="flux",
        prompt=final_prompt,
        response_format="url"
    )
    return response.data[0].url

# Async function to handle image generation
async def generate_and_store_image(prompt, style, negative_prompt, creativity):
    image_url = await generate_image(prompt, style, negative_prompt, creativity)
    image_data = requests.get(image_url).content
    image = Image.open(io.BytesIO(image_data))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append((prompt, image_url, timestamp, style, creativity))
    save_history()
    st.session_state.last_image = image
    st.session_state.last_image_data = image_data
    st.session_state.last_caption = f"Prompt: {prompt} | Style: {style} | Creativity: {creativity}"

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = load_history()
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'last_image' not in st.session_state:
    st.session_state.last_image = None
if 'last_image_data' not in st.session_state:
    st.session_state.last_image_data = None
if 'last_caption' not in st.session_state:
    st.session_state.last_caption = ""

# Custom CSS for an enhanced, vibrant UI
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');

        /* Global Styles */
        .stApp {
            background: linear-gradient(180deg, #0a0a0a, #1a1a2a);
            color: #e0e0e0;
            font-family: 'Inter', sans-serif;
            overflow-x: hidden;
            animation: bgPulse 10s infinite ease-in-out;
        }
        @keyframes bgPulse {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        :root {
            --primary-color: #7b3fe4;
            --accent-color: #00ff88;
            --glass-bg: rgba(255, 255, 255, 0.1);
            --glow: 0 0 15px rgba(123, 63, 228, 0.7);
            --neon-glow: 0 0 20px #00ff88;
        }

        /* Sidebar */
        .sidebar {
            background: linear-gradient(135deg, #0a0a1a, #2a2a4a);
            padding: 1.5rem;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            animation: sidebarGlow 5s infinite alternate;
        }
        @keyframes sidebarGlow {
            from { box-shadow: inset var(--glow); }
            to { box-shadow: inset 0 0 25px rgba(0, 255, 136, 0.5); }
        }
        .sidebar .stMarkdown {
            background: var(--glass-bg);
            backdrop-filter: blur(15px);
            padding: 1.2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .sidebar .stMarkdown:hover {
            transform: scale(1.02);
            box-shadow: var(--neon-glow);
        }
        .sidebar .stImage img {
            border-radius: 12px;
            transition: transform 0.4s ease, box-shadow 0.4s ease;
        }
        .sidebar .stImage img:hover {
            transform: scale(1.1) rotate(2deg);
            box-shadow: var(--neon-glow);
        }
        .sidebar button {
            background: linear-gradient(45deg, #ff4d4d, #ff8c00);
            color: #fff;
            border: none;
            padding: 0.7rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.4s ease;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);
        }
        .sidebar button:hover {
            background: linear-gradient(45deg, #ff1a1a, #ff6f00);
            transform: translateY(-3px);
            box-shadow: 0 0 20px rgba(255, 140, 0, 0.7);
        }

        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, var(--primary-color), #1e90ff, #00ff88);
            padding: 4.5rem 2.5rem;
            border-radius: 20px;
            margin: 2rem 1rem;
            text-align: center;
            position: relative;
            overflow: hidden;
            animation: heroPulse 6s infinite ease-in-out;
        }
        @keyframes heroPulse {
            0% { box-shadow: 0 0 20px rgba(0, 255, 136, 0.5); }
            50% { box-shadow: 0 0 40px rgba(123, 63, 228, 0.7); }
            100% { box-shadow: 0 0 20px rgba(0, 255, 136, 0.5); }
        }
        .hero::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.2), transparent);
            animation: rotateGlow 10s linear infinite;
        }
        @keyframes rotateGlow {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .hero h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 3.5rem;
            color: #fff;
            text-shadow: 0 0 15px #00ff88, 0 0 30px #7b3fe4;
            animation: textGlow 2s infinite alternate;
        }
        @keyframes textGlow {
            from { text-shadow: 0 0 15px #00ff88; }
            to { text-shadow: 0 0 30px #7b3fe4; }
        }
        .hero p {
            font-size: 1.3rem;
            color: rgba(255, 255, 255, 0.95);
            max-width: 750px;
            margin: 1.5rem auto;
            animation: fadeInUp 1.5s ease-out;
        }

        /* Input Container */
        .input-container {
            background: var(--glass-bg);
            backdrop-filter: blur(15px);
            padding: 2.5rem;
            border-radius: 15px;
            margin: 2rem 1rem;
            box-shadow: var(--glow);
            animation: containerFloat 4s infinite ease-in-out;
        }
        @keyframes containerFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .stTextInput > div > div > input {
            font-size: 1.3rem;
            padding: 1.2rem;
            border-radius: 10px;
            border: 3px solid var(--primary-color);
            background: rgba(10, 10, 10, 0.9);
            color: #e0e0e0;
            transition: all 0.4s ease;
            box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
        }
        .stTextInput > div > div > input:focus {
            box-shadow: 0 0 20px var(--accent-color), inset 0 0 10px rgba(0, 255, 136, 0.3);
            border-color: #00ff88;
        }
        .stSelectbox div[role="combobox"] {
            background: rgba(10, 10, 10, 0.9);
            border: 2px solid var(--primary-color);
            border-radius: 10px;
            padding: 0.8rem;
            transition: all 0.4s ease;
        }
        .stSelectbox div[role="combobox"]:hover {
            box-shadow: 0 0 15px var(--accent-color);
        }
        .stExpander {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 1rem;
            transition: all 0.3s ease;
        }
        .stExpander:hover {
            box-shadow: var(--neon-glow);
        }
        .stSlider > div > div {
            background: linear-gradient(to right, #7b3fe4, #00ff88);
            border-radius: 5px;
        }
        .stButton > button {
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            color: #fff;
            font-size: 1.2rem;
            padding: 1rem 2.5rem;
            border-radius: 10px;
            border: none;
            transition: all 0.5s ease;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);
            animation: buttonPulse 3s infinite ease-in-out;
        }
        @keyframes buttonPulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .stButton > button:hover {
            transform: translateY(-5px) scale(1.1);
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.8);
            background: linear-gradient(90deg, #5a2ec2, #00cc66);
        }

        /* Gallery */
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 2rem;
            padding: 2.5rem;
            animation: galleryFade 1s ease-out;
        }
        @keyframes galleryFade {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .gallery-item {
            position: relative;
            border-radius: 15px;
            overflow: hidden;
            background: var(--glass-bg);
            transition: all 0.6s ease;
            cursor: pointer;
            box-shadow: var(--glow);
        }
        .gallery-item:hover {
            transform: perspective(1200px) rotateX(5deg) rotateY(5deg) scale(1.05);
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
        }
        .gallery-item img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            transition: opacity 0.4s ease, filter 0.4s ease;
        }
        .gallery-item:hover img {
            filter: brightness(1.2);
        }
        .gallery-item .overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            opacity: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: opacity 0.4s ease;
            color: #fff;
        }
        .gallery-item:hover .overlay {
            opacity: 0.9;
        }
        .gallery-item .overlay button {
            background: linear-gradient(45deg, #ff4d4d, #ff8c00);
            color: #fff;
            border: none;
            padding: 0.7rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            margin: 0.7rem;
            transition: all 0.4s ease;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);
        }
        .gallery-item .overlay button:hover {
            background: linear-gradient(45deg, #ff1a1a, #ff6f00);
            transform: translateY(-3px);
            box-shadow: 0 0 20px rgba(255, 140, 0, 0.7);
        }

        /* Loader */
        .loader {
            border: 5px solid var(--accent-color);
            border-top: 5px solid transparent;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1.2s linear infinite, loaderGlow 2s infinite alternate;
            margin: 2.5rem auto;
        }
        @keyframes loaderGlow {
            from { box-shadow: 0 0 10px var(--accent-color); }
            to { box-shadow: 0 0 20px #00cc66; }
        }

        /* Animations */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .hero h1 { font-size: 2.5rem; }
            .hero p { font-size: 1.1rem; }
            .gallery { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
            .gallery-item img { height: 180px; }
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar History
with st.sidebar:
    st.markdown("### 📜 Art History")
    if st.session_state.history:
        for i, (p, url, ts, s, c) in enumerate(reversed(st.session_state.history)):
            st.markdown(f"**{ts}** | {s}")
            st.markdown(f"Prompt: `{p[:50]}{'...' if len(p) > 50 else ''}`")
            st.image(url, width=150)
            if st.button("🗑️ Delete", key=f"delete_{i}"):
                st.session_state.history.pop(len(st.session_state.history) - 1 - i)
                save_history()
                st.rerun()
            st.markdown("---")
    else:
        st.info("Your art history will appear here.")

# Hero Section
st.markdown("""
    <div class="hero">
        <h1>Unleash Your Imagination</h1>
        <p>Craft breathtaking AI-generated art with unparalleled precision. Explore infinite styles and bring your visions to life in seconds.</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
st.markdown('<div class="input-container">', unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])

with col1:
    # Form to manage state
    with st.form(key="input_form"):
        prompt = st.text_input(
            "", 
            placeholder="Describe your vision (e.g., 'A neon-lit cyberpunk city, cinematic')",
            label_visibility="collapsed",
            key="prompt_input",
            value="A dynamic 3D render of the Chola dynasty’s naval fleet battling in the Bay of Bengal, realistic materials, V-Ray rendering, dramatic lighting, 8k resolution, ideal for South Indian history memorabilia or maritime art promotions"
        )
        # Auto-suggestions
        suggestions = [
            "A glowing forest with ethereal creatures, digital art",
            "A futuristic metropolis under a starry sky, photorealistic",
            "A vibrant anime character in a fantasy realm",
            "A surreal oil painting of a dreamscape"
        ]
        suggestion = st.selectbox("Quick Ideas:", ["Pick a suggestion..."] + suggestions, index=0)

        # Advanced Options
        with st.expander("🛠️ Creative Controls"):
            style = st.selectbox("Art Style:", [
                "Photorealistic", "Cinematic", "Digital Art", 
                "3D Render", "Anime", "Oil Painting", "Sketch"
            ], index=0)  # Default to Photorealistic as per your input
            resolution = st.selectbox("Resolution:", [
                "1024x1024", "512x512", "768x768"
            ], index=0)  # Default to 1024x1024 as per your input
            negative_prompt = st.text_input("Avoid (optional):", 
                placeholder="e.g., blurry, distorted, low quality",
                value="blurry, distorted, low quality")  # Default to your input
            creativity = st.slider("Creativity Level:", 0.0, 1.0, 1.0)  # Default to 1.0 as per your input

        submit_button = st.form_submit_button("🚀 Create Art")
        if submit_button:
            if prompt.strip():
                with st.spinner(""):
                    st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
                    try:
                        asyncio.run(generate_and_store_image(prompt, style, negative_prompt, creativity))
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please provide a prompt to create art.")

    # Display image and download button outside the form
    if st.session_state.last_image is not None:
        st.image(st.session_state.last_image, caption=st.session_state.last_caption, use_column_width=True)
        st.download_button(
            label="📥 Download Art",
            data=st.session_state.last_image_data,
            file_name=f"visioncraft_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png",
            mime="image/png"
        )

with col2:
    # Live Style Preview
    st.markdown("### 🎨 Style Preview")
    style_previews = {
        "Photorealistic": "https://via.placeholder.com/150?text=Photorealistic",
        "Cinematic": "https://via.placeholder.com/150?text=Cinematic",
        "Digital Art": "https://via.placeholder.com/150?text=Digital+Art",
        "3D Render": "https://via.placeholder.com/150?text=3D+Render",
        "Anime": "https://via.placeholder.com/150?text=Anime",
        "Oil Painting": "https://via.placeholder.com/150?text=Oil+Painting",
        "Sketch": "https://via.placeholder.com/150?text=Sketch"
    }
    st.image(style_previews.get(style, "https://via.placeholder.com/150"), caption="Selected Style", use_column_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# History Gallery
st.markdown("### 🌟 Your Creations")
if st.session_state.history:
    st.markdown('<div class="gallery">', unsafe_allow_html=True)
    for i, (p, url, ts, s, c) in enumerate(reversed(st.session_state.history)):
        with st.container():
            st.markdown(f'<div class="gallery-item">', unsafe_allow_html=True)
            st.image(url, use_column_width=True)
            st.markdown(f"""
                <div class="overlay">
                    <button onclick="alert('Delete image?')">Delete</button>
                    <p style="font-size: 0.9rem; padding: 0.5rem;">{p[:30]}{'...' if len(p) > 30 else ''}</p>
                </div>
            """, unsafe_allow_html=True)
            st.caption(f"{ts} | {s} | Creativity: {c}")
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Start creating to see your art here!")