import openpyxl
from openpyxl.styles import Alignment


class HeadingValues:
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
        self, sheet_title: str, is_clinically_relevant: bool, workbook_save_path: str
    ):
        """
        This class is responsible for writing data to excel files. This will ALWAYS create a new workbook

        :param sheet_title: The name of the excel sheet
        :param is_clinically_relevant: Is the information being written clinically relevant?
        :param workbook_save_path: The path AND file name for the output excel file
        """
        self.__is_clinically_relevant = is_clinically_relevant
        self.__workbook = openpyxl.Workbook()
        self.__worksheet = self.__workbook.active
        self.__worksheet.title = sheet_title

        self.set_subheading_alignment()
        self.write_headings()

        self.__workbook.save(workbook_save_path)

    def set_subheading_alignment(self):
        for row in range(1, 3):
            for col in range(1, 23):
                self.__worksheet.cell(row=row, column=col).alignment = Alignment(
                    wrapText=True, horizontal="center", vertical="center"
                )

    def write_headings(self):
        # If we are writing a clinically relevant excel file, the top-left most heading should be modified
        if self.__is_clinically_relevant:
            self.__worksheet["A1"] = "Clinically Relevant"

            self.__worksheet.merge_cells("C1:C2")
            self.__worksheet["C1"] = "Typical\nPlasma\nConc"

            start_experiment_headings = 4
            end_experiment_headings = 19

        else:
            self.__worksheet["A1"] = "Identified Proteins"

            start_experiment_headings = 3
            end_experiment_headings = 18

        self.__worksheet["A2"] = "Protein\nName"
        self.__worksheet["B2"] = "Protein\nID"

        # Write and merge repeating cell headings
        self.__worksheet.merge_cells("A1:B1")
        for i, col_num in enumerate(
            range(start_experiment_headings, end_experiment_headings + 1, 5)
        ):
            # Set and merge row 1
            self.__worksheet.cell(
                row=1, column=col_num, value=HeadingValues.headings[i]
            )
            self.__worksheet.merge_cells(
                start_row=1, end_row=1, start_column=col_num, end_column=col_num + 4
            )

            # Write subheadings
            for sub_col_num in range(0, 5):
                self.__worksheet.cell(
                    row=2,
                    column=col_num + sub_col_num,
                    value=HeadingValues.subheadings[sub_col_num],
                )


if __name__ == "__main__":
    all_protein = PlasmaTable(
        sheet_title="All Proteins",
        is_clinically_relevant=False,
        workbook_save_path="/Users/joshl/Library/Application Support/JetBrains/PyCharm2021.3/scratches/all_protein.xlsx",
    )

    clinical_proteins = PlasmaTable(
        sheet_title="All Proteins",
        is_clinically_relevant=True,
        workbook_save_path="/Users/joshl/Library/Application Support/JetBrains/PyCharm2021.3/scratches/clinical_proteins.xlsx",
    )
