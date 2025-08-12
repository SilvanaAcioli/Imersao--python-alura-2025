import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Setup ---
st.set_page_config(
    page_title="Salaries in Data Dashboard",
    page_icon="📊",
    layout="wide",
)

URL_PT = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/main/dados-imersao-final.csv"
df = pd.read_csv(URL_PT)

COL_MAP = {
    "ano": "year",
    "senioridade": "seniority",
    "contrato": "contract_type",
    "cargo": "role",
    "salario": "salary",
    "moeda": "currency",
    "usd": "usd",
    "residencia": "country",
    "residencia_iso3": "country_iso3",  
    "experiencia": "experience",
    "tamanho_empresa": "company_size",
    "remoto": "work_model",
}
df = df.rename(columns=COL_MAP)

VALUE_MAP = {
    "executivo": "executive",
    "junior": "entry level",
    "pleno": "mid-level",
    "senior": "senior",
    "integral": "full time",
    "parcial": "part time",
    "contrato": 'contract',
    "remoto": "remote",
    "hibrido": "hybrid",
    "presencial": "onsite",
    "media": 'medium',
    "grande": 'large',
    "pequena": 'small',

}
df = df.replace(VALUE_MAP)

# --- Sidebar (Filters) ---
st.sidebar.header("🔍 Filters")

years_available = sorted(df["year"].unique())
years_selected = st.sidebar.multiselect("Year", years_available, default=years_available)

seniority_available = sorted(df["seniority"].unique())
seniority_selected = st.sidebar.multiselect("Seniority", seniority_available, default=seniority_available)

contracts_available = sorted(df["contract_type"].unique())
contracts_selected = st.sidebar.multiselect("Contract Type", contracts_available, default=contracts_available)

sizes_available = sorted(df["company_size"].unique())
sizes_selected = st.sidebar.multiselect("Company Size", sizes_available, default=sizes_available)

# --- Filtered DataFrame ---
df_filtered = df[
    (df["year"].isin(years_selected)) &
    (df["seniority"].isin(seniority_selected)) &
    (df["contract_type"].isin(contracts_selected)) &
    (df["company_size"].isin(sizes_selected))
]

# --- Main Content ---
st.title("🎲 Data Salaries Dashboard")
st.markdown("Explore salary data for data roles across recent years. Use the filters on the left to refine the view.")

# --- KPIs ---
st.subheader("Key Metrics (Annual Salary in USD)")

if not df_filtered.empty:
    avg_salary = df_filtered["usd"].mean()
    max_salary = df_filtered["usd"].max()
    total_records = df_filtered.shape[0]
    most_common_role = df_filtered["role"].mode()[0]
else:
    avg_salary = max_salary = 0
    total_records = 0
    most_common_role = ""

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average salary", f"${avg_salary:,.0f}")
c2.metric("Max salary", f"${max_salary:,.0f}")
c3.metric("Total records", f"{total_records:,}")
c4.metric("Most common role", most_common_role)

st.markdown("---")

# --- Charts ---
st.subheader("Charts")

col1, col2 = st.columns(2)

with col1:
    if not df_filtered.empty:
        top_roles = (
            df_filtered.groupby("role")["usd"]
            .mean().nlargest(10).sort_values(ascending=True).reset_index()
        )
        fig_roles = px.bar(
            top_roles,
            x="usd",
            y="role",
            orientation="h",
            title="Top 10 roles by average salary",
            labels={"usd": "Average annual salary (USD)", "role": ""}
        )
        fig_roles.update_layout(title_x=0.1, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_roles, use_container_width=True)
    else:
        st.warning("No data available for roles.")

with col2:
    if not df_filtered.empty:
        fig_hist = px.histogram(
            df_filtered,
            x="usd",
            nbins=30,
            title="Distribution of annual salaries",
            labels={"usd": "Salary range (USD)", "count": ""}
        )
        fig_hist.update_layout(title_x=0.1)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning("No data available for salary distribution.")

col3, col4 = st.columns(2)

with col3:
    if not df_filtered.empty:
        wm_counts = df_filtered["work_model"].value_counts().reset_index()
        wm_counts.columns = ["work_model", "count"]
        fig_pie = px.pie(
            wm_counts,
            names="work_model",
            values="count",
            title="Work model proportion",
            hole=0.5
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(title_x=0.1)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No data available for work model.")

with col4:
    if not df_filtered.empty:
        df_ds = df_filtered[df_filtered["role"] == "Data Scientist"]
        if not df_ds.empty:
            # fall back if your CSV doesn't have ISO3 after renaming
            iso_col = "country_iso3" if "country_iso3" in df_ds.columns else "residencia_iso3"
            fig_map = px.choropleth(
                df_ds.groupby(iso_col)["usd"].mean().reset_index(),
                locations=iso_col,
                color="usd",
                color_continuous_scale="RdYlGn",  # proper name
                title="Average Data Scientist salary by country",
                labels={"usd": "Average salary (USD)", iso_col: "Country"}
            )
            fig_map.update_layout(title_x=0.1)
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No Data Scientist records in the current filter.")
    else:
        st.warning("No data available for countries.")

# --- Detailed Table ---
st.subheader("Detailed Data")
st.dataframe(df_filtered)