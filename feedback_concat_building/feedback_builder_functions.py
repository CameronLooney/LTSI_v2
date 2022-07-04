import pandas as pd
def read_feedback(fb):
    try:
        feedback = pd.read_excel(fb, sheet_name=0, engine="openpyxl")
    except:
        return None
    return feedback


def read_main(df):
    main = pd.read_excel(df, sheet_name=0, engine="openpyxl")
    return main


def old_feedback_getter(df):
    cols = [8]
    col_count = 37
    if df.shape[1] >= 39:
        while col_count < df.shape[1]:
            cols.append(col_count)
            col_count += 1

    return df.iloc[:, cols]

def join_feedback_files(feedback_list):
    df_list = []
    for feedback in feedback_list:
        if feedback is not None:
            colname = feedback.columns[34]
            df = feedback.dropna(axis=0, subset=[colname])
            df_list.append(df)

    merged_df = pd.concat(df_list, ignore_index=True)
    return merged_df

def concat_feedback_and_prev(main,main_feedback_previous,merged_df):
    main = main.iloc[:, :34]
    main["Sales Order and Line Item"] = main["Sales Order and Line Item"].astype(str)
    main_feedback_previous["Sales Order and Line Item"] = main_feedback_previous["Sales Order and Line Item"].astype(
        str)
    done = main.merge(merged_df, on=["Sales Order and Line Item"], how="left")
    done = done.merge(main_feedback_previous, on=["Sales Order and Line Item"], how="left")
    return done