# UDP TFTP Client

from socket import *
# import to check existing file
import os.path

from TFTP3 import *
import codecs
import select
from PyQt5.Qt import *
import time





# Request IPv4 and UDP communication
clientSocket = socket(AF_INET, SOCK_DGRAM)

# wait until client receive a message
clientSocket.setblocking(True)

# Codes
pck_code = b'\x00\x00'
rrq_code = b'\x00\x01'
wrq_code = b'\x00\x02'
data_code = b'\x00\x03'
ack_code = b'\x00\x04'
err_code = b'\x00\x05'
oack_code = b'\x00\x06'

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.packetSize = 512
        self.setupUi(self)
        self.size
        self.serverPort = 69
        self.lastPos = 512
        self.size = 8
        self.setWindowTitle("TFTP Client")
        # self.setWindowIcon(QtGui.QIcon("tftp_xaco_logo.png"))
        self.radioButtonOp_1.clicked.connect(self.download)
        self.radioButtonOp_2.clicked.connect(self.upload)
        self.pushButton.clicked.connect(self.connection)
        self.download()
        self.pushButtonBrowse.clicked.connect(self.fileBrowse)
        self.lineEditIP.setCursorPosition(0);
        self.pushButtonRestore.clicked.connect(self.restore)
        self.horizontalSliderBlockSize.valueChanged.connect(self.blockSizeSlider)
        self.horizontalSliderBlockSize.sliderPressed.connect(self.lastPosition)
        self.horizontalSliderBlockSize.sliderReleased.connect(self.turnBackPosition)
        self.checkBoxPowerOf2.released.connect(self.turnBackPosition)
        self.labelUser.setTextInteractionFlags(Qt.TextBrowserInteraction);
        self.labelProgrammer.setTextInteractionFlags(Qt.TextBrowserInteraction);
        self.lineEditPort.textChanged.connect(self.port)


    def openLink(self):
        QDesktopServices.openUrl(QUrl("http://www.example.com/"));

    def download(self):
        self.pushButton.setText("Download")
        self.lineEditFile.clear()
        self.pushButtonBrowse.setDisabled(True)

    def upload(self):
        self.pushButton.setText("Upload")
        self.pushButtonBrowse.setEnabled(True)

    def port(self):
        self.serverPort = int(self.lineEditPort.text())

    def restore(self):
        self.lastPos = 512
        self.size = 9
        self.horizontalSliderBlockSize.setValue(512)
        self.labelBlockSize.setText("512")
        self.labelTimeout.setText("2")
        self.horizontalSliderTimeout.setValue(2)
        self.lineEditPort.setText("69")

    def lastPosition(self):
        if self.checkBoxPowerOf2.isChecked():
            self.lastPos = self.horizontalSliderBlockSize.value()

    def turnBackPosition(self):
        if self.checkBoxPowerOf2.isChecked():
            self.horizontalSliderBlockSize.setValue(pow(2, self.size))
            self.labelBlockSize.setText(str(self.horizontalSliderBlockSize.value()))
            self.packetSize = self.horizontalSliderBlockSize.value()

    def blockSizeSlider(self):
        if self.checkBoxPowerOf2.isChecked():
            if self.horizontalSliderBlockSize.value() < (pow(2, self.size) - pow(2, self.size - 1)/2) and self.lastPos > self.horizontalSliderBlockSize.value():
                self.size -= 1
                self.lastPos = self.horizontalSliderBlockSize.value()
            elif self.horizontalSliderBlockSize.value() > (pow(2, self.size + 1) - pow(2, self.size)/2) and self.lastPos < self.horizontalSliderBlockSize.value():
                self.size += 1
                self.lastPos = self.horizontalSliderBlockSize.value()
            self.turnBackPosition()
        else:
            self.labelBlockSize.setText(str(self.horizontalSliderBlockSize.value()))
            self.packetSize = self.horizontalSliderBlockSize.value()

    def fileBrowse(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self)
        self.lineEditFile.setText(filePath[0])

    def errorMessage(self, string):
        errPopup = QtWidgets.QMessageBox();
        errPopup.setWindowTitle("Error")
        errPopup.setText(string)
        errPopup.setIcon(QtWidgets.QMessageBox.Critical)
        errPopup.exec()

    def questionMessage(self, string):
        qPopup = QtWidgets.QMessageBox();
        qPopup.setWindowTitle("TFTP Client")
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

    def popupMessage(self, string, blocks, time):
        msg = QtWidgets.QMessageBox();
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("")
        msg.setText(string + "\n" + str(blocks) + " blocks transfered in " + str(time) + "s")
        msg.exec()

    def connection(self):
        
        if self.radioButtonFor_1.isChecked():
            mode = "netascii"
        else:
            mode = "octet"
        
        i = 0
        # Var to know how many pakcets have been sent
        totBlocks = 0
        filePath = self.lineEditFile.text()

        serverName = self.lineEditIP.text()

        if self.radioButtonOp_1.isChecked():
            # Read in some text from the user  

            # Variable to identify the operaition Codes
            opCodeBytes = rrq_code

            # Convert the file's name to bytes
            fileNameBytes = bytes(filePath, 'utf-8')

            # Variable to know the mode
            modeBytes = bytes(mode, 'utf-8')

            # Variable to know the end of string
            eosBytes = bytes(chr(0), 'utf-8')

            content = opCodeBytes + fileNameBytes + eosBytes + modeBytes + eosBytes + bytes("blksize", 'utf-8') + eosBytes + bytes(self.labelBlockSize.text(), 'utf-8') + eosBytes + bytes("timeout", 'utf-8') + eosBytes + bytes(str(self.horizontalSliderTimeout.value()), 'utf-8') + eosBytes

            # Catch errors
            try:
                start_time = time.time()
                while True:
                    try:
                        # Send the first packet to the server
                        clientSocket.sendto(content, (serverName,self.serverPort))
                        clientSocket.settimeout(self.horizontalSliderTimeout.value())
                        # Recieve the answer of the server
                        message, serverAddress = clientSocket.recvfrom(self.packetSize + 4)
                        break   
                    except Exception as inst:
                        self.questionMessage(str(inst))
                        if not self.answer:
                            return

                if message[0:2] == err_code:
                    n = 3
                    # Get error message sent by the server
                    while message[n] != 0:
                        n += 1
                    # Show error message
                    self.errorMessage(message[4:n].decode('utf-8'))
                    return

                # Send acknowledgement to the server
                ack = ack_code + i.to_bytes(2, 'big')
                clientSocket.sendto(ack, (serverName,self.serverPort))   
                i += 1

                if message[0:2] == oack_code:
                    while True:
                        try:
                            clientSocket.settimeout(self.horizontalSliderTimeout.value())
                            # Receive from server
                            message, serverAddress = clientSocket.recvfrom(self.packetSize + 4)
                            ack = ack_code + i.to_bytes(2, 'big')
                            # Send acknowledgement to the server
                            clientSocket.sendto(ack, (serverName,self.serverPort))
                            i += 1
                            break
                        except Exception as inst:
                            if not self.checkBoxReconnect.isChecked():
                                self.questionMessage(str(inst))
                                if not self.answer:
                                    return
                else:
                    # Set default values
                    packetSize = 512
                    timeout = 2

                # Create and open file
                fd = codecs.open(filePath, "w", "ISO-8859-1")
                while message[4:self.packetSize + 4].decode("ISO-8859-1") != b'' and message[0:2] != err_code:
                    fd.write(message[4:self.packetSize + 4].decode("ISO-8859-1"))
                    if len(message) < self.packetSize + 4:
                        break
                    while True:
                        try:
                            clientSocket.settimeout(self.horizontalSliderTimeout.value())
                            # Receive data from server
                            message, serverAddress = clientSocket.recvfrom(self.packetSize + 4)
                            # Check if duplicated
                            if int.from_bytes(message[2:4], 'big') == i - 1:
                                continue
                            # Send ack
                            self.progressBar.setFormat(str(int.from_bytes(message[2:4], 'big')))
                            clientSocket.sendto(ack_code  + i.to_bytes(2, 'big'), (serverName,self.serverPort))
                            totBlocks += 1
                            i += 1
                            break
                        except Exception as inst:
                            if not self.checkBoxReconnect.isChecked():
                                self.questionMessage(str(inst))
                                break
                            else:
                                clientSocket.sendto(ack_code  + i.to_bytes(2, 'big'), (serverName,self.serverPort))
                    
                    # Restart blockNum
                    if i == 65536:
                        i = 1;
                fd.close()
                self.popupMessage("File received succefully!", totBlocks, "{:.2f}".format(time.time() - start_time))
            except Exception as inst:
                self.errorMessage(str(inst))


        else:

            # Check if the file exists
            if os.path.exists(filePath):
                # Get filnename from the path
                fileName = filePath
                for j in range(len(filePath) - 1, 0, -1):
                    if filePath[j] == '/' or filePath[j] == '\\':
                        fileName = filePath[j + 1:len(filePath)]
                        break

                # Open the file to be read
                fd = open(filePath, "rb")
                
                # Loading bar vars
                # Go to the end of the file
                fd.seek(0, os.SEEK_END)
                av = 100/(fd.tell()/self.packetSize)
                value = 0;
                fd.seek(0, 0)

                # Variable to identify the operaition code
                opCodeBytes = wrq_code
                
                # Convert the file's name to bytes
                fileNameBytes = bytes(fileName, 'utf-8')
                
                # Variable to know the mode
                modeBytes = bytes(mode, 'utf-8')
                
                # Variable to know the end of string
                eosBytes = bytes(chr(0), 'utf-8')
                
                content = opCodeBytes + fileNameBytes + eosBytes + modeBytes + eosBytes + bytes("blksize", 'utf-8') + eosBytes + bytes(self.labelBlockSize.text(), 'utf-8') + eosBytes + bytes("timeout", 'utf-8') + eosBytes + bytes(str(self.horizontalSliderTimeout.value()), 'utf-8') + eosBytes
                try:
                    start_time = time.time()
                    i += 1
                    totBlocks += 1
                    while True:
                        try:
                            # Send the first packet to the server
                            clientSocket.sendto(content, (serverName, self.serverPort))
                            # Receive the answer of the server
                            clientSocket.settimeout(self.horizontalSliderTimeout.value())
                            serverACK, serverAddress = clientSocket.recvfrom(self.packetSize)
                            break
                        except Exception as inst:
                            if not self.checkBoxReconnect.isChecked():
                                self.questionMessage(str(inst))
                                if not self.answer:
                                    return
                    value += av;
                    self.progressBar.setValue(int(value))
                    while serverACK[0:2] != err_code:
                        # Reading from the .txt the packet size bytes minus the header bytes
                        data = fd.read(self.packetSize)
                        content = data_code + i.to_bytes(2, 'big') + data
                        value += av;
                        self.progressBar.setValue(int(value))
                        if not data:
                            while True:
                                try:
                                    if i - int.from_bytes(serverACK[2:4], 'big') > 1:
                                        continue
                                    clientSocket.sendto(data_code + i.to_bytes(2, 'big'), (serverName,self.serverPort))
                                    clientSocket.settimeout(self.horizontalSliderTimeout.value())
                                    serverACK, serverAddress = clientSocket.recvfrom(self.packetSize)
                                    break
                                except Exception as inst:
                                    if not self.checkBoxReconnect.isChecked():
                                        self.questionMessage(str(inst))
                                        if not self.answer:
                                            return
                            break
                        while True:
                            try:
                                # Send data to server
                                clientSocket.sendto(content, (serverName, self.serverPort))
                                
                                clientSocket.settimeout(self.horizontalSliderTimeout.value())
                                # Recieve the answer of the server
                                serverACK, serverAddress = clientSocket.recvfrom(self.packetSize)
                                break
                            except Exception as inst:
                                if not self.checkBoxReconnect.isChecked():
                                    self.questionMessage(str(inst))
                                    if not self.answer:
                                        return
                        i += 1
                        totBlocks += 1
                        # Restart blockNum
                        if i == 65536:
                            i = 1;
                        # End if data is lower than the chosen packet size
                        if len(data) < self.packetSize:
                            break
                    fd.close()

                    if serverACK[0:2] == err_code:
                        self.progressBar.setValue(0)
                        n = 3
                        # Get error message sent by the server
                        while serverACK[n] != 0:
                            n += 1
                        # Show error message
                        self.errorMessage(serverACK[4:n].decode('utf-8'))
                        clientSocket.sendto(b'\x00\x04' + i.to_bytes(2, 'big'), (serverName, self.serverPort))
                    else:
                        self.popupMessage("File sent succefully!", totBlocks, "{:.2f}".format(time.time() - start_time))
                
                except Exception as inst:
                    self.errorMessage(str(inst))

            # The file is not found
            else:
                self.errorMessage("The file does not exist in the directory.")
        # clientSocket.close()
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()