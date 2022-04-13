import subprocess

import PySimpleGUI as sg


def main():
    sg.theme('BluePurple')

    layout = [[sg.Text('Please select your excel file and at least one proteinGroups.txt file.'),
               sg.Text(size=(15, 1), key='-REQUEST-')],
              [sg.Text('Excel:', size=(8, 1)), sg.Input(), sg.FileBrowse(key='-EXCEL-')],
              [sg.Text('c18-sdc:', size=(8, 1)), sg.Input(), sg.FileBrowse(key='-PROTEIN1-')],
              [sg.Text('c18-urea:', size=(8, 1)), sg.Input(), sg.FileBrowse(key='-PROTEIN2-')],
              [sg.Text('direct-sdc:', size=(8, 1)), sg.Input(), sg.FileBrowse(key='-PROTEIN3-')],
              [sg.Text('direct-urea:', size=(8, 1)), sg.Input(), sg.FileBrowse(key='-PROTEIN4-')],
              [sg.Button('Run with Selected Files'), sg.Button('Exit')]]

    window = sg.Window('MaxQuantAnalysis', layout)

    while True:  # Event Loop
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Run with Selected Files':
           # subprocess.run(
            #    "python ./main.py --direct --urea --input C:/Users/isabe/Desktop/data/data/direct/urea/proteinGroups.txt --excel C:/Users/isabe/Desktop/data/data/experiment_results.xlsx")
             subprocess.run(
                 'python ./main.py -c -s -i{0} -x{1}'.format(str(values['-PROTEIN1-']), str(values['-EXCEL-'])))
             subprocess.run(
                 'python ./main.py -c -u -i{0} -x{1}'.format(str(values['-PROTEIN2-']), str(values['-EXCEL-'])))
             subprocess.run(
                 'python ./main.py -d -s -i{0} -x{1}'.format(str(values['-PROTEIN3-']), str(values['-EXCEL-'])))
             subprocess.run(
                 'python ./main.py -d -u -i{0} -x{1}'.format(str(values['-PROTEIN4-']), str(values['-EXCEL-'])))
            # Update the "output" text element to be the value of "input" element
            # window['-OUTPUT-'].update(values['-IN-'])

    window.close()


if __name__ == '__main__':
    main()
