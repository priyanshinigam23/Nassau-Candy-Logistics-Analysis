import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Nassau Candy Distributor",
    page_icon="🍬",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #F7F8FA;
}
h1 {
    color: #263746;
    font-size: 38px;
}
.subtitle {
    color: #657786;
    font-size: 17px;
}
div[data-testid="stMetric"] {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
}
</style>
""", unsafe_allow_html=True)

st.title("🍬 NASSAU CANDY DISTRIBUTOR")
st.markdown(
    '<p class="subtitle">Business Performance & Analysis Dashboard</p>',
    unsafe_allow_html=True
)

st.divider()

st.markdown("""
### Welcome to the Business Intelligence Dashboard

Explore sales performance, factory operations, shipping routes,
and profitability through interactive business analytics.
""")

file_path = Path(__file__).parent / "Nassau_Candy_Final_Analysis.xlsx"
try:
    df = pd.read_excel(file_path)

    st.success("Excel data connected successfully!")

    st.subheader("Business Overview")

    selected_factory = st.sidebar.selectbox(  
        "Select Factory",
        ["All Factories"] + sorted(df["Factory"].dropna().unique().tolist())
    )

    if selected_factory != "All Factories":
        df = df[df["Factory"] == selected_factory]

    
    selected_ship_mode = st.sidebar.selectbox(
        "Select Shipping Mode",
        ["All Shipping Modes"] + sorted(df["Ship Mode"].dropna().unique().tolist())
    )
    
    selected_region = st.sidebar.selectbox(
        "Select Region",
        ["All Regions"] + sorted(df["Region"].dropna().unique().tolist())
    )

    if selected_region != "All Regions":
        df = df[df["Region"] == selected_region]

    selected_state = st.sidebar.selectbox(
        "Select State",
        ["All States"] + sorted(df["State/Province"].dropna().unique().tolist())
    )

    if selected_state != "All States":
        df = df[df["State/Province"] == selected_state]


    if selected_ship_mode != "All Shipping Modes":
        df = df[df["Ship Mode"] == selected_ship_mode]

    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    start_date = df["Order Date"].min().date()
    end_date = df["Order Date"].max().date()

    selected_dates = st.sidebar.date_input(
        "Select Order Date Range",
        value=(start_date, end_date),
        min_value=start_date,
        max_value=end_date
    )

    if len(selected_dates) == 2:
        start, end = selected_dates
        df = df[
            (df["Order Date"].dt.date >= start) &
            (df["Order Date"].dt.date <= end)
        ]
        df_before_threshold = df.copy()
    # Lead-Time Threshold Filter
    if "Shipping Lead Time" in df.columns:
        df["Shipping Lead Time"] = pd.to_numeric(
            df["Shipping Lead Time"], errors="coerce"
        )

        valid_lead_times = df["Shipping Lead Time"].dropna()

        if not valid_lead_times.empty:
            max_lead_time = int(valid_lead_times.max())

            selected_threshold = st.sidebar.slider(
                "Maximum Shipping Lead Time",
                min_value=0,
                max_value=max(1, max_lead_time),
                value=max(1, max_lead_time)
            )

            df = df[
                df["Shipping Lead Time"].notna()
                & (df["Shipping Lead Time"] <= selected_threshold)
            ]

    total_orders = df["Order ID"].nunique()
    total_sales = df["Sales"].sum()
    total_units = df["Units"].sum()
    gross_profit = df["Gross Profit"].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
      st.metric("Total Orders", f"{total_orders:,}")

    with col2:
      st.metric("Total Sales", f"${total_sales:,.2f}")

    with col3:
      st.metric("Total Units Sold", f"{total_units:,.0f}")

    with col4:
      st.metric("Gross Profit", f"${gross_profit:,.2f}")


      st.divider()

      
    
    st.subheader("Factory-wise Sales Analysis")

    factory_sales = (
        df.groupby("Factory", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    st.bar_chart(
        factory_sales,
        x="Factory",
        y="Sales",
        color="#E15759"
    )

    st.subheader("Factory-wise Gross Profit")

    factory_profit = (
        df.groupby("Factory", as_index=False)["Gross Profit"]
        .sum()
        .sort_values("Gross Profit", ascending=False)
    )

    st.bar_chart(
        factory_profit,
        x="Factory",
        y="Gross Profit",
        color="#59A14F"
    )

    st.divider()

    st.subheader("Sales by Shipping Mode")

    shipping_sales = (
        df.groupby("Ship Mode", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    st.bar_chart(
        shipping_sales,
        x="Ship Mode",
        y="Sales",
        color="#4E79A7"
    )

    st.divider()


    st.subheader("Route-wise Sales Analysis")

    route_sales = (
        df.groupby("Route", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    st.bar_chart(
        route_sales,
        x="Route",
        y="Sales",
        color="#F28E2B"
    )

    st.divider()

    st.subheader("Orders by Factory")

    factory_orders = (
        df.groupby("Factory")["Order ID"]
        .nunique()
        .reset_index(name="Total Orders")
        .sort_values("Total Orders", ascending=False)
    )

    st.bar_chart(
        factory_orders,
        x="Factory",
        y="Total Orders",
        color="#B07AA1"
    )

    st.divider()
    
    st.subheader("Profitability Overview")

    if total_sales != 0:
        profit_margin = (gross_profit / total_sales) * 100
    else:
        profit_margin = 0

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Gross Profit", f"${gross_profit:,.2f}")

    with col2:
        st.metric("Profit Margin", f"{profit_margin:.2f}%")

    st.divider()

    
    st.subheader("💡 Key Business Insights")

    if not df.empty:
        best_factory = df.groupby("Factory")["Sales"].sum().idxmax()
        best_route = df.groupby("Route")["Sales"].sum().idxmax()
        best_ship_mode = df.groupby("Ship Mode")["Sales"].sum().idxmax()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info(f"🏭 Highest Sales Factory: {best_factory}")

        with col2:
            st.info(f"🛣️ Highest Sales Route: {best_route}")

        with col3:
            st.info(f"🚚 Highest Sales Shipping Mode: {best_ship_mode}")
    else:
        st.warning("No data available for the selected filters.")
    
    st.divider()

    
    st.subheader("⏱️ Recorded Lead-Time Threshold Analysis")

    if "Shipping Lead Time" in df.columns and not df.empty:
       
        recorded_lead_times = pd.to_numeric(
            df_before_threshold["Shipping Lead Time"], errors="coerce"
        ).dropna()


        if not recorded_lead_times.empty:
            exceeded_count = (
                recorded_lead_times > selected_threshold
            ).sum()

            exceedance_pct = (
                exceeded_count / len(recorded_lead_times)
            ) * 100

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Records Exceeding Threshold",
                    f"{exceeded_count:,}"
                )

            with col2:
                st.metric(
                    "Lead-Time Exceedance (%)",
                    f"{exceedance_pct:.1f}%"
                )

            st.caption(
                "This measures recorded lead times above the selected threshold. "
                "It does not confirm actual delivery delays because the dataset "
                "contains future ship dates."
            )

    with st.expander("🚚 Route Efficiency Analysis", expanded=True):

        route_efficiency = (
            df.groupby("Route", as_index=False)["Shipping Lead Time"]
            .mean()
            .sort_values("Shipping Lead Time", ascending=False)
            .head(10)
        )

        route_efficiency["Shipping Lead Time"] = (
            route_efficiency["Shipping Lead Time"].round(0)
        )

        fastest_routes = (
            df.groupby("Route", as_index=False)["Shipping Lead Time"]
            .mean()
            .sort_values("Shipping Lead Time", ascending=True)
            .head(10)
        )

        fastest_routes["Shipping Lead Time"] = (
            fastest_routes["Shipping Lead Time"].round(0)
        )

        st.subheader("⚡ Top 10 Fastest Routes")
        st.dataframe(fastest_routes, use_container_width=True)

        st.caption(
            "Top 10 routes with the highest average recorded shipping lead time (days)."
        )

        st.bar_chart(
            route_efficiency,
            x="Route",
            y="Shipping Lead Time",
            color="#E15759"
        )

        st.divider()
        st.subheader("📦 Orders by Route")

        route_orders = (
            df.groupby("Route")["Order ID"]
            .nunique()
            .reset_index(name="Total Orders")
            .sort_values("Total Orders", ascending=False)
            .head(10)
        )

        st.bar_chart(
            route_orders,
            x="Route",
            y="Total Orders",
            color="#4E79A7"
        )

        st.divider()


    st.subheader("🚚 Average Lead Time by Shipping Mode")

    
    ship_mode_efficiency = (
        df.groupby("Ship Mode", as_index=False)["Shipping Lead Time"]
        .mean()
        .sort_values("Shipping Lead Time", ascending=True)
    )


    ship_mode_efficiency["Shipping Lead Time"] = (
        ship_mode_efficiency["Shipping Lead Time"].round(0)
    )

    st.caption(
        "Average recorded shipping lead time in days for each shipping mode."
    )

    st.bar_chart(
        ship_mode_efficiency,
        x="Ship Mode",
        y="Shipping Lead Time",
        color="#59A14F"
    )

    st.divider()

    st.subheader("🏭 Factory-to-State Shipping Efficiency")

    factory_state_efficiency = (
        df.groupby(["Factory", "State/Province"], as_index=False)
        ["Shipping Lead Time"]
        .mean()
        .sort_values("Shipping Lead Time", ascending=False)
        .head(15)
    )

    factory_state_efficiency["Shipping Lead Time"] = (
        factory_state_efficiency["Shipping Lead Time"].round(0)
    )

    st.caption(
        "Top 15 factory-to-state combinations by average recorded shipping lead time (days)."
    )

    st.bar_chart(
        factory_state_efficiency,
        x="State/Province",
        y="Shipping Lead Time",
        color="#F28E2B"
    )

    st.dataframe(factory_state_efficiency, use_container_width=True)

    st.divider()

    st.subheader("📊 Shipping Lead Time Distribution")

    lead_time_data = df[["Shipping Lead Time"]].dropna()

    st.caption(
        "Distribution of recorded shipping lead times in days. "
        "Unusually long durations may reflect date anomalies in the dataset."
    )

    st.bar_chart(
        lead_time_data["Shipping Lead Time"].value_counts()
        .sort_index()
        .rename_axis("Lead Time (Days)")
        .reset_index(name="Number of Orders"),
        x="Lead Time (Days)",
        y="Number of Orders",
        color="#B07AA1"
    )

    st.divider()

    st.subheader("🔎 Shipping Data Quality Check")

    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

    future_shipments = (
        df["Ship Date"] > pd.Timestamp.today().normalize()
    ).sum()

    st.metric("Records with Future Ship Dates", f"{future_shipments:,}")

    if future_shipments > 0:
        st.warning(
            "Some records have Ship Dates in the future. "
            "Review these records before drawing conclusions about actual delivery efficiency."
        )
    else:
        st.success("No future Ship Dates found in the selected data.")

    st.divider()

    st.subheader("📦 Orders by Shipping Mode")

    ship_mode_orders = (
        df.groupby("Ship Mode")["Order ID"]
        .nunique()
        .reset_index(name="Total Orders")
        .sort_values("Total Orders", ascending=False)
    )

    st.bar_chart(
        ship_mode_orders,
        x="Ship Mode",
        y="Total Orders",
        color="#4E79A7"
    )

    st.divider()

    st.subheader("🛣️ Route Performance Summary")

    if not df.empty:
        route_summary = (
            df.groupby("Route")
            .agg(
                Total_Orders=("Order ID", "nunique"),
                Average_Lead_Time=("Shipping Lead Time", "mean")
            )
            .reset_index()
        )

        route_summary["Average_Lead_Time"] = (
            route_summary["Average_Lead_Time"].round(1)
        )

        col1, col2 = st.columns(2)

        with col1:
            busiest_route = route_summary.loc[
                route_summary["Total_Orders"].idxmax()
            ]
            st.metric(
                "Busiest Route",
                busiest_route["Route"],
                f'{busiest_route["Total_Orders"]:,} orders'
            )

        with col2:
            longest_route = route_summary.loc[
                route_summary["Average_Lead_Time"].idxmax()
            ]
            st.metric(
                "Highest Recorded Lead Time",
                longest_route["Route"],
                f'{longest_route["Average_Lead_Time"]:.1f} days'
            )
    else:
        st.warning("No data available for the selected filters.")

    st.divider()

    st.subheader("📈 Shipping Lead Time Statistics")

    lead_times = df["Shipping Lead Time"].dropna()

    if not lead_times.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Minimum (Days)", f"{lead_times.min():,.0f}")

        with col2:
            st.metric("Median (Days)", f"{lead_times.median():,.1f}")

        with col3:
            st.metric("Average (Days)", f"{lead_times.mean():,.1f}")

        with col4:
            st.metric("Maximum (Days)", f"{lead_times.max():,.0f}")

    st.caption(
        "Statistics reflect the recorded Shipping Lead Time values; "
        "verify date anomalies before interpreting them as real delivery performance."
    )

    st.divider()

    st.subheader("📋 Detailed Route Performance Table")

    detailed_route_table = (
        df.groupby("Route", as_index=False)
        .agg(
            Total_Orders=("Order ID", "nunique"),
            Total_Sales=("Sales", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Average_Lead_Time=("Shipping Lead Time", "mean")
        )
        .sort_values("Total_Orders", ascending=False)
    )

    detailed_route_table["Total_Sales"] = (
        detailed_route_table["Total_Sales"].round(2)
    )
    detailed_route_table["Gross_Profit"] = (
        detailed_route_table["Gross_Profit"].round(2)
    )
    detailed_route_table["Average_Lead_Time"] = (
        detailed_route_table["Average_Lead_Time"].round(1)
    )

    st.dataframe(
        detailed_route_table,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Explore Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🏭 Factory Analysis")
        st.write("Explore factory-wise sales, orders and performance.")
        st.button("Explore Factory Analysis", use_container_width=True)

    with col2:
        st.markdown("### 🚚 Shipping Analysis")
        st.write("Understand shipping modes, routes and order distribution.")
        st.button("Explore Shipping Analysis", use_container_width=True)

    with col3:
        st.markdown("### 📈 Profitability Analysis")
        st.write("Review gross profit, profit margins and factory performance.")
        st.button("Explore Profitability Analysis", use_container_width=True)

    st.divider()

    st.subheader("🔎 Order-Level Shipment Drill-Down")

    if not df.empty:
        order_ids = sorted(df["Order ID"].dropna().unique().tolist())

        selected_order = st.selectbox(
            "Select an Order ID",
            ["Select an order"] + order_ids
        )

        if selected_order != "Select an order":
            order_details = df[df["Order ID"] == selected_order].copy()

            detail_columns = [
                "Order ID", "Order Date", "Ship Date", "Ship Mode",
                "Factory", "Route", "Region", "State/Province",
                "Shipping Lead Time", "Sales", "Gross Profit"
            ]

            available_columns = [
                col for col in detail_columns if col in order_details.columns
            ]

            st.dataframe(
                order_details[available_columns],
                use_container_width=True
            )
    else:
        st.info("No shipment records match the current filters.")

    # Geographic Shipping Map
    st.subheader("🗺️ Geographic Shipping Bottlenecks")

    if (
        "State/Province" in df.columns
        and "Shipping Lead Time" in df.columns
        and not df.empty
    ):
        state_lead_time = (
            df.groupby("State/Province", as_index=False)
            .agg(
                Average_Lead_Time=("Shipping Lead Time", "mean"),
                Shipment_Records=("Order ID", "count")
            )
        )

        state_lead_time["Average_Lead_Time"] = (
            state_lead_time["Average_Lead_Time"].round(1)
        )

        fig_map = px.choropleth(
            state_lead_time,
            locations="State/Province",
            locationmode="USA-states",
            color="Average_Lead_Time",
            hover_name="State/Province",
            hover_data=["Shipment_Records"],
            scope="usa",
            color_continuous_scale="YlOrRd",
            labels={
                "Average_Lead_Time": "Average recorded lead time",
                "Shipment_Records": "Shipment records"
            },
            title="Average Recorded Shipping Lead Time by US State"
        )

        fig_map.update_layout(height=600)

        st.plotly_chart(fig_map, use_container_width=True)

        st.caption(
            "This map displays recorded lead times, not verified actual delivery "
            "performance. Future ship dates in the dataset may affect the results."
        )
    else:
        st.info("State or shipping lead-time data is unavailable.")

    st.subheader("Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)

    with st.expander("View all column names"):
        st.write(list(df.columns))

except FileNotFoundError:
    st.error(
       "Excel file not found. Please check that "
"'Nassau_Candy_Final_Analysis.xlsx' is in the same folder as app.py."

    )

except Exception as e:
    st.error(f" An error occurred while loading the data:{e}")

st.caption("Nassau Candy Distributor | Business Intelligence Project")