"""
This file does nothing, but as evidenced by the file name, it is the location for parsing command line arguments

The following arguments should be parsed
- Help (--help)
- Input file (/data/c18/sdc/proteinGroups.txt
- Save location (default to location next to input file)
- Experiment flags
    - Do not allow 'direct' & 'c18' at the same time
    - Do not allow 'sdc' & 'urea' at the same time

    - '--direct'
    - '--c18'
    - '--sdc'
    - '--urea'
"""
import argparse
import pathlib


class ArgParse:
    def __init__(self):
        """
        Available arguments:
        direct
        c18
        sdc
        urea
        input
        output
        """
        description = """
MaxQuantAnalysis is a tool to provide a platform for downstream analysis after execution of the MaxQuant program.

The -c/--c18 flag is not valid with the -d/--direct flag, as these are two methods of Mass Spectrometry analysis and it is not reasonable for them to be used together.
The -s/--sdc flag is not valid with the -u/--ures flag, as these are two types of experiments that should not be used together.
You should not have to worry about errors with invalid pairing of flags. If invalid flags are seen, the program with safely exit.

EXAMPLE
python3 main.py --direct --urea --input ./data/direct/urea/proteinGroups.txt

"""
        self.__parser = argparse.ArgumentParser(
            description=description, formatter_class=argparse.RawTextHelpFormatter
        )

        # Add method arguments
        self.__method_group = self.__parser.add_mutually_exclusive_group(required=True)
        self.__method_group.add_argument(
            "-d",
            "--direct",
            help="Mass Spectrometry method 'direct'",
            action="store_true",
        )
        self.__method_group.add_argument(
            "-c", "--c18", help="Mass Spectrometry method 'c18'", action="store_true"
        )

        # Add experiment arguments
        self.__experiment_group = self.__parser.add_mutually_exclusive_group(
            required=True
        )
        self.__experiment_group.add_argument(
            "-s", "--sdc", help="Experiment type SDC", action="store_true"
        )
        self.__experiment_group.add_argument(
            "-u", "--urea", help="Experiment type Urea", action="store_true"
        )

        # Add positional arguments
        self.__parser.add_argument(
            "-o", "--output", metavar="directory", help="The full output directory"
        )
        self.__parser.add_argument(
            "-i",
            "--input",
            required=True,
            metavar="file",
            help="The full input file path",
        )

        self.__args = self.__parser.parse_args()
        self.__validate_arguments()

    def __validate_arguments(self):
        """
        This function will validate the incoming parameters
        :return:
        """
        if self.__args.output is None:
            input_path = pathlib.Path(self.__args.input)
            self.__args.output = input_path.parent

        if self.__args.direct is not None:
            self.__args.method = "Direct"
        else:
            self.__args.method = "C18"

        if self.__args.urea is not None:
            self.__args.experiment = "Urea"
        else:
            self.__args.experiment = "SDC"

        if "proteinGroups.txt" not in self.__args.input:
            print(
                "You have not passed in the 'proteinGroups' text file. Please try again."
            )
            print(
                "Make sure the '--input' flag points to a file named 'proteinGroups.txt'"
            )

    @property
    def args(self):
        return self.__args


if __name__ == "__main__":
    ArgParse()
