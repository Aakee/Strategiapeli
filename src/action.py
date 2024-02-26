'''
File contains classes used to define user's actions (other than moving characters).
'''

from PyQt5.QtWidgets import QGridLayout, QPushButton, QLabel, QDialog, QWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

from skill import Skill
from functools import partial

class Action(QWidget):
    '''
    Dialog, which asks from user what to do.
    '''
    def __init__(self,gui,char):
        super().__init__()
        self.char = char
        self.gui = gui
        self.setWindowTitle("Valitse toiminto")
        self.setWindowIcon(QIcon(self.char.get_default_path()))
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        pm = QPixmap(self.char.get_default_path())
        label = QLabel()
        label.setPixmap(pm)
        self.grid.addWidget(label,0,0)
        
        gui_geometry = self.gui.get_geometry()
        self.move(gui_geometry[0]+self.gui.SQUARE_SIZE*gui_geometry[2]+60,290)
        
        i = 1
        label = QLabel()
        label.setText("Hyokkaykset:")
        self.grid.addWidget(label,0,1)
        attacks = self.char.get_attacks()
        for attack in attacks:
            name = attack.get_name()
            button = QPushButton(name)
            button.setToolTip(attack.get_flavor())
            button.clicked.connect(partial(self.return_attack, str(button.text())))
            self.grid.addWidget(button,i,1)
            i += 1
        
        all_skills = self.char.get_full_skills()
        skills = []
        for skill in all_skills:
            if skill.get_type() in Skill.active_skills:
                skills.append(skill)
        
        i = 0
        if len(skills) > 0:
            label = QLabel()
            label.setText("Kyvyt:")
            self.grid.addWidget(label,i,2)
            i += 1
        for skill in skills:
            name = skill.get_name()
            button = QPushButton(name)
            button.setToolTip(skill.get_flavor())
            button.clicked.connect(partial(self.return_skill, str(button.text())))
            self.grid.addWidget(button,i,2)
            i += 1
        
        i = 0
        label = QLabel()
        label.setText("Muut:")
        self.grid.addWidget(label,i,3)
        i += 1
            
        button = QPushButton("Pass")
        button.setToolTip("Lopeta vuoro")
        self.grid.addWidget(button,i,3)
        button.clicked.connect(partial(self.return_pass, str(button.text())))
        i += 1
            
        self.show()
           
            
    def return_attack(self,name):
        self.gui.set_action_return((name, "a"), self.char)

    def return_skill(self,name):
        self.gui.set_action_return((name, "s"), self.char)

    def return_pass(self, name):
        self.gui.set_action_return((name, "p"), self.char)
