# COLS TO BUILD
# 1. sales order number
import numpy as np
import pandas as pd
import streamlit as st
import datetime



# drop LOB AND date columns
def drop_lob_date_columns(df):
    df.drop(columns=['LOB', 'Date'],axis = 1, inplace=True)
    return df
# concat sales order number and sales order line item number together to create sales order number and insert into dataframe in index 8
def concat_key(df):
    new_col= df['sales_ord'].astype(str) + df['sd_line_item'].astype(str)
    df.insert(loc=9, column='Sales Order and Line Item', value=new_col)
    return df



# make a new column called "Valid" and set all rows to False
# check if sales_ord in working_file is in df_ltsi and if there is a match then change valid column value to True
def check_valid(working_file, df_ltsi):
    working_file.rename(columns={'sales_ord': 'salesOrderNum'}, inplace=True)
    working_file['Valid in LTSI Tool'] = "FALSE"
    for index, row in working_file.iterrows():
        if row['salesOrderNum'] in df_ltsi['salesOrderNum'].values:
            working_file.at[index, 'Valid in LTSI Tool'] = "TRUE"
    return working_file


def generate_status_column(merged):
    merged['del_blk'] = merged['del_blk'].fillna('')
    merged['del_blk'] = merged['del_blk'].astype(str)
    merged['sch_line_blocked_for_delv'] = merged['sch_line_blocked_for_delv'].fillna('')
    merged['sch_line_blocked_for_delv'] = merged['sch_line_blocked_for_delv'].astype(str)
    conditions = [merged["del_blk"] != "",
                  merged["sch_line_blocked_for_delv"] != "",
                  merged['order_method'] == "Manual SAP",
                  merged['delivery_priority'] == 13,
                  merged["Valid in LTSI Tool"] == "TRUE",
                  ]
    outputs = ["Blocked", "Blocked", "Shippable", "Shippable", "Shippable"]
    result = np.select(conditions, outputs, "Under Review with C-SAM")
    result = pd.Series(result)
    merged['Status (SS)'] = result
    return merged



def scheduled_out(merged):
    merged['cust_req_date'] = pd.to_datetime(merged['cust_req_date'])
    ten_days = datetime.datetime.now() + datetime.timedelta(10)
    merged.loc[(merged['cust_req_date'] > ten_days) & (
            merged['Status (SS)'] == 'Shippable') & (
                       merged["Valid in LTSI Tool"] == 'TRUE'), 'Status (SS)'] = 'Scheduled Out'
    return merged


def new_sdm_feedback(merged):
    date_today =datetime.datetime.today()
    currentDay = date_today.day
    date_num = datetime.date.today()
    currentMonth = date_num.strftime("%B")
    merged["Action (SDM) {} {}".format(currentDay, currentMonth)] = ""
    merged["Comments (SDM) {} {}".format(currentDay, currentMonth)] = ""
    merged["Estimated DN Date {} {}".format(currentDay, currentMonth)] = ""
    return merged


# create empty columns with the same name as the columns present in open dataframe past the index of Status SS column in the merged dataframe
def cols_from_previous_file(previous):
    cols_to_keep = ["Sales Order and Line Item"]
    for col in previous.columns[previous.columns.get_loc('Status (SS)')+1:]:
        cols_to_keep.append(col)
    return cols_to_keep

# drop all columns not in list of column names
def drop_cols_not_in_list(df, cols_to_keep):
    df.drop(columns=df.columns.difference(cols_to_keep), inplace=True)
    return df

# left join merged dataframe and previous dataframe on sales order and line item columns
def previous_sdm_feedback(merged, previous):
    merged["Sales Order and Line Item"] = merged["Sales Order and Line Item"].astype(str)
    previous["Sales Order and Line Item"] = previous["Sales Order and Line Item"].astype(str)
    merged = merged.merge(previous, how='left', on=['Sales Order and Line Item'])
    return merged


def status_override(merged):
    merged = merged.drop('index', 1)
    action_sdm = merged.columns[37]  # get the index of the action column
    merged[action_sdm] = merged[action_sdm].str.lower()  # lowercase the column
    merged[action_sdm] = merged[action_sdm].fillna("0")  # fill the column na  with 0
    # if SDM provided feedback containing the string cancel then change the status
    merged['Status (SS)'] = np.where(merged[action_sdm].str.contains('cancel', regex=False),
                                     'To be cancelled / reduced', merged['Status (SS)'])
    # if SDM provided feedback containing the string block then change the status
    merged['Status (SS)'] = np.where(merged[action_sdm].str.contains('block', regex=False),
                                     'Blocked', merged['Status (SS)'])
    merged[action_sdm] = merged[action_sdm].astype(str)
    # replace "0" with blank, (needed none NA to use numpy.where function)
    merged[action_sdm].replace(['0', '0.0'], '', inplace=True)
    return merged


def unique_status(merged,previous):
    standard_status = ["Shippable", "Blocked", "To be cancelled / reduced", "Under Review with C-SAM",
                       "Scheduled Out"]  # standard status
    prev = previous[~previous['Status (SS)'].isin(standard_status)]  # get the previous status that isnt in the standard status
    result = prev.groupby('Sales Order and Line Item')['Status (SS)'].apply(
        list).to_dict()  # get the status for each row
    for key, value in result.items():  # for each row
        merged["Status (SS)"] = np.where(merged["Sales Order and Line Item"] == key, value,
                                         merged["Status (SS)"])  # replace the status with the previous status
    return merged
