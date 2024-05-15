import streamlit as st
import asyncio
from backend import process_user_query, get_item_names
from PIL import Image
import re

# Load and display the image once
@st.cache_resource
def load_image():
    return Image.open("streamlit/static/images/MadeByTheCommunity_Black.png")

image = load_image()
st.image(image, use_column_width=True)

# Custom CSS to center the title, text, and image
st.markdown("""
<style>
.centered-title, .centered-text, img {
    text-align: center;
    margin-left: auto;
    margin-right: auto;
}
img {
    max-width: 35%;  /* Limits image width to 35% of the column width */
    height: auto;  /* Keeps the aspect ratio */
}
</style>
<h1 class="centered-title">Star Citizen Shop Assistant</h1>
<div class="centered-text">
    This tool helps you retrieve the price of "Extras" from the Roberts Space Industries website.
</div>
""", unsafe_allow_html=True)

# Fetch item names for the dropdown
item_names = ["Begin typing to search..."] + get_item_names()

# Select item from the list with search functionality
selected_item = st.selectbox(
    label="Search or Select from List below",
    label_visibility="hidden",
    options=item_names
)

def get_response(item_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process_user_query(item_name))
    loop.close()
    return result

if st.button('Get Answer'):
    if selected_item and selected_item != "Begin typing to search...":
        with st.spinner("Checking Limbo's database..."):
            response = get_response(selected_item)
            st.write(response)
    else:
        st.error("Please select an item from the list.")

# Add extra space before the footer
st.markdown("<br><br>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center;">
    <p>Copyright © 2024 In Limbo Gaming LLC</p>
</div>
""", unsafe_allow_html=True)

# Feedback form link
st.markdown("""
<div style="text-align: center; margin-top: -2px;">
    <a href="https://forms.gle/iXmBBBXvybmabUbj7" target="_blank">Provide Feedback</a>
</div>
""", unsafe_allow_html=True)
