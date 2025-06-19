
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="SmartPV Analytics", layout="wide")
st.title("🧪 SmartPV Analytics – ADR Line Listing Insights")

uploaded_file = st.file_uploader("📤 Upload EMA ADR Line Listing (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ File uploaded and parsed successfully!")

    # Data Preview
    with st.expander("🔍 Preview Raw Data"):
        st.dataframe(df.head(10))

    # Demographic Summary
    st.subheader("👥 Demographic Summary")
    demo = df.groupby(["Patient Age Group", "Patient Sex"]).size().reset_index(name="Count")
    st.dataframe(demo)

    fig, ax = plt.subplots()
    demo.pivot(index="Patient Age Group", columns="Patient Sex", values="Count").plot(kind="bar", ax=ax)
    plt.title("Patient Demographics")
    st.pyplot(fig)

    # Signal Detection
    st.subheader("⚠️ Top Drug-Reaction Signals")
    df['Drug'] = df['Suspect/interacting Drug List (Drug Char - Indication PT - Action taken - [Duration - Dose - Route])'].str.extract(r'\[(.*?)\]')
    df['Reaction'] = df['Reaction List PT (Duration – Outcome - Seriousness Criteria)'].str.extract(r'([A-Za-z ]+)')
    signals = df.groupby(['Drug', 'Reaction']).size().reset_index(name="Count").sort_values("Count", ascending=False).head(10)
    st.dataframe(signals)

    # Timeline
    st.subheader("📈 Monthly ADR Reporting Trend")
    df['EV Gateway Receipt Date'] = pd.to_datetime(df['EV Gateway Receipt Date'])
    timeline = df.groupby(df['EV Gateway Receipt Date'].dt.to_period('M')).size().reset_index(name="Reports")
    timeline['EV Gateway Receipt Date'] = timeline['EV Gateway Receipt Date'].astype(str)

    fig2, ax2 = plt.subplots()
    ax2.plot(timeline['EV Gateway Receipt Date'], timeline['Reports'], marker='o')
    plt.xticks(rotation=45)
    plt.title("Monthly ADR Reports")
    st.pyplot(fig2)

    # Outcome & Seriousness Summary
    st.subheader("🧠 Outcome & Seriousness Summary")
    outcome_series = df['Reaction List PT (Duration – Outcome - Seriousness Criteria)'].dropna().str.extract(r'– (.*?) –')[0]
    seriousness_series = df['Reaction List PT (Duration – Outcome - Seriousness Criteria)'].dropna().str.extract(r'– .*? – (.*?)\)')[0]

    outcome_counts = outcome_series.value_counts().reset_index()
    outcome_counts.columns = ["Outcome", "Count"]
    seriousness_counts = seriousness_series.value_counts().reset_index()
    seriousness_counts.columns = ["Seriousness", "Count"]

    st.markdown("**Most Common Outcomes**")
    st.dataframe(outcome_counts)

    st.markdown("**Most Common Seriousness Criteria**")
    st.dataframe(seriousness_counts)

    # Summary
    st.header("📝 Summary Insights")
    most_drug = df['Drug'].mode()[0] if not df['Drug'].mode().empty else "N/A"
    most_reaction = df['Reaction'].mode()[0] if not df['Reaction'].mode().empty else "N/A"
    top_demo = demo.sort_values("Count", ascending=False).iloc[0]

    top_outcome = outcome_counts.iloc[0]["Outcome"] if not outcome_counts.empty else "N/A"
    top_seriousness = seriousness_counts.iloc[0]["Seriousness"] if not seriousness_counts.empty else "N/A"

    st.markdown(f"""
    - **Total Reports:** {len(df)}
    - **Most Frequent Drug:** `{most_drug}`
    - **Most Frequent Reaction:** `{most_reaction}`
    - **Top Patient Group:** `{top_demo['Patient Age Group']}` ({top_demo['Count']} reports)
    - **Most Common Outcome:** `{top_outcome}`
    - **Most Common Seriousness Criteria:** `{top_seriousness}`
    """)
     # Disproportionality Analysis (Simplified PRR)
st.header("📌 Disproportionality Analysis PRR Approximation")
      total_reports = len(df)
      drug_event_counts = df.groupby(['Drug', 'Reaction']).size().reset_index(name='Count')
      drug_counts = df['Drug'].value_counts().reset_index()
      drug_counts.columns = ['Drug', 'TotalDrugReports']
      reaction_counts = df['Reaction'].value_counts().reset_index()
      reaction_counts.columns = ['Reaction', 'TotalReactionReports']

     # Merge and compute PRR-like metric
       merged = pd.merge(drug_event_counts, drug_counts, on='Drug')
       merged = pd.merge(merged, reaction_counts, on='Reaction')
       merged['PRR_approx'] = (merged['Count'] / merged['TotalDrugReports']) / (merged['TotalReactionReports'] / total_reports)
       merged = merged.sort_values('PRR_approx', ascending=False).head(10)

st.dataframe(merged[['Drug', 'Reaction', 'Count', 'PRR_approx']])
     # Drug-Reaction Mapping Table
       st.header("🧬 Drug-Reaction Network Mapping")
       network_table = df.groupby(['Drug', 'Reaction']).size().reset_index(name="Frequency")
       st.dataframe(network_table.sort_values("Frequency", ascending=False).head(20))
     # Geographic Heatmap Summary
       st.header("🌍 ADR Reports by Country")
       country_counts = df['Primary Source Country for Regulatory Purposes'].value_counts().reset_index()
       country_counts.columns = ["Country", "Report Count"]
      st.dataframe(country_counts)

    # Export processed data
    st.subheader("⬇️ Download Report")
    export_data = BytesIO()
    with pd.ExcelWriter(export_data, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Raw Data', index=False)
        demo.to_excel(writer, sheet_name='Demographics', index=False)
        signals.to_excel(writer, sheet_name='Signals', index=False)
        outcome_counts.to_excel(writer, sheet_name='Outcomes', index=False)
        seriousness_counts.to_excel(writer, sheet_name='Seriousness', index=False)
    st.download_button("Download Excel Report", data=export_data.getvalue(), file_name="pv_analytics_report.xlsx")
