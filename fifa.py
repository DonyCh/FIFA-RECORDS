import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import sqlite3
import shutil
import datetime
import ftplib
import os

from streamlit import components
from io import BytesIO
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

# Add CSS style to the title
st.set_page_config(page_title="FIFA 22 Records",
                   page_icon=":bar_chart:", layout="wide")

st.markdown(
    f'''
        <style>
            div.block-container{{padding-top:{0}rem;}}
            div.sidebar .sidebar-content{{padding-top:{0}rem;}}
        </style>
        ''', unsafe_allow_html=True)

st.markdown(
    f"<h3 style='text-align: left; color: #FEC310;'>FIFA 22 RECORDS", unsafe_allow_html=True)


# GETTING CURRENT DATE
date_format = "%d/%m/%Y %H:%M"
now = datetime.datetime.now().strftime(date_format)
now = now.replace("/", "")
now = now.replace(" ", "_")
now = now.replace(":", "")


def wholeApp():

    # ---- DB ----
    conn = sqlite3.connect('fifa22.db', timeout=10.0)
    # conn = sqlite3.connect('fifa22.db')
    sql_cursor = conn.cursor()
    # this is the code for the settings
    sql_cursor.execute("""CREATE TABLE IF NOT EXISTS records(
        id integer PRIMARY KEY AUTOINCREMENT,
        Winner text NOT NULL,
        "Winner's score" text NULL,
        "Loser's score" text NOT NULL,
        Loser text NOT NULL
    )
    """)

    initial_load = sql_cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND name='players';""")
    initial_load = initial_load.fetchone()

    if initial_load is None:
        # PLAYERS
        players = [" ", "DC", "Moose", "Amos", "Tuti", "Keda", "Kevy"]
        sql_cursor.execute("""CREATE TABLE IF NOT EXISTS players(
            id integer PRIMARY KEY AUTOINCREMENT,
            Player text NOT NULL
        )
        """)

        sql_cursor.execute("""DELETE FROM players""")

        for x in range(len(players)):
            sql_cursor.execute(
                """ INSERT INTO players(Player) VALUES (?)""", (players[x],))
            # sql_cursor.execute(""" INSERT INTO players (Player)
            # SELECT @players[x]
            # WHERE NOT EXISTS (SELECT 1 FROM players);""")

    sql_cursor.execute('SELECT Player FROM players')
    players = [row[0] for row in sql_cursor.fetchall()]
    # players

    # ---- DF ----
    # columns_records = ['Winner', "Winner's score", "Loser's score", 'Loser']

    # df_records = pd.DataFrame(columns = columns_records)

    columns_log = ['Shiri', 'Games Played', 'Games Won', 'Games Lost',
                   'Won/Lost', 'Goals For', 'Goals Against', 'Goals Ratio',
                   'WW FOR', 'WW Against', 'WW Ratio']

    df_log = pd.DataFrame(columns=columns_log)

    columns_points = ['Winner', 'Wins', 'Loser', "Losses", "Win/Loss",
                      "Goals For", "Goals Against", "Goals F/A", "WW For", "WW Against", "WW F/A"]

    df_points = pd.DataFrame(columns=columns_points)
    df_points_all = pd.DataFrame(columns=columns_points)

    # Read the query results into a DataFrame
    query = 'SELECT * FROM records'
    df_records = pd.read_sql_query(query, conn)

    # try:
    #     hide_value = sql_cursor.execute(
    #         """SELECT AllRecords FROM buttons;""")
    #     hide_value = hide_value.fetchone()
    # except:
    #     hide_value = 1

    # ---- METHODS ----
    # Define a function to generate a download link for the database file

    def fix_primary():
        # Create a new table with the desired schema, including a new primary key column.
        sql_cursor.execute("""CREATE TABLE new_table (id INTEGER PRIMARY KEY AUTOINCREMENT, Winner text NOT NULL, "Winner's score" text NULL,
                    "Loser's score" text NOT NULL, Loser text NOT NULL);""")

        # Insert data from the old table into the new table.
        sql_cursor.execute(
            """INSERT INTO new_table (Winner, "Winner's score", "Loser's score", Loser) SELECT Winner, "Winner's score", "Loser's score", Loser FROM records;""")

        # Drop the old table.
        sql_cursor.execute('DROP TABLE records;')

        # Rename the new table to the old table name.
        sql_cursor.execute('ALTER TABLE new_table RENAME TO records;')

    def change_hide_value_in_db(value):
        sql_cursor.execute("""CREATE TABLE IF NOT EXISTS buttons(
            id integer PRIMARY KEY AUTOINCREMENT,
            AllRecords text NOT NULL
        )
        """)

        sql_cursor.execute(
            """ INSERT INTO buttons(AllRecords) VALUES (?)""", (value,))

    def download_database():
        # Create a BytesIO object and write the database content to it
        data = BytesIO()
        with open('fifa22.db', 'rb') as f:
            data.write(f.read())

        # Return a download button that the user can click to download the database file
        return st.download_button(label="Download DB", data=data.getvalue(), file_name="fifa22_d.db")

    # Create an ExcelWriter object with a temporary file path
    with pd.ExcelWriter('fifa22DB.xlsx', engine='xlsxwriter') as writer:
        df_records.to_excel(writer, sheet_name='Sheet1', index=False)

    # Define a function to generate a download link for the Excel file
    def download_excel_file():
        with open('fifa22DB.xlsx', 'rb') as f:
            data = f.read()
        return st.download_button(label="Download Excel", data=data, file_name="fifa22DB.xlsx")

    def upload_excel_file():
        # if st.button("Upload Excel"):
        # Create a file uploader in Streamlit
        uploaded_file = st.file_uploader("Choose an Excel file")

        #     if st.button("Upload"):
        # If a file was uploaded
        if uploaded_file is not None:

            # Read the Excel file into a DataFrame
            df = pd.read_excel(uploaded_file)

            # Connect to the SQLite database
            conn = sqlite3.connect('fifa22.db')
            sql_cursor = conn.cursor()

            # Create a table in the database to store the data
            df.to_sql('records', conn, if_exists='replace', index=False)

            sql_cursor.execute('PRAGMA table_info(records)')
            rows = sql_cursor.fetchall()
            columns = [col[1] for col in rows]

            # sql_cursor.execute('ALTER TABLE records DROP COLUMN new_table;')
            # sql_cursor.execute('DROP TABLE new_table;')

            # if 'id' in columns:
            #     sql_cursor.execute('ALTER TABLE records RENAME COLUMN id TO old_id;')

            # sql_cursor.execute('ALTER TABLE records ADD COLUMN id INTEGER PRIMARY KEY AUTOINCREMENT;')

            if 'id' in columns:
                sql_cursor.execute('ALTER TABLE records DROP COLUMN id;')

            fix_primary()

            # Close the database connection
            conn.close()

            # Show a success message
            st.success("File uploaded and data inserted into database.")

    def save_record(record):
        if record["Winner"] and record["Winner's score"] and record["Loser's score"] and record["Loser"]:
            sql_cursor.execute(""" INSERT INTO records(Winner, "Winner's score", "Loser's score", Loser) VALUES (?,?,?,?)""",
                               (record["Winner"], record["Winner's score"], record["Loser's score"], record["Loser"]))

            # df_records.append(record, ignore_index=True)
            st.write("Record Saved. Please do not overclick. Click once then wait!")
            # st.session_state.first_name = players[0]

    # @st.cache
    def delete_record():
        sql_cursor.execute(
            "DELETE FROM records WHERE id = (SELECT MAX(id) FROM records)")
        st.write("Record Deleted!")

    def remove_player(player_name):
        # sql_cursor.execute("DELETE FROM players WHERE Player = ?", (player_name,))
        sql_cursor.execute(
            "DELETE FROM players WHERE id = (SELECT max(id) FROM players WHERE Player = ?)", (player_name,))
        st.write("Player Removed!")

    def add_player(player_name):
        # if player_name:
        sql_cursor.execute(
            """ INSERT INTO players(Player) VALUES (?)""", (player_name,))
        with scol:
            st.write("Player Added!")

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
        new_index = [i for i in range(1, 1+len(df))]
        # Reassign the new index to the DataFrame
        df.index = new_index
        # return df

    # BACKUP DB
    @st.cache
    def backup_DB():
        shutil.copy2('fifa.db', f'db_backups/fifa_{now}.db')

    # ---- SIDEBAR ----
    # st.sidebar.header("Please Filter Here:")

    # ---- MAINPAGE ----
    first_name_column, first_score_column, second_score_column, second_name_column = st.columns([
                                                                                                0.45, 0.1, 0.1, 0.45])
    with first_name_column:
        first_name = st.selectbox('Winner', players, index=0, key="first_name")
    with first_score_column:
        first_score = st.text_input("Score W")
    with second_score_column:
        second_score = st.text_input("Score L")
    with second_name_column:
        second_name = st.selectbox(
            'Loser', players, index=0, key="second_name")

    if st.button("Save record"):
        record = {'Winner': first_name,
                  "Winner's score": first_score,
                  "Loser's score": second_score,
                  'Loser': second_name}
        backup_DB()
        save_record(record)

    # get sqlite db into df
    query = 'SELECT * FROM records'

    # Read the query results into a DataFrame
    df_records = pd.read_sql_query(query, conn)
    df_records.drop(['id'], axis=1, inplace=True)
    df_records["Winner's score"] = df_records["Winner's score"].astype(int)
    df_records["Loser's score"] = df_records["Loser's score"].astype(int)
    df_records['WW'] = 1
    startIndexAtOne(df_records)
    df_records = df_records.sort_index(ascending=False)

    for x in range(len(df_records)):
        df_records["WW"].iloc[x] = 1 if df_records["Winner's score"].iloc[x] > (
            df_records["Loser's score"].iloc[x] + 2) else 0

    # df_records.style.applymap(color_red, subset="WW" )

    # filterc = st.columns
    filter_expander = st.expander("FILTER PLAYERS")
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
                # or players.index(winner) > players.index(loser)
                if winner == loser or winner == " " or loser == " ":
                    pass
                else:
                    df_filtered = df_records[(df_records["Winner"].isin([winner, loser])) & (
                        df_records["Loser"].isin([winner, loser]))][0:10]

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

                    goals_for = (df_filtered[df_filtered["Winner"] == winner]["Winner's score"].astype(int)).sum(
                    ) + (df_filtered[df_filtered["Loser"] == winner]["Loser's score"].astype(int)).sum()
                    goals_against = (df_filtered[df_filtered["Winner"] == loser]["Winner's score"].astype(
                        int)).sum() + (df_filtered[df_filtered["Loser"] == loser]["Loser's score"].astype(int)).sum()
                    goals_FA = goals_for / \
                        (goals_against if goals_against != 0 else 1)

                    WW_for = df_filtered[(df_filtered["Winner"] == winner) & (
                        df_filtered["WW"] == 1)]["WW"].sum()
                    WW_against = df_filtered[(df_filtered["Winner"] == loser) & (
                        df_filtered["WW"] == 1)]["WW"].sum()
                    WW_FA = WW_for/(WW_against if WW_against > 0 else 1)

                    record = ({
                        'Winner': winner,
                        "Wins": wins,
                        'Loser': loser,
                        "Losses": losses,
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
                    df_points = pd.concat(
                        [df_points, new_df], axis=0, ignore_index=True)

                    # # FOR ALL RECORDS
                    # if hide_value == 0:
                    #     df_filtered_all = df_records[(df_records["Winner"].isin([winner, loser])) & (
                    #         df_records["Loser"].isin([winner, loser]))]

                    #     with sc:
                    #         pass
                    #         # winner
                    #         # loser
                    #         # leng = len(df_filtered_all)
                    #         # leng
                    #         # df_filtered_all
                    #         # df_filtered_all[0:10]    #.iloc[0:10]
                    #         # exit()

                    #     wins = len(
                    #         df_filtered_all[df_filtered_all["Winner"] == winner])
                    #     losses = len(df_filtered_all) - wins
                    #     WL_RATIO = wins / (losses if losses != 0 else 1)

                    #     goals_for = (df_filtered_all[df_filtered_all["Winner"] == winner]["Winner's score"].astype(int)).sum(
                    #     ) + (df_filtered_all[df_filtered_all["Loser"] == winner]["Loser's score"].astype(int)).sum()
                    #     goals_against = (df_filtered_all[df_filtered_all["Winner"] == loser]["Winner's score"].astype(
                    #         int)).sum() + (df_filtered_all[df_filtered_all["Loser"] == loser]["Loser's score"].astype(int)).sum()
                    #     goals_FA = goals_for / \
                    #         (goals_against if goals_against != 0 else 1)

                    #     WW_for = df_filtered_all[(df_filtered_all["Winner"] == winner) & (
                    #         df_filtered_all["WW"] == 1)]["WW"].sum()
                    #     WW_against = df_filtered_all[(df_filtered_all["Winner"] == loser) & (
                    #         df_filtered_all["WW"] == 1)]["WW"].sum()
                    #     WW_FA = WW_for/(WW_against if WW_against > 0 else 1)

                    #     record = ({
                    #         'Winner': winner,
                    #         "Wins": wins,
                    #         'Loser': loser,
                    #         "Losses": losses,
                    #         "Win/Loss": WL_RATIO,
                    #         "Goals F/A": goals_FA,
                    #         "Goals For": goals_for,
                    #         "Goals Against": goals_against,
                    #         "WW F/A": WW_FA,
                    #         "WW For": WW_for,
                    #         "WW Against": WW_against,
                    #     })

                    #     # print(record)

                    #     new_df = pd.DataFrame([record])
                    #     df_points_all = pd.concat(
                    #         [df_points_all, new_df], axis=0, ignore_index=True)
        goals_FA

    # df_log
    player_vs_player_expander = st.expander("PLAYER VS PLAYER RECORDS")
    with player_vs_player_expander:
        startIndexAtOne(df_points)
        df_points

    # if hide_value == 0:
    #     player_vs_player_expander_all = st.expander(
    #         "ALL PLAYER VS PLAYER RECORDS")
    #     with player_vs_player_expander_all:
    #         startIndexAtOne(df_points_all)
    #         df_points_all

    with foc:
        log_expander = st.expander("THE LOG")
        with log_expander:
            df_logg = df_points.groupby("Winner", as_index=False)[
                "Win/Loss", "Goals F/A", "WW F/A"].sum()
            df_logg["Total"] = df_logg["Win/Loss"] + \
                df_logg["Goals F/A"] + df_logg["WW F/A"]
            # df_logg[""] = ""
            # df_logg["/50"] = df_logg[df_logg["Winner"] == df_logg["Win/Loss"]] df_points[df_points["Winner"] == df_logg["Win/Loss"]].sum()
            df_logg.sort_values(
                by=['Total'], ascending=False).reset_index(drop=True, inplace=True)
            df_logg.index += 1
            # startIndexAtOne(df_logg)
            df_logg

    # Apply the custom function to the DataFrame
    df_records.drop(['WW'], axis=1, inplace=True)

    with filter_expander:
        selected_players = st.multiselect(
            'Select players:', players, default=players)

    with fc:
        all_records_expander = st.expander("ALL RECORDS")
        with all_records_expander:
            df_records = df_records[(df_records["Winner"].isin(
                selected_players)) & (df_records["Loser"].isin(
                    selected_players))]
            styled_df_records = df_records.style.apply(highlight_row, axis=1)
            styled_df_records
            if st.button("Delete last record"):
                # sql_cursor.execute("""DELETE FROM records""")
                backup_DB()
                delete_record()

    # SPECIAL BUTTONS
    specials = st.expander("SIYANA NAZVO")
    with specials:
        fcol, scol, tcol, focol, ficol, sicol = st.columns(
            [0.2, 0.1, 0.35, 0.15, 0.15, 0.15])
        with fcol:
            password = st.text_input("Password")
        with scol:
            if password == "12354":
                player_name = st.text_input("Player Name")
                if st.button("Add Player"):
                    add_player(player_name.strip())
                if st.button("Remove Player"):
                    remove_player(player_name.strip())
        # with tcol:
        #     if hide_value == 0:
        #         if st.button("Hide All Records"):
        #             change_hide_value_in_db(1)
        #     elif hide_value == 1:
        #         if st.button("Unhide All Records"):
        #             change_hide_value_in_db(0)
        #     else:
                if st.button("Initiate Hide Button"):
                    change_hide_value_in_db(0)
        with focol:
            # Display the download link in the Streamlit app
            if password == "12354":
                download_database()
        with ficol:
            if password == "12354":
                download_excel_file()
        with sicol:
            if password == "12354":
                upload_excel_file()

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
