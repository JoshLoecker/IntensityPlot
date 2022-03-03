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
    intersect_df: pd.DataFrame = pd.DataFrame()

    return intersect_df
