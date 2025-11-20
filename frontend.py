import streamlit as st
from main import get_data_from_database, explain_results, detect_and_prepare_chart
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Speak2SQL",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Speak2SQL – AI Data Analyst")
st.caption("Ask questions about your database. Gets SQL → executes → explains → charts.")


# ----------------- CHAT MEMORY -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# ----------------- USER INPUT -----------------
user_query = st.chat_input("Ask a question about your data...")


if user_query:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.spinner("Analyzing..."):
        raw_sql_output = get_data_from_database(user_query)
        explanation = explain_results(user_query, raw_sql_output)
        chart_df = detect_and_prepare_chart(raw_sql_output)

    # ----- RAW DATA -----
    st.chat_message("assistant").write("### 🗂 SQL Result:")
    st.chat_message("assistant").write(raw_sql_output)

    # ----- EXPLANATION -----
    st.chat_message("assistant").write("### 📘 Explanation:")
    st.chat_message("assistant").write(explanation)

    # ----- CHART + CSV (SAFE, COLORFUL, FIXED) -----
    if chart_df is not None:
        st.chat_message("assistant").write("### 📊 Chart:")

        # ---------- CSV DOWNLOAD ----------
        csv_data = chart_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="result.csv",
            mime="text/csv"
        )

        # ---------- SAFETY CHECK ----------
        if chart_df.shape[1] < 2:
            st.info("Not enough data for a chart (needs at least 2 columns).")
        else:
            fig, ax = plt.subplots()

            x = chart_df.columns[0]
            y = chart_df.columns[1]

            # PIE CHART: if y is category/string
            if chart_df[y].dtype == "object" or chart_df[y].dtype.name == "category":
                ax.pie(
                    chart_df[x],
                    labels=chart_df[y],
                    autopct="%1.1f%%"
                )
                ax.set_title("Pie Chart")

            # BAR CHART: numeric
            elif chart_df[y].dtype in ["int64", "float64"]:
                ax.bar(chart_df[x], chart_df[y])
                ax.set_xlabel(str(x))
                ax.set_ylabel(str(y))
                ax.set_title("Bar Chart")

            st.pyplot(fig)

    # Save assistant reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": explanation
    })
