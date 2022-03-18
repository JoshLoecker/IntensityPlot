from enum import Enum


class PlotType(Enum):
    """
    This is a set of valid Enums available for plot types
    From: https://stackoverflow.com/a/1695250
    """

    abundance_variation = "abundance_variation"
    abundance_intensity = "abundance_intensity"
    intensity_variation = "intensity_variation"
