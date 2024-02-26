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
    Dialog showing a character's attack and active skills and collecting inputs from the player.
    '''
    def __init__(self,gui,char):
        super().__init__()

        # Set up window parameters
        self.char       = char
        self.gui        = gui
        self.grid       = QGridLayout()
        pm              = QPixmap(self.char.get_default_path())
        label           = QLabel()
        label.setPixmap(pm)
        self.grid.addWidget(label,0,0)
                
        gui_geometry = self.gui.get_geometry()
        self.setWindowTitle("Valitse toiminto")
        self.setWindowIcon(QIcon(self.char.get_default_path()))
        self.setLayout(self.grid)
        self.move(gui_geometry[0]+self.gui.SQUARE_SIZE*gui_geometry[2]+60,290)

        # List attacks
        label = QLabel()
        label.setText("Hyokkaykset:")
        self.grid.addWidget(label,0,1)
        attacks = self.char.get_attacks()
        for idx, attack in enumerate(attacks, start=1):     # Loop through all attacks and add their buttons to grid
            name = attack.get_name()
            button = QPushButton(name)
            button.setToolTip(attack.get_flavor())
            button.clicked.connect(partial(self.return_attack, str(button.text())))
            self.grid.addWidget(button,idx,1)
        
        # List skills
        all_skills = self.char.get_full_skills()
        skills = []
        for skill in all_skills:
            if skill.get_type() in Skill.active_skills:     # only activated skills
                skills.append(skill)
        
        # If there are at least one activated skill, loop through all skills and add them to the grid
        if len(skills) > 0:
            label = QLabel()
            label.setText("Kyvyt:")
            self.grid.addWidget(label,0,2)
        for idx, skill in enumerate(skills, start=1):
            name = skill.get_name()
            button = QPushButton(name)
            button.setToolTip(skill.get_flavor())
            button.clicked.connect(partial(self.return_skill, str(button.text())))
            self.grid.addWidget(button,idx,2)
        
        # Add an option for skipping the turn
        label = QLabel()
        label.setText("Muut:")
        self.grid.addWidget(label,0,3)
            
        button = QPushButton("Pass")
        button.setToolTip("Lopeta vuoro")
        self.grid.addWidget(button,1,3)
        button.clicked.connect(partial(self.return_pass, str(button.text())))
            
        self.show()
           
            
    def return_attack(self,name):
        '''
        Method is called when an "attack" button is clicked. Method relays the information back to main GUI class.
        @param name: Text in the button, i.e. the attack name
        '''
        self.gui.set_action_return((name, "a"), self.char)

    def return_skill(self,name):
        '''
        Method is called when a "skill" button is clicked. Method relays the information back to main GUI class.
        @param name: Text in the button, i.e. the skill name
        '''
        self.gui.set_action_return((name, "s"), self.char)

    def return_pass(self, name):
        '''
        Method is called when the "pass" button is clicked. Method relays the information back to main GUI class.
        @param name: Text in the button, i.e. "pass"
        '''
        self.gui.set_action_return((name, "p"), self.char)
