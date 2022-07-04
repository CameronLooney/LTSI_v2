import streamlit as st
import pandas as pd
from feedback_concat_building.feedback_builder_functions import *
from open_order_file_building.upload_download import write_to_excel
from email_format_building.email_format_builder import *


#test

st.set_page_config(page_title='LTSI Emails')

st.title("LTSI Email Template generator")
st.sidebar.write("""

        ## Instructions\n 
        **Step 1:** Upload LTSI open orders file \n 
        **Step 2:** Select which LTSI status to include in template \n
        **Step 3:** Click the Generate Templates Button\n""")
email = st.radio(
     "Please select which email format you would like to generate: ",
     ('All Under Review/ Blocked', 'Under Review with C-SAM', 'Blocked',"Reach out to Sales"))


excel_file = st.file_uploader("Upload Excel File", type="xlsx")

if st.button('Generate Templates'):
    if excel_file is not None: #if file is not empty
        df = pd.read_excel(excel_file, sheet_name=0, engine="openpyxl") #read excel file
        if email == 'All Under Review/ Blocked': #if email is all under review/blocked
            st.header("All Under Review/ Blocked Email Templates") #print header
            df = build_email_df(df, ['Under Review with C-SAM', 'Blocked']) #build email df

            order_list =orders_by_country(df) #get list of orders by country
            countries = get_countries(order_list) #get list of countries

            for country in countries: #for each country
                email_status_message(str(country), order_list) #print email status message
                email_message(str(country), order_list, "they are currently not frozen in the LTSI Tool and/or they are blocked")

        elif email == 'Under Review with C-SAM': #if email is under review with c-sam
            st.header("Under Review with C-SAM Email Templates") #print header
            df = build_email_df(df, ['Under Review with C-SAM'])#build email df
            order_list =orders_by_country(df)
            countries = get_countries(order_list)

            for country in countries:
                email_status_message(str(country), order_list)
                email_message(str(country), order_list, "they are currently not frozen in the LTSI Tool.")

        elif email == 'Blocked':
            st.header("Blocked Email Templates")
            df = build_email_df(df, ['Blocked'])
            order_list =orders_by_country(df)
            countries = get_countries(order_list)

            for country in countries:
                email_status_message(str(country), order_list)
                email_message(str(country), order_list, "they are currently blocked.")

        elif email == 'Reach out to Sales':
            st.header("Reach out to Sales Email Templates")
            df = build_email_df(df, ['Reach out to Sales'])
            order_list =orders_by_country(df)
            countries = get_countries(order_list)

            for country in countries:
                email_status_message(str(country), order_list)
                email_message(str(country), order_list, "they are currently not frozen in the LTSI Tool.")


