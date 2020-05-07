from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec4, Vec3
from panda3d.core import WindowProperties


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        properties = WindowProperties()
        properties.setSize(1000, 750)
        self.win.requestProperties(properties)

        self.disableMouse()

        self.keyMap = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "shoot": False
        }

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

        # Input
        self.accept("w", self.updateKeyMap, ["up", True])
        self.accept("w-up", self.updateKeyMap, ["up", False])
        self.accept("s", self.updateKeyMap, ["down", True])
        self.accept("s-up", self.updateKeyMap, ["down", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("mouse1", self.updateKeyMap, ["shoot", True])
        self.accept("mouse1-up", self.updateKeyMap, ["shoot", False])

        self.updateTask = self.taskMgr.add(self.update, "update")

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState

    def update(self, task):
        dt = globalClock.getDt()

        if self.keyMap["up"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, 5.0 * dt, 0))
        if self.keyMap["down"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, -5.0 * dt, 0))
        if self.keyMap["left"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(-5.0 * dt, 0, 0))
        if self.keyMap["right"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(5.0 * dt, 0, 0))
        if self.keyMap["shoot"]:
            print("Zap!")

        return task.cont


game = Game()
game.run()
