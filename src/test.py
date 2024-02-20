import unittest

import gameIO
from game_errors import IllegalMoveException

'''
Testit eiv‰t atm toimi, koska importit looppaa. Peli toimii kuitenkin.
Jos haluaa kokeilla testej‰, pit‰‰ poistaa character-tiedostosta
from skill import Skill.
'''


class Test(unittest.TestCase):
    '''
    Tests character moving.
    '''
    def setUp(self):
        unittest.TestCase.setUp(self)
        
        filename = "testsave.txt" # Should be in directory
        
        self.io = gameIO.IO()
        self.game = self.io.load_game(filename)
        self.board = self.game.get_board()
        
        
        
        
    def test_edge_of_range(self):
        try:
            char = self.board.get_piece((2,2))
            self.board.move_char(char,(5,2)) # Edge of range
            self.assertEqual(char, self.board.get_piece((5,2)), "Didn't find character where it should have been!")
            self.board.move_char((5,2),(2,3))
                        
        except IllegalMoveException:
            self.fail("Error when should be legal move")
            
            
    def test_through_wall_with_ghost(self):
        try:
            self.board.move_char((0,3),(0,7)) # Through wall; hass Ghost-Skill
            self.board.move_char((0,7),(0,3))
        except IllegalMoveException:
            self.fail("Error when should be legal move")
            
    def test_through_sand(self):
        try:
            self.board.move_char((1,3),(2,5)) # Through sand, edge of range
            self.board.move_char((2,5),(1,3))
        except IllegalMoveException:
            self.fail("Error when should be legal move")
            
    def test_through_ally(self):
        try:
            self.board.move_char((2,7),(0,7)) # Through an ally, which is legal
            self.board.move_char((0,7),(2,7))
        except IllegalMoveException:
            self.fail("Error when should be legal move")
            
    def test_too_far(self):
        e = self.error_move((2,2), (2,6))
        self.assertNotEqual(e, None, "Moving out of range didn't cause an expection")
        
    def test_through_water(self):
        e = self.error_move((0,3), (0,0))
        self.assertNotEqual(e, None, "Moving through water didn't cause an expection")
        
    def test_through_enemy(self):
        e = self.error_move((4,7), (6,7))
        self.assertNotEqual(e, None, "Moving through an enemy didn't cause an expection")
        
    def test_out_of_bounds(self):
        e = self.error_move((0,4), (0,9))
        self.assertNotEqual(e, None, "Moving through an enemy didn't cause an expection")
        
   
    def error_move(self, src, dst):
        # To check if illegal moves causes exceptions
        check_this = None
        try:
            self.board.move_char(src,dst)
        except IllegalMoveException as e:
            check_this = e
        return check_this
            

if __name__ == '__main__':
    unittest.main()
    