from __future__ import annotations

import time

from typing import Tuple


class MappingBlock:
    def __init__(self, address: int, size: int, name: str) -> None:
        self.address = address
        self.size = size
        if len(name) > 12:
            raise Exception("'name' should not exceed 12 bytes")
        self.name = name

    def data_block(self) -> bytearray:
        """Genera un bytearray en base al objeto MappingBlock, esto permite serializar y escribir
        los datos en memoria física"""
        dataBlock = bytearray((self.address).to_bytes(2, byteorder='big'))
        dataBlock += (self.size).to_bytes(2, byteorder='big')
        dataBlock += bytearray(self.name.ljust(12), encoding="ascii")
        dataBlock[0] += (11 << 4)
        return dataBlock

    def from_db(byteBlock: bytearray) -> MappingBlock:
        """Crea un objeto MappingBlock con base en un bytearray"""
        address = int.from_bytes(byteBlock[0:2], byteorder='big') - (11 << 12)
        size = int.from_bytes(byteBlock[2:4], byteorder='big')
        name = byteBlock[4:16].decode()
        return MappingBlock(address, size, name)


class FileSystem:
    """Define el sistema de archivo que tendrá manejo de
    los archivos (strings con un nombre) en la memoria"""

    def __init__(self, memory: MemoryEEPROM, rootaddress: int) -> None:
        self.maxMAdrressAllowed = 128
        self.maxNFiles = 16
        self.rootaddress = rootaddress
        self.memory = memory
        self.rootByteValue = self.memory.read(
            self.rootaddress)  # First Metadata block
        if self.rootByteValue > self.maxMAdrressAllowed:
            raise Exception("First Metadata block too high")

    def list_files(self):
        """Enlista los archivos actualmente alojados en memoria"""
        listFiles = []
        for i in range(self.maxNFiles):
            addressFile = self.rootByteValue + 16 * i
            if (self.memory.read(addressFile) >> 4) == 11:
                metaBlock = MappingBlock.from_db(
                    self.memory.read_block(addressFile, 16))
                listFiles.append(
                    (addressFile,
                     metaBlock.address,
                     metaBlock.size,
                     metaBlock.name))
        return listFiles

    def free_blocks(self) -> list[Tuple[int, int]]:
        """Retorna una lista de tuplas donde se especifica la posición inicial y final
        de memoria de bloques de bytes disponibles"""
        listFiles = self.list_files()
        freeBlocks = []
        if len(listFiles) == 0:
            lastAddCurrFile = (self.rootByteValue + self.maxNFiles * 16)
            freeBlocks.append(
                (lastAddCurrFile,
                 self.memory.capacity -
                 lastAddCurrFile))
        else:
            listFiles.append(
                (0,
                 0,
                 self.rootByteValue +
                 self.maxNFiles *
                 16,
                 "Metadata"))  # Virtual metadata file
            # Sorted by second column
            listFiles = sorted(listFiles, key=lambda x: x[1])

            for i in range(len(listFiles)):
                lastAddCurrFile = (listFiles[i][1] + listFiles[i][2])
                if i < len(listFiles) - 1:
                    freeBlocks.append(
                        (lastAddCurrFile, listFiles[i + 1][1] - lastAddCurrFile))
                else:  # Current file is the last one
                    freeBlocks.append(
                        (lastAddCurrFile, self.memory.capacity - lastAddCurrFile))
            if len(freeBlocks) == 0:
                lastAddCurrFile = (listFiles[0][1] + listFiles[0][2])
                freeBlocks.append(
                    (lastAddCurrFile, self.memory.capacity - lastAddCurrFile))

        return freeBlocks

    def new_meta(self):
        """Entrega la primer ubicación disponible para escribir la metadata
        de un nuevo archivo"""
        possiList = [
            self.rootByteValue + i*16 for i in range(self.maxNFiles)]
        metaAdress = [i[0] for i in self.list_files()]  # Current list of files
        for add in possiList:
            if add not in metaAdress:
                return add
        # if not success:
        raise Exception("There is not enough space for metadata")

    def new_file(self, name, data):
        lenData = len(data)
        # Find the smallest free space
        freeBcks = sorted(self.free_blocks(), key=lambda x: x[1])
        print("Espacios libres: ", freeBcks)
        for block in freeBcks:
            if block[1] >= lenData:
                metaFile = MappingBlock(block[0], lenData, name)
                self.memory.write(
                    self.new_meta(),
                    metaFile.data_block())
                self.memory.write(block[0], bytearray(data, encoding="ascii"))
                return block[0]
        # if not success:
        raise Exception("There is not enough space")

    def del_file(self, address: int) -> None:
        possiList = [
            self.rootByteValue + i*16 for i in range(self.maxNFiles)]
        if address in possiList:
            self.memory.write(address, bytes(1))
        else:
            raise Exception("This address is not metadata")

    def read_file(self, address: int) -> str:
        for add in self.list_files():
            if address == add[0]:
                sizeBytes = self.memory.read_block(address + 2, 2)
                sizeBytes = int.from_bytes(sizeBytes, byteorder='big')
                return self.memory.read_block(add[1], sizeBytes).decode()
        raise Exception("This address is not metadata")

    def metaPrepare(self):
        """Prepara el espacio de metadatos, eliminando previos archivos si es el caso"""
        possiList = [
            self.rootByteValue + i*16 for i in range(self.maxNFiles)]
        for add in possiList:
            self.memory.write(add, bytes(1))


class MemoryEEPROM:
    """Abstrae como objeto Python la memoria EEPROM"""

    def __init__(self, serial: Serial) -> None:
        # Capacidad total en KB de la memoria EEPROM
        self.capacity = 4096
        # Objeto interno que almacena los datos de la memoria
        self.memory = bytearray(self.capacity)
        self.serial = serial

    def read(self, address: int) -> int:
        self.serial.write(
            ("r " + str(address).zfill(4) + "\n").encode('utf-8'))
        return int(self.serial.readline())

    def read_block(self, address: int, size: int):
        """Lee un bloque con longitud 'size' de memoria comenzando en 'address'"""
        readB = bytes([])
        for i in range(size):
            self.serial.write(
                ("r " + str(address + i).zfill(4) + "\n").encode('utf-8'))
            time.sleep(0.03)
            readB += bytes([int(self.serial.readline())])
        return bytearray(readB)

    def write(self, address: int, data: bytes) -> None:
        for index, dt in enumerate(data):
            self.serial.write(("w " + str(address + index).zfill(4) +
                              " " + str(dt).zfill(3) + "\n").encode('utf-8'))
            time.sleep(0.03)

    def read_all(self) -> bytearray:
        return self.memory
