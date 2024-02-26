'''
The game is run from here.
'''

from gui import GUI
import sys
from PyQt5.QtWidgets import QApplication


def main():
    '''
    Launches the GUI.
    '''
    #global app
    app = QApplication(sys.argv)
    gui = GUI()

main()
