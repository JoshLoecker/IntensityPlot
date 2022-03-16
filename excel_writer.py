import argparse
import pathlib

import openpyxl
import pandas as pd
from openpyxl.styles import Alignment
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


class ClinicallyRelevant:
    def __init__(self):
        pass


class AllProteins:
    def __init__(self):
        pass


# TODO: Refactor this class to be split into two classes
# Class one: ClinicallyRelevant
# Class two: AllProteins
class PlasmaTable:
    def __init__(self, data_frame: pd.DataFrame, args: argparse.Namespace):

        """
        This class is responsible for writing data to excel files. This will ALWAYS create a new workbook

        :param data_frame: The data frame to work
        :param args: Variables gathered from the command line
        """
        self.__dataframe = data_frame
        self.__ingested_dataframe = pd.DataFrame()
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

        # TODO: Take this line out once finished with this class
        # It only needs to be written on first execution
        self.write_clinical_name_id()

        if self.__first_set_up:
            # Only need to write clinical names and IDs on first run
            self.write_clinical_name_id()

            # Delete Expected Plasma Concentration column from All Proteins as it is not needed
            self.__workbook[self.__all_proteins_sheetname].delete_cols(3)
            self.remerge_cells()

        # Write information
        self.write_clinical_data()

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

    def get_column_write_start(self, sheet_title: str):
        """
        This function is responsible for determining which column should be written to when adding data to the excel file
        :param sheet_title:
        :return:
        """
        # Write maxquant values to appropriate locations
        if str(self.__args.method).lower() == "direct":
            start_col = 4
        else:
            start_col = 9

        if str(self.__args.experiment).lower() == "urea":
            start_col += 10

        if not self.__first_set_up and sheet_title == self.__all_proteins_sheetname:
            start_col -= 1

        return start_col

    def write_protein_information(self) -> None:
        """
        This function will write the name of the protein and the ID into columns 1 and 2, respectively

        On the Clinically Relevant sheet, we will write the expected protein concentration

        :return: None
        """

        column_headers: list[str] = [
            "dried_average",
            "dried_variation",
            "liquid_average",
            "liquid_variation",
            "dried_liquid_ratio",
        ]

        for sheet in self.__workbook.worksheets:
            for i, (protein_id, protein_name, expected_concentration) in enumerate(
                zip(
                    self.__dataframe["protein_id"],
                    self.__dataframe["protein_name"],
                    self.__dataframe["expected_concentration"],
                )
            ):
                current_row = i + 3

                sheet.cell(
                    row=current_row,
                    column=3,
                    value=float(expected_concentration),
                )

                start_col = self.get_column_write_start(sheet.title)

                for j, column_index in enumerate(range(start_col, start_col + 5)):
                    if (
                        self.__dataframe.loc[i, "relevant"]
                        and sheet.title == self.__clinical_sheetname
                    ):

                        # Write to clinically relevant
                        sheet.cell(
                            row=current_row,
                            column=column_index,
                            value=self.__dataframe[column_headers[j]][i],
                        )
                    else:
                        sheet.cell(
                            row=current_row,
                            column=column_index,
                            value=self.__dataframe[column_headers[j]][i],
                        )

    def write_clinical_name_id(self) -> None:
        """
        This function will write ONLY the clinicaly name and ID contained in the clinically_relevant.tsv file to columns 1 and 2 in the excel file
        :return:
        """
        clinical_sheet: Worksheet = self.__workbook[self.__clinical_sheetname]
        clinical_df: pd.DataFrame = pd.read_csv("clinically_relevant.tsv", sep="\t")
        clinical_df.sort_values(
            "protein_name",
            ignore_index=True,
            inplace=True,
            # Sort by lowercase. From: https://stackoverflow.com/a/63141564
            key=lambda col: col.str.lower(),
        )

        for i, (protein_name, protein_id, concentration) in enumerate(
            zip(
                clinical_df["protein_name"],
                clinical_df["protein_id"],
                clinical_df["expected_concentration [log10(pg/ml)]"],
            )
        ):
            clinical_sheet.cell(row=i + 3, column=1, value=protein_name)
            clinical_sheet.cell(row=i + 3, column=2, value=protein_id)
            clinical_sheet.cell(row=i + 3, column=3, value=concentration)

    def write_clinical_data(self) -> None:
        """
        This function will match clinically relevant MaxQuant data lines located in the Clinically Relevant Proteins file
        :return: None
        """
        clinical_df: pd.DataFrame = self.__dataframe[
            self.__dataframe["relevant"]
        ].reset_index(drop=True)

        clinical_ws: Worksheet = self.__workbook[self.__clinical_sheetname]
        start_col = self.get_column_write_start(clinical_ws.title)

        column_headers: list[str] = [
            "dried_average",
            "dried_variation",
            "liquid_average",
            "liquid_variation",
            "dried_liquid_ratio",
        ]

        for i, (
            clinical_id,
            dried_average,
            dried_variation,
            liquid_average,
            liquid_variation,
            dried_liquid_ratio,
        ) in enumerate(
            zip(
                clinical_df["clinical_id"],
                clinical_df["dried_average"],
                clinical_df["dried_variation"],
                clinical_df["liquid_average"],
                clinical_df["liquid_variation"],
                clinical_df["dried_liquid_ratio"],
            )
        ):

            for j, row_contents in enumerate(
                clinical_ws.iter_rows(min_row=3, min_col=2, max_col=2)
            ):
                row_index = j + 3
                excel_id: str = row_contents[0].value

                if clinical_id == excel_id:

                    clinical_ws.cell(
                        row=row_index, column=start_col, value=dried_average
                    )
                    clinical_ws.cell(
                        row=row_index, column=start_col + 1, value=dried_variation
                    )
                    clinical_ws.cell(
                        row=row_index, column=start_col + 2, value=liquid_average
                    )
                    clinical_ws.cell(
                        row=row_index, column=start_col + 3, value=liquid_variation
                    )
                    clinical_ws.cell(
                        row=row_index, column=start_col + 4, value=dried_liquid_ratio
                    )

                    break

    def write_all_protein_name_id(self):
        pass

    def write_all_protein_data(self):
        pass

    def write_protein_name_ids(self) -> None:
        """
        This function will be responsible for writing the information contained under the protein_name and protein_id fields

        It will write all information to the All Proteins sheet
        It will only write clinically relevant proteins (using the "relevant" field) to the Clinically Relevant Proteins sheet
        :return: None
        """

        for sheet in self.__workbook.worksheets:
            # Get a dataframe containing all clinically relevant proteins
            if sheet.title == self.__clinical_sheetname:
                current_df: pd.DataFrame = self.__dataframe[
                    self.__dataframe["relevant"]
                ]
            # Otherwise get a dataframe with all proteins
            else:
                current_df: pd.DataFrame = self.__dataframe[
                    self.__dataframe["relevant"] == False
                ]

            current_df.sort_values("protein_name", ignore_index=True, inplace=True)

            for i, (protein_name, protein_id) in enumerate(
                zip(current_df["protein_name"], current_df["protein_id"])
            ):
                sheet.cell(row=i + 2, column=1, value=protein_name)
                sheet.cell(row=i + 2, column=2, value=protein_id)
