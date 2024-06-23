import streamlit as st
from rembg import remove
from PIL import Image
import io
import os
import zipfile
import tempfile
import shutil

def process_image(input_image):
    return remove(input_image)

def process_zip(zip_file):
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        output_dir = os.path.join(temp_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        for filename in os.listdir(temp_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_path = os.path.join(temp_dir, filename)
                output_path = os.path.join(output_dir, f'processed_{filename.split(".")[0]}.png')
                
                with Image.open(input_path) as img:
                    output = process_image(img)
                    output.save(output_path, 'PNG')
        
        output_zip = os.path.join(temp_dir, 'processed_images.zip')
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            for root, _, files in os.walk(output_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), file)
        
        with open(output_zip, 'rb') as f:
            return f.read()

st.title("Heroz Tech BG-Remover")

tab1, tab2 = st.tabs(["Single Image", "Bulk Images"])

with tab1:
    st.subheader("Single Image")
    image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], accept_multiple_files=False)

    if image_file is not None:
        input_image = Image.open(image_file)
        st.image(input_image, caption="Uploaded Image", use_column_width=True)

        if st.button("Remove Background"):
            output_image = process_image(input_image)
            st.image(output_image, caption="Image with Background Removed", use_column_width=True)
            
            buf = io.BytesIO()
            output_image.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="Download Image",
                data=byte_im,
                file_name="output_image.png",
                mime="image/png"
            )

with tab2:
    st.subheader("Bulk Images")
    zip_file = st.file_uploader("Upload a ZIP file containing images", type="zip")

    if zip_file is not None:
        if st.button("Process Bulk Images"):
            with st.spinner("Processing images... This may take a while."):
                processed_zip = process_zip(zip_file)
            
            st.success("Processing complete!")
            st.download_button(
                label="Download Processed Images",
                data=processed_zip,
                file_name="processed_images.zip",
                mime="application/zip"
            )