from panda3d.core import Vec3, Vec2
from direct.actor.Actor import Actor
from panda3d.core import CollisionSphere, CollisionNode

FRICTION = 150.0


class GameObject:
    def __init__(self, pos, model_name, model_anims, max_health, max_speed, collider_name):
        self.actor = Actor(model_name, model_anims)
        self.actor.reparentTo(self.render)
        self.actor.setPos(pos)

        self.maxHealth = max_health
        self.health = max_health

        self.maxSpeed = max_speed

        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 300.0

        self.walking = False

        collider_node = CollisionNode(collider_name)
        collider_node.addSolid(CollisionSphere(0, 0, 0, 0.3))
        self.collider = self.actor.attachNewNode(collider_node)
        self.collider.setPythonTag("owner", self)

    def update(self, dt):
        speed = self.velocity.length()
        if speed > self.maxSpeed:
            self.velocity.normalize()
            self.velocity *= self.maxSpeed
            speed = self.maxSpeed

        if not self.walking:
            friction_val = FRICTION * dt
            if friction_val > speed:
                self.velocity.set(0, 0, 0)
            else:
                friction_vec = -self.velocity
                friction_vec.normalize()
                friction_vec *= friction_val

                self.velocity += friction_vec

        self.actor.setPos(self.actor.getPos() + self.velocity * dt)

    def alter_health(self, d_health):
        self.health += d_health

        if self.health > self.maxHealth:
            self.health = self.maxHealth

    def cleanup(self):
        if self.collider is not None and not self.collider.isEmpty():
            self.collider.clearPythonTag("owner")
            base.cTrav.removeCollider(self.collider)
            base.pusher.removeCollider(self.collider)

        if self.actor is not None:
            self.actor.cleanup()
            self.actor.removeNode()
            self.actor = None

        self.collider = None


class Player(GameObject):
    def __init__(self):
        GameObject.__init__(self,
                            Vec3(0, 0, 0),
                            "Models/PandaChan/act_p3d_chan",
                            {
                                "stand": "Models/PandaChan/a_p3d_chan_idle",
                                "walk": "Models/PandaChan/a_p3d_chan_run"
                            },
                            5,
                            10,
                            "player")

        self.actor.getChild(0).setH(180)

        base.pusher.addCollider(self.collider, self.actor)
        base.cTrav.addCollider(self.collider, base.pusher)

        self.actor.loop("stand")
    
    def update(self, keys, dt):
        GameObject.update(self, dt)
        
        self.walking = False
        
        if keys["up"]:
            self.walking = True
            self.velocity.addY(self.acceleration * dt)
        if keys["down"]:
            self.walking = True
            self.velocity.addY(-self.acceleration * dt)
        if keys["left"]:
            self.walking = True
            self.velocity.addX(-self.acceleration * dt)
        if keys["right"]:
            self.walking = True
            self.velocity.addX(self.acceleration * dt)

        if self.walking:
            stand_control = self.actor.getAnimControl("stand")
            if stand_control.isPlaying():
                stand_control.stop()

            walk_control = self.actor.getAnimControl("walk")
            if not walk_control.isPlaying():
                self.actor.loop("walk")
        else:
            stand_control = self.actor.getAnimControl("stand")
            if not stand_control.isPlaying():
                self.actor.stop("walk")
                self.actor.loop("stand")


class Enemy(GameObject):
    pass


class WalkingEnemy(Enemy):
    pass
