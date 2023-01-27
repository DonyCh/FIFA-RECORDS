import streamlit as st  # pip install streamlit
import datetime


# BACKGROUND_COLOR = 'white'
# COLOR = 'black'

color = 'black'
background_color = 'white'


def set_page_container_style(
    max_width: int = 1100, max_width_100_percent: bool = False,
    padding_top: int = 1, padding_right: int = 10, padding_left: int = 1, padding_bottom: int = 10,
    color: str = color, background_color: str = background_color,
):
    if max_width_100_percent:
        max_width_str = f'max-width: 100%;'
    else:
        max_width_str = f'max-width: {max_width}px;'
    # st.markdown(
    #     f'''
    #     <style>
    #         .reportview-container .sidebar-content {{
    #             padding-top: {1}rem;
    #         }}
    #         .reportview-container .main .block-container {{
    #             padding-top: {1}rem;
    #         }}
    #     </style>
    #     ''',unsafe_allow_html=True)
        # .big-font {{font-size:{500}px !important;}}
    st.markdown(
        f'''
            <style>
                div.block-container{{padding-top:{0}rem;}}
                div.sidebar .sidebar-content{{padding-top:{0}rem;}}
            </style>
            ''', unsafe_allow_html=True)
    # st.markdown("""
    # <style>
    #        .css-18e3th9 {
    #             padding-top: 0rem;
    #             padding-bottom: 10rem;
    #             padding-left: 5rem;
    #             padding-right: 5rem;
    #         }
    #        .css-1d391kg {
    #             padding-top: 0rem;
    #             padding-right: 1rem;
    #             padding-bottom: 3.5rem;
    #             padding-left: 1rem;
    #         }
    # </style>
    # """, unsafe_allow_html=True)


def markdownText(text, heading=None, alignment=None, color=None):
    if (heading == None):
        heading = "6"
    if (alignment == None):
        alignment = "center"
    if (color == None):
        color = "white"

    text = st.markdown(
        f"<h{heading} style='text-align: {alignment}; color: {color};'>{text}</h{heading}>", unsafe_allow_html=True)
    return text


def create8Columns(column_sizes, column_texts):
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(column_sizes)
    with c1:
        # st.metric(label="", value=markdownText(column_texts[0]), delta="1.2 °F")
        markdownText(column_texts[0])
    with c2:
        markdownText(column_texts[1])
    with c3:
        markdownText(column_texts[2])
    with c4:
        markdownText(column_texts[3])
    with c5:
        markdownText(column_texts[4])
    with c6:
        markdownText(column_texts[5])
    with c7:
        markdownText(column_texts[6])
    with c8:
        markdownText(column_texts[7])


def create9Columns(column_sizes, column_texts):
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(column_sizes)
    with c1:
        # st.metric(label="", value=markdownText(column_texts[0]), delta="1.2 °F")
        markdownText(column_texts[0])
    with c2:
        markdownText(column_texts[1])
    with c3:
        markdownText(column_texts[2])
    with c4:
        markdownText(column_texts[3])
    with c5:
        markdownText(column_texts[4])
    with c6:
        markdownText(column_texts[5])
    with c7:
        markdownText(column_texts[6])
    with c8:
        markdownText(column_texts[7])
    with c9:
        markdownText(column_texts[8])


def addShiftAbility(month, shift):
    last_day = 100
    number_of_shifts = 0
    month = str(month)

    def firstTuesday():
        for x in range(1, 8):
            ans = datetime.date(2022, int(month), x)
            if (ans.strftime("%A") == "Tuesday"):
                return x

    shift_startDay = (int(shift)-1)*7 + firstTuesday()
    shift_endDay = shift_startDay + 7
    if (month == "1" or month == "3" or month == "5" or month == "7" or month == "8" or month == "10" or month == "12"):
        last_day = 31
    if (month == "4" or month == "6" or month == "9" or month == "11"):
        last_day = 30
    if (month == "2"):
        #                 if((int(year)/4).is_integer()):
        #                     last_day = 29
        #                 else:
        last_day = 28

    nof = firstTuesday()
    while nof < last_day:
        number_of_shifts += 1
        nof = nof+7

    values = {"last_day": last_day,
              "shift_startDay": shift_startDay,
              "shift_endDay": shift_endDay,
              "nof": nof, }

    return values


@st.experimental_memo(show_spinner=False)
def get_data_from_excel(driveway, site, name):
    df = pd.read_excel(
        # io=greendaleDriveway,
        # io=driveway,
        io=f"{name}/{driveway}.xlsx",
        engine="openpyxl",
        sheet_name="detailed driveway 2022",
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
