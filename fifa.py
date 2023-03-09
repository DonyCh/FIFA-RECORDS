import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import sqlite3
import shutil
import datetime
import ftplib
import os
import numba

from streamlit import components
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build

# #google drive
# creds = Credentials.from_authorized_user_file("client_secret_235904585131-2mtqpfk9oqvqfof1pmqnrco0s4rhh77v.apps.googleusercontent.com.json")
# drive_service = build('drive', 'v3', credentials=creds)

# # create a folder
# folder_name = 'fifa_folder'
# try:
#     mimetype = 'application/vnd.google-apps.folder'
#     file_metadata = {'name': folder_name, 'mimeType': mimetype}
#     folder = drive_service.files().create(body=file_metadata, fields='id').execute()
#     print(F'Folder has been created with Name "{folder_name}" and URL: "https://drive.google.com/drive/folders/{folder.get("id")}".')
# except HttpError as error:
#     print(F'An error occurred while creating the folder: {error}')
#     folder = None

# # upload file
# file_name = 'example.txt'
# file_metadata = {'name': file_name, 'parents':[folder.get("id")]}
# media = MediaFileUpload(file_name, mimetype='text/plain')
# file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
# print(F'File ID: {file.get("id")}')


st.set_page_config(page_title="FIFA 19 Records", page_icon=":bar_chart:", layout="wide")

#GETTING CURRENT DATE
date_format = "%d/%m/%Y %H:%M"
now = datetime.datetime.now().strftime(date_format)
now = now.replace("/", "")
now = now.replace(" ", "_")
now = now.replace(":", "")

def wholeApp():
    players = [" ", "DC", "Moose", "Amos", "Tuti", "Keda", "Kevy"]

    # ---- DB ----
    conn = sqlite3.connect('fifa.db')
    sql_cursor = conn.cursor()
    #this is the code for the settings
    sql_cursor.execute("""CREATE TABLE IF NOT EXISTS records(
        id integer PRIMARY KEY AUTOINCREMENT,
        Winner text NOT NULL,
        "Winner's score" text NULL,
        "Loser's score" text NOT NULL,
        Loser text NOT NULL
    )
    """)

    # ---- DF ----
    # columns_records = ['Winner', "Winner's score", "Loser's score", 'Loser']

    # df_records = pd.DataFrame(columns = columns_records)

    columns_log = ['Shiri', 'Games Played', 'Games Won', 'Games Lost', 
                'Won/Lost', 'Goals For', 'Goals Against', 'Goals Ratio', 
                'WW FOR', 'WW Against', 'WW Ratio']

    df_log = pd.DataFrame(columns = columns_log)

    columns_points = ['Winner', 'Wins', 'Loser', "Losses", "Win/Loss", "Goals For", "Goals Against", "Goals F/A", "WW For", "WW Against", "WW F/A"]

    df_points = pd.DataFrame(columns = columns_points)

    # ---- METHODS ----
    def save_record(record):
        if record["Winner"] and record["Winner's score"] and record["Loser's score"] and record["Loser"]:
            sql_cursor.execute(""" INSERT INTO records(Winner, "Winner's score", "Loser's score", Loser) VALUES (?,?,?,?)""",
                                (record["Winner"], record["Winner's score"], record["Loser's score"], record["Loser"]))
                                
            # df_records.append(record, ignore_index=True)
            st.write("Record Saved. Please do not overclick. Click once then wait!")
            # st.session_state.first_name = players[0]

    # @st.cache
    def delete_record():    
            sql_cursor.execute("DELETE FROM records WHERE id = (SELECT MAX(id) FROM records)")
                                
            st.write("Record Deleted!")

    @st.cache
    def color_red(val):
        color = 'red' if val == 1 else 'black'
        return 'color: %s' % color

    # Define the custom function
    @st.cache
    def highlight_row(row):
        if row["Winner's score"] > (row["Loser's score"] + 2): 
            css = 'background-color: green'
        else:
            css = 'background-color: black'

        return [css] * len(row)
        # is_one = s == 1
        # return ['background-color: lightgreen' if v else '' for v in is_one]    

    @st.cache
    def startIndexAtOne(df):
        # Create a new index
        new_index = [i + 1 for i in range(len(df))]
        # Reassign the new index to the DataFrame
        df.index = new_index
        # return df

    #BACKUP DB 
    @st.cache
    def backup_DB():
        shutil.copy2('fifa.db', f'db_backups/fifa_{now}.db')

    # ---- SIDEBAR ----
    # st.sidebar.header("Please Filter Here:")


    # ---- MAINPAGE ----
    first_name_column, first_score_column, second_score_column, second_name_column = st.columns([0.45, 0.1, 0.1, 0.45])
    lolo = "sfsf"
    with first_name_column:
        first_name = st.selectbox('Winner', players, index = 0, key = "first_name")
    with first_score_column:
        first_score = st.text_input("Score W")
    with second_score_column:
        second_score = st.text_input("Score L")
    with second_name_column:
        second_name = st.selectbox('Loser', players, index = 0, key = "second_name")


    if st.button("Save record"):
        record = {'Winner': first_name, 
                "Winner's score": first_score, 
                "Loser's score": second_score, 
                'Loser': second_name}
        backup_DB()
        save_record(record)

    #get sqlite db into df
    query = 'SELECT * FROM records'

    # Read the query results into a DataFrame
    df_records = pd.read_sql_query(query, conn)
    df_records.drop(['id'], axis = 1, inplace = True) 
    df_records["Winner's score"] = df_records["Winner's score"].astype(int)
    df_records["Loser's score"] = df_records["Loser's score"].astype(int)
    df_records['WW'] = 1 
    startIndexAtOne(df_records)
    df_records = df_records.sort_index(ascending=False)


    for x in range(len(df_records)):
        df_records["WW"].iloc[x] = 1 if df_records["Winner's score"].iloc[x] > (df_records["Loser's score"].iloc[x] + 2) else 0
                    
    # df_records.style.applymap(color_red, subset="WW" )   

    fc, sc, tc, foc = st.columns([0.45, 0.1, 0.1, 0.45])
    lolo = "sfsf"
    with fc:
        pass
    with sc:
        pass
    with tc:
        pass
    with foc:
        pass

    with tc:
        for winner in players:
            for loser in players:
                if winner == loser or winner == " " or loser == " ": # or players.index(winner) > players.index(loser)
                    pass
                else:
                    df_filtered = df_records[(df_records["Winner"].isin([winner, loser])) & (df_records["Loser"].isin([winner, loser]))][0:10]
                    
                    with sc:
                        pass
                        # winner
                        # loser
                        # leng = len(df_filtered)
                        # leng
                        # df_filtered
                        # df_filtered[0:10]    #.iloc[0:10]
                        # exit()

                    wins = len(df_filtered[df_filtered["Winner"] == winner])
                    losses = len(df_filtered) - wins
                    WL_RATIO = wins / (losses if losses != 0 else 1)
                    
                    goals_for = (df_filtered[df_filtered["Winner"] == winner]["Winner's score"].astype(int)).sum() + (df_filtered[df_filtered["Loser"] == winner]["Loser's score"].astype(int)).sum()
                    goals_against = (df_filtered[df_filtered["Winner"] == loser]["Winner's score"].astype(int)).sum() + (df_filtered[df_filtered["Loser"] == loser]["Loser's score"].astype(int)).sum()
                    goals_FA = goals_for / (goals_against if goals_against != 0 else 1)

                    WW_for = df_filtered[(df_filtered["Winner"] == winner) & (df_filtered["WW"] == 1)]["WW"].sum()
                    WW_against = df_filtered[(df_filtered["Winner"] == loser) & (df_filtered["WW"] == 1)]["WW"].sum()
                    WW_FA = WW_for/(WW_against if WW_against > 0 else 1)

                    record = ({
                        'Winner': winner, 
                        "Wins": wins,
                        'Loser': loser,
                        "Losses" : losses,
                        "Win/Loss": WL_RATIO, 
                        "Goals F/A": goals_FA, 
                        "Goals For": goals_for, 
                        "Goals Against": goals_against, 
                        "WW F/A": WW_FA,
                        "WW For": WW_for,
                        "WW Against": WW_against,
                        })

                    # print(record)

                    new_df = pd.DataFrame([record])
                    df_points = pd.concat([df_points, new_df], axis=0, ignore_index=True)
        goals_FA


    # df_log
    player_vs_player_expander = st.expander("PLAYER VS PLAYER RECORDS")
    with player_vs_player_expander:
        startIndexAtOne(df_points)
        df_points

    with foc:
        log_expander = st.expander("THE LOG")
        with log_expander:
            df_logg = df_points.groupby("Winner", as_index=False)["Win/Loss", "Goals F/A", "WW F/A"].sum()
            df_logg["Total"] = df_logg["Win/Loss"] + df_logg["Goals F/A"] + df_logg["WW F/A"]
            df_logg = df_logg.sort_values(by=['Total'], ascending=False)
            startIndexAtOne(df_logg)
            df_logg    

    # Apply the custom function to the DataFrame
    df_records.drop(['WW'], axis = 1, inplace = True) 
    styled_df_records = df_records.style.apply(highlight_row, axis=1)

    with fc:
        all_records_expander = st.expander("ALL RECORDS")
        with all_records_expander:
            styled_df_records
            if st.button("Delete last record"):
                # sql_cursor.execute("""DELETE FROM records""")
                backup_DB()
                delete_record()                        



    conn.commit()
    conn.close()


wholeApp()



# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
