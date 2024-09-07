"""
Classes FinanceData and Expense to handle expenses and all data.

 ／l、               
（ﾟ､ ｡ ７         
  l  ~ヽ       
  じしf_,)ノ
"""

import pandas as pd
from datetime import datetime
from copy import deepcopy
from dataclasses import dataclass
import os

def create_blank_csv(filename: str) -> "Idfk":
    if not os.path.exists(filename):
        with open(filename, 'w+') as h:
            h.write("date,category,title,amount,notes,month")
        return True
    else:
        return False

@dataclass
class Expense:
    date: datetime.date
    category: str
    title: str
    amount: float
    notes: str

    @property
    def as_df(self):
        return pd.DataFrame(
            {
                "date": [str(self.date)],
                "category": [self.category],
                "title": [self.title],
                "amount": [self.amount],
                "notes": [self.notes],
            }
        )


class FinanceData(object):
    def __init__(self, csv_filepath: str) -> None:
        """FinanceData.data should be mutable -- simply stores the dataframe. This class also provides methods monthlys(), dump_csv(), add_expense(), and month_sums based on the stored dataframe."""
        self.data = pd.read_csv(csv_filepath)
        self.data = self.preprocess_expenses(self.data)

        self._csv_filepath = csv_filepath

    @staticmethod
    def preprocess_expenses(finances: pd.DataFrame) -> pd.DataFrame:
        # convert date column to datetime to extract month (can also do it with strings, this is slower maybe but more robust)
        finances["date"] = pd.to_datetime(finances["date"], format="mixed")
        finances.sort_values(by="date", ascending=False)
        finances.set_index("date")

        finances["month"] = finances["date"].apply(
            lambda date: f"{date.month}-{date.year}"
        )
        finances.sort_values(by="date", ascending=False, inplace=True)
        finances['date'] = finances['date'].apply(lambda d: str(d)[:10]) # convert back to string for display purposes
        return finances.reset_index(drop=True)[
            ["date", "category", "title", "amount", "notes", "month"]
        ]

    def monthlys(self, selected_month: str) -> pd.DataFrame:
        if len(self.data) == 0:
            return None
        
        _fin: pd.DataFrame = deepcopy(self.data)
        if selected_month == "ALL":
            _fin = _fin[["category", "amount"]].groupby("category").sum()
        else:
            if selected_month not in list(_fin["month"]):
                raise ValueError("month not found")
            _fin = _fin[_fin["month"] == selected_month]
            _fin = _fin[["category", "amount"]].groupby("category").sum()

        _fin["height"] = _fin["amount"] / max(_fin["amount"])
        return _fin.reset_index()

    def dump_csv(self) -> None:
        self.data.to_csv(self._csv_filepath, index=False)

    def add_expense(self, expense: Expense) -> None:
        if len(self.data) != 0:
            self.data = pd.concat([self.data, expense.as_df]).reset_index(
                drop=True
            )
        else:
            self.data = expense.as_df

    @property
    def month_sums(self) -> pd.DataFrame:
        months = list(set(self.data["month"]))
        month_data: dict = {}
        for month in months:
            sum = self.data[self.data["month"] == month]["amount"].sum()
            month_data[month] = sum
        ms = pd.DataFrame({"month": month_data.keys(), "sum": month_data.values()})
        ms['month'] = pd.to_datetime(ms['month'], format="%m-%Y")
        return ms.sort_values(by='month')
    



