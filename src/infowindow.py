'''
File contains classes used to construct the infowindow.
'''
import pathlib
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import configload
from game_enums import Stats

class Infowindow(QWidget):
    '''
    Class depicts an infowindow, which shows information for the game.
    '''
    def __init__(self,parent):
        super().__init__()
        self.gui = parent
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.widgets = [] # List of widgets in the grid
        self.popups = [] # List of small infowindows
        
        self.game = parent.get_game()
        self.setWindowTitle('Info')
        self.setWindowIcon(QIcon(configload.get_image('testchar_red.png' )))
        if self.game != None:
            self.blue = self.game.get_blue_player()
            self.red = self.game.get_red_player()
            self.refresh()
            
            gui_geometry = self.gui.get_geometry()
            self.move(gui_geometry[0]+self.gui.SQUARE_SIZE*gui_geometry[2]+60,gui_geometry[1]-30)
    
    def refresh(self):
        blue_characters = self.blue.get_characters()
        red_characters = self.red.get_characters()
        self.empty()
        i = 0
        for char in blue_characters:
            label = QLabel()
            image = ImageInfo(char,self)
            self.grid.addWidget(image,0,i)
            self.widgets.append(image)
            string = ""
            string += char.get_name() + "\n"
            string += "HP: " + str(char.get_hp()) + " / " + str(char.get_maxhp()) + "\n"
            square = char.get_square()
            string += "In tile (" + str(square[0]+1) + "," + str(square[1]+1) + ")"
            label.setText(string)
            self.grid.addWidget(label,1,i)
            self.widgets.append(label)
            i += 1
            
        i = 0
        for char in red_characters:
            label = QLabel()
            image = ImageInfo(char,self)
            self.grid.addWidget(image,2,i)
            self.widgets.append(image)
            string = ""
            string += char.get_name() + "\n"
            string += "HP: " + str(char.get_hp()) + " / " + str(char.get_maxhp()) + "\n"
            square = char.get_square()
            string += "In tile (" + str(square[0]+1) + "," + str(square[1]+1) + ")"
            label.setText(string)
            self.grid.addWidget(label,3,i)
            self.widgets.append(label)
            i += 1
            
        for popup in self.popups:
            try:
                popup.refresh()
            except TypeError as err:
                print(err)
                popup.close()
        self.show()
            
            
    def empty(self):
        for widget in self.widgets:
            widget.setParent(None)
        self.widgets = []
            
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
        self.widgets = []
        self.setWindowTitle(self.char.get_name())
        self.setWindowIcon(QIcon(self.char.get_default_path()))
        self.refresh()
        self.show()


    def refresh(self):

        def _format_skills(char):
            s = ""
            all_skills          = char.get_full_skills()
            permanent_skills    = [sk for sk in all_skills if sk.max_uses == 0]
            limited_skills      = [sk for sk in all_skills if sk.max_uses < 0]
            statuses            = [st for st in all_skills if st.max_uses > 0]
            if len(permanent_skills) > 0 or len(limited_skills) > 0:
                s += "<font color='blue'>Skills:</font>"
                for sk in permanent_skills:
                    s += f"<br>{sk.get_name()}: {sk.get_flavor()}"
                for sk in limited_skills:
                    s += f"<br>{sk.get_name()}: {sk.get_flavor()}<br>  Uses left: {abs(sk.max_uses)-sk.use_count}"
            if len(statuses) > 0:
                s += "<br><br><font color='blue'>Statuses:</font>"
                for st in statuses:
                    if st.positive == True:
                        s += f"<br>{st.get_name()}: {st.get_flavor()}<br>-- <font color='green'>Turns left: {st.max_uses-st.use_count}</font>"
                    elif st.positive == False:
                        s += f"<br>{st.get_name()}: {st.get_flavor()}<br>-- <font color='green'>Turns left: {st.max_uses-st.use_count}</font>"
                    else:
                        s += f"<br>{st.get_name()}: {st.get_flavor()}<br>-- <font color='green'>Turns left: {st.max_uses-st.use_count}</font>"
            return s
        
        def _format_stats(char):
            stats = char.get_stats()
            orig_stats = char.get_initial_stats()
            stats_ordered = [("Attack", Stats.ATTACK), ("Defense", Stats.DEFENSE), ("Magic", Stats.MAGIC), ("Resistance", Stats.RESISTANCE), 
                             ("Speed", Stats.SPEED), ("Evasion", Stats.EVASION), ("Range", Stats.RANGE),]
            s = "<font color='blue'>Stats:</font><br>"
            for stat_name, stat_enum in stats_ordered:
                val = stats[stat_enum]
                orig_val = orig_stats[stat_enum]
                if val > orig_val:
                    s += f"<font color='green'>{stat_name}: {val}</font><br>"
                elif val < orig_val:
                    s += f"<font color='red'>{stat_name}: {val}</font><br>"
                else:
                    s += f"{stat_name}: {val}<br>"
            return s
        
        self.empty()
        
        i = 0
        label = QLabel()
        pm = QPixmap(self.char.get_default_path())
        label.setPixmap(pm)
        self.grid.addWidget(label,0,1)
        self.widgets.append(label)
        i += 1
        
        
        label = QLabel()
        string = ""
        string += f"<font color='blue'>{self.char.get_name()}</font><br>"
        string += "HP: " + str(self.char.get_hp()) + " / " + str(self.char.get_maxhp()) + "<br>"
        square = self.char.get_square()
        string += "In tile (" + str(square[0]+1) + "," + str(square[1]+1) + ")"
        label.setText(string)
        self.grid.addWidget(label,1,1)
        self.widgets.append(label)
        i += 1
    
        attacks = self.char.get_attacks()
        label = QLabel()
        string = "<font color='blue'>Attacks:</font>"
        for attack in attacks:
            name = attack.get_name()
            flavor = attack.get_flavor()
            string += "<br>" + name + ": " + flavor + "<br>-- "
            string += "Power: " + str(attack.get_power()) + ", accuracy: " + str(attack.get_accuracy()) + "%, min range: " + str(attack.get_range()[0]) \
            + ", max range: " + str(attack.get_range()[1])
            
        label.setText(string)
        self.grid.addWidget(label,2,1)
        self.widgets.append(label)
        
        label = QLabel()
        label.setText(_format_skills(self.char))
        self.grid.addWidget(label,3,1)
        self.widgets.append(label)
        
        label       = QLabel()
        label.setText(_format_stats(self.char))
        self.grid.addWidget(label,4,1)
        self.widgets.append(label)
        
        
    def empty(self):
        for widget in self.widgets:
            widget.setParent(None)
        self.widgets=[]