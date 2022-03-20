import json
import re
from pathlib import Path
from typing import List

import pandas as pd
import unidecode


def _get_date_info(df_singers: pd.DataFrame, input_col: str) -> pd.DataFrame:
    """Extract date info from a string column

    Args:
        df_singers (pd.DataFrame): Dataframe to get date info from
        input_col (str): Name of date column (either "Naissance" or "Décès")

    Returns:
        pd.DataFrame: Dataframe with the date column transformed into two new columns
            ("Date de [Naissance|Décès]", "Année de [Naissance|Décès])
    """
    df_date = df_singers.loc[:, [input_col]]
    df_date["year"] = df_date[input_col].str.extract(r"([12]\d{3})")[0]

    reg_month = "janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre"
    df_date["day_month"] = df_date[input_col].str.extract(
        r"(\d{1,2}\s*(?:" + reg_month + "))"
    )[0]
    df_date["day"] = df_date.day_month.str.extract(r"(\d{1,2})")

    matching_month = {
        month: str(value).zfill(2)
        for month, value in zip(reg_month.split("|"), range(1, 13))
    }
    df_date["month"] = df_date.day_month.str.extract(r"(" + reg_month + ")")[0].map(
        matching_month
    )

    df_singers[f"Date de {input_col}"] = (
        df_date.year + "-" + df_date.month + "-" + df_date.day
    )
    df_singers[f"Année de {input_col}"] = df_date.year.astype(float)
    return df_singers


def _fix_string_field(df_singers: pd.DataFrame, fields: List[str]) -> pd.DataFrame:
    """Makes some string transformation (unicode, lower, strip,...) to string columns

    Args:
        df_singers (pd.DataFrame): Dataframe
        fields (List[str]): List of fields to fix

    Returns:
        pd.DataFrame: Dataframe with the fields fixed
    """
    for field in fields:
        df_str_to_fix = df_singers.loc[df_singers[field].notna(), field]
        df_str_to_fix = df_str_to_fix.map(
            lambda x: re.sub(
                r"\s,", ",", (re.sub(r"\s\s+", " ", unidecode.unidecode(x).lower()))
            )
        )
        df_singers.loc[df_singers[field].notna(), field] = df_str_to_fix
    return df_singers


def _clean_data_singers(df_singers: pd.DataFrame) -> pd.DataFrame:
    """Clean the DataFrame obtained by scrapping into an usable DataFrame

    Args:
        df_singers (pd.DataFrame): Input Dataframe

    Returns:
        pd.DataFrame: Clean Dataframe
    """
    singer_columns = [
        "name",
        "Nom de naissance",
        "Naissance",
        "Activité principale",
        "Genre musical",
        "Nationalité",
        "Instruments",
        "Années actives",
        "Décès",
        "Labels",
        "Période d'activité",
    ]
    df_singers = df_singers.loc[:, singer_columns]
    df_singers["name"] = df_singers.name.str.split("(", expand=True)[0]
    df_singers["Nom de naissance"] = df_singers["Nom de naissance"].fillna(
        df_singers.name
    )

    df_singers = _get_date_info(df_singers, input_col="Naissance")
    df_singers = _get_date_info(df_singers, input_col="Décès")

    df_singers = df_singers.drop(["Naissance", "Décès"], axis=1)
    df_singers = _fix_string_field(
        df_singers,
        fields=[
            "Activité principale",
            "Instruments",
            "Genre musical",
            "Labels",
            "Nationalité",
        ],
    )
    df_singers = df_singers.rename(columns={"name": "Nom connu"})
    return df_singers


def transform_scrapped_singers_to_csv(
    scrapped_singer_path: Path, output_csv: Path
) -> None:
    """Clean the dataframe obtained by scrapy and save it into a csv file

    Args:
        scrapped_singer_path (Path): Saved scrapy results
        output_csv (Path): Saving path for csv results
    """

    with open(scrapped_singer_path, "r") as f:
        data_singers = json.load(f)

    df_singers = pd.DataFrame(data_singers)
    df_singers = _clean_data_singers(df_singers)
    df_singers.to_csv(output_csv, index=False)
