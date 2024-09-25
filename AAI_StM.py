### %pip install streamlit plotly

import streamlit as st
import json
import os
import hashlib
import pandas as pd
import plotly.express as px

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to load users
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as file:
            return json.load(file)
    return {}

# Function to save users
def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file)

# Sign-up page function
def signup_page():
    st.title("Welcome to the Sign Up Page")
    
    name = st.text_input("Name", key="signup_name")
    phone = st.text_input("Phone", key="signup_phone")
    dob = st.date_input("DOB", key="signup_dob")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Sign Up", key="signup_button"):
        users = load_users()
        if email in users:
            st.error("A user with this email already exists!")
        else:
            hashed_password = hash_password(password)
            users[email] = {
                "name": name,
                "phone": phone,
                "dob": str(dob),
                "password": hashed_password
            }
            save_users(users)
            os.makedirs(f"./{email}", exist_ok=True)  # Create folder for the user
            st.success("Sign-up successful! You can now log in.")
            st.session_state['current_page'] = 'login'

# Login page function
def login_page():
    st.title("Welcome to the Login Page")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        users = load_users()
        hashed_password = hash_password(password)
        
        if email in users and users[email]["password"] == hashed_password:
            st.success(f"Welcome {users[email]['name']}!")
            st.session_state['logged_in'] = True
            st.session_state['email'] = email
            st.session_state['current_page'] = 'input_marks'
        else:
            st.error("Invalid email or password.")

# Input marks page function
def input_marks_page():
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        st.title(f"Welcome {st.session_state['email']}")
        
        # Enter marks for at least 7 subjects
        subjects = ['Maths', 'Science', 'History', 'English', 'Geography', 'Physics', 'Chemistry']
        marks = {}
        
        for i, subject in enumerate(subjects):
            marks[subject] = st.slider(f"Choose your marks for {subject}", 0, 100, key=f"marks_{subject}_{i}")
        
        if st.button("Submit", key="submit_marks"):
            df = pd.DataFrame(list(marks.items()), columns=['Subject', 'Marks'])
            csv_path = f"./{st.session_state['email']}/marks.csv"
            df.to_csv(csv_path, index=False)
            st.success("Marks saved successfully!")
            st.session_state['current_page'] = 'report'
    else:
        st.error("You need to log in first!")

# Report page function
def report_page():
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        st.title("Your Reports are Ready!")
        
        csv_path = f"./{st.session_state['email']}/marks.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)

            # Bar Chart: Average marks
            avg_marks = df['Marks'].mean()
            fig_bar = px.bar(df, x='Subject', y='Marks', title=f"Average Marks: {avg_marks}")
            st.plotly_chart(fig_bar, key="bar_chart")

            # Line Chart: Marks for each subject
            fig_line = px.line(df, x='Subject', y='Marks', title="Marks as per each subject")
            st.plotly_chart(fig_line, key="line_chart")

            # Pie Chart: Marks distribution
            fig_pie = px.pie(df, names='Subject', values='Marks', title="Marks Distribution")
            st.plotly_chart(fig_pie, key="pie_chart")
        else:
            st.error("No marks found. Please input your marks first.")
    else:
        st.error("You need to log in first!")

# Main app function to control page navigation using buttons
def main():
    # Set up session state for page control
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'signup'

    # Navigation based on session state
    if st.session_state['current_page'] == 'signup':
        signup_page()
        if st.button("Go to Login", key="to_login_button"):
            st.session_state['current_page'] = 'login'
    elif st.session_state['current_page'] == 'login':
        login_page()
        if st.button("Go to Sign Up", key="to_signup_button"):
            st.session_state['current_page'] = 'signup'
    elif st.session_state['current_page'] == 'input_marks':
        input_marks_page()
        if st.button("Go to Report", key="to_report_button"):
            st.session_state['current_page'] = 'report'
    elif st.session_state['current_page'] == 'report':
        report_page()
        if st.button("Go to Input Marks", key="to_input_marks_button"):
            st.session_state['current_page'] = 'input_marks'

if __name__ == "__main__":
    main()
