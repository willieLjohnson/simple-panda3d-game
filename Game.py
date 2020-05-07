from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight
from panda3d.core import CollisionHandlerPusher
from panda3d.core import CollisionSphere, CollisionNode
from panda3d.core import CollisionTube
from panda3d.core import CollisionTraverser
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

        ambient_light = AmbientLight("ambient light")
        ambient_light.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.ambientLightNodePath = self.render.attachNewNode(ambient_light)
        self.render.setLight(self.ambientLightNodePath)

        main_light = DirectionalLight("main light")
        self.mainLightNodePath = self.render.attachNewNode(main_light)
        self.mainLightNodePath.setHpr(45, -45, 0)
        self.render.setLight(self.mainLightNodePath)

        self.render.setShaderAuto()

        # Input
        self.accept("w", self.update_key_map, ["up", True])
        self.accept("w-up", self.update_key_map, ["up", False])
        self.accept("s", self.update_key_map, ["down", True])
        self.accept("s-up", self.update_key_map, ["down", False])
        self.accept("a", self.update_key_map, ["left", True])
        self.accept("a-up", self.update_key_map, ["left", False])
        self.accept("d", self.update_key_map, ["right", True])
        self.accept("d-up", self.update_key_map, ["right", False])
        self.accept("mouse1", self.update_key_map, ["shoot", True])
        self.accept("mouse1-up", self.update_key_map, ["shoot", False])

        self.updateTask = self.taskMgr.add(self.update, "update")

        # Collision detection
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.pusher.setHorizontal(True)

        collider_node = CollisionNode("player")
        collider_node.addSolid(CollisionSphere(0, 0, 0, 0.3))
        collider = self.tempActor.attachNewNode(collider_node)
        # collider.show()

        self.pusher.addCollider(collider, self.tempActor)
        self.cTrav.addCollider(collider, self.pusher)

        # Environment walls
        wall_solid = CollisionTube(-8.0, 0, 0, 8.0, 0, 0, 0.2)
        wall_node = CollisionNode("wall")
        wall_node.addSolid(wall_solid)
        wall = self.render.attachNewNode(wall_node)
        wall.setY(8.0)

        wall_solid = CollisionTube(-8.0, 0, 0, 8.0, 0, 0, 0.2)
        wall_node = CollisionNode("wall")
        wall_node.addSolid(wall_solid)
        wall = self.render.attachNewNode(wall_node)
        wall.setY(-8.0)

        wall_solid = CollisionTube(0, -8.0, 0, 0, 8.0, 0, 0.2)
        wall_node = CollisionNode("wall")
        wall_node.addSolid(wall_solid)
        wall = self.render.attachNewNode(wall_node)
        wall.setX(8.0)

        wall_solid = CollisionTube(0, -8.0, 0, 0, 8.0, 0, 0.2)
        wall_node = CollisionNode("wall")
        wall_node.addSolid(wall_solid)
        wall = self.render.attachNewNode(wall_node)
        wall.setX(-8.0)

    def update_key_map(self, control_name, control_state):
        self.keyMap[control_name] = control_state

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
