import csv
import pathlib

import numpy as np
import pandas as pd


class _GatherProteinData:
    def __init__(self):
        self._clinical_protein_names: list[str] = []
        self._clinical_protein_ids: list[str] = []
        self._expected_concentration: list[str] = []

        # Gather clinically relevant proteins and protein IDS
        with open("clinically_relevant.tsv", "r") as i_stream:
            reader = csv.reader(i_stream, delimiter="\t")
            next(reader)

            for line in reader:
                self._clinical_protein_names.append(line[0])
                self._clinical_protein_ids.append(line[1])
                self._expected_concentration.append(line[2])

    @property
    def clinical_names(self) -> list[str]:
        return self._clinical_protein_names

    @property
    def clinical_ids(self) -> list[str]:
        return self._clinical_protein_ids

    @property
    def expected_concentrations(self) -> list[str]:
        return self._expected_concentration


def filter_variation(data_frame: pd.DataFrame, max_variation: int = 20) -> pd.DataFrame:
    """
    This function will filter variation values

    Any variantion values LESS THAN max_variation will be accepted
    We must also filter GREATER THAN 0 because NaN values in the dataframe have been set to 0

    We are currently accepting liquid OR dried variation less than max_variation

    :param data_frame: The dataframe to filter from
    :param max_variation: The maximum variation value to accept
    :return: A pandas dataframe containing the filtered values
    """
    data_frame = data_frame[
        (
            (0 < data_frame["dried_variation"])
            & (data_frame["dried_variation"] <= max_variation)
        )
        | (
            (0 < data_frame["liquid_variation"])
            & (data_frame["liquid_variation"] <= max_variation)
        )
    ]
    data_frame.reset_index(drop=True, inplace=True)

    return data_frame


def substring_id_match(max_quant_ids: str, clinical_ids: str) -> bool:
    """
    This function is responsible for matching protein ID sets from one row of results

    For example:
    - max_quant_ids: A123;B234
    - clinical_ids: F789;G234;A123

    This function will find the "A123" match between both lists, and return true

    :param max_quant_ids: A semi-colon (;) separated list of protein IDs from max quant
    :param clinical_ids: A semi-colon (;) separated list of clinically relevant protein IDs
    :return: Boolean
    """
    for max_quant_id in max_quant_ids.split(";"):
        for clinical_id in clinical_ids.split(";"):

            if clinical_id == max_quant_id:
                return True
    return False


def substring_name_match(max_quant_name: str, clinical_name: str) -> bool:
    """
    This function will be responsible for matching proteins by name
    This function will only be called if matching by protein IDs failed

    :param max_quant_name: The MaxQuant protein name
    :param clinical_name: The clinically relevant protein name
    :return: Boolean stating if proteins match
    """
    # TODO: Write this function
    return False


def add_clinical_relevance(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    This function will add clinically relevant information to the data frame

    It will add a column "relevant" and "expected_concentration"
    These values will only be modified if the protein is clinically relevant

    Default values:
    - relevant: False
    - expected_concentration: -1

    :param data_frame: The incoming data frame
    :return: pd.DataFrame()
    """
    data_frame.assign(
        relevant=np.nan, expected_concentration=np.nan, clinical_id=np.nan
    )

    # Gather a list of clinically relevant proteins
    gather_proteins = _GatherProteinData()
    clinical_ids = gather_proteins.clinical_ids
    clinical_names = gather_proteins.clinical_names
    expected_concentrations = gather_proteins.expected_concentrations

    for i, (max_quant_id, max_quant_name) in enumerate(
        zip(data_frame["protein_id"], data_frame["protein_name"])
    ):

        for j, (clinical_id, clinical_name, expected_conc) in enumerate(
            zip(clinical_ids, clinical_names, expected_concentrations)
        ):

            if substring_id_match(max_quant_id, clinical_id) or substring_name_match(
                max_quant_id, clinical_id
            ):
                data_frame.loc[i, "relevant"] = True
                data_frame.loc[i, "expected_concentration"] = expected_conc
                data_frame.loc[i, "clinical_id"] = clinical_id

                break

    # Must replace NaN values otherwise pandas throws a ValueError when trying to filter
    data_frame["relevant"].replace(
        to_replace=np.nan,
        value=False,
        inplace=True,
    )
    data_frame["clinical_id"].replace(to_replace=np.nan, value="", inplace=True)

    return data_frame


def set_abundance_values():
    """
    This function will add an abundance column to clinically relevant proteins

    If the protein does not have an expected concentration, the abundance value can be set to 0
    :return:
    """
    pass


if __name__ == "__main__":
    import main

    input_file = pathlib.Path("./data/c18/sdc/proteinGroups.txt")
    data_frame: pd.DataFrame = main.create_intensity_dataframe(input_file)
    add_clinical_relevance(data_frame)
