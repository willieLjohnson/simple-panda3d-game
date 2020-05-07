from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties

from direct.actor.Actor import Actor

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        properties = WindowProperties()
        properties.setSize(1000, 750)
        self.win.requestProperties(properties)

        self.disableMouse()

        self.environment = self.loader.loadModel("models/environment")
        self.environment.reparentTo(self.render)

        self.tempActor = Actor("Models/PandaChan/act_p3d_chan", {"walk": "Models/PandaChan/a_p3d_chan_run"})
        self.tempActor.reparentTo(self.render)
        self.tempActor.setPos(0, 7, 0)

game = Game()
game.run()
