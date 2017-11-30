from PyQt5 import Qt
import os
import pickle
import socket

app = Qt.QApplication([])

class MainWindow(Qt.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Cute Fileserver Client")
        # Create a container object
        self._container = Qt.QWidget()
        self.setCentralWidget(self._container)
        # Create a grid
        self.grid = Qt.QGridLayout()
        # Create the ip address selection text field
        self.address_field = Qt.QLineEdit()
        self.address_field.setPlaceholderText("127.0.0.1:3001")
        self.grid.addWidget(self.address_field)
        # Create the connect button
        self.connect_btn = Qt.QPushButton()
        self.connect_btn.setText("Connect")
        self.connect_btn.clicked.connect(self.connect)
        self.grid.addWidget(self.connect_btn)
        # Create the file selection combobox
        self.file_selector = Qt.QComboBox()
        self.file_selector.setEnabled(False)
        self.grid.addWidget(self.file_selector)
        # Create the download button
        self.download_btn = Qt.QPushButton()
        self.download_btn.setText("Download")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.download)
        self.grid.addWidget(self.download_btn)
        # Set the grid as layout
        self._container.setLayout(self.grid)
        # Extra data
        self.client_socket = None

    def connect(self):
        # Disable the connect button
        self.address_field.setEnabled(False)
        self.connect_btn.setEnabled(False)
        # Split address and port
        try:
            address, ports = self.address_field.text().split(":", 1)
        except IndexError:
            address = self.address_field.text()
            ports = "3001"
        try:
            port = int(ports)
        except ValueError:
            print("Invalid port number")
            return
        # Connect to the server
        self.client_socket = socket.socket()
        self.client_socket.connect((address, port))
        # Get the file list
        files = pickle.loads(self.client_socket.recv(4096))
        separator = {
            "posix": "/",  # Linux
            "nt": "\\",  # Windows
            "java": "/"  # MacOS
        }
        for directory in files:
            for file in directory[2]:
                self.file_selector.addItem(f"{directory[0]}{separator[os.name]}{file}")
        # Toggle the enabled status on the download buttons
        self.file_selector.setEnabled(True)
        self.download_btn.setEnabled(True)

    def download(self):
        # Disable the download buttons
        self.file_selector.setEnabled(False)
        self.download_btn.setEnabled(False)
        # Send the requested filename
        self.client_socket.send(bytes(self.file_selector.currentText(), encoding="utf8"))
        # Receive the status from the server
        status = int(str(self.client_socket.recv(256), encoding="utf8"))
        # Create an empty file
        with open("download/" + self.file_selector.currentText(), "w") as file:
            file.write("")
        # Download the file
        while status > 0:
            data = self.client_socket.recv(256)
            with open("download/" + self.file_selector.currentText(), "ab") as file:
                file.write(data)
            status -= 256

mw = MainWindow()
mw.show()

app.exec_()