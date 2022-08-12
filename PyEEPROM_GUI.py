import time

import serial
import PySimpleGUI as sg

from lib_py_EEPROM import *


def main() -> None:
    layout = [[sg.Text("Lectura EEPROM", size=(50, 1))],
              [sg.Button("Preparación EEPROM", key="-prepaEEPROM-")],
              [sg.Button("Lectura o borrado de un archivo", key="-readf-")],
              [sg.Button("Escritura de un archivo", key="-writef-")],
              [sg.Button('Exit')]]

    window = sg.Window("Ajustar dispositivo", layout, layout, size=(400, 200))

    try:
        SerialEEPROM = serial.Serial("/dev/ttyACM0", 115200, timeout=0.5)
        time.sleep(2.0)

        memoEEPROM = MemoryEEPROM(SerialEEPROM)
        fsEEPROM = FileSystem(memoEEPROM, 0)
        while True:
            event, _ = window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            elif event == "-readf-":
                read_del_file(fsEEPROM)
            elif event == "-writef-":
                new_file(fsEEPROM)
            elif event == "-prepaEEPROM-":
                prepare_EEPROM(fsEEPROM, memoEEPROM)
    finally:
        SerialEEPROM.close()
        print("Programa finalizado")
        window.close()


def read_del_file(fsEeprom) -> None:
    layout = [[sg.Text("Lista de archivos: ", size=(60, 1))],
              [sg.Multiline(size=(80, 9), key='-filelist-')],
              [sg.Button("Obtener lista", key="-getlist-")],
              [sg.Text("_________________________", size=(80, 1))],
              [sg.Text("¿Qué Archivo desea leer o borrar? Introduzca su ID", size=(80, 1))],
              [sg.Input(key="-IDfile-")],
              [[sg.Button("Obtener", key="-getfile-"), sg.Button("Borrar", key="-delfile-")]],
              [sg.Multiline(size=(80, 6), key='-datafile-')],
              [sg.Button('Exit')]]
    window_readDelFile = sg.Window(
        "Lectura o borrado de archivos", layout, size=(500, 450))

    while True:
        event, values = window_readDelFile.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "-getlist-":
            fileList = fsEeprom.list_files()
            stringFiles = "ID\tDirección\t\tTamaño[Bytes]\t\tNombre\n"

            for file in fileList:
                stringFiles += str(file[0]) + "\t" + str(file[1]) + \
                    "\t\t" + str(file[2]) + "\t\t" + str(file[3]) + "\n"
            window_readDelFile['-filelist-'].update(stringFiles)

        if event == "-getfile-":
            try:
                idFile = int(values["-IDfile-"])
                dataFile = fsEeprom.read_file(idFile)
            except BaseException:
                window_readDelFile['-datafile-'].update(
                    "Usar una posición válida")
                continue
            else:
                window_readDelFile['-datafile-'].update(dataFile)

        if event == "-delfile-":
            try:
                idFile = int(values["-IDfile-"])
                fsEeprom.del_file(idFile)
            except BaseException:
                window_readDelFile['-datafile-'].update(
                    "Usar una posición valida")
                continue
            else:
                window_readDelFile['-datafile-'].update("Borrado")

    window_readDelFile.close()


def new_file(fsEeprom) -> None:
    layout = [[sg.Text("Lista de archivos: ", size=(60, 1))],
              [sg.Multiline(size=(80, 9), key='-filelist-')],
              [sg.Button("Obtener lista", key="-getlist-")],
              [sg.Text("_________________________", size=(80, 1))],
              [sg.Text("¿Cuál es la información de este nuevo archivo?", size=(80, 1))],
              [sg.Text("Nombre", size=(80, 1))],
              [sg.Input(key="-namefile-")],
              [sg.Text("Datos", size=(80, 1))],
              [sg.Multiline(size=(80, 5), key="-datafile-")],
              [sg.Button("Crear", key="-newfile-")],
              [sg.Multiline(size=(80, 5), key='-output-')],
              [sg.Button('Exit')]]
    window_newFile = sg.Window("Creación de archivos", layout, size=(500, 550))

    while True:
        event, values = window_newFile.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "-getlist-":
            fileList = fsEeprom.list_files()
            stringFiles = "ID\tDirección\ttamaño\tNombre\n"

            for file in fileList:
                stringFiles += str(file[0]) + "\t" + str(file[1]) + \
                    "\t\t" + str(file[2]) + "\t\t" + str(file[3]) + "\n"
            window_newFile['-filelist-'].update(stringFiles)

        if event == "-newfile-":
            try:
                dataFile = values["-datafile-"]
                nameFile = values["-namefile-"]

                if len(nameFile) > 12:
                    window_newFile['-output-'].update("Nombre demasiado largo")
                elif len(dataFile) == 0 or len(nameFile) == 0:
                    window_newFile['-output-'].update(
                        "Datos introducidos inválidos")
                else:
                    fsEeprom.new_file(nameFile, dataFile)
                    window_newFile['-output-'].update(
                        "Archivo escrito: \n" + "nombre: " + nameFile + "\nDatos: " + dataFile)
            except ValueError:
                window_newFile['-output-'].update("Usar una posición valida")
                continue

    window_newFile.close()


def prepare_EEPROM(fsEeprom, memoEEPROM):
    layout = [[sg.Text("Los metadatos se encuentran a partir de una posición en memoria encontrada en otra posición conocida como root, la cual por defecto es la primera posición en memoria (0).", size=(80, 4))],
              [sg.Text(
                  "La posición de metadatos por defecto puede ser encontrada en 20, ¿desea cambiarla?", size=(60, 2))],
              [sg.Text("¿Qué posición de memoria? No introducir nada o 0 usará el valor por defecto (20).", size=(80, 1))],
              [sg.Input(key="-metapos-", size=(80, 1))],
              [sg.Button("Ingresar", key="-metaaddbutton-")],
              [sg.Text("¿Desea preparar el espacio de metadatos?, esto borrará el punto de acceso a los archivos existentes", size=(80, 2))],
              [sg.Button("Preparar", key="-metaprepabutton-")],
              [sg.Multiline(size=(80, 5), key='-output-')],
              [sg.Button('Exit')]]
    window_prepa_meta = sg.Window(
        "Preparación EEPROM", layout, size=(520, 420))

    while True:
        event, values = window_prepa_meta.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "-metaaddbutton-":
            metapos = values["-metapos-"]
            if metapos == "" or metapos == "0":
                memoEEPROM.write(0, [20])
                strSalida = "Nueva posición para metadatos inscrita (20)"
            elif int(metapos) < 128:
                memoEEPROM.write(0, [int(metapos)])
                strSalida = "Nueva posición para metadatos inscrita"
            else:
                strSalida = "No se introdujo un valor válido"
            window_prepa_meta['-output-'].update(strSalida)

        if event == "-metaprepabutton-":
            fsEeprom.metaPrepare()
            window_prepa_meta['-output-'].update(
                "Espacio de metadatos preparado")

    window_prepa_meta.close()


if __name__ == "__main__":
    main()
