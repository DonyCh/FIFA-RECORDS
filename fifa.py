import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import sqlite3

from streamlit import components

st.set_page_config(page_title="FIFA 19 Records", page_icon=":bar_chart:", layout="wide")

players = [" ", "DC", "Moose", "Amos", "Tuti", "Keda", "Berto", "Kevy"]

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
        st.write("Button was clicked!")
        # st.session_state.first_name = players[0]

def delete_record():    
        sql_cursor.execute("DELETE FROM records WHERE id = (SELECT MAX(id) FROM records)")
                            
        st.write("Record Deleted!")


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
    save_record(record)

#get sqlite db into df
query = 'SELECT * FROM records'

# Read the query results into a DataFrame
df_records = pd.read_sql_query(query, conn)
df_records.drop(['id'], axis = 1, inplace = True) 

fc, sc, tc, foc = st.columns([0.45, 0.1, 0.1, 0.45])
lolo = "sfsf"
with fc:
    df_records = df_records.sort_index(ascending=False)
    df_records
    if st.button("Delete last record"):
        delete_record()
with sc:
    pass
with tc:
    pass
with foc:
    pass

df_records["Winner's score"] = df_records["Winner's score"].astype(int)
df_records["Loser's score"] = df_records["Loser's score"].astype(int)

with tc:
    for winner in players:
        for loser in players:
            if winner == loser or winner == " " or loser == " ": # or players.index(winner) > players.index(loser)
                pass
            else:
                df_filtered = df_records[(df_records["Winner"].isin([winner, loser])) & (df_records["Loser"].isin([winner, loser]))][-10:]
                
                df_filtered['WW'] = 1 
                for x in range(len(df_filtered)):
                    df_filtered["WW"].iloc[x] = 1 if df_filtered["Winner's score"].iloc[x] > (df_filtered["Loser's score"].iloc[x] + 2) else 0
                
                with foc:
                    pass
                    # df_filtered

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


df_log
df_points
df_logg = df_points.groupby("Winner", as_index=False)["Win/Loss", "Goals F/A", "WW F/A"].sum()
df_logg["Total"] = df_logg["Win/Loss"] + df_logg["Goals F/A"] + df_logg["WW F/A"]
df_logg = df_logg.sort_values(by=['Total'], ascending=False)
df_logg                    


conn.commit()
conn.close()


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
