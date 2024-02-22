'''
File contains classes used to construct the infowindow.
'''
import pathlib
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import configload
from stats import Stats

class Infowindow(QWidget):
    '''
    Class depicts an infowindow, which shows information for the game.
    '''
    def __init__(self,parent):
        super().__init__()
        self.gui = parent
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.list = [] # List of widgets in the grid
        self.popups = [] # List of small infowindows
        
        self.game = parent.get_game()
        self.setWindowTitle('Info')
        self.setWindowIcon(QIcon(configload.get_image('testchar_player.png' )))
        if self.game != None:
            self.player = self.game.get_human()
            self.ai = self.game.get_ai()
            self.refresh()
            
            gui_geometry = self.gui.get_geometry()
            self.move(gui_geometry[0]+self.gui.SQUARE_SIZE*gui_geometry[2]+60,gui_geometry[1]-30)
    
    def refresh(self):
        player_characters = self.player.get_characters()
        ai_characters = self.ai.get_characters()
        self.empty()
        i = 0
        for char in player_characters:
            label = QLabel()
            image = ImageInfo(char,self)
            self.grid.addWidget(image,0,i)
            self.list.append(image)
            string = ""
            string += char.get_name() + "\n"
            string += "HP: " + str(char.get_hp()) + " / " + str(char.get_maxhp()) + "\n"
            square = char.get_square()
            string += "In tile (" + str(square[0]+1) + "," + str(square[1]+1) + ")"
            label.setText(string)
            self.grid.addWidget(label,1,i)
            self.list.append(label)
            i += 1
            
        i = 0
        for char in ai_characters:
            label = QLabel()
            image = ImageInfo(char,self)
            self.grid.addWidget(image,2,i)
            self.list.append(image)
            string = ""
            string += char.get_name() + "\n"
            string += "HP: " + str(char.get_hp()) + " / " + str(char.get_maxhp()) + "\n"
            square = char.get_square()
            string += "In tile (" + str(square[0]+1) + "," + str(square[1]+1) + ")"
            label.setText(string)
            self.grid.addWidget(label,3,i)
            self.list.append(label)
            i += 1
            
        for popup in self.popups:
            popup.refresh()
        self.show()
            
            
    def empty(self):
        for widget in self.list:
            widget.setParent(None)
        self.list = []
            
    def add_to_popups(self,wnd):
        self.popups.append(wnd)
            
    
        
        
        
class ImageInfo(QLabel):
    '''
    Used in Infowindow. Reacts to mouse click.
    '''
    def __init__(self,char,parent):
        super().__init__()
        self.char = char
        self.parent = parent
        self.setPixmap(QPixmap(char.get_path()))
        
    def mousePressEvent(self, e):

        if e.buttons() != Qt.LeftButton:
            return
        
        self.wnd = CharacterInfo(self.char)
        self.parent.add_to_popups(self.wnd)

        
class CharacterInfo(QWidget):
    '''
    Shows info for one character.
    '''
    def __init__(self,char):
        super().__init__()
        self.char = char
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.list = []
        self.setWindowTitle(self.char.get_name())
        self.setWindowIcon(QIcon(self.char.get_default_path()))
        self.refresh()
        self.show()


    def refresh(self):
        
        self.empty()
        
        i = 0
        label = QLabel()
        pm = QPixmap(self.char.get_default_path())
        label.setPixmap(pm)
        self.grid.addWidget(label,0,1)
        self.list.append(label)
        i += 1
        
        
        label = QLabel()
        string = ""
        string += self.char.get_name() + "\n"
        string += "HP: " + str(self.char.get_hp()) + " / " + str(self.char.get_maxhp()) + "\n"
        square = self.char.get_square()
        string += "In tile (" + str(square[0]+1) + "," + str(square[1]+1) + ")"
        label.setText(string)
        self.grid.addWidget(label,1,1)
        self.list.append(label)
        i += 1
    
        attacks = self.char.get_attacks()
        label = QLabel()
        string = "Attacks:"
        for attack in attacks:
            name = attack.get_name()
            flavor = attack.get_flavor()
            string += "\n" + name + ": " + flavor + "\n    "
            string += "Power: " + str(attack.get_power()) + ", accuracy: " + str(attack.get_accuracy()) + "%, min range: " + str(attack.get_range()[0]) \
            + ", max range: " + str(attack.get_range()[1])
            
        label.setText(string)
        self.grid.addWidget(label,2,1)
        self.list.append(label)
        
        
        skills = self.char.get_full_skills()
        label = QLabel()
        string = "Skills:"
        for skill in skills:
            name = skill.get_name()
            flavor = skill.get_flavor()
            string += "\n" + name + ": " + flavor
        label.setText(string)
        self.grid.addWidget(label,3,1)
        self.list.append(label)
        
        
        label = QLabel()
        stats = self.char.get_stats()
        attack = str(stats[Stats.ATTACK])
        defense = str(stats[Stats.DEFENSE])
        magic = str(stats[Stats.MAGIC])
        resistance = str(stats[Stats.RESISTANCE])
        speed = str(stats[Stats.SPEED])
        evasion = str(stats[Stats.EVASION])
        range = str(self.char.get_range())
        string = "Stats:\nAtt: " + attack + "\nDef: " + defense +"\nMag: " + magic \
        + "\nRes: " + resistance + "\nSpd: " + speed + "\nEva: " + evasion + "\nRng: " + range
        label.setText(string)
        self.grid.addWidget(label,4,1)
        self.list.append(label)
        
        
    def empty(self):
        for widget in self.list:
            widget.setParent(None)