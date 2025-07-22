import streamlit as st
import time

#TO RUN: 
#streamlit run ui/app.py

st.set_page_config(page_title="Resume AI Agents", page_icon="📝", layout="wide")

st.title("Resume AI Agents")

st.write("Welcome to the Resume AI Agent System.")
st.write("This dashboard will showcase agent outputs, job recommendations, and personalized emails.")

if st.button("Run Example"):
    st.success("This is where your agent workflow outputs will appear.")

#useful for resume ai agents


#class learning

#counter

st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Select a page", ["Home", "Counter"])

#good for data sciencetist as well for visualization

st.write("Regular Text")
st.markdown("**Bold Text**")

#message
st.success("This is a success message!")
st.info("This is an info message.")
st.warning("This is a warning message!")
st.error("This is an error message!")
st.exception("This is an exception message!")

if st.button("Click Me!"):
    st.write("Button clicked!")
# Displaying a spinner
with st.spinner("Loading..."):
    time.sleep(2)  # Simulating a long computation
st.success("Loading complete!")
# Displaying a progress bar
progress = st.progress(0)
for i in range(100):
    time.sleep(0.05)  # Simulating a long computation
    progress.progress(i + 1)
st.success("Progress complete!")

# Displaying a checkbox
if st.checkbox("Show/Hide"):
    st.write("Checkbox is checked!")
# Displaying a radio button
option = st.radio("Choose an option:", ["Option 1", "Option 2", "Option 3"])
st.write(f"You selected: {option}") 

# Bar Graph

import plotly.express as px
import pandas as pd

df = pd.DataFrame({"x": [1, 2, 3, 4, 5],
                   "y": [10, 20, 30, 40, 50]})
fig = px.bar(df, x="x", y="y", title="Bar Graph Example")
st.plotly_chart(fig)


st.markdown("### Bold Texts and Italics")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("left column")
    if st.button("Click Me in Column 1"):
        st.write("Button clicked in Column 1!")
    st.image("https://via.placeholder.com/150", caption="Placeholder Image 1")

with col2:
    st.write("middle column")
    if st.button("Click Me in Column 2"):
        st.write("Button clicked in Column 2!")
    st.image("https://via.placeholder.com/150", caption="Placeholder Image 2")
with col3:
    st.write("right column")
    if st.button("Click Me in Column 3"):
        st.write("Button clicked in Column 3!")
    st.image("https://via.placeholder.com/150", caption="Placeholder Image 3")



if 'counter' not in st.session_state:
    st.session_state.counter = 0
if st.button("Increment Counter"):
    st.session_state.counter += 1
st.write(f"Counter: {st.session_state.counter}")





#image processing app

st.title("Image Processing App")
st.write("Upload an image to apply filters and transformations.")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    from PIL import Image, ImageFilter
    import io

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Apply filters
    if st.button("Apply Grayscale"):
        gray_image = image.convert("L")
        st.image(gray_image, caption="Grayscale Image", use_column_width=True)

    if st.button("Apply Blur"):
        blurred_image = image.filter(ImageFilter.BLUR)
        st.image(blurred_image, caption="Blurred Image", use_column_width=True)

    if st.button("Rotate 90 degrees"):
        rotated_image = image.rotate(90)
        st.image(rotated_image, caption="Rotated Image", use_column_width=True)
    if st.button("Save Image"):
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        st.download_button(
            label="Download Image",
            data=buffer,
            file_name="processed_image.png",
            mime="image/png"
        )
# Displaying a table
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "Los Angeles", "Chicago"]
}
df = pd.DataFrame(data)
st.write("Data Table:")
st.dataframe(df)
