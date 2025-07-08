# laundry_app.py

import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials # Remove this line
# import os # Already imported
from PIL import Image
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
#from google.colab import auth # Add this line
import google.auth # Add this line
import json
from google.oauth2.service_account import Credentials

# ------------------ SETUP GOOGLE SHEETS + DRIVE ------------------ #

# Google Sheets & Drive auth
# scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets'] # Remove this line
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope) # Remove this line
# client = gspread.authorize(creds) # Remove this line

creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

auth.authenticate_user() # Add this line
credentials, project_id = google.auth.default() # Add this line
client = gspread.authorize(credentials) # Add this line


# Open the sheet
sheet = client.open("Laundry_Records").sheet1

# Google Drive service (for image upload)
drive_service = build('drive', 'v3', credentials=credentials) # Use the same credentials

def upload_to_drive(local_file, student_name):
    folder_id = 'your-folder-id'  # TODO: Create a folder in Google Drive and paste the ID here
    file_metadata = {
        'name': local_file,
        'parents': [folder_id]
    }
    media = MediaFileUpload(local_file, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get("id")
    return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

# ------------------ STREAMLIT UI ------------------ #

st.title("🧺 Laundry Submission Portal")
st.subheader("Submit your clothes safely")

with st.form("laundry_form", clear_on_submit=True):
    name = st.text_input("Your Name")
    roll = st.text_input("Roll Number")
    hostel = st.selectbox("Hostel", ["C1", "C2", "C3"])
    room = st.text_input("Room Number")
    dept = st.text_input("Department")
    image = st.file_uploader("Upload a photo of your laundry", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Submit")

    if submitted:
        if not all([name, roll, room, dept, image]):
            st.warning("Please fill all fields and upload a photo.")
        else:
            file_name = f"{roll}_{image.name}"
            with open(file_name, "wb") as f:
                f.write(image.getbuffer())

            image_link = upload_to_drive(file_name, name)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([timestamp, name, roll, hostel, room, dept, image_link, "Pending", ""])

            st.success("✅ Laundry recorded successfully!")
            st.markdown(f"🔗 [View your laundry photo here]({image_link})")
