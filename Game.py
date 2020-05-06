from direct.showbase.ShowBase import  import ShowBase

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
game = Game()
game.run()