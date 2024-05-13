import streamlit as st
import asyncio
# Import the necessary functions from your backend script
from backend import process_user_query, get_item_names

st.title('Star Citizen Price Assistant')
st.markdown('This tool helps you retrieve the price of "Extras" from the Roberts Space Industries website.')

# Fetch item names for the dropdown
item_names = get_item_names()

# Allow users to choose the interaction mode
mode = st.radio("Would you like to search or select from a list?:", ('Search', 'Select from List'))

selected_item = None
if mode == 'Search':
    # User input for search functionality
    user_input = st.text_input("Type to search for a Ship or Item", help="Type to search for a ship or item.")
    if user_input:
        # Suggest matches based on what the user is typing
        suggestions = [item for item in item_names if user_input.lower() in item.lower()]
        selected_item = st.selectbox("Choose a Ship or Item to get the price for:", suggestions)
elif mode == 'Select from List':
    # Dropdown to select from all items
    selected_item = st.selectbox("Choose a Ship or Item to get the price for:", item_names)

def get_response(item_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Directly pass the selected item name to process the query
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

# Optional footer
# st.image('path/to/your/image.jpg', caption='Image caption')
# st.write('Your footer text here')
