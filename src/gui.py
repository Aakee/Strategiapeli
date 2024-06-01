'''
This file contains classes which are used to draw and update the map.
'''
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGraphicsRectItem, QApplication, QMainWindow, QGraphicsScene, QAction, QFileDialog, QGridLayout
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QCoreApplication
import sys
import configload
from character import Character
from game_errors import IllegalMoveException, CorruptedMapDataException,\
    CorruptedSaveFileException, ErrorWindow
from infowindow import Infowindow
from action import Action
import gameIO
from game_enums import PlayerColor

class ActionStorage:
    '''
    Data class to keep track of which character is moving or attacking.
    '''
    NONE    = 0
    MOVE    = 1
    ATTACK  = 2

    def __init__(self) -> None:
        self.reset()

    def reset(self):
        self.char   = None
        self.type   = ActionStorage.NONE
        self.attack = None

    def set(self, char=None, type=None, attack=None):
        self.char = char
        self.attack = attack
        self.type = ActionStorage.NONE if type is None else type



class GUI(QMainWindow):
    '''
    The main class of GUI. Draws the map and refreshes it between turns.
    '''
    
    SQUARE_SIZE = 50
    
    def __init__(self):                
        super().__init__()
        self.setCentralWidget(QtWidgets.QWidget())
        self.grid = QGridLayout()
        self.centralWidget().setLayout(self.grid)
        
        self.statusBar().showMessage('Avaa peli.')
        self.game = None
        self.winner_declared = False
        self.square_size = 50

        self.x = 10
        self.y = 35
        app = QApplication(sys.argv)
        self.setWindowIcon(QIcon(configload.get_image('testchar_blue.png')))

        self.action_storage = ActionStorage()
        self.active_character = None
        
        self.setWindowTitle('Strategiapeli')
        self.infownd = Infowindow(self)
        self.actionwnd=None
        self.init_menu()
        
        self.load_file(configload.get_filepath('savedata','save_yaml.yaml'))
        
        self.show()
    
        sys.exit(app.exec_())
    
    
    def init_game(self):
        '''
        Initializes the view and class members based on the self.game object
        '''
        self.initUI()
        self.refresh_map()
        self.infownd.close()
        self.infownd = Infowindow(self)
        self.setGeometry(self.x, self.y, GUI.SQUARE_SIZE*self.game.get_board().get_width()+50, GUI.SQUARE_SIZE*self.game.get_board().get_height()+90)
        
        print("Aloitetaan uusi peli!\n")
        self.winner_declared = False

        self.blue_is_ai = self.game.get_blue_player().is_ai()
        self.red_is_ai = self.game.get_red_player().is_ai()

        if self.blue_is_ai and self.red_is_ai:
            self.nof_ai_players = 2
            self.nof_human_players = 0
        elif not self.blue_is_ai and not self.red_is_ai:
            self.nof_ai_players = 0
            self.nof_human_players = 2
        else:
            self.nof_ai_players = 1
            self.nof_human_players = 1

        if self.game.whose_turn == PlayerColor.BLUE:
            print("Sinisen pelaajan vuoro!")
        else:
            print("Punaisen pelaajan vuoro!")


    def initUI(self):
        '''
        Draws the map.
        '''
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.game.get_board().get_width()*GUI.SQUARE_SIZE, self.game.get_board().get_height()*GUI.SQUARE_SIZE)
                
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.adjustSize()
        self.view.show()

        self.view.gui_tiles = []
        self.grid.addWidget(self.view,0,0)

        for y in range(self.game.get_board().get_height()):
            row = []
            for x in range(self.game.get_board().get_width()):
                tile = self.game.get_board().get_tile((x,y))
                #color_line = QColor(20,20,20)
                #color = tile.get_color()
                square = Square(x, y, GUI.SQUARE_SIZE, GUI.SQUARE_SIZE,tile,self)
                #square.setBrush(color)
                #square.setPen(color_line)
                self.scene.addItem(square)
                row.append(square)
            self.view.gui_tiles.append(row)

        self.refresh_map()

                
    def char_info(self):
        '''
        Method opens the action window for the currently active character.
        '''
        char = self.active_character
        if char != None:
            if self.actionwnd is not None:
                self.actionwnd.close()

            self.actionwnd = Action(self,char)


    def empty(self):
        '''
        Method empties whole scenery.
        '''
        self.view.setParent(None)


    def init_menu(self):
        '''
        Method creates the dropdown menus for the main window.
        '''
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit game')
        exitAction.triggered.connect(QCoreApplication.quit)
        
        infowndAction = QAction('&Infowindow',self)
        infowndAction.setShortcut('Ctrl+I')
        infowndAction.setStatusTip('Show infowindow')
        infowndAction.triggered.connect(self.new_infownd)
        
        saveAction = QAction('&Save game', self)
        saveAction.setStatusTip('Save current board positions')
        saveAction.triggered.connect(self.save_game)

        loadAction = QAction('&Load game',self)
        loadAction.setStatusTip('Load game from file')
        loadAction.triggered.connect(self.load_file)
        
        endTurnAction = QAction('&End turn',self)
        endTurnAction.setShortcut('Ctrl+E')
        endTurnAction.setStatusTip('End your turn')
        endTurnAction.triggered.connect(self.set_all_ready)

        self.statusBar()

        menubar = self.menuBar()
        gameMenu = menubar.addMenu('&Game')
        gameMenu.addAction(saveAction)
        gameMenu.addAction(loadAction)
        gameMenu.addAction(endTurnAction)
        gameMenu.addAction(exitAction)

        viewMenu = menubar.addMenu('&Show')
        viewMenu.addAction(infowndAction)
                
                    
    def refresh_map(self):
        '''
        Method refreshes the map: all tiles are recolored back to normal,
        and characters are printed to their current tile.
        '''
        for y in range(self.game.get_board().get_height()):
            for x in range(self.game.get_board().get_width()):
                tile = self.game.get_board().get_tile((x,y))
                color = tile.get_color()
                #square = tile.get_gui_tile()
                square = self.view.gui_tiles[y][x]
                square.setBrush(color)

                square.destroy_image()
                                
                if tile.get_object() != None:
                    empty_square = True
                    char = tile.get_object()

                    if char.get_carrying():
                        photo = Image(char.get_carrying())
                        pm = self.scene.addPixmap(photo)
                        #tile.get_gui_tile().set_image(pm,True)
                        pm.setPos(x*GUI.SQUARE_SIZE+1,y*GUI.SQUARE_SIZE+1)
                        empty_square = False
                    
                    photo = Image(char)
                    
                    pm = self.scene.addPixmap(photo)
                    
                    #tile.get_gui_tile().set_image(pm, empty_square)
                    square.set_image(pm, empty_square)
                    pm.setPos(x*GUI.SQUARE_SIZE+1,y*GUI.SQUARE_SIZE+1)
        
                    
    def recolor_map_move(self,squares):
        '''
        Shows where character can move to.
        @param squares: List of squares in (x,y)-format.
        These are the squares we try to paint again.
        '''
        for coordinates in squares:
            tile = self.game.get_board().get_tile(coordinates)
            gui_tile = self.view.gui_tiles[coordinates[1]][coordinates[0]]
            #gui_tile = tile.get_gui_tile()
            color = tile.get_color2()
            gui_tile.setBrush(color)


    def recolor_map_attack(self,squares):
        '''
        Shows where character can attack to.
        @param squares: List of squares in (x,y)-format.
        These are the squares we try to paint again.
        '''
        for coordinates in squares:
            tile = self.game.get_board().get_tile(coordinates)
            #gui_tile = tile.get_gui_tile()
            gui_tile = self.view.gui_tiles[coordinates[1]][coordinates[0]]
            color = tile.get_color_attack()
            gui_tile.setBrush(color)
            
    def recolor_map_skill(self,squares):
        '''
        Shows where character can use a skill to.
        @param squares: List of squares in (x,y)-format.
        These are the squares we try to paint again.
        '''
        for coordinates in squares:
            tile = self.game.get_board().get_tile(coordinates)
            #gui_tile = tile.get_gui_tile()
            gui_tile = self.view.gui_tiles[coordinates[1]][coordinates[0]]
            color = tile.get_color_skill()
            gui_tile.setBrush(color)
            
    def load_file(self,*arg):
        '''
        Method loads game from text file.
        @param: File's name; if none, methos asks from the player
        '''
        if arg[0] != False:
            fname = arg
        else:
            directory = configload.getdir('savedata')
            fname = QFileDialog.getOpenFileName(self, 'Open file', directory)
            
        if fname[0] == '': #If canceled
            return
        try:
            self.game = gameIO.load_game(fname[0])
            self.init_game()

        except CorruptedMapDataException as e:
            self.error = ErrorWindow(str(e))
            self.error.show()
            self.statusBar().showMessage('Tiedostossa oli virhe!')
            
        except CorruptedSaveFileException as e:
            self.error = ErrorWindow(str(e))
            self.error.show()
            self.statusBar().showMessage('Tiedostossa oli virhe!')
        finally:
            pass
        
    
    def save_game(self, *arg):
        '''
        Method saves the game.
        @param: save file's name; if none, method asks from the palyer.
        '''
        if arg[0] != False:
            fname = arg
        try:
            if arg[0] == False:
                directory = configload.getdir('savedata')
                fname = QFileDialog.getSaveFileName(self, 'Save file', directory, "Save files (*.save)")
            gameIO.save_game(self.game, fname[0])
            self.statusBar().showMessage('Tallentaminen onnistui!')
        except CorruptedSaveFileException:
            self.statusBar().showMessage('Tallentaminen ei onnistunut.')
        
        
    def get_game(self):
        return self.game
    
    def set_active_character(self,char):
        if char != self.active_character:
            self.active_character = char
            self.char_info()
        if char is None and self.actionwnd is not None:
            self.actionwnd.close()
        
    def get_active_character(self):
        return self.active_character
    
    def set_actionwnd(self,wnd):
        if self.actionwnd != None:
            self.actionwnd.close()
        self.activewnd = wnd
        
    def get_actionwnd(self):
        return self.activewnd

    def get_scene(self):
        return self.scene
    
    def get_infownd(self):
        return self.infownd
    
    def set_all_ready(self):
        if not self.game.get_current_player().is_ai():
            self.game.end_turn()
            self.new_turn()
    
    def new_infownd(self):
        self.infownd.close()
        self.infownd = Infowindow(self)
    
    def declare_winner(self):
        '''
        Declares the winner of the game if the game has ended.
        '''
        winner = self.game.get_winner()
        if self.winner_declared or winner is None:
            return
        if self.nof_human_players == 1:
            if (winner == PlayerColor.BLUE and not self.game.get_blue_player().is_ai()) or (winner == PlayerColor.RED and not self.game.get_red_player().is_ai()):
                print("Voitit pelin!")
                self.statusBar().showMessage('Voitit pelin!')
            else:
                print("Havisit pelin!")
                self.statusBar().showMessage('Havisit pelin!')
        else:
            if winner == PlayerColor.BLUE:
                print("Sininen pelaaja voitti!")
            if winner == PlayerColor.RED:
                print("Punainen pelaaja voitti!")
            self.statusBar().showMessage('Peli ohi')
        self.winner_declared = True
        

    
    def get_geometry(self):
        '''
        Method returns main window's geometry, so other widgets can move themselves
        according to that.
        @return: Tuple in format (xPosition, yPosition, width of the grid, height of the grid)
        '''
        return (self.x,self.y,self.game.get_board().get_width(),self.game.get_board().get_height())
    
    def map_clicked(self,x,y):
        '''
        Method handles mouse click events. The method is called from the Square objects, which also give
        coordinates to this method.
        @param x,y: Coordinates of clicked square (in game coordinate system, not measured in pixels)
        '''
        self.infownd.refresh()

        # Return if winner is already determined
        if self.game.is_game_over():
            self.declare_winner()
            return
        
        # Check if about to change turns, and do so if needed
        if self.game.is_player_ready():
            self.new_turn()
            return
        
        # If it's AI's turn, set it to do its turn independently
        if self.game.get_current_player().is_ai():
            self.game.ai_make_turn()
            self.refresh_map()
            self.get_infownd().refresh()
            return
        
        # Refresh map to remove all old highlightnings
        self.refresh_map()

        # Fetch the currently-set active character and what it is set to do
        active_char = self.action_storage.char
        clicked_char = self.get_game().get_board().get_piece((x,y))
        clicked_char_owner = None if clicked_char is None else clicked_char.get_owner()

        # If clicked own character and either character is moving or nothing is set: select this character to be moved
        if self.action_storage.type in ( ActionStorage.NONE, ActionStorage.MOVE ) and clicked_char_owner == self.game.get_current_player():
            if clicked_char.is_ready():
                self.action_storage.reset()
                self.statusBar().showMessage('Hahmo ei voi enaa liikkua!')
            else:
                self.action_storage.set(char=clicked_char, type=ActionStorage.MOVE)
                self.set_active_character(clicked_char)
                legal_squares = clicked_char.get_legal_squares()
                self.recolor_map_move(legal_squares)
                self.statusBar().showMessage('Valitse ruutu.')

        else:
            # Move the active character to the chosen tile
            if self.action_storage.type == ActionStorage.MOVE:
                try:
                    self.game.move_character(active_char, (x,y))
                except IllegalMoveException:
                    self.statusBar().showMessage('Et voi siirtaa hahmoa siihen!')

            # Attack with the active character and active attack to the chosen tile
            elif self.action_storage.type == ActionStorage.ATTACK:
                try:
                    attack = self.action_storage.attack
                    self.game.use_attack(active_char, (x,y), attack)
                    self.set_active_character(None)
                except IllegalMoveException:
                    self.statusBar().showMessage('Et voi hyokata siihen!')

            # Reset the active character and refresh the map
            self.action_storage.reset()
            self.refresh_map()
            self.statusBar().showMessage('Valitse hahmo.')

        # Refresh the infowindow in any case
        self.infownd.refresh()



    def new_turn(self):
        '''
        Method prints needed information into the console and then tries to change the turn between players.
        '''
        # Return if the current player is not ready
        if not self.game.is_player_ready():
            return
        
        # Red player is starting their turn
        if self.game.get_current_player() == self.game.get_blue_player():
            print("\n\nPunaisen pelaajan vuoro!\n")

        # Blue player is starting their turn
        else:
            print("\n\nSinisen pelaajan vuoro!\n")

        # Backup save each turn
        self.save_game(configload.get_filepath('savedata','backup.save'))

        # Set status bar message
        if not self.game.get_current_player().is_ai():
            self.statusBar().showMessage('Valitse hahmo.')
        else:
            self.statusBar().showMessage('Tietokoneen vuoro... (Klikkaa karttaa edetaksesi)')

        # Change turn
        if self.game.change_turn():
            self.refresh_map()

        self.infownd.refresh()


    
    def set_action_return(self,contents,char):
        '''
        Gets inputs from action dialog.
        @param contents: tuple in form of (actions name, actions type). Type is "a" for attack, "s" for skill, or "p" for pass.
        @param char: the character who did the action
        '''
        self.refresh_map()
        return_cont, return_type = contents[0], contents[1]

        # Case 1: Attack
        if return_type == "a":
            attacks = char.get_attacks()
            for attack in attacks:      # Find the attack which corresponds to the button text
                if attack.get_name() == return_cont:
                    return_cont = attack
            
            # Find the squares where the character can use this attack to
            attack = return_cont
            range = attack.get_range()
            min_range, max_range = range[0], range[1]
            squares = char.define_attack_targets(char.get_square(),max_range,attack.targets_enemy())
               
            # Return if there are no legal targets
            if len(squares) == 0:
                self.statusBar().showMessage('Hyokkayksella ei ole laillisia kohteita!')
                self.action_storage.reset()
                return
            
            # Recolor map highlighting squares where can be attacked, and set the character and attack to action_storage
            self.recolor_map_attack(squares)
            self.action_storage.set(char=char, type=ActionStorage.ATTACK, attack=return_cont)
            self.statusBar().showMessage('Valitse kohde.')
        

        # Case 2: Skill
        elif return_type == "s":
            skills = char.get_full_skills()
            for skill in skills: # Find the skill which corresponds to the button text
                if skill.get_name() == return_cont:
                    return_cont = skill
            
            # Find the squares where the character can use this skill to
            skill = return_cont
            range = skill.get_range()
            all_squares = self.game.get_board().get_tiles_in_range(char.get_square(),range)
            squares = char.define_attack_targets(char.get_square(),range,skill.targets_enemy())
            
            # Return if the skill targets a single character and there are no legal targets
            if len(squares) == 0 and skill.targets():
                self.statusBar().showMessage('Kyvylla ei ole laillisia kohteita!')
                self.action_storage.reset()
                return
            
            # Highlight the squares where this skill can be used to in case it targets, or all squares in area if it does not
            if skill.affects_all() or not skill.targets():
                self.recolor_map_skill(all_squares)
            else:
                self.recolor_map_skill(squares)
            
            # Set the character and skill to action_storage
            self.action_storage.set(char=char, type=ActionStorage.ATTACK, attack=return_cont)
            self.statusBar().showMessage('Valitse kohde.')
                         
        # Case 3: Pass
        elif return_type == "p":
            # Pass the character turn
            self.game.pass_character_turn(char)
            self.set_active_character(None)
            self.action_storage.reset()
            self.refresh_map()
        

        else:
            self.action_storage.reset()
            self.set_active_character(None)
            self.refresh_map()
        
        self.get_infownd().refresh()
            

                    
                
                
class Image(QPixmap):
    '''
    Image of a character on the map.
    In addition to the pixmap, holds information of the character it depicts.
    '''
    
    def __init__(self,char):
        super().__init__(char.get_path())
        self.char = char
        
        
        
        
class Square(QGraphicsRectItem):
    '''
    One square in GUI map.
    '''
    def __init__(self,x,y,width,height,tile,gui):
        super().__init__(x*GUI.SQUARE_SIZE,y*GUI.SQUARE_SIZE,width,height)
        self.x = x
        self.y = y
        self.gui = gui
        self.image = []   # List of the chars' images currently on square
        
        
    def set_image(self,img,empty_square):
        '''
        @param img: Pixmap of character currently trying to put on tile.
        @param empty_square: True if all previous pixmaps are removed from tile, False if theyt are left there
        '''
        if len(self.image) > 0 and empty_square:
            scene = self.gui.get_scene()
            for image in self.image:
                scene.removeItem(image)
            self.image = []
        self.image.append(img)


    def destroy_image(self):
        '''
        Destroys the pixmap on this tile. Used when a character moves or dies.
        '''
        scene = self.gui.get_scene()
        for img in self.image:
            scene.removeItem(img)
        self.image = []


    def mousePressEvent(self, e):
        '''
        Method is called when this square is clicked. The method in turn calls the GUI.map_clicked method.
        '''
        if e.buttons() != Qt.LeftButton:
            return
        self.gui.map_clicked(self.x,self.y)
