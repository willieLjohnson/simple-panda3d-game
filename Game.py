from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec4
from panda3d.core import WindowProperties


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        properties = WindowProperties()
        properties.setSize(1000, 750)
        self.win.requestProperties(properties)

        self.disableMouse()

        self.environment = self.loader.loadModel("Models/Environment/environment")
        self.environment.reparentTo(self.render)

        self.tempActor = Actor("Models/PandaChan/act_p3d_chan", {"walk": "Models/PandaChan/a_p3d_chan_run"})
        self.tempActor.reparentTo(self.render)
        self.tempActor.getChild(0).setH(180)
        self.tempActor.loop("walk")

        # Top down view
        self.camera.setPos(0, 0, 32)
        self.camera.setP(-90)

        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.ambientLightNodePath = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambientLightNodePath)

        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = self.render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(45, -45, 0)
        self.render.setLight(self.mainLightNodePath)

        self.render.setShaderAuto()

game = Game()
game.run()
