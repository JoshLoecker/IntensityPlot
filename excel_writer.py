import argparse
import openpyxl
from openpyxl.styles import Alignment
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.workbook.workbook import Workbook
import pandas as pd
import pathlib


class PlasmaTable:
    def __init__(self, data_frame: pd.DataFrame, args: argparse.Namespace):

        """
        This class is responsible for writing data to excel files. This will ALWAYS create a new workbook

        :param workbook_save_path: The path AND file name for the output excel file
        """
        self.__dataframe = data_frame
        self.__args = args
        self.__clinical_sheetname = "Clinically Relevant Proteins"
        self.__all_proteins_sheetname = "All Proteins"
        self.__headings = ["SDC", "SDC-C18", "Urea", "Urea-C18"]
        self.__subheadings = [
            "Dried\nAverage",
            "Dried\n%CV",
            "Liquid\nAverage",
            "Liquid\n%CV",
            "D/L\nRatio",
        ]

        self.__workbook: Workbook = Workbook()

        self.__first_set_up = self.set_up_workbook()
        self.write_data()
        self.write_protein_information()

        if self.__first_set_up:
            # Delete Expected Plasma Concentration column from All Proteins as it is not needed
            self.__workbook[self.__all_proteins_sheetname].delete_cols(3)
            self.remerge_cells()

        self.__workbook.save(self.__args.excel)

    def set_up_workbook(self) -> bool:
        """
        This function will check if excel file to write to currently exists

        If it does exist, it will return an object of openpyxl.load_workbook()
        If the file does not exist, it will return a new file of openpyxl.Workbook()

        :return:
        """
        if pathlib.Path.exists(pathlib.Path(self.__args.excel)):
            self.__workbook = openpyxl.load_workbook(self.__args.excel)
            return False
        else:
            self.__workbook = openpyxl.Workbook()

            # We do not want Sheet. It is easier to make two new sheets
            del self.__workbook["Sheet"]

            # Create our sheets to write to
            self.__workbook.create_sheet(self.__clinical_sheetname)
            self.__workbook.create_sheet(self.__all_proteins_sheetname)

            self.set_subheading_alignment()
            self.write_headings()

            return True

    def set_subheading_alignment(self) -> None:
        """
        This function is responsible for setting a 'center' alignment for each of the header cells
        :return:
        """
        # Iterate through each worksheet
        for sheet in self.__workbook.worksheets:

            for row in range(1, 3):
                for col in range(1, 24):

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

            # Write values that are consistent between the two sheets
            sheet["A2"] = "Protein\nName"
            sheet["B2"] = "Majority\nProtein\nID"
            sheet.merge_cells("A1:B1")

            # Start writing the top-most headings
            for i, col_num in enumerate(range(4, 24, 5)):

                sheet.cell(row=1, column=col_num, value=self.__headings[i])
                sheet.merge_cells(
                    start_row=1, end_row=1, start_column=col_num, end_column=col_num + 4
                )

                # Write subheadings (dried average, dried %CV, liquid average, etc.)
                for sub_col_num in range(0, 5):
                    sheet.cell(
                        row=2,
                        column=col_num + sub_col_num,
                        value=self.__subheadings[sub_col_num],
                    )

    def remerge_cells(self):
        """
        This function will re-merge cells after deleting a column

        From: https://stackoverflow.com/questions/58412906

        :return: None
        """
        delete_index = 3
        for merged_cells in self.__workbook[self.__all_proteins_sheetname].merged_cells:
            if delete_index < merged_cells.min_col:
                merged_cells.shift(col_shift=-1)
            elif delete_index <= merged_cells.max_col:
                merged_cells.shrink(right=1)

    def write_protein_information(self) -> None:
        """
        This function will write the name of the protein and the ID into columns 1 and 2, respectively

        On the Clinically Relevant sheet, we will write the expected protein concentration

        :return: None
        """

        columns_to_write: list[str] = [
            "dried_average",
            "dried_variation",
            "liquid_average",
            "liquid_variation",
            "dried_liquid_ratio",
        ]

        for value in self.__dataframe["dried_average"]:
            print(value)
        print("\nHERE\n")

        for sheet in self.__workbook.worksheets:
            for i, (protein_id, protein_name, expected_concentration) in enumerate(
                zip(
                    self.__dataframe["protein_id"],
                    self.__dataframe["protein_name"],
                    self.__dataframe["expected_concentration"],
                )
            ):
                current_row = i + 3

                sheet.cell(row=current_row, column=1, value=protein_name)
                sheet.cell(row=current_row, column=2, value=protein_id)
                sheet.cell(
                    row=current_row,
                    column=3,
                    value=float(expected_concentration),
                )

                # Write maxquant values to appropriate locations
                if str(self.__args.method).lower() == "direct":
                    start_col = 4
                else:
                    start_col = 9

                if str(self.__args.experiment).lower() == "urea":
                    start_col += 10

                if (
                    not self.__first_set_up
                    and sheet.title == self.__all_proteins_sheetname
                ):
                    start_col -= 1

                for j, column_index in enumerate(range(start_col, start_col + 5)):
                    if (
                        self.__dataframe.loc[i, "relevant"]
                        and sheet.title == self.__clinical_sheetname
                    ):
                        # TODO: Only write on correct protein name
                        # TODO: Only write clinically relevant proteins in clinically relevant protein file

                        # Write to clinically relevant
                        sheet.cell(
                            row=current_row,
                            column=column_index,
                            value=self.__dataframe[columns_to_write[j]][i],
                        )
                    else:
                        sheet.cell(
                            row=current_row,
                            column=column_index,
                            value=self.__dataframe[columns_to_write[j]][i],
                        )

                """
                "Dried
Average"	"Dried
%CV"	"Liquid
Average"	"Liquid
%CV"	"D/L
Ratio"
                """

    def write_data(self) -> None:
        """
        This function will be responsible for writing the data contained in the 'dataframe' argument

        If the 'relevant' column is True then the row should be written to the Clinical worksheet and the All Proteins worksheet
            Otherwise, if the value is false, it should only be written to the All Proteins worksheet
        :return: None
        """
        pass
