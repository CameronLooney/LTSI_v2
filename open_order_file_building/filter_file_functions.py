import pandas as pd
from datetime import datetime, timedelta
import re
def filer_ltsi_raw_columns(df):
    df = df[["prodId" ,"salesOrderNum"]]
    df["salesOrderNum"] = df["salesOrderNum"].astype(str)
    df["salesOrderNum"] = [re.sub(r"[a-zA-Z]", "", x) for x in df["salesOrderNum"]]
    return df

def filter_backlog_raw_columns(df):
    df = df[['sales_org','country','cust_num','customer_name','sales_dis','rtm','sales_ord'	,'sd_line_item'	 ,'order_method','del_blk'	,'cust_req_date','ord_entry_date','cust_po_num','ship_num','ship_cust','ship_city','plant',	'material_num','brand','lob','project_code','material_desc','mpn_desc','ord_qty',	'shpd_qty','delivery_qty','remaining_qty','delivery_priority','opt_delivery_qt','rem_mod_opt_qt','sch_line_blocked_for_delv']]
    return df
def delete_no_qty(master):
    master = master.loc[master['remaining_qty'] != 0]
    return master

def mpn_date_fill(vlookup):
    vlookup.rename(columns={'MPN': 'material_num'}, inplace=True)
    vlookup['Date'] = vlookup['Date'].fillna("01.01.90")
    vlookup['Date'] = pd.to_datetime(vlookup.Date, dayfirst=True)
    vlookup['Date'] = [x.date() for x in vlookup.Date]
    vlookup['Date'] = pd.to_datetime(vlookup.Date)
    return vlookup


# if mpn = mpn then if date in backlog is after date in mpn then valid
# compare material_num between two dataframes and if they are equal if the date in backlog is after the date in mpn then valid
def filter_backlog_mpn(backlog, mpn):
    backlog = backlog.merge(mpn, on='material_num', how='left')
    backlog = backlog[backlog['Date'] > backlog['Date_x']]
    backlog = backlog[['sales_org','country','cust_num','customer_name','sales_dis','rtm','sales_ord'	,'sd_line_item'	 ,'order_method','del_blk'	,'cust_req_date','ord_entry_date','cust_po_num','ship_num','ship_cust','ship_city','plant',	'material_num','brand','lob','project_code','material_desc','mpn_desc','ord_qty',	'shpd_qty','delivery_qty','remaining_qty','delivery_priority','opt_delivery_qt','rem_mod_opt_qt','sch_line_blocked_for_delv']]
    return backlog


def backlog_mpn_merge(backlog, mpn):
    master = backlog.merge(mpn, on='material_num', how='left')
    return master


def drop_rows_based_on_date(backlog, mpn):
    master = backlog_mpn_merge(backlog, mpn)
    # if the date the order was placed is before it became valid LTSI drop from df
    rows = master[(master['Date'] > master['ord_entry_date']) & (master["delivery_priority"] != 13)].index.to_list()
    master = master.drop(rows).reset_index()
    return master


def delete_old_blocked_orders(master):
    six_months = datetime.now() - timedelta(188)
    master['ord_entry_date'] = pd.to_datetime(master['ord_entry_date'])
    rows_94 = master[
        (master['ord_entry_date'] < six_months) & (
                master["sch_line_blocked_for_delv"] == 94) & (master['delivery_priority'] != 13) ].index.to_list()
    master = master.drop(rows_94).reset_index(drop=True)
    return master


def delete_old_orders(master):
    twelve_months = datetime.now() - timedelta(240)
    rows_old = master[(master['ord_entry_date'] < twelve_months) & (master['delivery_priority'] != 13) &(master['order_method']!="Manual SAP")].index.to_list()
    master = master.drop(rows_old).reset_index(drop=True)
    return master

