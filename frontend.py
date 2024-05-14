import streamlit as st
import asyncio
from backend import process_user_query, get_item_names
from PIL import Image

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
<br>  <!-- Adding a line break here -->
""", unsafe_allow_html=True)

# Fetch item names for the dropdown
item_names = get_item_names()

# Interaction mode selection
mode = st.radio("Would you like to search for an item or select from a list?:", ('Search', 'Select From List'))
selected_item = None

if mode == 'Search':
    user_input = st.text_input("Type to search for a Ship or Item", help="Type to search for a ship or item.")
    if user_input:
        suggestions = [item for item in item_names if user_input.lower() in item.lower()]
        selected_item = st.selectbox("Choose a Ship or Item to get the price for:", suggestions)
elif mode == 'Select From List':
    selected_item = st.selectbox("Choose a Ship or Item to get the price for:", item_names)

def get_response(item_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process_user_query(item_name))
    loop.close()
    return result

if st.button('Get Answer'):
    if selected_item:
        with st.spinner("Checking Limbo's database..."):
            response = get_response(selected_item)
            st.write(response)
    else:
        st.error("Please select or search for an item.")

# Load and display the image
image = Image.open("streamlit/static/images/MadeByTheCommunity_Black.png")
st.image(image, use_column_width=True)

# Footer
st.markdown("""
<div style="text-align: center;">
    <p>Copyright © 2024 In Limbo Gaming LLC</p>
</div>
""", unsafe_allow_html=True)

# Feedback form link
st.markdown("""
<div style="text-align: center; margin-top: 20px;">
    <a href="https://forms.gle/iXmBBBXvybmabUbj7" target="_blank">Provide Feedback</a>
</div>
""", unsafe_allow_html=True)
