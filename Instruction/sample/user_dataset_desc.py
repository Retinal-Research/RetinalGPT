from __future__ import annotations

import pandas as pd


class UserDatasetDescription:
    def __init__(self, metadata_csv: str, image_column: str = "image"):
        self.image_column = image_column
        self.metadata = pd.read_csv(metadata_csv)
        if image_column not in self.metadata.columns:
            raise ValueError(f"Missing required image column: {image_column}")
        self.metadata = self.metadata.set_index(image_column, drop=False)

    def _get_row(self, image_name: str):
        if image_name in self.metadata.index:
            return self.metadata.loc[image_name]

        stem = image_name.rsplit(".", 1)[0]
        stem_matches = self.metadata[self.metadata[self.image_column].astype(str).str.rsplit(".", n=1).str[0] == stem]
        if len(stem_matches) == 1:
            return stem_matches.iloc[0]

        return None

    @staticmethod
    def _clean_value(value):
        if pd.isna(value):
            return ""
        text = str(value).strip()
        return "" if text.lower() in {"", "nan", "none"} else text

    def get_description(self, file_name: str = "") -> str:
        row = self._get_row(file_name)
        if row is None:
            return ""

        fields = [
            ("modality", "modality"),
            ("quality", "image quality rating"),
            ("disease", "disease or abnormalities"),
            ("vascular", "vascular quantitative analysis"),
            ("notes", "additional retinal notes"),
        ]

        parts = []
        for column, label in fields:
            if column not in row.index:
                continue
            value = self._clean_value(row[column])
            if value:
                parts.append(f"{label}: {value}")

        return ",".join(parts)
