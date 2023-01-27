import pickle
import streamlit_authenticator as stauth
import os
import pandas as pd  # pip install pandas openpyxl
import numpy as np
import plotly.express as px
from requests import session  # pip install plotly-express
import streamlit as st  # pip install streamlit
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly
import calendar
import datetime
import types
import random

from pathlib import Path
from PIL import Image
from common import set_page_container_style, create8Columns, create9Columns, markdownText, addShiftAbility
from dropdownData import dropdown_lists, default_lists

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
im = Image.open("logo.png")
st.set_page_config(page_title="Bravo Petroleum Dashboard",
                   page_icon=im, layout="wide")

set_page_container_style(
    max_width=1100, max_width_100_percent=True,
    padding_top=0, padding_right=10, padding_left=5, padding_bottom=10,
    color='black', background_color='white',
)

# st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)

# --- USER AUTHENTICATION
names = ["Donald Chiwundura", "Blessing Nyambuya", "Itai Mukudu", "User"]
usernames = ["DC", "bnyambuya", "IM", "User"]
HUSH = "JOKE"

# load hashed passwordsG
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:  # rb = readby
    hashed_passwords = pickle.load(file)

credentials = {
    "usernames": {
        usernames[0]: {
            "name": names[0],
            "password": hashed_passwords[0]
        },
        usernames[1]: {
            "name": names[1],
            "password": hashed_passwords[1]
        },
        usernames[2]: {
            "name": names[2],
            "password": hashed_passwords[2]
        }
    }
}

authenticator = stauth.Authenticate(
    credentials, "olympus_dashboard", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    # reset_password_button = st.sidebar.button("Reset Password")
    # if reset_password_button:
    #     # authenticator.reset_password(username, 'Reset password')
    #     try:
    #         if authenticator.reset_password(username, 'Reset password'):
    #             st.success('Password modified successfully')
    #     except Exception as e:
    #         st.error(e)
    #     st.stop()
    # ---- READ EXCEL ----
    # st.write(st.session_state)
    drivewayExpander = st.expander("UPLOAD DRIVEWAYS HERE")
    if "ardbennie" not in st.session_state:
        st.session_state['ardbennie'] = st.session_state['greendale'] = st.session_state['accounts'] = "unloaded"
        st.session_state['button'] = "not pressed"

    if "num" not in st.session_state:
        st.session_state['num'] = random.randint(1, 1000)
        # st.session_state['num']
        # random number then ttl = 1 day

    # st.session_state['button']
    with drivewayExpander:
        aD, gD, AS = st.columns(3)
        with aD:
            ardbennieDriveway = st.file_uploader("Upload ARDBENNIE DRIVEWAY")
            if ardbennieDriveway:
                st.session_state['ardbennie'] = "loaded"
        with gD:
            greendaleDriveway = st.file_uploader("Upload GREENDALE DRIVEWAY")
            if greendaleDriveway:
                st.session_state['greendale'] = "loaded"
        with AS:
            accountsStatement = st.file_uploader("Upload Accounts Statement")
            if accountsStatement:
                st.session_state['accounts'] = "loaded"
        a, b, c = st.columns([0.45, 0.2, 0.4])
        with b:
            updateButton = st.button("Update Driveways")

    def save_uploadedfile(uploadedfile):
        path = f"{name}"
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, uploadedfile.name), "wb") as f:
            f.write(uploadedfile.getbuffer())

    if updateButton:
        if ((ardbennieDriveway is not None) and (greendaleDriveway is not None) and (accountsStatement is not None)):
            save_uploadedfile(ardbennieDriveway)
            save_uploadedfile(greendaleDriveway)
            save_uploadedfile(accountsStatement)
            st.session_state['button'] = "pressed"
            st.success("Updated Files")
            # get_data_from_excel.clear()
        else:
            with drivewayExpander:
                a, b, c = st.columns([0.45, 0.2, 0.4])
                with b:
                    st.write("Upload all documents")
        # df = create_df()

    # if (st.session_state['button'] == "not pressed" or st.session_state['ardbennie'] == "unloaded" or st.session_state['greendale'] == "unloaded" or st.session_state['accounts'] == "unloaded"):
    #     st.stop()

    # METHODS
    def shiftDf(shift):
        shift_values = addShiftAbility(month, shift)

        if (shift_values["shift_endDay"] > shift_values["last_day"]):
            shift_startMonth = int(month)
            shift_endMonth = int(month) + 1
            shift_endDay = (
                shift_values["shift_endDay"] - shift_values["last_day"])

            filteredDf1 = df[(df['Site'].isin(site)) & (df["Month"] == shift_startMonth) & (
                df["Day"] >= shift_values["shift_startDay"])]
            filteredDf2 = df[(df['Site'].isin(site)) & (
                df["Month"] == shift_endMonth) & (df["Day"] < shift_endDay)]
            filteredDf = filteredDf1.append(filteredDf2, ignore_index=True)
            # filteredDf
        else:
            filteredDf = df[(df['Site'].isin(site)) & (df["Month"] == int(month)) & (
                df["Day"] >= shift_values["shift_startDay"]) & (df["Day"] < shift_values["shift_endDay"])]

        return filteredDf

    def shiftDfNoSite(shift, df):
        shift_values = addShiftAbility(month, shift)

        if (shift_values["shift_endDay"] > shift_values["last_day"]):
            shift_startMonth = int(month)
            shift_endMonth = int(month) + 1
            shift_endDay = shift_values["shift_endDay"] - \
                shift_values["last_day"]

            filteredDf1 = df[(df["Month"] == shift_startMonth) & (
                df["Day"] >= shift_values["shift_startDay"])]
            filteredDf2 = df[(df["Month"] == shift_endMonth)
                             & (df["Day"] < shift_endDay)]
            filteredDf = filteredDf1.append(filteredDf2, ignore_index=True)
        else:
            filteredDf = df[(df["Month"] == int(month)) & (
                df["Day"] >= shift_values["shift_startDay"]) & (df["Day"] < shift_values["shift_endDay"])]

        return filteredDf

    def calculateMonthName(month):
        months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                  7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

        try:
            return months[month]
        except:
            return "All"

    def calculateMonthNameShort(month):
        months = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                  7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

        try:
            return months[month]
        except:
            return "All"

    def calculateMonthNumber(month):
        months = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                  "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

        try:
            return months[month]
        except:
            return "All"

    def xlookup(lookup_value, lookup_array, return_array, if_not_found: str = ''):
        match_value = return_array.loc[lookup_array <= lookup_value]
        if match_value.empty:
            return f'"{lookup_value}" not found!' if if_not_found == '' else if_not_found
        else:
            return match_value.tolist()[-1]

    # image_file = st.file_uploader("Upload An Image",type=['png','jpeg','jpg'])
    # if image_file is not None:
    #     file_details = {"FileName":image_file.name,"FileType":image_file.type}
    #     st.write(file_details)
    #     img = load_image(image_file)
    #     st.image(img,height=250,width=250)
        # with open(os.path.join("tempDir",image_file.name),"wb") as f:
        #   f.write(image_file.getbuffer())
    #     st.success("Saved File")

    # @st.cache(hash_funcs={dict: lambda _: None}) # hash_funcs because dict can't be hashed
    # def get_dic_of_fig():
    #     dico_of_fig = {}
    #     for param in list_of_params:
    #         plotly_fig = plot_plotly_fig(param)
    #         dico_of_fig [param] = plotly_fig
    #     return dico_of_fig

    # dico_of_fig = get_dic_of_fig() # this dic is cached

    # if 'aD' not in st.session_state:
    #     st.session_state['aD'] = 'uploaded'
    # names = x.keys()

    # @st.cache(show_spinner=False)
    @st.experimental_memo(show_spinner=False, ttl=86400)
    def get_data_from_excel(driveway, site, num):
        file_name = (driveway.split()[1]).capitalize()
        df = pd.read_excel(
            # io=greendaleDriveway,
            # io=driveway,
            io=f"{name}/{driveway}.xlsx",
            engine="openpyxl",
            # sheet_name=f"detailed driveway 2022 ",
            sheet_name=f"{file_name} Site",
            header=7,
            usecols="B, D, E, G, H, T, U, AK, AL, AR, AS, DG, DH, DK, DJ, AM, AT, BE, BH",
            # skiprows=5,
            # nrows=1000,
        )
        # DG = COUPONS DIESEL; DH = COUPONS PETROL;
        # DJ(DQ) = DrawdownP; DK(DR) = DrawdownD;
        # AR = DieselTo; AS = Add back volume of test.1;
        # AK = PetrolTo; AL = Add back volume of test;
        # B = DATE; D = L; E = L.1; U = DIESEL.4; T = BLEND.4;

        # DI = CouponsD; DJ = Coupons(P)

        # return df
        df = df.drop(df.index[range(0, 5)])
        df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True)
        df["Year"] = df['DATE'].dt.year
        df["Month"] = df['DATE'].dt.month
        df["Day"] = df['DATE'].dt.day
        df = df.fillna(0)
        # df
        # t1 = type(df["COUPONS DIESEL"].iloc[350])
        # t2 = type(df["DIESEL.4"].iloc[350])
        # t1
        # t2

        df["CouponsD"] = df["COUPONS DIESEL"]/df["DIESEL.4"]
        df["CouponsP"] = df["COUPONS PETROL"]/df["BLEND.4"]
        df["CashD"] = df["DieselTotal Sales"] - \
            (df["DRAWDOWN - DIESEL"]/df["DIESEL.4"]) - \
            df["CouponsD"]-df["Add back volume of test.1"]
        df["CashP"] = df["BLEND Total Sales"] - \
            (df["DRAWDOWN - PETROL"]/df["BLEND.4"]) - \
            df["CouponsP"]-df["Add back volume of test"]
        df["DrawdownsD"] = df["DRAWDOWN - DIESEL"]/df["DIESEL.4"]
        df["DrawdownsP"] = df["DRAWDOWN - PETROL"]/df["BLEND.4"]

        df = df[(df["Month"] != 0) & (df["Year"] == 2022) & ((df["DieselTotal Sales"] + df["BLEND Total Sales"]) != 0)][
            ["Month", "Day", "CouponsD", "CouponsP", "DrawdownsD", "DrawdownsP", "CashD", "CashP", "L.1", "L",
                "Diesel Stock Bal ", "BLEND Stock Bal ", "TOTAL.2", "TOTAL.3", "DIESEL.4", "BLEND.4", "DIESEL", "BLEND"]]

        # df = df.groupby(["Month", "Day"], as_index = False)[
        # "CouponsD", "CouponsP", "DrawdownsD", "DrawdownsP", "CashD", "CashP", "L.1", "L", "Diesel Stock Bal ", "BLEND Stock Bal "].sum()

        df.rename(columns={"L.1": "DelieveriesD"}, inplace=True)
        df.rename(columns={"L": "DelieveriesP"}, inplace=True)
        df.rename(columns={"TOTAL.2": "BlendDip"}, inplace=True)
        df.rename(columns={"TOTAL.3": "DieselDip"}, inplace=True)
        df.rename(columns={"BLEND.4": "SellingPriceP"}, inplace=True)
        df.rename(columns={"DIESEL.4": "SellingPriceD"}, inplace=True)
        df.rename(columns={"BLEND": "BuyingPriceP"}, inplace=True)
        df.rename(columns={"DIESEL": "BuyingPriceD"}, inplace=True)

        df["CouponsT"] = df["CouponsD"]+df["CouponsP"]
        df["DrawdownsT"] = df["DrawdownsD"]+df["DrawdownsP"]
        df["CashT"] = df["CashD"]+df["CashP"]
        df["DelieveriesT"] = df["DelieveriesD"]+df["DelieveriesP"]
        df["StockVarianceD"] = df["DieselDip"] - df["Diesel Stock Bal "]
        df["StockVarianceP"] = df["BlendDip"] - df["BLEND Stock Bal "]
        df["Site"] = site

        df["Month"] = df["Month"].astype(int)
        df["Day"] = df["Day"].astype(int)

        df["TotalD"] = df["CouponsD"]+df["DrawdownsD"]+df["CashD"]
        df["TotalP"] = df["CouponsP"]+df["DrawdownsP"]+df["CashP"]
        df["CumulativeTD"] = df["TotalD"].cumsum()
        df["CumulativeTP"] = df["TotalP"].cumsum()

        balance_bfD = df["DieselDip"].iloc[0]
        balance_bfP = df["BlendDip"].iloc[0]

        # first_delievery_ind = df['DelieveriesD'].ne(0).idxmax()
        # df["CumDeD"] = (df["DelieveriesD"].iloc[first_delievery_ind:]).cumsum() + balance_bfD

        df["CumDeD"] = (df["DelieveriesD"].iloc[2:]).cumsum() + balance_bfD
        df["CumDeP"] = (df["DelieveriesP"].iloc[4:]).cumsum() + balance_bfP
        df = df.fillna(0)

        # df["BuyingPriceD"] = 1.19
        # df["BuyingPriceD"].iloc[12:19] = 1.12
        # df["BuyingPriceP"] = 1.32

        df["ProfitMarginD"] = df["SellingPriceD"] - df["BuyingPriceD"]
        df["ProfitMarginP"] = df["SellingPriceP"] - df["BuyingPriceP"]

        # val = xlookup(df['CumulativeTD'], df['CumDeD'],df2['purchase'])
        # val = xlookup(24411, df['CumDeD'], df["CumDeD"])
        # val

        df['1D'] = df['CumulativeTD'].apply(
            xlookup, args=(df['CumDeD'], df["CumDeD"]))
        df['2D'] = df['CumulativeTD'].apply(
            xlookup, args=(df['CumDeD'], df["ProfitMarginD"]))
        df['3D'] = (df['CumulativeTD']-df['TotalD']).apply(xlookup,
                                                           args=(df['CumDeD'], df["ProfitMarginD"]))

        df['1P'] = df['CumulativeTP'].apply(
            xlookup, args=(df['CumDeP'], df["CumDeP"]))
        df['2P'] = df['CumulativeTP'].apply(
            xlookup, args=(df['CumDeP'], df["ProfitMarginP"]))
        df['3P'] = (df['CumulativeTP']-df['TotalP']).apply(xlookup,
                                                           args=(df['CumDeP'], df["ProfitMarginP"]))

        df["ProfitD"] = ((df['CumulativeTD']-df['1D'])*df['2D']) + \
            ((df['1D']-(df['CumulativeTD']-df['TotalD']))*df['3D'])
        df["ProfitP"] = ((df['CumulativeTP']-df['1P'])*df['2P']) + \
            ((df['1P']-(df['CumulativeTP']-df['TotalP']))*df['3P'])
        # df["ProfitP"]
        # max_date = [df["Month"].max(), df["Day"].max()]
        # max_date

        # return val
        return df

    if updateButton:
        if 'num' not in st.session_state:
            st.session_state['num'] = 0
        else:
            st.session_state['num'] += random.randint(1, 1000)
        # get_data_from_excel.clear()
        # use session in place of name
    # def create_df():
    with st.spinner("Loading data..."):
        # try:
        dfG = get_data_from_excel(
            "DRIVEWAY GREENDALE + REPORTS", "Greendale", f"{name}{st.session_state['num']}")
        # "JTrade Control-  Greendale 2022", "Greendale", f"{name}{st.session_state['num']}")
        dfA = get_data_from_excel(
            "DRIVEWAY ARDBENNIE + REPORTS", "Ardbennie", f"{name}{st.session_state['num']}")
        # "Bravo Trade Control- Ardbennie 2022", "Ardbennie", f"{name}{st.session_state['num']}")
        df = dfA.append(dfG, ignore_index=True)
        # except:
        #     st.write("Please Upload driveways and Account files")
        #     st.stop()

    # return df
    # df
    # st.dataframe(df)

    @st.cache
    # def get_dd_df_data_from_csv(retail_or_commercial):
    #     dd_df = pd.read_csv("../Collected and Engineered Data/Bravo_2.csv")
    #     dd_df = dd_df[["Date", "Company", "Product", "Narration", "Vehicle Reg", "Fuel"]]
    #     if(retail_or_commercial == "retail"):
    #         dd_df = dd_df[(dd_df["Fuel"] != 0) & (dd_df["Narration"] != "Coupons") & (dd_df["Narration"] != "Delivery")]
    #     elif(retail_or_commercial == "commercial"):
    #         dd_df = dd_df[(dd_df["Fuel"] != 0) & (dd_df["Narration"] != "Coupons") & (dd_df["Narration"] == "Delivery")]
    #     dd_df['Date'] = pd.to_datetime(dd_df['Date'], dayfirst=True)
    #     dd_df["Month"] = dd_df['Date'].dt.month
    #     dd_df["Day"] = dd_df['Date'].dt.day
    #     return dd_df
    @st.cache
    # def get_profit_data_from_excel():
    #     df = pd.read_excel("../Collected and Engineered Data/Sheets/Bravo_cons_breakdown.xlsx")
    #     return df
    # profit_df = get_profit_data_from_excel()
    # profit_df
    # @st.cache(show_spinner=False)
    @st.experimental_memo(show_spinner=False, ttl=86400)
    def read_excel_sheets(sheet):
        df = pd.read_excel(
            # io=accountsStatement,
            io="Accounts Statements 2022.xlsx",
            engine="openpyxl",
            sheet_name=sheet,
            # header = header,
            # usecols = "B, D, E, T, U, AK, AL, AR, AS, DG, DH, DK, DJ, AM, AT, BE, BH",
            # skiprows=5,
            nrows=1000,
        )

        # rename columns header
        col = df.columns[0]
        df[col] = df[col].astype(str, copy=False)
        # df[col] = df[col].fillna(0)
        df[col] = pd.to_datetime(df[col], errors='ignore', dayfirst=True)

        # df[col] = df[col].str.strip()
        # index_num = df.index[df[col]=='Date'].tolist()[0]
        # df[col] = df[col].str.capitalize()
        index_num = df.index[df[col].str.contains(
            'Date', na=False, case=False)].tolist()[0]
        df = df.rename(columns=df.iloc[index_num])
        df = df.drop(df.index[range(0, index_num+1)])

        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.capitalize()
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce', dayfirst=True)
        df["Year"] = df['Date'].dt.year
        df["Month"] = df['Date'].dt.month
        df["Day"] = df['Date'].dt.day
        df = df[(df["Month"] != 0) & (df["Year"] == 2022)]
        df["Company"] = sheet
        df["Month"] = df["Month"].astype(int)
        df["Day"] = df["Day"].astype(int)
        # df["Description"] = df["Description"].str.strip()

        return df

    sheet_names_df = pd.read_excel(
        # io=accountsStatement,
        io="Accounts Statements 2022.xlsx",
        engine="openpyxl",
        sheet_name="REPORT",
        header=1,
        nrows=41
    )

    # col = df.columns[0]
    # index_num = df.index[df[col].str.contains('TOTAL', na=False)].tolist()[0]
    # df = df.drop(df.index[range(index_num, index_num+100)])

    sheet_names = list(sheet_names_df["ACCOUNT NAME"])
    # sheet_names

    # df = read_excel_sheets("CHASPERS")
    # df
    # ---- SIDEBAR ----
    authenticator.logout("logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    st.sidebar.header("Filter Data Here:")

    retail_or_commercial = st.sidebar.radio(
        "Filter by retail or commercial sales",
        ('Retail', 'Commercial'), horizontal=True)

    lists = dropdown_lists("", "", "", "", "", "", "", df)
    day_or_shift, day, shift = "", "All", "All"

    data = st.sidebar.selectbox(
        'Select which data to view',
        lists["data"])
    # lists = dropdown_lists(data, "", "", "", "", "", "", df)

    # if(data != "Detailed Drawdowns"):
    chart = st.sidebar.selectbox(
        'Select which chart to view',
        # lists["chart"], index = 2)
        lists["chart"])
    site = ["Both Sites", "Ardbennie", "Greendale"]
    if (data != "Detailed Drawdowns"):
        site = st.sidebar.selectbox(
            'Select which site to view',
            lists["site"], key="ss")
        if (site == "Combined"):
            site = ["Both Sites", "Ardbennie", "Greendale"]
        elif (site == "Ardbennie"):
            site = ["Ardbennie"]
        elif (site == "Greendale"):
            site = ["Greendale"]
        else:
            site = site

    product = st.sidebar.selectbox(
        'Select which product to view',
        lists["product"])

    month = st.sidebar.selectbox(
        'Select which month to view',
        # ["All"] + [str(x) for x in range(1, df["Month"].max()+1)])
        ["All"] + [calculateMonthName(x) for x in range(1, df["Month"].max()+1)])

    month = calculateMonthNumber(month)

    # month
    # CALCULATIONS
    if (month != "All"):
        last_day = df[df["Month"] == int(month)]["Day"].max()

        def numberOfShifts():

            def firstTuesday():
                for x in range(1, 8):
                    ans = datetime.date(2022, int(month), x)
                    if (ans.strftime("%A") == "Tuesday"):
                        return x

            number_of_shifts = 0
            tuesday = firstTuesday()
            while tuesday < last_day:
                number_of_shifts += 1
                tuesday = tuesday+7

            return {"ft": firstTuesday(),
                    "ns": number_of_shifts}

        number_of_shifts = numberOfShifts()["ns"]
        first_tuesday = numberOfShifts()["ft"]

    def caculateMonthlyAverage():
        for x in range(1, df["Month"].max()+1):
            dfToUse = df[(df['Site'].isin(site))]
            couponsD_MA = (dfToUse["CouponsD"].sum())
            cashD_MA = (dfToUse["CashD"].sum())
            drawdownsD_MA = (dfToUse["DrawdownsD"].sum())
            couponsP_MA = (dfToUse["CouponsP"].sum())
            cashP_MA = (dfToUse["CashP"].sum())
            drawdownsP_MA = (dfToUse["DrawdownsP"].sum())

        monthly_averages = {"couponsD_MA": round(couponsD_MA/df["Month"].max(), 1),
                            "cashD_MA": round(cashD_MA/df["Month"].max(), 1),
                            "drawdownsD_MA": round(drawdownsD_MA/df["Month"].max(), 1),
                            "totalD_MA": round(couponsD_MA/df["Month"].max() +
                                               cashD_MA/df["Month"].max() + drawdownsD_MA/df["Month"].max(), 1),
                            "couponsP_MA": round(couponsP_MA/df["Month"].max(), 1),
                            "cashP_MA": round(cashP_MA/df["Month"].max(), 1),
                            "drawdownsP_MA": round(drawdownsP_MA/df["Month"].max(), 1),
                            "totalP_MA": round(couponsP_MA/df["Month"].max() +
                                               cashP_MA/df["Month"].max() + drawdownsP_MA/df["Month"].max(), 1)}

        return monthly_averages

    def monthValues(month):
        if (month == "All"):
            dfToUse = df[(df['Site'].isin(site))]
        else:
            dfToUse = df[(df['Site'].isin(site)) & (df["Month"] == int(month))]

        month_values = {"couponsD_month": round((dfToUse["CouponsD"].sum()), 1),
                        "cashD_month": round((dfToUse["CashD"].sum()), 1),
                        "drawdownsD_month": round((dfToUse["DrawdownsD"].sum()), 1),
                        "totalD_month": round((dfToUse["CouponsD"].sum()) +
                                              (dfToUse["CashD"].sum()) +
                                              (dfToUse["DrawdownsD"].sum()), 1),
                        "couponsP_month": round((dfToUse["CouponsP"].sum()), 1),
                        "cashP_month": round((dfToUse["CashP"].sum()), 1),
                        "drawdownsP_month": round((dfToUse["DrawdownsP"].sum()), 1),
                        "totalP_month": round((dfToUse["CouponsP"].sum()) +
                                              (dfToUse["CashP"].sum()) +
                                              (dfToUse["DrawdownsP"].sum()), 1)}

        return month_values

    def caculateMonthlyProfitAverage():
        for x in range(1, int(df["Month"].max())+1):
            dfToUse = df[(df['Site'].isin(site))]
            profitD_MA = (dfToUse["ProfitD"].sum())
            profitP_MA = (dfToUse["ProfitP"].sum())

        monthly_averages = {"profitD_MA": round(profitD_MA/df["Month"].max(), 2),
                            "profitP_MA": round(profitP_MA/df["Month"].max(), 2),
                            "gross_MA": round(profitD_MA/df["Month"].max()
                                              + profitP_MA/df["Month"].max(), 2)}

        return monthly_averages

    def profitValues(month):
        if (month == "All"):
            dfToUse = df[(df['Site'].isin(site))]
        else:
            dfToUse = df[(df['Site'].isin(site)) & (df["Month"] == int(month))]

        profit_values = {"profitD": round((dfToUse["ProfitD"].sum()), 2),
                         "profitP": round((dfToUse["ProfitP"].sum()), 2),
                         "gross": round((dfToUse["ProfitD"].sum()) + (dfToUse["ProfitP"].sum()), 2)}

        return profit_values

    monthly_averages = caculateMonthlyAverage()
    all_months_values = monthValues("All")
    month_values = monthValues(month)
    latest_month_values = monthValues(str(df["Month"].max()))

    profit_averages = caculateMonthlyProfitAverage()
    all_profit_values = profitValues("All")
    profit_values = profitValues(month)
    latest_profit_values = profitValues((df["Month"].max()))

    # ---- SIDEBAR ---- continued
    if (month != "All"):
        day_or_shift = st.sidebar.radio(
            "Filter by day or shift",
            ('Day', 'Shift'), horizontal=True)
        if (day_or_shift == "Day"):
            day = st.sidebar.selectbox(
                'Select which day to view',
                ["All"] + [str(x) for x in range(1, last_day+1)])
        else:
            x = number_of_shifts
            if ((first_tuesday + 7*(x-1) + 6) > last_day):
                shift_endDay = (first_tuesday + 7*(x-1) + 6) - last_day
                s_list = [(str(x) + f" => {first_tuesday + 7*(x-1)} - {first_tuesday + 7*(x-1) + 6}")
                          for x in range(1, number_of_shifts)]
                s_list.append(
                    (str(x) + f" => {first_tuesday + 7*(x-1)} - {shift_endDay}"))
                shift = st.sidebar.selectbox(
                    'Select which shift to view',
                    ["All"] + s_list)
            else:
                shift = st.sidebar.selectbox(
                    'Select which shift to view',
                    ["All"] + [(str(x) + f" => {first_tuesday + 7*(x-1)} - {first_tuesday + 7*(x-1) + 6}")
                               for x in range(1, number_of_shifts+1)])

            shift = shift.split()[0]
    # shift
    # first_tuesday

    # if(data == "Detailed Drawdowns"):
    # if(data == "Type of Consumption"):
    # if (data == "Detailed Drawdowns"):
    #     if (chart == 'Pie' and (product == 'Both' or product == 'Petrol' or product == 'Diesel')):
    #         pass
    #     else:
    #         company = st.sidebar.selectbox(
    #             'Select which company to view',
    #             dd_df['Company'].unique())
            # lists["company"])

    #### ---- MAINPAGE ---- ####
    if (site[0] == "Both Sites"):
        site_name = "Both"
    else:
        site_name = site[0]
    lle, left_column, middle_column, right_column = st.columns([0.4, 3, 2, 1])
    with lle:
        st.image(im)
    with left_column:
        st.markdown(
            f"<h1 style='text-align: left; color: #ADD8E6;'>Bravo Petroleum Dashboard", unsafe_allow_html=True)
        # st.title("Bravo Petroleum Dashboard") #Olympus Petroleum
    with middle_column:
        st.markdown(
            f"<h4 style='text-align: left; color: red;'>Site: {site_name} Month: {calculateMonthName(month)}</h4", unsafe_allow_html=True)
    with right_column:
        M = df["Month"].max()
        D = df[df["Month"] == M]["Day"].max()
        st.markdown(
            f"<h4 style='text-align: left; color: red;'>{D}/{M}/2022</h4", unsafe_allow_html=True)
        # f"DATA AS AT DAY => {D}/{M}/2022"

    st.markdown("##")

    # SALES VALUES AND EXPANDERS
    left_column, middle_column, right_column = st.columns([1, 2.0, 2.0])
    with left_column:
        ""
    with middle_column:
        markdownText("DIESEL (L)", "4", color="red")
    with right_column:
        markdownText("PETROL (L)", "4", color="green")

    left_column, middle_column, right_column = st.columns([1, 2.0, 2.0])
    with left_column:
        markdownText("CURRENT STOCKS:", "5")
    with middle_column:
        markdownText((df[(df["Site"].isin(site)) & (df["Month"] == M) & (
            df["Day"] == D)]["DieselDip"]).sum(), "5")
    with right_column:
        markdownText((df[(df["Site"].isin(site)) & (df["Month"] == M) & (
            df["Day"] == D)]["BlendDip"]).sum(), "5")

    # SELECTED SITE: {site}, SELECTED MONTH: {month}, SELECTED DAY: {day}")
    sales_expander = st.expander(f"SALES VALUES (L) :")
    profits_expander = st.expander(f"PROFIT VALUES ($) :")

    # @st.cache(allow_output_mutation=True)
    # @st.cache(hash_funcs={types.GeneratorType: id})
    def salesExSV():
        with sales_expander:
            c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
                [2, 1, 1, 1, 1, 1, 1, 1, 1])
            with c1:
                ""
            with c2:
                markdownText("TOTAL")
            with c3:
                markdownText("Drawdowns")
            with c4:
                markdownText("Coupons")
            with c5:
                markdownText("Cash")
            with c6:
                markdownText("TOTAL")
            with c7:
                markdownText("Drawdowns")
            with c8:
                markdownText("Coupons")
            with c9:
                markdownText("Cash")

            create9Columns([2, 1, 1, 1, 1, 1, 1, 1, 1], ["THIS YEAR'S TOTAL SALES:",
                                                         all_months_values["totalD_month"], all_months_values["drawdownsD_month"],
                                                         all_months_values["couponsD_month"], all_months_values["cashD_month"],
                                                         all_months_values["totalP_month"], all_months_values["drawdownsP_month"],
                                                         all_months_values["couponsP_month"], all_months_values["cashP_month"]])

            create9Columns([2, 1, 1, 1, 1, 1, 1, 1, 1], ["MONTHLY AVERAGE SALES:",
                                                         monthly_averages["totalD_MA"], monthly_averages["drawdownsD_MA"],
                                                         monthly_averages["couponsD_MA"], monthly_averages["cashD_MA"],
                                                         monthly_averages["totalP_MA"], monthly_averages["drawdownsP_MA"],
                                                         monthly_averages["couponsP_MA"], monthly_averages["cashP_MA"]])

            if (month != "All"):
                create9Columns([2, 1, 1, 1, 1, 1, 1, 1, 1], ["SELECTED MONTH'S SALES:",
                                                             month_values["totalD_month"], month_values["drawdownsD_month"],
                                                             month_values["couponsD_month"], month_values["cashD_month"],
                                                             month_values["totalP_month"], month_values["drawdownsP_month"],
                                                             month_values["couponsP_month"], month_values["cashP_month"]])

            create9Columns([2, 1, 1, 1, 1, 1, 1, 1, 1], ["CURRENT MONTH'S SALES:",
                                                         latest_month_values["totalD_month"], latest_month_values["drawdownsD_month"],
                                                         latest_month_values["couponsD_month"], latest_month_values["cashD_month"],
                                                         latest_month_values["totalP_month"], latest_month_values["drawdownsP_month"],
                                                         latest_month_values["couponsP_month"], latest_month_values["cashP_month"]])

    def profitsExPV():
        # def profitsExPV(all_profit_values, profit_averages, profit_values, latest_profit_values):
        with profits_expander:
            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(
                [2, 1, 1, 1, 1, 1, 1, 1])
            with c1:
                ""
            with c2:
                markdownText("Diesel")
            with c3:
                markdownText("Petrol")
            with c4:
                markdownText("Gross Profit")
            with c5:
                markdownText("Expenses")
            with c6:
                markdownText("Net Profit")
            with c7:
                markdownText("Budgeted")
            with c8:
                markdownText("Difference")

            gross = all_profit_values["profitD"]+all_profit_values["profitP"]
            expenses = 10000
            expenses_monthly = round(expenses/df["Month"].max(), 2)
            budgeted = 100000
            budgeted_monthly = round(100000/df["Month"].max(), 2)

            create8Columns([2, 1, 1, 1, 1, 1, 1, 1], ["THIS YEAR'S TOTAL PROFITS:",
                                                      all_profit_values["profitD"], all_profit_values["profitP"],
                                                      gross, expenses,
                                                      gross - expenses, budgeted,
                                                      round(gross - expenses - budgeted, 2)])

            create8Columns([2, 1, 1, 1, 1, 1, 1, 1], ["MONTHLY AVERAGE PROFITS:",
                                                      profit_averages["profitD_MA"], profit_averages["profitP_MA"],
                                                      profit_averages["gross_MA"], expenses_monthly,
                                                      round(
                                                          profit_averages["gross_MA"] - expenses_monthly, 2),
                                                      budgeted_monthly,
                                                      round(profit_averages["gross_MA"] - expenses_monthly - budgeted_monthly, 2)])

            if (month != "All"):
                create8Columns([2, 1, 1, 1, 1, 1, 1, 1], ["SELECTED MONTH'S PROFITS:",
                                                          profit_values["profitD"], profit_values["profitP"],
                                                          profit_values["gross"], expenses_monthly,
                                                          round(
                                                              profit_values["gross"] - expenses_monthly, 2),
                                                          budgeted_monthly,
                                                          round(profit_values["gross"] - expenses_monthly - budgeted_monthly, 2)])

            create8Columns([2, 1, 1, 1, 1, 1, 1, 1], ["CURRENT MONTH'S PROFITS:",
                                                      latest_profit_values["profitD"], latest_profit_values["profitP"],
                                                      latest_profit_values["gross"], expenses_monthly,
                                                      round(
                                                          latest_profit_values["gross"] - expenses_monthly, 2),
                                                      budgeted_monthly,
                                                      round(latest_profit_values["gross"] - expenses_monthly - budgeted_monthly, 2)])

    salesExSV()

    # profitsExPV()

    if (day_or_shift == "Shift"):
        def allShiftsDfMethod(shiftMethod):
            sFDf = pd.Series([0, 0, 0, 0, 0, 0], index=[
                             "DrawdownsD", "CouponsD", "CashD", "DrawdownsP", "CouponsP", "CashP"])
            allShiftsFDf = pd.DataFrame()

            for num in range(1, number_of_shifts+1):
                sDf = shiftMethod(num)

                allShiftsDf = sDf.groupby("Day", as_index=False)[
                    "DrawdownsD", "CouponsD", "CashD", "DrawdownsP", "CouponsP", "CashP", "DrawdownsT", "CouponsT", "CashT"].sum()
                allShiftsDf["Shift"] = num
                allShiftsFDf = allShiftsFDf.append(
                    allShiftsDf, ignore_index=True)

                sDf = sDf[["DrawdownsD", "CouponsD", "CashD",
                           "DrawdownsP", "CouponsP", "CashP"]].sum()

                sFDf = sFDf + sDf

            sFDf = sFDf/number_of_shifts

            allShiftsFDf = allShiftsFDf.groupby("Shift", as_index=True)[
                "DrawdownsD", "CouponsD", "CashD", "DrawdownsP", "CouponsP", "CashP", "DrawdownsT", "CouponsT", "CashT"].sum()

            def sAVal(loc): return round(sFDf.iloc[loc], 1)
            with sales_expander:
                create9Columns([2, 1, 1, 1, 1, 1, 1, 1, 1], ["SHIFT AVERAGE'S SALES:",
                                                             round(
                                                                 sAVal(0)+sAVal(1)+sAVal(2), 1),
                                                             sAVal(0), sAVal(
                                                                 1), sAVal(2),
                                                             round(
                                                                 sAVal(3)+sAVal(4)+sAVal(5), 1),
                                                             sAVal(3), sAVal(4), sAVal(5)])

            return allShiftsFDf

    if (month != "All"):
        Df = (df[(df['Site'].isin(site)) & (df["Month"] == int(month))]
                [["DrawdownsD", "CouponsD", "CashD", "DrawdownsP", "CouponsP", "CashP"]].sum())/last_day

        def dAVal(loc): return round(Df.iloc[loc], 1)

        with sales_expander:
            create9Columns([2, 1, 1, 1, 1, 1, 1, 1, 1], ["DAILY AVERAGE'S SALES:",
                                                         round(
                                                             dAVal(0)+dAVal(1)+dAVal(2), 1),
                                                         dAVal(0), dAVal(
                                                             1), dAVal(2),
                                                         round(
                                                             dAVal(3)+dAVal(4)+dAVal(5), 1),
                                                         dAVal(3), dAVal(4), dAVal(5)])

    st.markdown("""---""")

    # ---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    product_left_column, site_right_column = st.columns(2)

    # TOTAL CONSUMPTION CHARTS
    # Control Pie Chart Figure

    def TC_pieFigData(title, column, Data_df):

        # Data_df

        Data_df.columns = ['By', column, 'Amount']

        outer = Data_df.groupby(column).sum()
        # outer
        outer_labels = outer.index.get_level_values(0)
        # outer_labels
        outer = list(outer["Amount"])

        inner = Data_df.groupby([column, 'By']).sum()
        # inner
        inner_labels = inner.index.get_level_values(1)
        # inner_labels
        inner = list(inner["Amount"])

        data = [  # Portfolio (inner donut)
            go.Pie(values=outer,
                   # labels=['Diesel', 'Petrol'],
                   domain={'x': [0.2, 0.8], 'y':[0.1, 0.9]},
                   hole=0.5,
                   direction='clockwise',
                   sort=False,
                   text=outer_labels,
                   # legendgroup ="Product",
                   marker={'colors': ['#CB4335', '#2E86C1']},
                   showlegend=False),
            # Individual components (outer donut)
            go.Pie(values=inner,
                   # labels=['CashD', 'CouponsD', 'DrawdownsD', 'CashP','CouponsP','DrawdownsP'],
                   domain={'x': [0.1, 0.9], 'y':[0, 1]},
                   hole=0.75,
                   direction='clockwise',
                   sort=False,
                   text=inner_labels,
                   # legendgroup="Consumption",
                   marker={'colors': ['#EC7063', '#F1948A',
                                      '#5DADE2', '#85C1E9', '#38E2C2', '#45B1A2']},
                   showlegend=False)]

        fig = go.Figure(data=data, layout={'title': title})
        # plotly.offline.iplot(fig)
        # st.pyplot(fig)
        return {"fig": fig,
                "df": Data_df}

    # Petrol vs Diesel Pie Chart
    def TC_PvDPieChart(site, month, day):
        column = 'Product'

        if (day != "All" or shift != "All"):
            if (day_or_shift == "Shift"):

                filteredDf = shiftDf(shift)

                title = f'Petrol vs Diesel Consumption {site[0]} for {calendar.month_name[int(month)]}, shift {shift}'
            else:
                title = f'Petrol vs Diesel Consumption {site[0]} for {calendar.month_name[int(month)]}, day {day}'
                filteredDf = df[(df['Site'].isin(site)) & (
                    df["Month"] == int(month)) & (df["Day"] == int(day))]
        elif (month != "All"):
            title = f'Petrol vs Diesel Consumption {site[0]} for {calendar.month_name[int(month)]}'
            filteredDf = df[(df['Site'].isin(site)) &
                            (df["Month"] == int(month))]
        else:
            title = f'Petrol vs Diesel Consumption {site[0]} for all months'
            filteredDf = df[(df['Site'].isin(site))]

        PvD_df = pd.DataFrame([['Coupons', 'Petrol', filteredDf["CouponsP"].sum()],
                               ['Cash', 'Petrol', filteredDf["CashP"].sum()],
                               ['Drawdowns', 'Petrol',
                                   filteredDf["DrawdownsP"].sum()],
                               ['Coupons', 'Diesel', filteredDf["CouponsD"].sum()],
                               ['Cash', 'Diesel', filteredDf["CashD"].sum()],
                               ['Drawdowns', 'Diesel', filteredDf["DrawdownsD"].sum()]],
                              index=range(1, 7), columns=["Type", "Product", "Value"])

        if (day != "All" or shift != "All"):
            if (day_or_shift == "Shift"):
                with sales_expander:
                    def sVal(loc): return round(PvD_df.iloc[loc]["Value"], 1)

                    create9Columns([2, 1, 1, 1, 1, 1, 1, 1, 1], ["SHIFT SALES:",
                                                                 round(
                                                                     sVal(5)+sVal(4)+sVal(3), 1), sVal(5), sVal(3), sVal(4),
                                                                 round(sVal(2)+sVal(1)+sVal(0), 1), sVal(2), sVal(0), sVal(1)])
            else:
                with sales_expander:
                    # def dVal(loc):
                    #     # return st.metric(label="", value=round(PvD_df.iloc[loc]["Value"], 1), delta="-5")
                    #     return round(PvD_df.iloc[loc]["Value"], 1)

                    def dVal(loc): return round(PvD_df.iloc[loc]["Value"], 1)

                    create9Columns([2, 1, 1, 1, 1, 1, 1, 1, 1], ["DAY SALES:",
                                                                 round(
                                                                     dVal(5)+dVal(4)+dVal(3), 1), dVal(5), dVal(3), dVal(4),
                                                                 round(dVal(2)+dVal(1)+dVal(0), 1), dVal(2), dVal(0), dVal(1)])

        # with value_right_column:
        #     with st.expander("Petrol vs Diesel Values"):
        #         PvD_df

        return TC_pieFigData(title, column, PvD_df)

    # Site vs Site Pie Chart
    def TC_SvSPieChart(product, month, day):

        if (product == "Both"):
            product = "T"
            fuel = "Fuel"
        elif (product == "Petrol"):
            product = "P"
            fuel = "Petrol"
        else:
            product = "D"
            fuel = "Diesel"

        column = 'Site'

        if (day != "All" or shift != "All"):
            if (day_or_shift == "Shift"):
                filteredDf = shiftDfNoSite(shift, df)
                title = f'Detailed {fuel} Consumption Ardbennie vs Greendale for {calendar.month_name[int(month)]}, shift {shift}'
            else:
                title = f'Detailed {fuel} Consumption Ardbennie vs Greendale for {calendar.month_name[int(month)]}, day {day}'
                filteredDf = df[(df["Month"] == int(month))
                                & (df["Day"] == int(day))]
        elif (month != "All"):
            title = f'Detailed {fuel} Consumption Ardbennie vs Greendale for {calendar.month_name[int(month)]}'
            filteredDf = df[(df["Month"] == int(month))]
        else:
            title = f'Detailed {fuel} Consumption Ardbennie vs Greendale for all months'
            filteredDf = df

        SvS_df = pd.DataFrame([['Coupons', 'Ardbennie', filteredDf[(filteredDf["Site"] == "Ardbennie")]["Coupons"+product].sum()],
                               ['Cash', 'Ardbennie', filteredDf[(
                                   filteredDf["Site"] == "Ardbennie")]["Cash"+product].sum()],
                               ['Drawdowns', 'Ardbennie', filteredDf[(
                                   filteredDf["Site"] == "Ardbennie")]["Drawdowns"+product].sum()],
                               ['Coupons', 'Greendale', filteredDf[(
                                   filteredDf["Site"] == "Greendale")]["Coupons"+product].sum()],
                               ['Cash', 'Greendale', filteredDf[(
                                   filteredDf["Site"] == "Greendale")]["Cash"+product].sum()],
                               ['Drawdowns', 'Greendale', filteredDf[(filteredDf["Site"] == "Greendale")]["Drawdowns"+product].sum()]],
                              index=range(1, 7), columns=["Type", "Site", "Value"])

        # with value_left_column:
        #     with st.expander("Site vs Site Values"):
        #         SvS_df

        return TC_pieFigData(title, column, SvS_df)

    # Consumption comparison Bar graph and Fig Data
    def TC_bar(product, site, month):

        if (product == "Both"):
            product = "T"
            fuel = "Fuel"
        elif (product == "Petrol"):
            product = "P"
            fuel = "Petrol"
        else:
            product = "D"
            fuel = "Diesel"

        if (day_or_shift == "Shift"):
            if (shift != "All"):

                filteredDf = shiftDf(shift)

                filteredDf = pd.DataFrame(filteredDf.sort_values(['Month', 'Day'], ascending=True)
                                          .groupby(['Month', 'Day'], as_index=False)[
                    ['Coupons'+product, 'Cash'+product, 'Drawdowns'+product]].sum())
                # filteredDf.set_index("Day", inplace=True)

                title = f'{fuel} Consumption {site[0]} for {calendar.month_name[int(month)]}, shift {shift}'
                month_months = filteredDf["Month"].values.tolist()
                month_days = filteredDf["Day"].values.tolist()
                months = []
                for m in month_months:
                    months.append(calculateMonthNameShort(m))
                # months = months_nums
                months = [months, month_days]
            else:
                title = f'{fuel} Consumption {site[0]} for {calendar.month_name[int(month)]}, shift {shift}'
                allShiftsFDf = allShiftsDfMethod(shiftDf)
                filteredDf = allShiftsFDf[[
                    'Coupons'+product, 'Cash'+product, 'Drawdowns'+product]]
                months = filteredDf.index.values.tolist()
        elif (month != "All"):
            title = f'{calendar.month_name[int(month)]} {fuel} Consumption daily comparison for {site[0]}'
            # filteredDf = (df[(df['Site'].isin(site)) & (df["Month"] == int(month))])[
            #         ["Day", "Coupons"+product, "Cash"+product, "Drawdowns"+product]]

            filteredDf = pd.DataFrame(df[(df['Site'].isin(site)) & (df["Month"] == int(month))].groupby('Day', as_index=False)[
                ['Coupons'+product, 'Cash'+product, 'Drawdowns'+product]].sum())
            # filteredDf
            # filteredDf.set_index("Day", inplace=True)
            months = filteredDf["Day"].values.tolist()
        else:
            title = f'{fuel} Consumption monthly comparison for {site[0]}'
            filteredDf = pd.DataFrame(df[(df['Site'].isin(site))].groupby('Month', as_index=False)[
                ['Coupons'+product, 'Cash'+product, 'Drawdowns'+product]].sum())
            # filteredDf.set_index("Month", inplace=True)
            months_nums = filteredDf["Month"].values.tolist()
            months = []
            for m in months_nums:
                months.append(calculateMonthNameShort(m))

        fig = go.Figure(data=[
            go.Bar(name=f'Coupons{product}', x=months, y=list(
                filteredDf[f"Coupons{product}"]), text=filteredDf[f"Coupons{product}"]),
            go.Bar(name=f'Cash{product}', x=months, y=list(
                filteredDf[f"Cash{product}"]), text=filteredDf[f"Cash{product}"]),
            go.Bar(name=f'Drawdowns{product}', x=months, y=list(
                filteredDf[f"Drawdowns{product}"]), text=filteredDf[f"Drawdowns{product}"])
        ])
        # Change the bar mode
        fig.update_traces(texttemplate='%{text:.3s}', textposition='outside')
        fig.update_layout(barmode='group', title=title)
        # fig.update_xaxes(
        # xaxis={'categoryorder': 'array', 'categoryarray': [29, 30, 31, 1, 2, 3, 4]})
        fig.update_xaxes(categoryorder="trace")
        # return fig
        fig
        with st.expander("Values"):
            filteredDf

    # Consumption comparison Line graph and Fig Data
    def TC_line(product, site, month):

        if (product == "Both"):
            product = "T"
            fuel = "Fuel"
        elif (product == "Petrol"):
            product = "P"
            fuel = "Petrol"
        else:
            product = "D"
            fuel = "Diesel"

        if (month != "All"):
            title = f'{calendar.month_name[int(month)]} {fuel} Consumption daily comparison for {site[0]}'
            filteredDf = (df[(df['Site'].isin(site)) & (df["Month"] == int(month))])[
                ["Day", "Coupons"+product, "Cash"+product, "Drawdowns"+product]]
            filteredDf.set_index("Day", inplace=True)
        else:
            title = f'{fuel} Consumption monthly comparison for {site[0]}'
            filteredDf = pd.DataFrame(df[(df['Site'].isin(site))].groupby('Month', as_index=False)[
                ['Coupons'+product, 'Cash'+product, 'Drawdowns'+product]].sum())
            filteredDf.set_index("Month", inplace=True)

        # filteredDf

        # comb_month_by.rename(columns={"1":"Jan" } ,inplace=True)

        months = filteredDf.index.values.tolist()

        fig = go.Figure()

        fig.add_trace(go.Scatter(mode='lines+markers', name=f'Coupons{product}', x=months, y=list(
            filteredDf[f"Coupons{product}"]), text=filteredDf[f"Coupons{product}"])),
        fig.add_trace(go.Scatter(mode='lines+markers', name=f'Cash{product}', x=months, y=list(
            filteredDf[f"Cash{product}"]), text=filteredDf[f"Cash{product}"])),
        fig.add_trace(go.Scatter(mode='lines+markers', name=f'Drawdowns{product}', x=months, y=list(
            filteredDf[f"Drawdowns{product}"]), text=filteredDf[f"Drawdowns{product}"]))

        # Change the bar mode
        # fig.update_traces(texttemplate='%{text:.3s}', textposition='outside')
        # fig.update_layout(barmode='group', title = title)

        # return fig
        fig

    SvS_data = TC_SvSPieChart(product, month, day)
    PvD_data = TC_PvDPieChart(site, month, day)

    # DETAILED DRAWDOWNS CHARTS
    # Consumption by company Pie Chart

    def DD_Pie(product, month):
        if (month == "All"):
            month = [x for x in range(1, 13)]
            title_string = "all months"
            title = f'Companies {product} consumption for {title_string}'
        else:
            month = [int(month)]
            title_string = month[0]
            title = f'Companies {product} consumption for {title_string}'

        if (product == "Petrol vs Diesel"):
            # dd_pie_data = {"Product": ["Petrol", "Diesel"],
            #         "Amount": [dd_df[(dd_df["Product"] == "Petrol") & (dd_df["Month"].isin(month))]["Fuel"].sum(),
            #         dd_df[(dd_df["Product"] == "Diesel") & (dd_df["Month"].isin(month))]["Fuel"].sum()]}
            dd_pie_data = {"Product": ["Petrol", "Diesel"],
                           "Amount": [dd_df[(dd_df["Month"].isin(month))]["Petrol"].sum(),
                                      dd_df[(dd_df["Month"].isin(month))]["Diesel"].sum()]}
            dd_pie_df = pd.DataFrame(dd_pie_data)

            values = dd_pie_df["Amount"]
            labels = dd_pie_df["Product"]

            title = f'Companies Petrol vs Diesel consumption for {title_string}'
        else:
            if (product == "Both"):
                # product = ["Petrol", "Diesel"]
                dd_pie_df = pd.DataFrame(dd_df[(dd_df["Month"].isin(month))].groupby(
                    'Company', as_index=False)['Diesel', 'Petrol'].sum())
                dd_pie_df['Fuel'] = dd_pie_df['Diesel']+dd_pie_df['Petrol']
                dd_pie_df = dd_pie_df.sort_values(by=['Fuel'], ascending=False)
                values = dd_pie_df["Fuel"]
            elif (product == "Diesel"):
                # product = ["Diesel"]
                dd_pie_df = pd.DataFrame(dd_df[(dd_df["Month"].isin(month))].groupby(
                    'Company', as_index=False)['Diesel'].sum())
                dd_pie_df = dd_pie_df.sort_values(
                    by=['Diesel'], ascending=False)
                values = dd_pie_df["Diesel"]
            elif (product == "Petrol"):
                # product = ["Petrol"]
                dd_pie_df = pd.DataFrame(dd_df[(dd_df["Month"].isin(month))].groupby(
                    'Company', as_index=False)['Petrol'].sum())
                dd_pie_df = dd_pie_df.sort_values(
                    by=['Petrol'], ascending=False)
                values = dd_pie_df["Petrol"]

            # dd_pie_df = pd.DataFrame(dd_df[(dd_df["Product"].isin(product)) &
            #                     (dd_df["Month"].isin(month))].groupby('Company', as_index = False)['Fuel'].sum())

            # dd_pie_df = dd_pie_df.sort_values(by = ['Fuel'], ascending = False)

            # values = dd_pie_df["Fuel"]
            labels = dd_pie_df["Company"]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='percent',
                                     insidetextorientation='radial'
                                     )])
        fig.update_layout(title=title)
        fig.update_layout(height=650)

        # fig
        return {"fig": fig,
                "df": dd_pie_df}

    # Bar Companies vs companies
    def DD_Bar(product, month):
        # if(day_or_shift == "Shift"):
        #     if(shift != "All"):

        #         filteredDf = shiftDf(shift)

        #         filteredDf = pd.DataFrame(filteredDf.groupby('Day', as_index = True)[
        #                 ['Coupons'+product, 'Cash'+product, 'Drawdowns'+product]].sum())

        #         title = f'Petrol vs Diesel Consumption {site[0]} for {calendar.month_name[int(month)]}, shift {shift}'
        #     else:
        #         title = f'Petrol vs Diesel Consumption {site[0]} for {calendar.month_name[int(month)]}, shift {shift}'
        #         filteredDf = allShiftsFDf[['Coupons'+product, 'Cash'+product, 'Drawdowns'+product]]
        if (month != "All"):
            month = [int(month)]
            title_string = month[0]
            title = f'Companies {product} consumption for {title_string}'
        else:
            month = [x for x in range(1, 13)]
            title_string = "all months"
            title = f'Companies {product} consumption for {title_string}'

        if (product == "Petrol vs Diesel"):
            petrol_consumption_by_company = pd.DataFrame(
                dd_df[dd_df['Product'] == "Petrol"].groupby('Company', as_index=True)['Fuel'].sum())
            petrol_consumption_by_company = petrol_consumption_by_company.sort_values(
                by=['Fuel'], ascending=False)

            diesel_consumption_by_company = pd.DataFrame(
                dd_df[dd_df['Product'] == "Diesel"].groupby('Company', as_index=False)['Fuel'].sum())
            diesel_consumption_by_company = diesel_consumption_by_company.sort_values(
                by=['Fuel'], ascending=False)

            comb = pd.merge(petrol_consumption_by_company, diesel_consumption_by_company,
                            on='Company', how='outer', suffixes=('Petrol', 'Diesel'))
            comb

            data = {'Company': comb["Company"],
                    'Petrol': comb["FuelPetrol"], 'Diesel': comb['FuelDiesel']}
            dd_bar_df = pd.DataFrame(data).sort_values(
                by=['Diesel'], ascending=False)

            # values = dd_bar_df["Amount"]
            labels = dd_bar_df["Company"]

            title = f'Companies Petrol vs Diesel consumption for {title_string}'

            fig = go.Figure(data=[
                go.Bar(name=f'vsP', x=labels, y=dd_bar_df["Petrol"], text=""),
                go.Bar(name=f'vsD', x=labels, y=dd_bar_df["Diesel"], text=""),
            ])
        else:
            if (product == "Both"):
                product = ["Petrol", "Diesel"]
            elif (product == "Diesel"):
                product = ["Diesel"]
            elif (product == "Petrol"):
                product = ["Petrol"]

            dd_bar_df = pd.DataFrame(dd_df[(dd_df["Product"].isin(product)) &
                                           (dd_df["Month"].isin(month))].groupby('Company', as_index=False)['Fuel'].sum())

            dd_bar_df = dd_bar_df.sort_values(by=['Fuel'], ascending=False)

            values = dd_bar_df["Fuel"]
            labels = dd_bar_df["Company"]

            fig = go.Figure(data=[
                go.Bar(name=f'not vs', x=labels, y=values, text=""),
            ])

        # Change the bar mode
        fig.update_traces(texttemplate='%{text:.3s}', textposition='outside')
        fig.update_layout(barmode='group', title=title)

        # fig
        return {"fig": fig,
                "df": dd_bar_df}

    # Total fuel month by month
    def DD_BarEach(product, company):
        # months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]
        bar_months = []
        months = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                  7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

        # months[7]
        dd_bar_each_df = pd.DataFrame(columns=dd_df.columns)
        # dd_bar_each_df

        if (product == "Petrol vs Diesel" or product == "Both"):
            # dd_df
            if (month != "All"):
                # dd_bar_each_df = pd.DataFrame()
                if (day_or_shift == "Shift"):
                    if (shift != "All"):
                        filteredDf = shiftDfNoSite(shift, dd_df)
                        filteredDf = filteredDf.groupby(
                            ['Month', 'Day', 'Company'], as_index=False).sum()
                        dd_bar_each_df = filteredDf[filteredDf["Company"] == company]
                        bar_months = dd_bar_each_df["Day"]
                        # dd_bar_each_df
                    else:
                        allShiftsFDf = allShiftsDfMethod(shiftDfNoSite, dd_df)
                        allShiftsFDf
                else:
                    dd_bar_each_df = dd_df[(dd_df["Company"] == company) & (
                        dd_df["Month"] == month)][["Month", "Day", "Petrol", "Diesel", "Company"]]
                    bar_months = dd_bar_each_df["Day"]
                    dd_bar_each_df
            else:
                dd_bar_each_df = pd.DataFrame(dd_df[(dd_df["Company"] == company)].groupby(
                    'Month', as_index=False)['Petrol', 'Diesel'].sum())
                for x in dd_bar_each_df["Month"]:
                    bar_months.append(months[x])

            dd_bar_each_df['Fuel'] = dd_bar_each_df['Diesel'] + \
                dd_bar_each_df['Petrol']
            # dd_bar_each_df

            # title = f'Companies Petrol vs Diesel consumption for {title_string}'
            fig = go.Figure(data=[
                go.Bar(name=f'Petrol', x=bar_months,
                       y=dd_bar_each_df["Petrol"], text=""),
                go.Bar(name=f'Diesel', x=bar_months,
                       y=dd_bar_each_df["Diesel"], text=""),
            ])

            if (product == "Both"):
                fig.update_layout(barmode='stack')
            # fig
        else:
            if (month != "All"):
                dd_bar_each_df = pd.DataFrame()
                if (day_or_shift == "Shift"):
                    if (shift != "All"):
                        filteredDf = shiftDfNoSite(shift, dd_df)
                        dd_bar_each_df = filteredDf[filteredDf["Company"] == company]
                        bar_months = dd_bar_each_df["Day"]
                        dd_bar_each_df
                        # filteredDf = pd.DataFrame(filteredDf.groupby('Day', as_index = True)[
                        # ['Coupons'+product, 'Cash'+product, 'Drawdowns'+product]].sum())
                else:
                    dd_bar_each_df = dd_df[(dd_df["Company"] == company) & (
                        dd_df["Month"] == month)][["Month", "Day", product, "Company"]]
                    bar_months = dd_bar_each_df["Day"]
            else:
                dd_bar_each_df = pd.DataFrame(dd_df[(dd_df["Company"] == company)].groupby(
                    'Month', as_index=False)[product].sum())
                for x in dd_bar_each_df["Month"]:
                    bar_months.append(months[x])

            # dd_bar_each_df['Fuel'] = dd_bar_each_df['Diesel'] + dd_bar_each_df['Petrol']
            # dd_bar_each_df
            # dd_bar_each_df = pd.DataFrame(dd_df[(dd_df["Company"] == company)].groupby('Month', as_index= False)['Diesel', 'Petrol'].sum())
            # dd_bar_each_df
            values = dd_bar_each_df[product]

            # for x in dd_bar_each_df["Month"]:
            #     bar_months.append(months[x])

            fig = go.Figure(data=[
                go.Bar(name=f'not vs', x=bar_months, y=values, text=""),
            ])
            # fig

        return {"fig": fig,
                "df": dd_bar_each_df}

    # LOADING DRAWDOWNS

    # @st.cache(show_spinner=False)
    @st.experimental_memo(show_spinner=False, ttl=86400)
    def get_drawdown_data_from_excel(retail_or_commercial, num):
        dd_df = read_excel_sheets("ABUJA")
        for sheet in sheet_names:
            dff = read_excel_sheets(sheet)

            dd_df = dd_df.append(dff, ignore_index=True)
        # dd_df = ABUJA_df
        dd_df = dd_df.drop_duplicates()
        dd_df.columns = dd_df.columns.str.strip()
        dd_df = dd_df.fillna(0)

        dd_df.loc[dd_df['Product'] == 'Diesel', 'Diesel2'] = dd_df["Qty"]
        dd_df.loc[dd_df['Product'] == 'Diesel',
                  'Diesel3'] = dd_df["Litrage"]
        dd_df.loc[dd_df['Product'] == 'Petrol', 'Petrol2'] = dd_df["Qty"]
        dd_df.loc[dd_df['Product'] == 'Petrol',
                  'Petrol3'] = dd_df["Litrage"]
        dd_df = dd_df.fillna(0)

        dd_df["Diesel"] = (dd_df["Diesel"] + dd_df["Qty diesel"] + dd_df["Qty (diesel)"] +
                           dd_df["Qty(dzl)"] + dd_df["Diesel quantity (l)"] + dd_df["Diesel2"] + dd_df["Diesel3"])
        dd_df["Petrol"] = (dd_df["Petrol"] + dd_df["Qty petrol"] + dd_df["Qty (petrol)"] +
                           dd_df["Qty (ptrl)"] + dd_df["Petrol quantity (l)"] + dd_df["Petrol2"] + dd_df["Petrol3"])
        dd_df["Narration"] = dd_df["Narration"].astype(str)
        dd_df["Description"] = dd_df["Description"].astype(str)
        dd_df["Naration"] = dd_df["Naration"].astype(str)
        dd_df["Narration"] = dd_df["Narration"] + \
            dd_df["Description"] + dd_df["Naration"]
        dd_df["Narration"] = dd_df["Narration"].str.strip("0")

        dd_df = dd_df[["Month", "Day", "Product",
                       "Narration", "Diesel", "Petrol", "Company"]]

        if (retail_or_commercial == "retail"):
            dd_df = dd_df[((dd_df["Diesel"] + dd_df["Petrol"]) != 0) & (dd_df["Narration"] != "Coupons")
                          & (dd_df["Narration"] != "Delivery") & (dd_df["Narration"] != "Payment")]
        elif (retail_or_commercial == "commercial"):
            dd_df = dd_df[((dd_df["Diesel"] + dd_df["Petrol"]) != 0) & (dd_df["Narration"] != "Coupons")
                          & (dd_df["Narration"] == "Delivery") & (dd_df["Narration"] != "Payment")]

        return dd_df

    # dd_df = get_drawdown_data_from_excel()

    # (dd_df.loc[:3,'Diesel']) = (dd_df.loc[:3,'Diesel']).astype(float)
    # dd_df.loc[:3,'Diesel']

    # dd_df["Diesel"].apply(lambda x: (dd_df["Product"] == "Diesel"): x = dd_df["Qty"])
    # dd_df["hoo"] = dd_df['Product'].apply(lambda x: "dfdd" if x == "Diesel" else "dddfd")

    # dd_df
    # st.stop()

    # ---- SIDEBAR ----
    if (retail_or_commercial == "Retail" and data == "Detailed Drawdowns"):
        # pass
        with st.spinner("Loading data..."):
            dd_df = get_drawdown_data_from_excel(
                "retail", f"{name}{st.session_state['num']}")
        # dd_df = get_dd_df_data_from_csv("retail")
    elif (retail_or_commercial == "Commercial" and data == "Detailed Drawdowns"):
        # pass
        with st.spinner("Loading data..."):
            dd_df = get_drawdown_data_from_excel(
                "commercial", f"{name}{st.session_state['num']}")
        # dd_df = get_dd_df_data_from_csv("commercial")

    if (data == "Detailed Drawdowns"):
        # and (product == 'Both' or product == 'Petrol' or product == 'Diesel')):
        if (chart == 'Pie'):
            pass
        else:
            company = st.sidebar.selectbox(
                'Select which company to view',
                dd_df['Company'].unique())

    # dd_df = dd_df.drop_duplicates()
    # desc = dd_df.describe()
    # dd_df[dd_df.duplicated()]

    # expenses_expander = st.expander("EXPENSES")
    # with expenses_expander:
        # st.write("Expenses")

    # Display figures or charts
    if (data == "Type of Consumption"):
        if (retail_or_commercial == "Commercial"):
            markdownText("COMING SOON", "1", color="white")
        elif (chart == "Pie"):
            first_left_column, first_right_column = st.columns(2)
            first_left_column.plotly_chart(
                SvS_data["fig"], use_container_width=True)
            first_right_column.plotly_chart(
                PvD_data["fig"], use_container_width=True)

            value_left_column, value_right_column = st.columns(2)
            with value_left_column:
                with st.expander("Site vs Site Values"):
                    SvS_data["df"]
            with value_right_column:
                with st.expander("Petrol vs Diesel Values"):
                    PvD_data["df"]
        elif (chart == "Bar"):
            fc, sc, tc = st.columns([1, 3, 1])
            # second_left_column.plotly_chart(TC_bar(product, site, "All"), use_container_width=True)
            with sc:
                TC_bar(product, site, month)
        else:
            TC_line(product, site, month)
        # get_drawdown_data_from_excel("retail")
        # get_drawdown_data_from_excel("commercial")

    elif (data == "Detailed Drawdowns"):
        if (chart == "Pie"):
            df = DD_Pie(product, month)
            l, c, r = st.columns([1, 3, 1])
            with c:
                df["fig"]
            exp = st.expander("Values")
            with exp:
                df["df"]
        elif (chart == "Bar"):
            # df = DD_Bar(product, month)
            df = DD_BarEach(product, company)
            l, c, r = st.columns([1, 3, 1])
            with c:
                df["fig"]
            exp = st.expander("Values")
            with exp:
                df["df"]
