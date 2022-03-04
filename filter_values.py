import csv
import pathlib
import pandas as pd


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


def filter_clinically_relevant(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    This function will take an incoming dataframe and filter its protein_name column against clinically relevant proteins from the 'clinicallyRelevant.txt' file

    Use fuzzywuzzy as a search algorithm? https://pypi.org/project/fuzzywuzzy/

    :param data_frame: The incoming dataframe
    :return: A new dataframe containing the intersect of MaxQuant proteins and clinically relevant proteins
    """
    intersection: pd.DataFrame = pd.DataFrame()

    with open("./clinically_relevant.tsv") as i_stream:
        reader = csv.reader(i_stream, delimiter="\t")
        header = next(reader)
        for line in reader:
            protein = line[0]
            protein_id = line[1]

    return intersection


if __name__ == "__main__":
    import main

    input_file = pathlib.Path("./data/c18/sdc/proteinGroups.txt")
    data_frame: pd.DataFrame = main.create_intensity_dataframe(input_file)
    filter_clinically_relevant(data_frame)
