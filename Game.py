import random

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

from GameObject import *


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()

        properties = WindowProperties()
        properties.setSize(1000, 750)
        self.win.requestProperties(properties)

        ambient_light = AmbientLight("ambient light")
        ambient_light.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.ambientLightNodePath = self.render.attachNewNode(ambient_light)
        self.render.setLight(self.ambientLightNodePath)

        main_light = DirectionalLight("main light")
        self.mainLightNodePath = self.render.attachNewNode(main_light)
        self.mainLightNodePath.setHpr(45, -45, 0)
        self.render.setLight(self.mainLightNodePath)

        self.render.setShaderAuto()

        self.environment = self.loader.loadModel("Models/Environment/environment")
        self.environment.reparentTo(self.render)

        # Top down view
        self.camera.setPos(0, 0, 32)
        self.camera.setP(-90)

        self.keyMap = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "shoot": False
        }

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

        self.pusher = CollisionHandlerPusher()
        self.cTrav = CollisionTraverser()

        self.pusher.setHorizontal(True)

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

        self.player = None

        self.enemies = []
        self.trapEnemies = []

        self.deadEnemies = []

        self.spawnPoints = []
        num_points_per_wall = 5
        for i in range(num_points_per_wall):
            coord = 7.0 / num_points_per_wall + 0.5
            self.spawnPoints.append(Vec3(-7.0, coord, 0))
            self.spawnPoints.append(Vec3(7.0, coord, 0))
            self.spawnPoints.append(Vec3(coord, -7.0, 0))
            self.spawnPoints.append(Vec3(coord, 7.0, 0))

        self.initialSpawnInterval = 1.0
        self.minimumSpawnInterval = 0.2
        self.spawnInterval = self.initialSpawnInterval
        self.spawnTimer = self.spawnInterval
        self.maxEnemies = 2
        self.maximumMaxEnemies = 20

        self.numTrapsPerSide = 2

        self.difficultyInterval = 5.0
        self.difficultyTimer = self.difficultyInterval

        self.start_game()

        self.updateTask = self.taskMgr.add(self.update, "update")

        self.pusher.add_in_pattern("%fn-into-%in")

        self.accept("trapEnemy-into-wall", self.stop_trap)
        self.accept("trapEnemy-into-trapEnemy", self.stop_trap)
        self.accept("trapEnemy-into-player", self.trap_hits_something)
        self.accept("trapEnemy-into-walkingEnemy", self.trap_hits_something)

        self.exitFunc = self.cleanup

    def start_game(self):
        self.cleanup()

        self.player = Player()

        self.maxEnemies = 2
        self.spawnInterval = self.initialSpawnInterval

        self.difficultyTimer = self.difficultyInterval

        side_trap_slots = [
            [],
            [],
            [],
            []
        ]
        trap_slot_distance = 0.4
        slot_pos = -8 + trap_slot_distance
        while slot_pos < 8:
            if abs(slot_pos) > 1.0:
                side_trap_slots[0].append(slot_pos)
                side_trap_slots[1].append(slot_pos)
                side_trap_slots[2].append(slot_pos)
                side_trap_slots[3].append(slot_pos)
            slot_pos += trap_slot_distance

        for i in range(self.numTrapsPerSide):
            slot = side_trap_slots[0].pop(random.randint(0, len(side_trap_slots[0]) - 1))
            trap = TrapEnemy(Vec3(slot, 7.0, 0))
            self.trapEnemies.append(trap)

            slot = side_trap_slots[1].pop(random.randint(0, len(side_trap_slots[1]) - 1))
            trap = TrapEnemy(Vec3(slot, -7.0, 0))
            self.trapEnemies.append(trap)

            slot = side_trap_slots[2].pop(random.randint(0, len(side_trap_slots[2]) - 1))
            trap = TrapEnemy(Vec3(7.0, slot, 0))
            trap.moveInX = True
            self.trapEnemies.append(trap)

            slot = side_trap_slots[3].pop(random.randint(0, len(side_trap_slots[3]) - 1))
            trap = TrapEnemy(Vec3(-7.0, slot, 0))
            trap.moveInX = True
            self.trapEnemies.append(trap)

    def cleanup(self):
        for enemy in self.enemies:
            enemy.cleanup()
        self.enemies = []

        for enemy in self.deadEnemies:
            enemy.cleanup()
        self.deadEnemies = []

        for trap in self.trapEnemies:
            trap.cleanup()
        self.trapEnemies = []

        if self.player is not None:
            self.player.cleanup()
            self.player = None

    def quit(self):
        self.cleanup()
        base.userExit()

    def spawn_enemy(self):
        if len(self.enemies) < self.maxEnemies:
            spawn_point = random.choice(self.spawnPoints)
            new_enemy = WalkingEnemy(spawn_point)
            self.enemies.append(new_enemy)

    def stop_trap(self, entry):
        collider = entry.getFromNodePath()
        if collider.hasPythonTag("owner"):
            trap = collider.getPythonTag("owner")
            trap.moveDirection = 0
            trap.ignorePlayer = False

    def trap_hits_something(self, entry):
        collider = entry.getFromNodePath()
        if collider.hasPythonTag("owner"):
            trap = collider.getPythonTag("owner")

            if trap.moveDirection == 0:
                return

            collider = entry.getIntoNodePath()
            if collider.hasPythonTag("owner"):
                obj = collider.getPythonTag("owner")
                if isinstance(obj, Player):
                    if not trap.ignorePlayer:
                        obj.alter_health(-1)
                        trap.ignorePlayer = True
                else:
                    obj.alter_health(-10)

    def update_key_map(self, control_name, control_state):
        self.keyMap[control_name] = control_state

    def update(self, task):
        dt = globalClock.getDt()

        if self.player is not None:
            if self.player.health > 0:
                self.player.update(self.keyMap, dt)

                # Wait to spawn an enemy...
                self.spawnTimer -= dt
                if self.spawnTimer <= 0:
                    # Spawn one!
                    self.spawnTimer = self.spawnInterval
                    self.spawn_enemy()

                # Update all enemies and traps
                [enemy.update(self.player, dt) for enemy in self.enemies]
                [trap.update(self.player, dt) for trap in self.trapEnemies]

                # Find the enemies that have just
                # died, if any
                newly_dead_enemies = [enemy for enemy in self.enemies if enemy.health <= 0]
                # And re-build the enemy-list to exclude
                # those that have just died.
                self.enemies = [enemy for enemy in self.enemies if enemy.health > 0]

                # Newly-dead enemies should have no collider,
                # and should play their "die" animation.
                # In addition, increase the player's score.
                for enemy in newly_dead_enemies:
                    enemy.collider.removeNode()
                    enemy.actor.play("die")
                    self.player.score += enemy.scoreValue
                if len(newly_dead_enemies) > 0:
                    self.player.update_score()

                self.deadEnemies += newly_dead_enemies

                # Check our "dead enemies" to see
                # whether they're still animating their
                # "die" animation. In not, clean them up,
                # and drop them from the "dead enemies" list.
                enemies_animating_deaths = []
                for enemy in self.deadEnemies:
                    death_anim_control = enemy.actor.getAnimControl("die")
                    if death_anim_control is None or not death_anim_control.isPlaying():
                        enemy.cleanup()
                    else:
                        enemies_animating_deaths.append(enemy)
                self.deadEnemies = enemies_animating_deaths

                # Make the game more difficult over time!
                self.difficultyTimer -= dt
                if self.difficultyTimer <= 0:
                    self.difficultyTimer = self.difficultyInterval
                    if self.maxEnemies < self.maximumMaxEnemies:
                        self.maxEnemies += 1
                    if self.spawnInterval > self.minimumSpawnInterval:
                        self.spawnInterval -= 0.1

        return task.cont


game = Game()
game.run()
