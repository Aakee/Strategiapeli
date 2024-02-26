'''
This file contains classes which are used to draw and update the map.
'''
import pathlib
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
        self.square_size = 50
        self.x = 10
        self.y = 35
        self.buffer = False
        self.game_ended = False
        app = QApplication(sys.argv)
        self.setWindowIcon(QIcon(configload.get_image('testchar_player.png')))

        self.action_storage = ActionStorage()
        self.active = None
        
        self.setWindowTitle('Strategiapeli')
        self.infownd = Infowindow(self)
        self.init_menu()
        
        self.load_file(configload.get_filepath('savedata','save.txt'))
        
        self.show()
    
        sys.exit(app.exec_())
    
    
    def init_game(self):
        '''
        Initializes the view and class members based on the self.game object
        '''
        self.game.set_gui(self)
        self.initUI()
        self.refresh_map()
        self.infownd = Infowindow(self)
        self.setGeometry(self.x, self.y, GUI.SQUARE_SIZE*self.game.get_board().get_width()+50, GUI.SQUARE_SIZE*self.game.get_board().get_height()+90)
        
        print("Aloitetaan uusi peli!\n")
        print("Pelaajan vuoro.")
        self.game.get_human().new_turn()
        
        if self.game.get_turns() > 0:
            print("Voitat {} vuoron paasta.\n".format(self.game.get_turns()))
        if self.game.get_turns() < 0:
            print("Haviat {} vuoron paasta. \n".format(-1 *self.game.get_turns()))


    def initUI(self):
        '''
        Draws the map.
        '''
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.game.get_board().get_width()*GUI.SQUARE_SIZE, self.game.get_board().get_height()*GUI.SQUARE_SIZE)
        #self.grid.addWidget(self.scene,0,0)
                
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.adjustSize()
        self.view.show()
        
        #self.horizontal.addWidget(self.view)
        self.grid.addWidget(self.view,0,0)
            
        for y in range(self.game.get_board().get_height()):
            for x in range(self.game.get_board().get_width()):
                tile = self.game.get_board().get_tile((x,y))
                color_line = QColor(20,20,20)
                color = tile.get_color()
                square = Square(x, y, GUI.SQUARE_SIZE, GUI.SQUARE_SIZE,tile,self)
                square.setBrush(color)
                square.setPen(color_line)
                self.scene.addItem(square)

                
    def char_info(self):
        char = self.active
        if char != None:
            try:
                self.actionwnd.close()
            except:
                pass
            self.actionwnd = Action(self,char)
            #self.grid.addWidget(self.actionwnd,1,0)
        pass
                
    def empty(self):
        '''
        Method empties whole scenery.
        '''
        self.view.setParent(None)
                
    def init_menu(self):
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
                square = tile.get_gui_tile()
                square.setBrush(color)
                                
                if tile.get_object() != None:
                    empty_square = True
                    char = tile.get_object()

                    if char.get_carrying():
                        photo = Image(char.get_carrying())
                        
                        
                        pm = self.scene.addPixmap(photo)
                        tile.get_gui_tile().set_image(pm,True)
                        pm.setPos(x*GUI.SQUARE_SIZE+1,y*GUI.SQUARE_SIZE+1)
                        empty_square = False
                    
                    photo = Image(char)
                    
                    pm = self.scene.addPixmap(photo)
                    
                    tile.get_gui_tile().set_image(pm, empty_square)
                    pm.setPos(x*GUI.SQUARE_SIZE+1,y*GUI.SQUARE_SIZE+1)
        
                    
    def recolor_map(self,squares):
        '''
        Shows where character can move to.
        @param squares: List of squares in (x,y)-format.
        These are the squares we try to paint again.
        '''
        for coordinates in squares:
            tile = self.game.get_board().get_tile(coordinates)
            gui_tile = tile.get_gui_tile()
            color = tile.get_color2()
            gui_tile.setBrush(color)
        
        self.char_info()
                
    def recolor_map_attacking(self,squares):
        '''
        Shows where character can attack to.
        @param squares: List of squares in (x,y)-format.
        These are the squares we try to paint again.
        '''
        for coordinates in squares:
            tile = self.game.get_board().get_tile(coordinates)
            gui_tile = tile.get_gui_tile()
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
            gui_tile = tile.get_gui_tile()
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
            fname = QFileDialog.getOpenFileName(self, 'Open file','',"Text files (*.txt)")
            
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
                fname = QFileDialog.getSaveFileName(self, 'Save file', '', "Text files (*.txt)")
            gameIO.save_game(self.game, fname[0])
            self.statusBar().showMessage('Tallentaminen onnistui!')
        except CorruptedSaveFileException:
            self.statusBar().showMessage('Tallentaminen ei onnistunut.')
        
        
    def get_game(self):
        return self.game
    
    def set_active(self,char):
        if char != self.active:
            self.active = char
            self.char_info()
        if char == None:
            try:
                self.actionwnd.close()
            except:
                pass
        
    def get_active(self):
        return self.active
    
    def set_actionwnd(self,wnd):
        if self.actionwnd != None:
            self.actionwnd.close()
        self.activewnd = wnd
        
    def get_actionwnd(self):
        return self.activewnd
    
    def set_moving(self,char):
        self.moving = char

    def get_moving(self):
        return self.moving
    
    def set_attacking(self, char, attack):
        self.attacking = char
        self.attack = attack
    
    def get_attacking(self):
        return self.attacking, self.attack
    
    def get_scene(self):
        return self.scene
    
    def get_infownd(self):
        return self.infownd
    
    def set_all_ready(self):
        if self.game.whose_turn == self.game.human:
            self.game.get_human().end_turn()
            self.end_turn()
    
    def new_infownd(self):
        self.infownd.close()
        self.infownd = Infowindow(self)
    
    def get_buffer(self):
        '''
        To help minimize wrong inputs to map, every other click is ignored.
        When this method is called, method returns its state and then alters it.
        @return: False: Next click will be recognized, True: Next click will be ignored
        '''
        #self.buffer = (self.buffer == False)
        #return self.buffer == False
        return False
        
    
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
        #self.end_turn()

        if self.game.is_game_over():
            return
        
        if self.game.whose_turn != self.game.get_human():
            self.game.ai.make_turn()

                
        # There are no character moving or attacking
        if self.action_storage.type == ActionStorage.NONE:

            char = self.get_game().get_board().get_piece((x,y))
            if char is None:
                return
                
            if char.get_owner() == self.game.get_human() and not char.is_ready():
                self.action_storage.set(char=char, type=ActionStorage.MOVE)
                self.set_active(char)
                legal_squares = char.get_legal_squares()
                self.recolor_map(legal_squares)
                self.statusBar().showMessage('Valitse ruutu.')
                
            elif char.get_owner() == self.game.get_human():
                self.statusBar().showMessage('Hahmo ei voi enaa liikkua!')
                    
            else:
                self.statusBar().showMessage('Valitse hahmo.')
                self.refresh_map()
            self.get_infownd().refresh()
        
        # A character is moving            
        elif self.action_storage.type == ActionStorage.MOVE:
            char = self.action_storage.char
            legal_squares = char.get_legal_squares()
            other_char = self.get_game().get_board().get_piece((x,y))
            if other_char != None and other_char.get_owner() == self.get_game().get_human() and not char.is_ready():
                self.refresh_map()
                self.action_storage.set(char=other_char, type=ActionStorage.MOVE)
                self.set_active(other_char)
                legal_squares = other_char.get_legal_squares()
                self.recolor_map(legal_squares)
                self.statusBar().showMessage('Valitse ruutu.')                
            else:    
                try:
                    #self.game.get_board().move_char(char,(x,y))
                    self.game.move_character(char,(x,y))
                    self.refresh_map()
                    
                except IllegalMoveException:
                    self.statusBar().showMessage('Et voi siirtaa hahmoa siihen!')   
                    self.refresh_map()
                finally:
                    self.action_storage.reset()
                    self.refresh_map()
                    self.get_infownd().refresh()
        
        # A character is attacking or using a skill
        else:
            buffer = self.get_buffer()
            if buffer:
                return
            try:
                char, attack = self.action_storage.char, self.action_storage.attack
                #char.attack(attack,(x,y))
                self.game.use_attack(char,(x,y),attack)
                self.statusBar().showMessage('Valitse hahmo.')
            except IllegalMoveException:
                self.statusBar().showMessage('Et voi hyokata siihen!')
            finally:
                self.action_storage.reset()
                self.set_active(None)
                self.refresh_map()
                self.get_infownd().refresh()
    

    def end_turn(self):
        '''
        Method is called every time player clicks on the map to check, whose turn it should be.
        Method also declares the winner, if game has ended.
        '''
        return
        if self.action_storage.type == ActionStorage.NONE:
            self.refresh_map()
            self.infownd.refresh()
            
        if not self.game.get_ai().is_alive() or self.game.get_human().is_won():
            self.statusBar().showMessage('Voitit pelin!')
            print("\nVoitit pelin!")
            self.game_ended = True
            
        elif not self.game.get_human().is_alive() or self.game.get_ai().is_won():
            self.statusBar().showMessage('Havisit pelin!')
            print("\nHavisit pelin!")
            self.game_ended = True
            
            
        elif self.game.whose_turn == self.game.get_human(): # Player's turn
            
            if self.game.get_human().is_ready(): # If player has already moven all their characters
                self.refresh_map()
                print("\n\nTietokoneen vuoro!\n")
                self.game.get_ai().new_turn()
                self.game.get_human().set_all_not_ready()
                self.statusBar().showMessage('Tietokoneen vuoro... (Klikkaa karttaa edetaksesi)')
                self.infownd.close()
                self.infownd = Infowindow(self)
                self.refresh_map()
                self.infownd.refresh()
                
        else: # Computer's turn
            if not self.game.get_ai().is_ready(): # If there are still pieces to move for ai
                self.game.get_ai().make_turn()
                self.refresh_map()
                self.infownd.refresh()
            
            else: # If computer has moven all their characters
                self.game.get_ai().set_all_not_ready()
                print("\n\nPelaajan vuoro!\n")
                    
                self.game.get_human().new_turn()
                self.infownd.empty()
                self.infownd.close()
                self.infownd = Infowindow(self)
                self.statusBar().showMessage('Valitse hahmo.')
                self.refresh_map()
                self.infownd.refresh()
                
                if self.game.get_turns() > 0:
                    print("Voitat {} vuoron paasta.\n".format(abs(self.game.get_turns())))
                if self.game.get_turns() < 0:
                    print("Haviat {} vuoron paasta. \n".format(abs(self.game.get_turns())))
                
                self.save_game(configload.get_filepath('savedata','backup.txt')) # Backup save each turn
                
                self.end_turn() # To check if game ended during computer's turn
            
            
    def game_over(self):
        return self.game_ended
    
    def set_action_return(self,contents,char):
        '''
        Gets inputs from action dialog.
        @param contents: tuple in form of (actions name, actions type). Type is either "a" for attack or "s" for skill.
        '''
        self.refresh_map()
        self.return_cont = contents[0]
        self.return_type = contents[1]
        if self.return_type == "a":
            attacks = char.get_attacks()
            for attack in attacks:
                if attack.get_name() == self.return_cont:
                    self.return_cont = attack
            
            attack = self.return_cont
            range = attack.get_range()
            min_range = range[0]
            max_range = range[1]
            squares = []
            squares = char.define_attack_targets(char.get_square(),max_range,attack.targets_enemy())
               
            if len(squares) == 0:
                self.statusBar().showMessage('Hyokkayksella ei ole laillisia kohteita!')
                self.action_storage.reset()
                return
            
            self.recolor_map_attacking(squares)
            self.action_storage.set(char=char, type=ActionStorage.ATTACK, attack=self.return_cont)
            self.statusBar().showMessage('Valitse kohde.')
        
        
        elif self.return_type == "s":
            skills = char.get_full_skills()
            for skill in skills:
                if skill.get_name() == self.return_cont:
                    self.return_cont = skill
            
            skill = self.return_cont
            range = skill.get_range()
            all_squares = self.game.get_board().get_tiles_in_range(char.get_square(),range)
            squares = char.define_attack_targets(char.get_square(),range,skill.targets_enemy())
            
            if len(squares) == 0 and skill.targets():
                self.statusBar().showMessage('Kyvylla ei ole laillisia kohteita!')
                self.action_storage.reset()
                return
            
            if skill.affects_all() or not skill.targets():
                self.recolor_map_skill(all_squares)
            else:
                self.recolor_map_skill(squares)
                
            self.action_storage.set(char=char, type=ActionStorage.ATTACK, attack=self.return_cont)
            self.statusBar().showMessage('Valitse kohde.')
                         
        else:
            self.action_storage.reset()
            self.set_active(None)
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
        self.tile = tile
        self.gui = gui
        self.game = gui.get_game()
        self.tile.set_gui_tile(self)
        self.buffer = 0
        self.image = []   # List of the chars' images currently on square
        
        
    def set_image(self,img,empty_square):
        '''
        @param img: Pixmap of character currently trying to put on tile.
        @param empty_square: True if all previous pixmaps are removed from tile, False if theyt are left there
        '''
        if self.image != [] and empty_square:
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

        if e.buttons() != Qt.LeftButton:
            return

        self.gui.map_clicked(self.x,self.y)
