import os
import json
from datetime import datetime
import pandas as pd
from abc import ABC, abstractmethod


class DataPreprocessor(ABC):
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def info(self, export=False, export_dir='info_exports', file_prefix='data_info'):
        delimiter_string = '---------------------------'
        info_dict = {}

        today = datetime.today()
        today_str = today.strftime('%d_%m_%Y')
        today_iso = today.isoformat()
        info_dict['export_date'] = today_iso

        info_dict['shape'] = self.data.shape
        print('SHAPE OF DATA:', self.data.shape, delimiter_string, sep='\n')

        dtype_counts = self.data.dtypes.value_counts()
        info_dict['raw_column_data_types'] = {str(k): int(v) for k, v in dtype_counts.items()}
        print('RAW COLUMN DATA TYPES:', dtype_counts, delimiter_string, sep='\n')

        null_percentages = self.data.isnull().mean() * 100
        null_counts = self.data.isnull().sum()
        sorted_nulls = sorted(null_percentages.items(), key=lambda x: x[1], reverse=True)

        null_info = {}
        print('PERCENTAGE OF NULL/NONE VALUES:')
        print('(Only columns with at least one NULL/NONE value are shown)')
        for column, percent in sorted_nulls:
            count = null_counts[column]
            if count > 0:
                print(f"{column}: %{percent:.2f} null ({count} data point)")
                null_info[column] = {'percentage': round(percent, 2), 'count': int(count)}
        print('', delimiter_string)
        info_dict['null_info'] = null_info

        if export:
            os.makedirs(export_dir, exist_ok=True)
            export_path = os.path.join(export_dir, f"{file_prefix}_{today_str}.json")
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(info_dict, f, ensure_ascii=False, indent=4)
            print(f"Info exported to {export_path}")

    def one_hot_encode(self, columns: list[str], drop_original: bool = True) -> pd.DataFrame:
        data_copy = self.data.copy()

        for col in columns:
            data_copy[col] = data_copy[col].fillna("Empty")

        df_encoded = pd.get_dummies(data_copy, columns=columns, prefix=columns, dtype=int)
        df_encoded.columns = [col.replace(" ", "") for col in df_encoded.columns]
        return df_encoded if drop_original else pd.concat([data_copy, df_encoded], axis=1)

    def ordinal_encode(self, columns: list[str], order: list[str] = ['Low', 'Moderate', 'High', 'Very High', 'Extreme'], new_columns=None) -> pd.DataFrame:
        data_copy = self.data.copy()

        full_order = ["Empty"] + [item for item in order if item != "Empty"]
        encoding = {key: idx for idx, key in enumerate(full_order)}

        if new_columns is None:
            new_columns = columns

        for col, new_col in zip(columns, new_columns):
            data_copy[new_col] = (
                data_copy[col]
                .fillna("Empty")
                .map(lambda x: encoding.get(x, encoding["Empty"]))
            )
        return data_copy

    @abstractmethod
    def preprocess(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        raise NotImplementedError()
