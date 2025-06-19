
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

    # Summary
    st.subheader("📝 Summary Insights")
    most_drug = df['Drug'].mode()[0] if not df['Drug'].mode().empty else "N/A"
    most_reaction = df['Reaction'].mode()[0] if not df['Reaction'].mode().empty else "N/A"
    top_demo = demo.sort_values("Count", ascending=False).iloc[0]

    st.markdown(f"""
    - **Total Reports**: {len(df)}
    - **Most Frequent Drug**: `{most_drug}`
    - **Most Frequent Reaction**: `{most_reaction}`
    - **Top Patient Group**: `{top_demo['Patient Age Group']}` ({top_demo['Count']} reports)
    """)

    # Export processed data
    st.subheader("⬇️ Download Report")
    export_data = BytesIO()
    with pd.ExcelWriter(export_data, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Raw Data', index=False)
        demo.to_excel(writer, sheet_name='Demographics', index=False)
        signals.to_excel(writer, sheet_name='Signals', index=False)
    st.download_button("Download Excel Report", data=export_data.getvalue(), file_name="pv_analytics_report.xlsx")
