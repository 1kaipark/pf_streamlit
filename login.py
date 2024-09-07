import streamlit as st
from utils.pf_csv_interface import create_blank_csv
import os

with st.container():
    user = st.text_input(label="User Name")
    if st.button("Login"):
        if user is not None:
            if os.path.exists(f'expenses_{user}.csv'):
                st.session_state['name'] = user  # Set the name in session state
                st.success("Logged in successfully!")
                st.switch_page('pages/app.py')
            else:
                st.error("User not found.")


with st.form(key='new_user', clear_on_submit=True):
    st.subheader(body='New User')
    new_user = st.text_input(label='User Name', key='newuser')
    submitted = st.form_submit_button(label='Create user')
    if submitted:
        if create_blank_csv(f'expenses_{new_user}.csv'):
            st.success('User Created')
        else:
            st.warning('User already found.')