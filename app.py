import gspread
import datetime
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from dateutil.relativedelta import relativedelta

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = st.secrets["tape_calibration_log"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(credentials_dict), scope)
client = gspread.authorize(creds)
sheet = client.open('tape_calibration_log').sheet1
data = sheet.get_all_values()

st.set_page_config(page_title="Star Garments")
st.title("Measuring Tape Calibration")

tab1, tab2 = st.tabs(["➕ Add To Calibration", "➖ Finished Calibration"])

with tab1:
    st.header("Add To Calibration")

    with st.form("form_add1"):
        cols1       = st.columns([2, 2])
        tape_number = cols1[0].text_input("Tape Number:", key="tape_number")
        epf_number  = cols1[1].text_input("EPF Number:", key="epf_number")

        cols2       = st.columns([2, 2])
        departmrnts = cols2[0].selectbox("Department:", ("Quality", "Finishing", "Cutting", "Technical", "Stores", "Sample"), key="dept")
        name        = cols2[1].text_input("Employer:", key="employer")

        submitted1  = st.form_submit_button("Submit", use_container_width=True)

    if submitted1:
        given_date  = datetime.date.today().strftime("%Y-%m-%d")
        future_date = datetime.date.today() + relativedelta(months=3)
        finished_date = future_date.strftime("%Y-%m-%d")

        if str(epf_number) in sheet.col_values(2):
            pre_epf_status_check = True
            for row in data:
                if row[1] == str(epf_number) and row[9] == "FALSE":
                    pre_epf_status_check = False
                    st.error("Finish the previous calibration.")
                    break
            if pre_epf_status_check:
                sheet.append_row([tape_number, epf_number, departmrnts, name, given_date, finished_date, given_date, None, None, False])
                st.success("✅ Successfully updated existing member to the sheet.")
        else:
            sheet.append_row([tape_number, epf_number, departmrnts, name, given_date, finished_date, given_date, None, None, False])
            st.success("✅ Successfully added new member to the sheet.")

with tab2:
    st.header("Finished Calibration")

    false_rows_all = []
    false_rows = []

    for idx, row in enumerate(data[1:], start=2):
        if row[9] == 'FALSE':
            false_rows_all.append(row[1])
            false_rows.append([row[0], row[1], row[2], row[3]])

    with st.form("form_add2"):
        option_finished = st.selectbox("EPF Number:", false_rows_all)
        submitted2 = st.form_submit_button("Submit", use_container_width=True)

    if submitted2:
        index = 0
        for row in data:
            index+=1
            if row[1] == str(option_finished) and row[9] == "FALSE":
                finished_date = datetime.date.today().strftime("%Y-%m-%d")
                sheet.update_cell(index, 9, finished_date)
                sheet.update_cell(index, 10, True)
        
        given_date  = datetime.date.today().strftime("%Y-%m-%d")
        future_date = datetime.date.today() + relativedelta(months=3)
        future_date = future_date.strftime("%Y-%m-%d")

        for false_row_info in false_rows:
            if false_row_info[1] == option_finished:
                tape_number = false_row_info[0]
                epf_number  = false_row_info[1]
                departmrnts = false_row_info[2]
                name        = false_row_info[3]

        sheet.append_row([tape_number, epf_number, departmrnts, name, given_date, future_date, given_date, None, None, False])
        st.success("✅ Successfully updated the row.")