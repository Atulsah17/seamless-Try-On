
import streamlit as st
import requests
from PIL import Image
import io
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# API configuration
API_URL = "https://try-on-diffusion.p.rapidapi.com/try-on-file"
API_KEY = os.getenv("RAPIDAPI_KEY")  # Load API key from .env file
if not API_KEY:
    st.error("API key not found in .env file. Please set RAPIDAPI_KEY.")
    st.stop()

HEADERS = {
    "x-rapidapi-host": "try-on-diffusion.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

# Streamlit app configuration
st.set_page_config(page_title="Seamless Try-On", page_icon="👗", layout="wide")

# Inject Tailwind CSS and custom styles
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        /* Apply solid black background to the entire app */
        html, body, .stApp, [data-testid="stAppViewContainer"] {
            background: #000000 !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Ensure nested containers are transparent */
        [data-testid="stAppViewContainer"] > div, [data-testid="stVerticalBlock"] > div {
            background: transparent !important;
        }
        .gradient-header {
            background: linear-gradient(to right, #7c3aed, #db2777);
            border-radius: 12px;
            padding: 2rem;
            margin: 1rem auto;
            max-width: 1200px;
        }
        .card {
            background: #ffffff; /* Fully opaque white */
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin: 1rem auto;
            max-width: 1200px;
            position: relative; /* For positioning download button */
        }
        .btn-primary {
            background: linear-gradient(to right, #7c3aed, #db2777);
            color: white;
            padding: 12px 48px; /* Increased horizontal padding for wider button */
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .btn-primary:disabled {
            background: #d1d5db;
            cursor: not-allowed;
        }
        /* Center the generated image */
        .image-container {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }
        .stImage img {
            max-width: 300px !important;
            max-height: 400px !important;
            width: 100%;
            height: auto;
            object-fit: contain;
            border-radius: 8px;
        }
        /* Style for download button */
        .btn-secondary {
            background: #6b7280;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            transition: background 0.2s;
            position: absolute;
            top: 1.5rem;
            left: 1.5rem;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .btn-secondary:hover {
            background: #4b5563;
        }
        @media (max-width: 640px) {
            .gradient-header {
                padding: 1.5rem;
            }
            .card {
                padding: 1rem;
                margin: 0.5rem;
            }
            .stImage img {
                max-width: 200px !important;
                max-height: 300px !important;
            }
            .btn-primary {
                padding: 12px 32px;
            }
            .btn-secondary {
                padding: 6px 12px;
                top: 1rem;
                left: 1rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for result image
if 'result_image' not in st.session_state:
    st.session_state.result_image = None
if 'result_bytes' not in st.session_state:
    st.session_state.result_bytes = None

# App title and description
st.markdown("""
    <div class="gradient-header text-white text-center">
        <h1 class="text-4xl font-bold tracking-tight">Seamless Try-On</h1>
    </div>
""", unsafe_allow_html=True)

# File uploaders
st.markdown("<div class='card'>", unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="medium")
with col1:
    avatar_file = st.file_uploader("Upload Person Avatar", type=["jpg", "jpeg", "png"], key="avatar")
with col2:
    cloth_file = st.file_uploader("Upload Clothing Item", type=["jpg", "jpeg", "png"], key="cloth")
st.markdown("</div>", unsafe_allow_html=True)

# Preview uploaded images
if avatar_file and cloth_file:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Uploaded Images")
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        avatar_image = Image.open(avatar_file)
        st.image(avatar_image, caption="Person Avatar", use_container_width=False, clamp=True, output_format="JPEG")
    with col2:
        cloth_image = Image.open(cloth_file)
        st.image(cloth_image, caption="Clothing Item", use_container_width=False, clamp=True, output_format="JPEG")
    st.markdown("</div>", unsafe_allow_html=True)

# Try-on button (centered)
st.markdown("<div class='text-center mt-8'>", unsafe_allow_html=True)
if st.button("Generate Try-On", disabled=not (avatar_file and cloth_file), key="generate", help="Click to generate the try-on result"):
    with st.spinner("Generating try-on result..."):
        try:
            # Prepare files for API
            files = {
                "avatar_image": ("avatar.jpg", avatar_file.getvalue(), "image/jpeg"),
                "clothing_image": ("cloth.jpg", cloth_file.getvalue(), "image/jpeg")
            }

            # Send API request
            response = requests.post(API_URL, headers=HEADERS, files=files)

            # Handle response
            if response.status_code == 200 and response.headers.get("content-type").startswith("image/"):
                # Store result in session state
                st.session_state.result_image = Image.open(io.BytesIO(response.content))
                buffered = io.BytesIO()
                st.session_state.result_image.save(buffered, format="JPEG")
                st.session_state.result_bytes = buffered.getvalue()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display result if available
if st.session_state.result_image:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Try-On Result")
    # Download button positioned at top-left with secondary styling
    st.download_button(
        label="↓",
        data=st.session_state.result_bytes,
        file_name="try_on_result.jpg",
        mime="image/jpeg",
        key="download",
        help="Download the try-on result image",
        args={'_class': 'btn-secondary'}  # Use secondary button styling
    )
    # Centered image with flex container
    st.markdown("<div class='image-container'>", unsafe_allow_html=True)
    st.image(st.session_state.result_image, caption="Seamless Try-On Result", use_container_width=False, clamp=True, output_format="JPEG")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
