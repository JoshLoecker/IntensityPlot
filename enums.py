from enum import Enum


class PlotType(Enum):
    """
    This is a set of valid Enums available for plot types
    From: https://stackoverflow.com/a/1695250
    """

    abundance_variation = "abundance_variation"
    abundance_lfq = "abundance_lfq"
    lfq_variation = "lfq_variation"
