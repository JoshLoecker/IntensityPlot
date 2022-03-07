import csv
import pathlib
import pandas as pd


class _GatherProteinData:
    def __init__(self):
        self.clinically_relevant_proteins: list[str] = []
        self.clinically_relevant_protein_ids: list[str] = []

        # Gather clinically relevant proteins and protein IDS
        with open("clinically_relevant.tsv", "r") as i_stream:
            reader = csv.reader(i_stream, delimiter="\t")
            next(reader)

            for line in reader:
                self.clinically_relevant_proteins.append(line[0])
                self.clinically_relevant_protein_ids.append(line[1])


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

    return data_frame[
        (
            (0 < data_frame["dried_variation"])
            & (data_frame["dried_variation"] < max_variation)
        )
        | (
            (0 < data_frame["liquid_variation"])
            & (data_frame["liquid_variation"] < max_variation)
        )
    ]


def substring_match(max_quant_ids: str, clinical_ids: str) -> bool:
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


def filter_clinically_relevant(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    This function will take an incoming dataframe and filter its protein_name column against clinically relevant proteins from the 'clinicallyRelevant.txt' file

    Use fuzzywuzzy as a search algorithm? https://pypi.org/project/fuzzywuzzy/

    :param data_frame: The incoming dataframe
    :return: A new dataframe containing the intersect of MaxQuant proteins and clinically relevant proteins
    """

    clinically_relevant_data_frame = pd.DataFrame(
        {column: [] for column in data_frame.columns}
    )
    gather_proteins = _GatherProteinData()
    clinically_relevant_protein_ids = gather_proteins.clinically_relevant_protein_ids

    for i, max_quant_id in enumerate(data_frame["protein_id"]):

        for clinical_id in clinically_relevant_protein_ids:

            # search for protein IDS
            if substring_match(max_quant_id, clinical_id):
                clinically_relevant_data_frame = pd.concat(
                    [clinically_relevant_data_frame, data_frame.iloc[i]],
                    axis=1,
                    ignore_index=True,
                    join="outer",
                )
                break  # Only care if one ID matches

    clinically_relevant_data_frame = clinically_relevant_data_frame.transpose()
    clinically_relevant_data_frame.dropna(how="all", inplace=True)
    clinically_relevant_data_frame.reset_index(drop=True, inplace=True)

    return clinically_relevant_data_frame


if __name__ == "__main__":
    import main

    input_file = pathlib.Path("./data/c18/sdc/proteinGroups.txt")
    data_frame: pd.DataFrame = main.create_intensity_dataframe(input_file)
    filter_clinically_relevant(data_frame)
