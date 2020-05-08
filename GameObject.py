from panda3d.core import Vec3, Vec2
from direct.actor.Actor import Actor
from panda3d.core import CollisionSphere, CollisionNode
import math

FRICTION = 150.0


class GameObject:
    def __init__(self, pos, model_name, model_anims, max_health, max_speed, collider_name):
        self.actor = Actor(model_name, model_anims)
        self.actor.reparentTo(render)
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
    def __init__(self, pos, model_name, model_anims, max_health, max_speed, collider_name):
        GameObject.__init__(self, pos, model_name, model_anims, max_health, max_speed, collider_name)
        self.scoreValue = 1

    def update(self, player, dt):
        GameObject.update(self, dt)

        self.run_logic(player, dt)

        if self.walking:
            walking_control = self.actor.getAnimControl("walk")
            if not walking_control.isPlaying():
                self.actor.loop("walk")
        else:
            spawn_control = self.actor.getAnimControl("spawn")
            if spawn_control is None or not spawn_control.isPlaying():
                attack_control = self.actor.getAnimControl("attack")
                if attack_control is None or not attack_control.isPlaying():
                    stand_control = self.actor.getAnimControl("stand")
                    if not stand_control.isPlaying():
                        self.actor.loop("stand")

    def run_logic(self, player, dt):
        pass


class WalkingEnemy(Enemy):
    def __init__(self, pos):
        Enemy.__init__(self, pos,
                       "Models/SimpleEnemy/simpleEnemy",
                       {
                           "stand": "Models/SimpleEnemy/simpleEnemy-stand",
                           "walk": "Models/SimpleEnemy/simpleEnemy-walk",
                           "attack": "Models/SimpleEnemy/simpleEnemy-attack",
                           "die": "Models/SimpleEnemy/simpleEnemy-die",
                           "spawn": "Models/SimpleEnemy/simpleEnemy-spawn"
                       },
                       3.0,
                       7.0,
                       "walkingEnemy")

        self.attackDistance = 0.75

        self.acceleration = 100.0

        self.yVector = Vec2(0, 1)

    def run_logic(self, player, dt):
        vector_to_player = player.actor.getPos() - self.actor.getPos()

        vector_to_player_2d = vector_to_player.getXy()
        distance_to_player = vector_to_player_2d.length()

        vector_to_player_2d.normalize()

        heading = self.yVector.signedAngleDeg(vector_to_player_2d)

        if distance_to_player > self.attackDistance * 0.9:
            self.walking = True
            vector_to_player.setZ(0)
            vector_to_player.normalize()
            self.velocity += vector_to_player * self.acceleration * dt
        else:
            self.walking = False
            self.velocity.set(0, 0, 0)

        self.actor.setH(heading)


class TrapEnemy(Enemy):
    def __init__(self, pos):
        Enemy.__init__(self, pos,
                       "Models/SlidingTrap/trap",
                       {
                           "stand": "Models/SlidingTrap/trap-stand",
                           "walk": "Models/SlidingTrap/trap-walk"
                       },
                       100.0,
                       10.0,
                       "trapEnemy")

        base.pusher.addCollider(self.collider, self.actor)
        base.cTrav.addCollider(self.collider, base.pusher)

        self.moveInX = False

        self.moveDirection = 0

        self.ignorePlayer = False


def run_logic(self, player, dt):
    if self.moveDirection != 0:
        self.walking = True
        if self.moveInX:
            self.velocity.addX(self.moveDirection * self.acceleration * dt)
        else:
            self.velocity.addY(self.moveDirection * self.acceleration * dt)
    else:
        self.walking = False
        diff = player.actor.getPos() - self.actor.getPos()
        if self.moveInX:
            detector = diff.y
            movement = diff.x
        else:
            detector = diff.x
            movement = diff.y

        if abs(detector) < 0.5:
            self.moveDirection = math.copysign(1, movement)


def alter_health(self, d_health):
    pass
