from panda3d.core import Vec3, Vec2
from direct.actor.Actor import Actor
from panda3d.core import BitMask32
from panda3d.core import CollisionRay, CollisionHandlerQueue
from panda3d.core import CollisionSegment
from panda3d.core import CollisionSphere, CollisionNode
from panda3d.core import Plane, Point3
import random
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

        mask = BitMask32()
        mask.setBit(1)

        self.collider.node().setIntoCollideMask(mask)

        mask = BitMask32()
        mask.setBit(1)

        self.collider.node().setFromCollideMask(mask)

        self.ray = CollisionRay(0, 0, 0, 0, 1, 0)
        ray_node = CollisionNode("playerRay")
        ray_node.addSolid(self.ray)

        self.rayNodePath = render.attachNewNode(ray_node)
        self.rayQueue = CollisionHandlerQueue()

        base.cTrav.addCollider(self.rayNodePath, self.rayQueue)

        mask = BitMask32()
        mask.setBit(2)
        ray_node.setFromCollideMask(mask)

        mask = BitMask32()
        ray_node.setIntoCollideMask(mask)

        self.damagePerSecond = -5.0

        self.beamModel = loader.loadModel("Models/BambooLaser/bambooLaser")
        self.beamModel.reparentTo(self.actor)
        self.beamModel.setZ(1.5)
        self.beamModel.setLightOff()
        self.beamModel.hide()

        self.lastMousePos = Vec2(0, 0)

        self.groundPlane = Plane(Vec3(0, 0, 1), Vec3(0, 0, 0))

        self.yVector = Vec2(0, 1)

    def update(self, keys, dt):
        GameObject.update(self, dt)

        self.walking = False

        mouse_watcher = base.mouseWatcherNode
        if mouse_watcher.hasMouse():
            mouse_pos = mouse_watcher.getMouse()
        else:
            mouse_pos = self.lastMousePos

        mouse_pos_3d = Point3()
        near_point = Point3()
        far_point = Point3()

        base.camLens.extrude(mouse_pos, near_point, far_point)

        self.groundPlane.intersectsLine(mouse_pos_3d,
                                        render.getRelativePoint(base.camera, near_point),
                                        render.getRelativePoint(base.camera, far_point))

        firing_vector = Vec3(mouse_pos_3d - self.actor.getPos())
        firing_vector_2d = firing_vector.getXy()
        firing_vector_2d.normalize()
        firing_vector.normalize()

        heading = self.yVector.signedAngleDeg(firing_vector_2d)

        self.actor.setH(heading)

        if firing_vector.length() > 0.001:
            self.ray.setOrigin(self.actor.getPos())
            self.ray.setDirection(firing_vector)

        self.lastMousePos = mouse_pos

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
        if keys["shoot"]:
            if self.rayQueue.getNumEntries() > 0:
                self.rayQueue.sortEntries()
                ray_hit = self.rayQueue.getEntry(0)
                hit_pos = ray_hit.getSurfacePoint(render)

                hit_node_path = ray_hit.getIntoNodePath()
                if hit_node_path.hasPythonTag("owner"):
                    hit_object = hit_node_path.getPythonTag("owner")
                    if not isinstance(hit_object, TrapEnemy):
                        hit_object.alter_health(self.damagePerSecond * dt)

                beam_length = (hit_pos - self.actor.getPos()).length()
                self.beamModel.setSy(beam_length)

                self.beamModel.show()
        else:
            self.beamModel.hide()

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

    def cleanup(self):
        base.cTrav.removeCollider(self.rayNodePath)

        GameObject.cleanup(self)


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

        mask = BitMask32()
        mask.setBit(2)

        self.collider.node().setIntoCollideMask(mask)

        self.attackSegment = CollisionSegment(0, 0, 0, 1, 0, 0)
        segment_node = CollisionNode("enemyAttackSegment")
        segment_node.addSolid(self.attackSegment)

        mask = BitMask32()
        mask.setBit(1)
        segment_node.setFromCollideMask(mask)

        mask = BitMask32()
        segment_node.setIntoCollideMask(mask)

        self.attackSegmentNodePath = render.attachNewNode(segment_node)
        self.segmentQueue = CollisionHandlerQueue()

        base.cTrav.addCollider(self.attackSegmentNodePath, self.segmentQueue)

        self.attackDamage = -1

        self.attackDelay = 0.3
        self.attackDelayTimer = 0
        self.attackWaitTimer = 0

    def run_logic(self, player, dt):
        vector_to_player = player.actor.getPos() - self.actor.getPos()

        vector_to_player_2d = vector_to_player.getXy()
        distance_to_player = vector_to_player_2d.length()

        vector_to_player_2d.normalize()

        heading = self.yVector.signedAngleDeg(vector_to_player_2d)

        if distance_to_player > self.attackDistance * 0.9:
            attack_control = self.actor.getAnimControl("attack")
            if not attack_control.isPlaying():
                self.walking = True
                vector_to_player.setZ(0)
                vector_to_player.normalize()
                self.velocity += vector_to_player * self.acceleration * dt
                self.attackWaitTimer = 0.2
                self.attackDelayTimer = 0
        else:
            self.walking = False
            self.velocity.set(0, 0, 0)

            if self.attackDelayTimer > 0:
                self.attackDelayTimer -= dt
                if self.attackDelayTimer <= 0:
                    if self.segmentQueue.getNumEntries() > 0:
                        self.segmentQueue.sortEntries()
                        segment_hit = self.segmentQueue.getEntry(0)

                        hit_node_path = segment_hit.getIntoNodePath()
                        if hit_node_path.hasPythonTag("owner"):
                            hit_object = hit_node_path.getPythonTag("owner")
                            hit_object.alter_health(self.attackDamage)
                            self.attackWaitTimer = 1.0
            elif self.attackWaitTimer > 0:
                self.attackWaitTimer -= dt
                if self.attackWaitTimer <= 0:
                    self.attackWaitTimer = random.uniform(0.5, 0.7)
                    self.attackDelayTimer = self.attackDelay
                    self.actor.play("attack")

        self.actor.setH(heading)

        self.attackSegment.setPointA(self.actor.getPos())
        self.attackSegment.setPointB(self.actor.getPos() + self.actor.getQuat().getForward() * self.attackDistance)

    def cleanup(self):
        base.cTrav.removeCollider(self.attackSegmentNodePath)
        self.attackSegmentNodePath.removeNode()

        GameObject.cleanup()


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

        mask = BitMask32()
        mask.setBit(2)
        mask.setBit(1)

        self.collider.node().setIntoCollideMask(mask)

        mask = BitMask32()
        mask.setBit(2)
        mask.setBit(1)

        self.collider.node().setFromCollideMask(mask)

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
