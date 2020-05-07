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


class Player(GameObject):
    pass


class Enemy(GameObject):
    pass


class WalkingEnemy(Enemy):
    pass
