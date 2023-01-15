from clickhouse_driver import Client
import pandas as pd

import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Python Dashboard", page_icon=":bar-chart:", layout="wide"
)


try:
    client = Client(
        host="localhost",
    )
    print("connected")

except Exception as e:
    print(e)

columns = [
    "id",
    "sms_id",
    "network",
    "msisdn",
    "shortcode",
    "nin",
    "request",
    "request_type",
    "status",
    "response",
    "status_response_err",
    "response_err",
    "status_response_sidmach",
    "response_sidmach",
    "status_response_nvs",
    "response_nvs",
    "charged",
    "time_request",
    "time_response",
    "meta",
]

curr = client.execute("SELECT * FROM jamb_ng.request")
df = pd.DataFrame(curr)
df.columns = columns

df["time"] = pd.to_datetime(df["time_request"], format="%d%m%Y %H:%M:%S")
df["day"] = df["time"].dt.day.astype(str)
df["month"] = df["time"].dt.month.astype(str)

st.sidebar.header("Please Filter Here:")

request_type = st.sidebar.multiselect(
    "select the request:",
    options=df["request"].unique(),
    default=df["request"].unique(),
)

status_type = st.sidebar.multiselect(
    "select the status code:",
    options=df["status"].unique(),
    default=df["status"].unique(),
)

network = st.sidebar.multiselect(
    "select the network:",
    options=df["network"].unique(),
    default=df["network"].unique(),
)
time = st.sidebar.multiselect(
    "select the date:",
    options=df["time"].unique(),
    default=df["time"].unique(),
)

df_selection = df.query(
    "request == @request_type & status ==@status_type & network == @network & time == @time"
)

status = df_selection["status"].count()
network = df_selection["network"].count()

st.title(":bar_chart: Sales Dashboard")
st.markdown("##")

total_request = int(df_selection["request"].count())

left_column, middle_column, right_column = st.columns(3)

with left_column:
    st.subheader("Total Request count:")
    st.subheader(f"{str(total_request)}")
with middle_column:
    st.subheader("Total #")
    st.subheader(f"{str(status)}")
with right_column:
    st.subheader("Total Number of ")
    st.subheader(f"{str(network)}")

st.markdown("""---""")

request = df.groupby(by=["request"]).count()[["network"]]

plot_request = px.bar(
    request,
    x="network",
    # color="network",
    y=request.index,
    orientation="h",
    title="<b>Request per keyword</b>",
    color_discrete_sequence=["#0083B8"] * len(request),
    template="plotly_white",
    text_auto=True,
    labels={"x": "counts", "y": "Requests"},
)

plot_request.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    width=750,
    height=500,
)

daily_request = df_selection.groupby(by=["month"]).count()[["request"]]
daily_request_plot = px.line(
    daily_request,
    x=daily_request.index,
    y="request",
    title="<b>Request per Day</b>",
    color_discrete_sequence=["#0083B8"] * len(daily_request),
    template="plotly_white",
)
daily_request_plot.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(daily_request_plot, use_container_width=True)
right_column.plotly_chart(plot_request, use_container_width=True)

# st.dataframe(df)
