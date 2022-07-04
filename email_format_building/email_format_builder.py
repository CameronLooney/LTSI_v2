import pandas as pd
import streamlit as st

def build_email_df(df,status):
    status_to_keep = status #['Under Review with C-SAM', 'Blocked']
    df = df[df["Status (SS)"].isin(status_to_keep)] #keep only the status we want
    comments = df.columns[35] #get the column name for the comments
    df = df[["country", "Sales Order and Line Item", "Status (SS)", comments]] #keep only the columns we want
    return df

def orders_by_country(df):
    order_list = df.groupby('country')['Sales Order and Line Item'].agg(list) #group by country and get the list of orders
    return order_list

def get_countries(order_list):
    countries = list(order_list.index) #get the list of countries
    return countries

def email_status_message(country,order_list):
    st.success("Country: {} \n\n Number of Orders: {}".format(country, len(order_list[country]))) #print the country and number of orders

def email_message(country,order_list,reason):
    st.write(
        "Hello {} Team, \n\n could you please confirm if you want the following orders as {}. If no action is taken they will be deleted.\n\n".format(
            country,reason)) #print the country and reason
    orders = order_list[country]
    for order in orders:
        st.write(order)
    st.write("\n\n")
    st.write("Best Regards,\n\n""Reseller Operations Team")
