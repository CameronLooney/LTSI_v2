import streamlit as st
import pandas as pd
from feedback_concat_building.feedback_builder_functions import *
from open_order_file_building.upload_download import write_to_excel

def app():



    st.title('LTSI Feedback Joiner')
    st.sidebar.write("""
        ### Instructions: \n
        - Upload feedback files from SDM (up to 3)\n
        - Upload open orders file\n
        - Click the Upload button""")
    st.write("## Upload 1 to 3 Feedback Files")
    fb1 = st.file_uploader("Upload Feedback File 1", type="xlsx")
    fb2 = st.file_uploader("Upload Feedback File 2", type="xlsx")
    fb3 = st.file_uploader("Upload Feedback File 3", type="xlsx")
    st.header("Upload Open Orders File")
    main_file = st.file_uploader("Upload Open Orders File", type="xlsx")

    if st.button("Upload Files"):
        feedback1 = read_feedback(fb1)
        feedback2 = read_feedback(fb2) #read feedback files
        feedback3 = read_feedback(fb3)
        feedback_list = [feedback1, feedback2, feedback3]

        merged_df = join_feedback_files(feedback_list)

        cols_to_keep = [] #create list of columns to keep
        action_sdm = merged_df.columns[34] #get column name for action sdm
        comment_sdm = merged_df.columns[35]
        dn_sdm = merged_df.columns[36]
        cols_to_keep.extend(["Sales Order and Line Item",action_sdm, comment_sdm, dn_sdm]) #add columns to keep
        merged_df = merged_df[cols_to_keep] #keep columns

        merged_df["Sales Order and Line Item"] = merged_df["Sales Order and Line Item"].astype(str) #convert sales order and line item to string


        main = read_main(main_file) #read main file
        main_feedback_previous = old_feedback_getter(main) #get previous feedback
        finished_file = concat_feedback_and_prev(main,main_feedback_previous,merged_df) #concatenate feedback and previous feedback
        write_to_excel(finished_file)






app()