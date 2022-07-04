from open_order_file_building.upload_download import *
from open_order_file_building.filter_file_functions import *
from open_order_file_building.building_file_functions import *


# LTSI Steps
# 1. Filter out dates if the date of the order is before the date in the mpn file
# 2. If the delivery priority is 13 then its valid
# 3. if manual order then valid
# 4. If the order is Valid in tool then its valid
# 5. if the blocks are empty its valid
from PIL import  Image
display = Image.open('logo.png')
st.image(display, width = 650)



def app():
    st.title('LTSI Backlog File Builder')
    st.sidebar.write("""

        ## Instructions\n 
        - First Save all files as .xlsx \n
        - **Upload 1:** Raw LTSI download \n
        - **Upload 2:** Upload Updated Open Order File from Yesterday (the one uploaded to Box) \n
        - **Upload 3:** File with list of MPNs that are Valid LTSI and the date they became LTSI
        - **Upload 4:** Upload Raw Backlog file (downloaded from ZV07 using variant)\n""")


    upload_ltsi_raw, upload_previous_open_orders, upload_mpn, upload_backlog = upload_files()
    if st.button("Upload Files"):
        if upload_ltsi_raw is None:
            st.error("Please upload the LTSI Raw File")
        if upload_previous_open_orders is None:
            st.error("Please upload the Previous Open Orders File")
        if upload_mpn is None:
            st.error("Please upload the MPN File")
        if upload_backlog is None:
            st.error("Please upload the Backlog File from FrontEnd (ZVO6)")
        try:
            # read files to dataframes
            df_ltsi, df_previous_open_orders, df_mpn, df_backlog = read_files_to_df(upload_ltsi_raw, upload_previous_open_orders, upload_mpn, upload_backlog)
            df_mpn = mpn_date_fill(df_mpn) #fill in the dates for the MPNs
            previous_status = df_previous_open_orders.copy() #copy the previous status
            df_backlog = filter_backlog_raw_columns(df_backlog) #filter the backlog columns
            working_file = drop_rows_based_on_date(df_backlog, df_mpn) #drop rows based on date
            working_file = delete_no_qty(working_file) #delete rows with no qty

            working_file = delete_old_blocked_orders(working_file) #delete rows with old blocked orders
            working_file = delete_old_orders(working_file) #delete rows with old orders

            working_file = drop_lob_date_columns(working_file) #drop lob and date columns
            working_file = concat_key(working_file)#concatenate key
            working_file = check_valid(working_file, df_ltsi) #check if valid
            working_file = generate_status_column(working_file) #generate status column
            working_file = scheduled_out(working_file) #scheduled out
            working_file = new_sdm_feedback(working_file) #new sdm feedback
            x = cols_from_previous_file(df_previous_open_orders) #get columns from previous file
            df_previous_open_orders = drop_cols_not_in_list(df_previous_open_orders, x) #drop columns not in list
            working_file = previous_sdm_feedback(working_file, df_previous_open_orders) #previous sdm feedback
            working_file = status_override(working_file) #status override
            working_file = unique_status(working_file,previous_status) #unique status
            write_to_excel(working_file) #write to excel
        except:
            st.error("Please check the files and try again, if the problem persists please contact the developer")



app()
