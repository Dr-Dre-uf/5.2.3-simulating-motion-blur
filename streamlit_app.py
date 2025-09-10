import streamlit as st
import numpy as np
import cv2
from PIL import Image

st.set_page_config(page_title="Motion Blur Simulation", layout="wide")

st.title("Simulating Motion Blur on Images")

# Warning about uploads
st.warning("⚠️ Do not upload sensitive or personal data. Images are processed locally in this demo app.")

# Sidebar: choose image source
st.sidebar.header("Image Selection")
use_uploaded = st.sidebar.checkbox("Upload your own image")

uploaded_img = None
if use_uploaded:
    uploaded_img = st.sidebar.file_uploader(
        "Upload an Image",
        type=["jpg", "jpeg", "png"]
    )
else:
    image_choice = st.sidebar.selectbox(
        "Select Example Image",
        ["Fluorescence (IFCells)", "Brightfield (BloodSmear)"],
        help="Choose a sample image."
    )

# Sidebar: motion blur settings
st.sidebar.header("Motion Blur Settings")
blur_length = st.sidebar.slider(
    "Blur Length", 3, 50, 20, step=1,
    help="Controls how long the blur streak is."
)
blur_angle = st.sidebar.slider(
    "Blur Angle (degrees)", 0, 180, 45, step=1,
    help="Controls the angle of the blur, simulating motion direction."
)

# Motion blur kernel generator
def motion_blur_kernel(length, angle):
    kernel = np.zeros((length, length))
    kernel[int((length - 1) / 2), :] = np.ones(length)
    M = cv2.getRotationMatrix2D((length / 2 - 0.5, length / 2 - 0.5), angle, 1)
    kernel = cv2.warpAffine(kernel, M, (length, length))
    kernel /= length
    return kernel

motion_kernel = motion_blur_kernel(blur_length, blur_angle)

# Default paths
bf_path = "assets/BloodSmear.png"
if_path = "assets/IFCells.jpg"

# Load selected image
if use_uploaded and uploaded_img is not None:
    img = np.array(Image.open(uploaded_img).convert("RGB"))
elif not use_uploaded:
    if image_choice == "Fluorescence (IFCells)":
        img = np.array(Image.open(if_path).convert("RGB"))
    else:
        img = np.array(Image.open(bf_path).convert("RGB"))
else:
    img = None

# Process and display
if img is not None:
    img_motion = cv2.filter2D(img, -1, motion_kernel)

    st.subheader("Motion Blur Simulation")

    col1, col2 = st.columns(2)
    col1.image(img, caption="Original Image", use_container_width=True)
    col2.image(img_motion, caption="With Motion Blur", use_container_width=True)
else:
    st.info("Please upload an image or select one from the examples to begin.")
