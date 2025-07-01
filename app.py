# === Imports ===
import datetime

import gspread
import streamlit as st

from dateutil.relativedelta import relativedelta
from oauth2client.service_account import ServiceAccountCredentials

# === Google Sheets API Setup ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

credentials_dict = st.secrets["tape_calibration_log"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    dict(credentials_dict), scope
)

client = gspread.authorize(creds)
sheet = client.open("tape_calibration_log").sheet1
data = sheet.get_all_values()

# === Streamlit Page Setup ===
st.set_page_config(page_title="Star Garments")
st.title("Measuring Tape Calibration")

# === Tab Navigation ===
tab1, tab2, tab3 = st.tabs([
    "➖ Add To New",
    "➖ Add To Given",
    "➖ Finished Calibration"
])

# === Tab 1: Add To Calibration ===
with tab1:
    st.header("Add To Calibration")

    with st.form("form_add1_tab1"):
        cols1 = st.columns([2, 2])
        tape_number = cols1[0].text_input("Tape Number:", key="tape_number")
        epf_number  = cols1[1].text_input("EPF Number:", key="epf_number")

        cols2 = st.columns([2, 2])
        departmrnts = cols2[0].selectbox("Department:",("Quality", "Finishing", "Cutting", "Technical", "Stores", "Sample", "Other"))
        
        name = cols2[1].text_input("Employer:", key="employer")

        submitted1 = st.form_submit_button("Submit", use_container_width=True)

    if submitted1:
        given_date    = datetime.date.today().strftime("%Y-%m-%d")
        future_date   = datetime.date.today() + relativedelta(months=3)
        finished_date = future_date.strftime("%Y-%m-%d")

        existing = False
        status   = True

        for idx, row in enumerate(data[1:], start=1):
            if row[0] == tape_number and row[1] == epf_number:
                existing = True
                break

        if existing:
            st.error("This row already exists.")
        else:
            sheet.append_row([tape_number, epf_number, departmrnts, name, given_date, finished_date, None, None, None, False])
            st.success("✅ Successfully updated existing member to the sheet.")

# === Tab 2: Add To Given ===
with tab2:
    st.header("Add To Given")

    with st.form("form_add2"):
        tape_number = st.text_input("Tape Number:")
        epf_number  = st.text_input("EPF Number:")
        submitted1  = st.form_submit_button("Submit", use_container_width=True)

    if submitted1:
        found = False  # flag to track if a matching row is found

        for idx, row in enumerate(data[1:], start=2):  # start=2 to match sheet row indexing
            if row[0] == tape_number and row[1] == epf_number:
                if row[9] == "FALSE":
                    if row[6] == '':
                        sheet.update_cell(idx, 7, datetime.date.today().strftime("%Y-%m-%d"))
                        st.success("✅ Successfully updated existing member to the sheet.")
                    else:
                        st.warning("⚠️ This Given date has already updated.")       
                    break                                

# === Tab 3: Finished Calibration ===
with tab3:
    st.header("Finished Calibration")

    false_rows = []
    for idx, row in enumerate(data[1:], start=2):  
        if row[9] == 'FALSE':
            false_rows.append(row[1])

    if false_rows:
        with st.form("form_add3"):
            cols = st.columns([2, 2])
            epf_number = cols[0].selectbox("EPF Number:", false_rows)
            tape_number = cols[1].text_input("Tape Number:")
            submitted1 = st.form_submit_button("Submit", use_container_width=True)

        if submitted1:
            for idx, row in enumerate(data[1:], start=2):
                if (row[0] == str(tape_number) and row[1] == str(epf_number) and row[9] == "FALSE"):
                    if row[6] != '':
                        finished_date = datetime.date.today().strftime("%Y-%m-%d")
                        sheet.update_cell(idx, 9, finished_date)
                        sheet.update_cell(idx, 10, True)

                        given_date = datetime.date.today().strftime("%Y-%m-%d")
                        future_date = (datetime.date.today() + relativedelta(months=3)).strftime("%Y-%m-%d")

                        sheet.append_row([row[0], row[1], row[2], row[3], given_date, future_date, None, None, None, False])
                        st.success("✅ Successfully updated the row.")
                        break
                    else:
                        st.warning("⚠️ This person have not given the tape.")
                        break


