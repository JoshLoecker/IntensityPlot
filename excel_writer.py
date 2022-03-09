import argparse
import openpyxl
from openpyxl.styles import Alignment
from openpyxl.worksheet.worksheet import Worksheet
import pandas as pd
import pathlib


headings = ["SDC", "SDC-C18", "Urea", "Urea-C18"]
subheadings = [
    "Dried\nAverage",
    "Dried\n%CV",
    "Liquid\nAverage",
    "Liquid\n%CV",
    "D/L\nRatio",
]


class PlasmaTable:
    def __init__(
        self,
        data_frame: pd.DataFrame,
        args: argparse.Namespace,
        workbook_save_path: pathlib.Path,
    ):

        """
        This class is responsible for writing data to excel files. This will ALWAYS create a new workbook

        :param workbook_save_path: The path AND file name for the output excel file
        """
        self.__dataframe = data_frame
        self.__args = args
        self.__workbook = openpyxl.Workbook()

        # We do not want Sheet. It is easier to make two new sheets
        del self.__workbook["Sheet"]

        self.__clinical_sheetname = "Clinically Relevant Proteins"
        self.__all_proteins_sheetname = "All Proteins"

        self.__workbook.create_sheet(self.__clinical_sheetname)
        self.__workbook.create_sheet(self.__all_proteins_sheetname)

        self.set_subheading_alignment()
        self.write_headings()
        self.write_data()

        self.__workbook.save(workbook_save_path)

    def set_subheading_alignment(self) -> None:
        """
        This function is responsible for setting a 'center' alignment for each of the header cells
        :return:
        """
        # Iterate through each worksheet
        for sheet in self.__workbook.worksheets:

            for row in range(1, 3):
                for col in range(1, 23):

                    sheet.cell(row, col).alignment = Alignment(
                        wrapText=True, horizontal="center", vertical="center"
                    )

    def write_headings(self) -> None:
        """
        This function will write the heading values for each worksheet
        It attempts to do this in the least amount of copy-paste code as possible
        :return:
        """
        # Get worksheets to write data that is independent between the two
        clinical_sheet: Worksheet = self.__workbook[self.__clinical_sheetname]
        all_proteins_sheet: Worksheet = self.__workbook[self.__all_proteins_sheetname]

        # Set clinical worksheet headings
        clinical_sheet["A1"] = "Clinically Relevant"
        clinical_sheet["C1"] = "Typical\nPlasma\nConc"
        clinical_sheet.merge_cells("C1:C2")

        # Set All Proteins sheet headings
        all_proteins_sheet["A1"] = "Identified Proteins"

        # Iterate through each sheet in the workbook
        for sheet in self.__workbook.worksheets:

            # We must start the SDC, SDC-C18, Urea, Urea-C18 headings at different locations depending on the workbook
            # This is because the clinical sheet has an extra "Typical Plasma Conc" column
            if sheet.title == self.__clinical_sheetname:
                start_heading = 4
                end_heading = 19
            else:
                start_heading = 3
                end_heading = 18

            # Write values that are consistent between the two sheets
            sheet["A2"] = "Protein\nName"
            sheet["B2"] = "Protein\nID"
            sheet.merge_cells("A1:B1")

            # Start writing the top-most headings
            for i, col_num in enumerate(range(start_heading, end_heading + 1, 5)):

                sheet.cell(row=1, column=col_num, value=headings[i])
                sheet.merge_cells(
                    start_row=1, end_row=1, start_column=col_num, end_column=col_num + 4
                )

                # Write subheadings (dried average, dried %CV, liquid average, etc.)
                for sub_col_num in range(0, 5):
                    sheet.cell(
                        row=2,
                        column=col_num + sub_col_num,
                        value=subheadings[sub_col_num],
                    )

    def get_column_to_write(self) -> dict[str, int]:
        """
        This function will be responsible for returning the appropriate column number to write intensity values

        For example, if the input data is from SDC-C18, then the following dictionary should be returned:
            {
                "dried_average": 3
                "dried_variation": 4
                "liquid_average": 5
                "liquid_variation": 6
                "dried_liquid_ratio": 7
            }

        If the input data is from Urea, the following dictionary will be returned:
            {
                "dried_average": 13
                "dried_variation": 14
                "liquid_average": 15
                "liquid_variation": 16
                "dried_liquid_ratio": 17
            }

        :return: Dicionary of [str, int]
        """
        column_index = {
            "dried_average": -1,
            "dried_variation": -1,
            "liquid_average": -1,
            "liquid_variation": -1,
            "dried_liquid_ratio": -1,
        }

        """
        We only need to do an explicit check for 'direct' and 'urea'
        This is because if the method is C18, the first if/else statement will set start to 8, and end to 12.
        
        If the experiment type is urea, it will add 10 to start and end. If it is of type SDC, the values are already set for these experiments
        """

        if str(self.__args.method).lower() == "direct":
            start = 3
            end = 7
        else:
            start = 8
            end = 12

        if str(self.__args.experiment).lower() == "urea":
            start += 10
            end += 10

        for i, (key, set_index) in enumerate(zip(column_index, range(start, end + 1))):
            column_index[key] = set_index

        return column_index

    def write_data(self) -> None:
        """
        This function will be responsible for writing the data contained in the 'dataframe' argument

        If the 'relevant' column is True then the row should be written to the Clinical worksheet and the All Proteins worksheet
            Otherwise, if the value is false, it should only be written to the All Proteins worksheet
        :return: None
        """
        column_indices: dict[str, int] = self.get_column_to_write()
        print(column_indices)
