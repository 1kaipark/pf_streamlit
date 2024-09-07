import streamlit as st
import pandas as pd
from datetime import datetime

from utils.pf_csv_interface import FinanceData, Expense, create_blank_csv

user = st.session_state['name']
filename = f"expenses_{user}.csv"
try:
    finance_data = FinanceData(filename)
except FileNotFoundError:
    create_blank_csv(filename)
    finance_data = FinanceData(filename)

categories: list[str] = ["living", "transport", "food", "fun", "education"]
months: list[str] = ["ALL"] + sorted(list(set(finance_data.data["month"])), reverse=True)


st.header(body="Personal Finance")

with st.container():
    st.subheader(body="Dashboard")
    month = st.selectbox("Month", options=months)
    monthly = finance_data.monthlys(selected_month=month)

    if monthly is not None:
        st.bar_chart(monthly, x="category", y="height")

        total = "${:20,.2f}".format(sum(monthly["amount"]))
        st.markdown(f"**Total Expenses**: {total}")

        st.dataframe(
            monthly[["category", "amount"]], use_container_width=True, hide_index=True
        )

        monthsums: pd.DataFrame = finance_data.month_sums
        if len(monthsums) > 1:
            st.line_chart(data=monthsums, x="month", y="sum")

with st.form(key="my_form", clear_on_submit=True):
    st.subheader(body="Add Expense")
    date = st.date_input("Date", value=datetime.today())
    category = st.selectbox("Category", options=categories)
    title = st.text_input("Title")
    amount = st.number_input("Amount", format="%2f")
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        expense = Expense(date, category, title, amount, notes)
        finance_data.add_expense(expense)
        monthly = finance_data.monthlys(selected_month=month)

        finance_data.dump_csv()
        st.success("Expense added successfully!")
        st.rerun()


with st.container():
    st.header(body="All Expenses")

    # delete checkbox
    finance_data.data["delete"] = False
    finance_data.data = finance_data.data[
        ["delete"] + [col for col in finance_data.data.columns if col != "delete"]
    ]

    edited_finances = st.data_editor(
        data=finance_data.data[
            ["delete", "date", "title", "category", "amount", "notes"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    if st.button("Delete Selected Rows"):
        finance_data.data = (
            finance_data.data[edited_finances["delete"] == False]
            .drop(columns="delete")
            .reset_index(drop=True)
        )
        finance_data.dump_csv()
        st.success("Selected rows deleted successfully!")
        st.rerun()

    if st.button("Dump to CSV"):
        finance_data.data = (
            finance_data.data[edited_finances["delete"] == False]
            .drop(columns="delete")
            .reset_index(drop=True)
        )

        finance_data.data.update(
            edited_finances.drop(columns="delete").reset_index(drop=True)
        )
        finance_data.dump_csv()

        st.success("Changes saved successfully!")
        st.rerun()
