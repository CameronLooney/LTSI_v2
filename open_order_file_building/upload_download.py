import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import io
import re

def upload_files():
    upload_ltsi_raw = st.file_uploader("Upload Raw LTSI Status File", type="xlsx")
    upload_previous_open_orders = st.file_uploader("Upload Yesterdays Open Orders", type="xlsx")
    upload_mpn= st.file_uploader("Upload MPN File", type="xlsx")
    upload_backlog = st.file_uploader("Upload Raw File", type="xlsx")
    return upload_ltsi_raw, upload_previous_open_orders, upload_mpn, upload_backlog

def read_files_to_df(upload_ltsi_raw, upload_previous_open_orders, upload_mpn, upload_backlog):
    df_ltsi_raw = pd.read_excel(upload_ltsi_raw, sheet_name=0, engine="openpyxl")
    df_previous_open_orders = pd.read_excel(upload_previous_open_orders, sheet_name=0, engine="openpyxl")
    df_mpn = pd.read_excel(upload_mpn, sheet_name=0, engine="openpyxl")
    df_backlog = pd.read_excel(upload_backlog, sheet_name=0, engine="openpyxl")
    return df_ltsi_raw, df_previous_open_orders, df_mpn, df_backlog


def write_to_excel(merged):
    # Writing df to Excel Sheet
    buffer = io.BytesIO()
    # engine required
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # write the merged dataframe to the excel sheet
        merged.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook = writer.book  # get the workbook
        worksheet = writer.sheets['Sheet1']  # get the worksheet
        formatdict = {'num_format': 'dd/mm/yyyy'}  # set the date format
        fmt = workbook.add_format(formatdict)  # add the format to the workbook
        worksheet.set_column('K:K', None, fmt)  # set the date format for the column
        worksheet.set_column('L:L', None, fmt)  # set the date format for the column
        # Light yellow fill with dark yellow text.
        number_rows = len(merged.index) + 1  # get the number of rows in the dataframe

        # colour rows based on the status

        # if status is Under Review then colour it light yellow
        yellow_format = workbook.add_format({'bg_color': '#FFEB9C'})
        worksheet.conditional_format('A2:AH%d' % (number_rows),
                                     {'type': 'formula',
                                      'criteria': '=$AH2="Under Review with C-SAM"',
                                      'format': yellow_format})
        worksheet.conditional_format('A2:AH%d' % (number_rows),
                                     {'type': 'formula',
                                      'criteria': '=$AH2="Under Review with CSAM"',
                                      'format': yellow_format})

        # if status is blocked colour it red
        red_format = workbook.add_format({'bg_color': '#ffc7ce'})
        worksheet.conditional_format('A2:AH%d' % (number_rows),
                                     {'type': 'formula',
                                      'criteria': '=$AH2="Blocked"',
                                      'format': red_format})
        # if status is shippable / scheduled out colour it green
        green_format = workbook.add_format({'bg_color': '#c6efce'})
        worksheet.conditional_format('A2:AH%d' % (number_rows),
                                     {'type': 'formula',
                                      'criteria': '=$AH2="Shippable"',
                                      'format': green_format})
        worksheet.conditional_format('A2:AH%d' % (number_rows),
                                     {'type': 'formula',
                                      'criteria': '=$AH2="Scheduled Out"',
                                      'format': green_format})

        # if status is To be cancelled / reduced colour it grey
        grey_format = workbook.add_format({'bg_color': '#C0C0C0'})
        worksheet.conditional_format('A2:AH%d' % (number_rows),
                                     {'type': 'formula',
                                      'criteria': '=$AH2="To be cancelled / reduced"',
                                      'format': grey_format})

        # setting the column width to fit the data
        for column in merged:
            column_width = max(merged[column].astype(str).map(len).max(), len(column))
            col_idx = merged.columns.get_loc(column)
            writer.sheets['Sheet1'].set_column(col_idx, col_idx, column_width)
            worksheet.autofilter(0, 0, merged.shape[0], merged.shape[1])
        worksheet.set_column(11, 12, 20)  # set the width of the columns
        worksheet.set_column(12, 13, 20)
        worksheet.set_column(13, 14, 20)
        # set the header to bold
        header_format = workbook.add_format({'bold': True,
                                             'bottom': 2,
                                             'bg_color': '#0AB2F7'})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(merged.columns.values):
            worksheet.write(0, col_num, value, header_format)
        my_format = workbook.add_format()
        my_format.set_align('left')

        worksheet.set_column('N:N', None, my_format)
        writer.save()
        today = datetime.today()
        d1 = today.strftime("%d/%m/%Y")
        st.write("Download Completed File:")

        # download the file
        st.download_button(
            label="Download Excel worksheets",
            data=buffer,
            file_name="LTSI_file_" + d1 + ".xlsx",
            mime="application/vnd.ms-excel"
        )

