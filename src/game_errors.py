import pathlib

from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class CorruptedMapDataException(Exception):

    def __init__(self, message):
        super(CorruptedMapDataException, self).__init__(message)




class CorruptedSaveFileException(Exception):

    def __init__(self, message):
        super(CorruptedSaveFileException, self).__init__(message)



class IllegalMoveException(Exception):

    def __init__(self, message):
        super(IllegalMoveException, self).__init__(message)
        

class ErrorWindow(QDialog):
    
    def __init__(self,text):
        super().__init__()
        self.setWindowTitle('Virhe!')
        self.setWindowIcon(QIcon(str( pathlib.Path(__file__).parent / 'images' / 'testchar_player.png' )))
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        label = QLabel()
        label.setText(text)
        self.grid.addWidget(label, 0, 0)
        self.setWindowModality(Qt.ApplicationModal)