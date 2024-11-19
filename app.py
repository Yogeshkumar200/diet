import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import plotly.graph_objs as go
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.runnables import RunnableLambda
import langchain.globals as lcg
import base64

# Set verbose mode as per requirement
lcg.set_verbose(True)  # Enable verbose mode for debugging

# Set environment variable for Google API key
os.environ["GOOGLE_API_KEY"] = 'AIzaSyBGKnyD4gAXmoeXT61bikW-wkQ4SRr3yU4'
config = {"temperature": 0.6, "top_p": 1, "top_k": 1, "max_output_tokens": 2048}
ai_model = GoogleGenerativeAI(model="gemini-pro", generation_config=config)

# Customize prompt template for diet and workout suggestions
diet_prompt_template = PromptTemplate(
    input_variables=['full_name', 'age_group', 'gender_identity', 'body_weight', 'height_in_cm', 'diet_preference', 'allergic_reactions'],
    template="Diet and Exercise Recommendation System:\n"
             "I want you to suggest 6 types of home workouts with detailed instructions in points, 6 breakfast ideas with nutritional information, "
             "5 dinner options with nutritional information, and 6 gym workout plans in detailed points and for each day of the week."
             "Based on the following details:\n"
             "Full Name: {full_name}\n"
             "Age: {age_group}\n"
             "Gender: {gender_identity}\n"
             "Weight: {body_weight}\n"
             "Height: {height_in_cm}\n"
             "Diet Preference: {diet_preference}\n"
             "Allergic Reactions: {allergic_reactions}\n"
)

# Define RunnableChain for invoking model
recommendation_chain = RunnableLambda(lambda inputs: diet_prompt_template.format(**inputs)) | ai_model

# Function to load and encode background image
def get_base64_image(image_path):
    with open(image_path, "rb") as file:
        data = file.read()
    return base64.b64encode(data).decode()

# Set background image
background_image_path = "fitt.jpg"
base64_image = get_base64_image(background_image_path)

# Custom CSS with animations
st.markdown(
    f"""
    <style>
        .stApp {{
            background: url("data:image/jpg;base64,{base64_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .header {{
            font-size: 30px;
            font-weight: bold;
            font-family: 'Arial', sans-serif;
            text-align: center;
            color: #FFFFFF;
            margin-bottom: 20px;
            background: rgba(0, 0, 0, 0.6);
            padding: 10px;
            border-radius: 8px;
            animation: fadeIn 2s;
        }}
        .subheader {{
            font-size: 18px;
            font-family: 'Helvetica', sans-serif;
            text-align: center;
            color: #FFFFFF;
            margin-bottom: 25px;
            background: rgba(0, 0, 0, 0.6);
            padding: 8px;
            border-radius: 8px;
        }}
        .recommendation-box {{
            margin-top: 15px;
            font-family: 'Helvetica', sans-serif;
            background: rgba(255, 255, 255, 0.8);
            padding: 15px;
            border-radius: 10px;
            animation: fadeInUp 1.5s ease-in-out;
        }}
        .stButton button {{
            justify-self: center;
            display: flex;
            transition: background-color 0.3s, transform 0.3s;
        }}
        .stButton button:hover {{
               border-color: rgb(19 1 1);
       color: rgb(0 0 0);
    background-color: #defff4;
            transform: scale(1.05);
            box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Main Page Header
st.markdown('<div class="header">Personalized Diet & Fitness Recommendation</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Tailored suggestions based on your profile</div>', unsafe_allow_html=True)

# User Input Form
with st.form(key='user_profile_form', clear_on_submit=True):
    st.text_input("Full Name", key='full_name', placeholder="Enter your full name")
    st.text_input("Age", key='age_group', placeholder="Enter your age")
    st.selectbox("Gender", ['Male', 'Female'], key='gender_identity')
    st.text_input("Weight (kg)", key='body_weight', placeholder="Enter your weight in kg")
    st.text_input("Height (cm)", key='height_in_cm', placeholder="Enter your height in cm")
    st.selectbox("Diet Preference", ['Veg', 'Non-Veg'], key='diet_preference')
    st.text_input("Allergic Reactions", key='allergic_reactions', placeholder="Enter any allergies")
    submit_button = st.form_submit_button(label="Get Recommendations")

# Process Input
if submit_button:
    if all(st.session_state.get(key) for key in ['full_name', 'age_group', 'gender_identity', 'body_weight', 'height_in_cm', 'diet_preference', 'allergic_reactions']):
        # Invoke the recommendation model
        user_data = {key: st.session_state[key] for key in ['full_name', 'age_group', 'gender_identity', 'body_weight', 'height_in_cm', 'diet_preference', 'allergic_reactions']}
        recommendations = recommendation_chain.invoke(user_data)

        # Display Recommendations with Animation
        st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
        st.markdown(recommendations, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Calculate BMI
        bmi = round(float(st.session_state['body_weight']) / ((float(st.session_state['height_in_cm']) / 100) ** 2), 2)
        bmi_category = (
            "Underweight" if bmi < 18.5 else
            "Normal weight" if bmi < 25 else
            "Overweight" if bmi < 30 else "Obesity"
        )
        st.write(f"Your BMI: **{bmi} ({bmi_category})**")
