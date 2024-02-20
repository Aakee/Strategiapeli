'''
File includes classes needed for attack/skill confirmations.
'''


from PyQt5.QtWidgets import QGridLayout, QPushButton, QLabel, QDialog, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class ConfirmAttack(QDialog):
    '''
    Pops a window which works as confirmation for attacking
    '''
    def __init__(self,user,attack,target):
        '''
        @param target: Character object who is taking the attack
        @param attack: Attack object char is attacking with
        '''
        super().__init__()
        self.char = user
        self.attack = attack
        self.target = target
        self.setWindowTitle("Confirm action")
        self.setWindowIcon(QIcon(self.char.get_default_path()))
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.setWindowModality(Qt.ApplicationModal)  # Cannot interact with board before dialog is dealt with
        
        label = QLabel()
        max_dmg = attack.calculate_max_damage(self.target)
        accuracy = attack.calculate_accuracy(target)
        name = attack.get_name()
        string = name + "\nDamage: " + str(max_dmg) + "\nAccuracy: " + str(accuracy) + "%"
        label.setText(string)
        self.grid.addWidget(label,0,1)
        
        yesbutton = QPushButton("Confirm")
        yesbutton.clicked.connect(self.accept)
        self.grid.addWidget(yesbutton,1,0)
        
        yesbutton = QPushButton("Cancel")
        yesbutton.clicked.connect(self.reject)
        self.grid.addWidget(yesbutton,1,2)
        
        self.show()
        
        
class ConfirmSkill(QDialog):
    '''
    Pops a window which works as confirmation for using a skill
    '''
    def __init__(self,user,skill,info):
        '''
        @param info: String of basic info of action
        @param skill: Skill object character is using
        '''
        super().__init__()
        self.setWindowTitle("Confirm action")
        self.grid = QGridLayout()
        self.char = user
        self.setWindowIcon(QIcon(self.char.get_default_path()))
        self.setLayout(self.grid)
        self.setWindowModality(Qt.ApplicationModal)  # Cannot interact with board before dialog is dealt with
        
        label = QLabel()
        string = skill.get_name() + "\n" + info
        label.setText(string)
        self.grid.addWidget(label,0,1)
        
        yesbutton = QPushButton("Confirm")
        yesbutton.clicked.connect(self.accept)
        self.grid.addWidget(yesbutton,1,0)
        
        yesbutton = QPushButton("Cancel")
        yesbutton.clicked.connect(self.reject)
        self.grid.addWidget(yesbutton,1,2)
        
        self.show()