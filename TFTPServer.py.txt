# UDP TFTP Client

from socket import *
# import to check existing file
import os.path

from TFTPS3 import *
import codecs
import select
import sys
from PyQt5.Qt import *
import numpy as np
from threading import Thread
from PyQt5.QtCore import QThread

timeout = 2.0

# Function to encode
def b(num):
    return num.to_bytes(2, 'big')

# Get the blocksize and time sent by the client
def oack(start, message):
    a = start
    while message[a] != 0:
        a += 1
    while a != len(message) - 1:
        # Get packet size option from message
        if message[start:a].decode('utf-8') == "blksize":
            a += 1
            start = a
            while message[a] != 0:
                a += 1
            global packetSize
            packetSize = int(message[start:a].decode('utf-8'))
            oack = 1
            a += 1
            start = a
            while message[a] != 0:
                a += 1
        # Get time out option from message
        if message[start:a].decode('utf-8') == "timeout":
            a += 1
            start = a
            while message[a] != 0:
                a += 1
            global timeout
            timeout = float(message[start:a].decode('utf-8'))
            global serverSocket
            serverSocket.settimeout(timeout)
        else:
            a += 1
    return packetSize, timeout

# OP Codes
pck_code = b'\x00\x00'
rrq_code = b'\x00\x01'
wrq_code = b'\x00\x02'
data_code = b'\x00\x03'
ack_code = b'\x00\x04'
err_code = b'\x00\x05'
oack_code = b'\x00\x06'

packetSize = 512

# Error messages
err_msg = [
    bytes("Not defined.", 'utf-8'),
    bytes("File not found.", 'utf-8'),
    bytes("Acces violation.", 'utf-8'),
    bytes("Disk full or allocation exceeded.", 'utf-8'),
    bytes("Illegal location exceeded.", 'utf-8'),
    bytes("Unknown transfer ID.", 'utf-8'),
    bytes("File already exists.", 'utf-8'),
    bytes("No such user.", 'utf-8')
]

serverDir = "C:\\Users\\desfa\\Documents\\UPC\\EPSEVG\\Q4\\XACO\\PRACT TFTP\\SERVER\\Files" # Server files directory

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.serverAddress = '1.0.0.'
        self.serverPort = 69
        self.lastPos = 512
        self.setWindowTitle("TFTP Server")
        self.pushButtonStart.clicked.connect(self.handle)
        self.pushButtonBrowse.clicked.connect(self.fileBrowse)
        self.lineEditIP.setCursorPosition(0);
        self.labelUser.setTextInteractionFlags(Qt.TextBrowserInteraction);
        self.labelProgrammer.setTextInteractionFlags(Qt.TextBrowserInteraction);
        self.lineEditPort.textChanged.connect(self.port)
        self.lineEditIP.textChanged.connect(self.address)

        self.lineEditErr0.textChanged.connect(self.errorMsg0)
        self.lineEditErr1.textChanged.connect(self.errorMsg1)
        self.lineEditErr2.textChanged.connect(self.errorMsg2)
        self.lineEditErr3.textChanged.connect(self.errorMsg3)
        self.lineEditErr4.textChanged.connect(self.errorMsg4)
        self.lineEditErr5.textChanged.connect(self.errorMsg5)
        self.lineEditErr6.textChanged.connect(self.errorMsg6)
        self.lineEditErr7.textChanged.connect(self.errorMsg7)

    def errorMsg0(self):
        global err_msg
        err_msg[0] = bytes(self.lineEditErr0.text(), 'utf-8')

    def errorMsg1(self):
        global err_msg
        err_msg[1] = bytes(self.lineEditErr1.text(), 'utf-8')

    def errorMsg2(self):
        global err_msg
        err_msg[2] = bytes(self.lineEditErr2.text(), 'utf-8')

    def errorMsg3(self):
        global err_msg
        err_msg[3] = bytes(self.lineEditErr3.text(), 'utf-8')

    def errorMsg4(self):
        global err_msg
        err_msg[4] = bytes(self.lineEditErr4.text(), 'utf-8')

    def errorMsg5(self):
        global err_msg
        err_msg[5] = bytes(self.lineEditErr5.text(), 'utf-8')

    def errorMsg6(self):
        global err_msg
        err_msg[6] = bytes(self.lineEditErr6.text(), 'utf-8')

    def errorMsg7(self):
        global err_msg
        err_msg[7] = bytes(self.lineEditErr7.text(), 'utf-8')

    def port(self):
        self.serverPort = int(self.lineEditPort.text())

    def address(self):
        self.serverAddress = self.lineEditIP.text()


    def fileBrowse(self):
        dialog = QtWidgets.QFileDialog();
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        dialog.exec()
        self.lineEditFileDir.setText(dialog.selectedFiles()[0])
        global serverDir
        serverDir = dialog.selectedFiles()[0] 

    def errorMessage(self, string):
        errPopup = QtWidgets.QMessageBox();
        errPopup.setWindowTitle("Error")
        errPopup.setText(string)
        errPopup.setIcon(QtWidgets.QMessageBox.Critical)
        errPopup.exec()

    def questionMessage(self, string):
        qPopup = QtWidgets.QMessageBox();
        qPopup.setWindowTitle("TFTP Server")
        qPopup.setText(string)
        qPopup.setIcon(QtWidgets.QMessageBox.Question)
        qPopup.setStandardButtons(QtWidgets.QMessageBox.Retry|QtWidgets.QMessageBox.Abort)
        qPopup.buttonClicked.connect(self.questionAnswer)
        qPopup.exec()

    def questionAnswer(self, ans):
        if ans.text() == "Retry":
            self.answer = 1
        else:
            self.answer = 0

    def popupMessage(self, string):
        msg = QtWidgets.QMessageBox();
        msg.setWindowTitle("")
        msg.setText(string)
        msg.exec()

    def handle(self):
        if self.pushButtonStart.text() == "Start":
            global serverSocket
            global packetSize
            try:
                serverSocket = socket(AF_INET, SOCK_DGRAM)
                serverSocket.bind((self.serverAddress, self.serverPort))
                serverSocket.setblocking(True)
            except Exception as inst:
                print("inst:", inst)
                self.errorMessage(str(inst))
                return
            self._thread = QThread(self)
            self._worker = serverConnection(packetSize)
            self._worker.moveToThread(self._thread)
            self._worker.sig_msg.connect(self.plainTextEdit.appendPlainText)

            self._thread.started.connect(self._worker.run)
            self._thread.start()
            self.pushButtonStart.setText("Stop")
        else:
            self.pushButtonStart.setText("Start")
            self._thread.terminate()
            serverSocket.setblocking(False)
            serverSocket.close()


class serverConnection(QtCore.QObject):

    sig_msg = pyqtSignal(str)  # message to be shown to user

    def __init__(self, parent=None):
        super().__init__()

    def run(self,):
        global serverSocket
        global serverDir
        global packetSize
        serverSocket.setblocking(True)
        while True:

            print()
            n = 3
            global oack_data
            #Receive first message from client
            message, clientAddress = serverSocket.recvfrom(packetSize)
            self.sig_msg.emit("< Connection with " + clientAddress[0] + " established >")
            opCode = int.from_bytes(message[0:2], 'big')

            while message[n] != 0:
                n += 1
            # netascii
            if message[n + 1] == 110:
                if n + 10 < len(message):
                    oack_data = message[n + 10:len(message) - 1]
                    packetSize, timeout = oack(n + 10, message)
            # octet
            else:
                if n + 7 < len(message):
                    oack_data = message[n + 7:len(message) - 1]
                    packetSize, timeout = oack(n + 7, message)

            if opCode == 1:
                self.download(message, message[2:n].decode("utf-8"), message[n + 1:n + 3].decode("utf-8"), packetSize, clientAddress)
            
            elif opCode == 2:
                self.upload(message, message[2:n].decode("utf-8"), message[n + 1:n + 3].decode("utf-8"), packetSize, clientAddress)

            self.sig_msg.emit("< Connection with " + clientAddress[0] + " finished >")

    def download(self, message, fileName, mode, packetSize, clientAddress):
        blkNum = 0
        loop = 1
        # Check if file exists
        if os.path.exists(serverDir + "\\" + fileName):
            if oack:
                serverSocket.sendto(oack_code + oack_data, clientAddress)
                serverACK, clientAddress = serverSocket.recvfrom(packetSize)
                if serverACK[2:4] != b'\x00\x00':
                    loop = 0

            blkNum += 1
            fd = open(serverDir + "\\" + fileName, "rb")

            while loop:
                data = fd.read(packetSize)
                while True:
                    # Get last block number acknowledgement bt the clien
                    lastBlkNum = int.from_bytes(serverACK[2:4], 'big')
                    try:
                        # Check if duplicated ack
                        if blkNum - lastBlkNum > 1:
                            serverACK, clientAddress = serverSocket.recvfrom(packetSize)
                            continue
                        # Send data
                        serverSocket.sendto(data_code + b(blkNum) + data, clientAddress)
                        self.sig_msg.emit("Sent block #" + str(blkNum))
                        # Receive ack
                        serverACK, clientAddress = serverSocket.recvfrom(packetSize)
                        blkNum += 1
                        break
                    except Exception as inst:
                        print(inst)

                # Restart blockNum        
                if blkNum == 65536:
                    blkNum = 0

                if not data or len(data) < packetSize:
                    break

            fd.close()
                
        else: # Err 1
            content = err_code + b'\x00\x01' + err_msg[1] + b'\x00'
            serverSocket.sendto(content, clientAddress)
            serverACK, clientAddress = serverSocket.recvfrom(packetSize)
        return

    def upload(self, message, fileName, mode, packetSize, clientAddress):
        blkNum = 0

        if os.path.exists(serverDir + "\\" + fileName): # Err 6
            serverSocket.sendto(err_code + b'\x00\x06' + err_msg[6] + b'\x00', clientAddress)
            serverACK, clientAddress = serverSocket.recvfrom(packetSize)
        else:
            loop = 1
            fd = open(serverDir + "\\" + fileName, "ab")

            if oack:
                serverSocket.sendto(oack_code + oack_data, clientAddress)
                # Receive data
                data, clientAddress = serverSocket.recvfrom(packetSize + 4)
                # Write data into file
                fd.write(data[4:packetSize + 4])
                blkNum += 1
                if len(data[4:packetSize + 4]) < packetSize:
                    loop = 0
            serverSocket.sendto(ack_code + b(blkNum), clientAddress)
            blkNum += 1

            while loop:
                while True:
                    try:
                        data, clientAddress = serverSocket.recvfrom(packetSize + 4)
                        if int.from_bytes(data[2:4], 'big') == blkNum - 1:
                            continue
                        self.sig_msg.emit("Received block #" + str(int.from_bytes(data[2:4], 'big')))
                        serverSocket.sendto(ack_code + b(blkNum), clientAddress)
                        fd.write(data[4:packetSize + 4])
                        blkNum += 1
                        break
                    except Exception as inst:
                        print(inst)

                if len(data[4:packetSize + 4]) < packetSize:
                    break

                # Restart blockNum
                if blkNum == 65536:
                    blkNum = 0
            fd.close()
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
