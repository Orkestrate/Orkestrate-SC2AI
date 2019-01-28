import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.player import Human
from sc2.ids.unit_typeid import UnitTypeId

class ProxyRaxBot(sc2.BotAI):
    def select_target(self):
        target = self.known_enemy_structures
        if target.exists:
            return target.random.position

        target = self.known_enemy_units
        if target.exists:
            return target.random.position

        if min([u.position.distance_to(self.enemy_start_locations[0]) for u in self.units]) < 5:
            return self.enemy_start_locations[0].position

        return self.state.mineral_field.random.position

    async def on_step(self, iteration):
        cc = (self.units(UnitTypeId.COMMANDCENTER) | self.units(UnitTypeId.ORBITALCOMMAND))
        if not cc.exists:
            target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
            for unit in self.workers | self.units(UnitTypeId.BATTLECRUISER):
                await self.do(unit.attack(target))
            return
        else:
            cc = cc.first


        if iteration % 50 == 0 and self.units(UnitTypeId.BATTLECRUISER).amount > 2:
            target = self.select_target()
            forces = self.units(UnitTypeId.BATTLECRUISER)
            if (iteration//50) % 10 == 0:
                for unit in forces:
                    await self.do(unit.attack(target))
            else:
                for unit in forces.idle:
                    await self.do(unit.attack(target))

        if self.can_afford(UnitTypeId.SCV) and self.workers.amount < 22 and cc.noqueue:
            await self.do(cc.train(UnitTypeId.SCV))

        if self.units(UnitTypeId.FUSIONCORE).exists and self.can_afford(UnitTypeId.BATTLECRUISER):
            for sp in self.units(UnitTypeId.STARPORT):
                if sp.has_add_on and sp.noqueue:
                    if not self.can_afford(UnitTypeId.BATTLECRUISER):
                        break
                    await self.do(sp.train(UnitTypeId.BATTLECRUISER))

        elif self.supply_left < 3:
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 8))

        if self.units(UnitTypeId.SUPPLYDEPOT).exists:
            if not self.units(UnitTypeId.BARRACKS).exists:
                if self.can_afford(UnitTypeId.BARRACKS):
                    await self.build(UnitTypeId.BARRACKS, near=cc.position.towards(self.game_info.map_center, 8))

            elif self.units(UnitTypeId.BARRACKS).exists and self.units(UnitTypeId.REFINERY).amount < 2:
                if self.can_afford(UnitTypeId.REFINERY):
                    vgs = self.state.vespene_geyser.closer_than(20.0, cc)
                    for vg in vgs:
                        if self.units(UnitTypeId.REFINERY).closer_than(1.0, vg).exists:
                            break

                        worker = self.select_build_worker(vg.position)
                        if worker is None:
                            break

                        await self.do(worker.build(UnitTypeId.REFINERY, vg))
                        break

            if self.units(UnitTypeId.BARRACKS).ready.exists:
                f = self.units(UnitTypeId.FACTORY)
                if not f.exists:
                    if self.can_afford(UnitTypeId.FACTORY):
                        await self.build(UnitTypeId.FACTORY, near=cc.position.towards(self.game_info.map_center, 8))
                elif f.ready.exists and self.units(UnitTypeId.STARPORT).amount < 2:
                    if self.can_afford(UnitTypeId.STARPORT):
                        await self.build(UnitTypeId.STARPORT, near=cc.position.towards(self.game_info.map_center, 30).random_on_distance(8))

        for sp in self.units(UnitTypeId.STARPORT).ready:
            if sp.add_on_tag == 0:
                await self.do(sp.build(UnitTypeId.STARPORTTECHLAB))

        if self.units(UnitTypeId.STARPORT).ready.exists:
            if self.can_afford(UnitTypeId.FUSIONCORE) and not self.units(UnitTypeId.FUSIONCORE).exists:
                await self.build(UnitTypeId.FUSIONCORE, near=cc.position.towards(self.game_info.map_center, 8))

        for a in self.units(UnitTypeId.REFINERY):
            if a.assigned_harvesters < a.ideal_harvesters:
                w = self.workers.closer_than(20, a)
                if w.exists:
                    await self.do(w.random.gather(a))

        for scv in self.units(UnitTypeId.SCV).idle:
            await self.do(scv.gather(self.state.mineral_field.closest_to(cc)))

def main():
    sc2.run_game(sc2.maps.get("(2)CatalystLE"), [
        # Human(Race.Terran),
        Bot(Race.Terran, ProxyRaxBot()),
        Computer(Race.Zerg, Difficulty.Hard)
    ], realtime=False)

if __name__ == '__main__':
    main()
