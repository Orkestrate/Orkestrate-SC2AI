import random

import sc2
from sc2 import Race, Difficulty, game_info
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId


class WarpGateBot(sc2.BotAI):

    # async def intel(self):
    #
    #     game_data = np.zeros((self.game_info.map_ .map_si [1], self.game_info.map_center[0], 3), np.float64)
    #     for nexus in self.units(UnitTypeId.NEXUS):
    #         next_pos = nexus.position
    #         cv2.circle(game_data, (int(next_pos[0]), int(next_pos[1])), 10, (0, 255, 0), -1)
    #     flipped = cv2.flip(game_data)
    #     resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)
    #     cv2.imshow('Intel', resized)
    #     cv2.waitKey(1)


    def __init__(self):
        self.warpgate_started = False
        self.proxy_built = False

    def select_target(self, state):
        return self.enemy_start_locations[0]

    async def warp_new_units(self, proxy):
        for warpgate in self.units(UnitTypeId.GATEWAY).ready.noqueue:
            # abilities = await self.get_available_abilities(warpgate)
            # all the units have the same cooldown anyway so let's just look at ZEALOT
            # if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
            #     pos = proxy.position.to2.random_on_distance(4)
            #     placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
            #     if placement is None:
            #         return ActionResult.CantFindPlacementLocation
                    # print("can't place")
                    # return
            if self.can_afford(UnitTypeId.STALKER):
                await self.do(warpgate.train(UnitTypeId.STALKER))


    async def on_step(self, iteration):
        await self.distribute_workers()
        # await self.intel()

        if not self.units(UnitTypeId.NEXUS).ready.exists:
            for worker in self.workers:
                await self.do(worker.attack(self.enemy_start_locations[0]))
            return
        else:
            nexus = self.units(UnitTypeId.NEXUS).ready.random

        if self.supply_left < 3 and not self.already_pending(UnitTypeId.PYLON):
            if self.can_afford(UnitTypeId.PYLON):
                print('self.supply_left ' + str(self.supply_left))
                await self.build(UnitTypeId.PYLON, near=nexus)
            return

        if self.workers.amount < self.units(UnitTypeId.NEXUS).amount*22 and nexus.noqueue:
            if self.can_afford(UnitTypeId.PROBE):
                await self.do(nexus.train(UnitTypeId.PROBE))

        # elif self.units(UnitTypeId.PYLON).amount < 5 and not self.already_pending(UnitTypeId.PYLON):
        #     if self.can_afford(UnitTypeId.PYLON):
        #         await self.build(UnitTypeId.PYLON, near=nexus.position.towards(self.game_info.map_center, 5))


        if self.units(UnitTypeId.PYLON).ready.exists:
            proxy = self.units(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
            pylon = self.units(UnitTypeId.PYLON).ready.random
            if self.units(UnitTypeId.GATEWAY).ready.exists:
                if not self.units(UnitTypeId.CYBERNETICSCORE).exists:
                    if self.can_afford(UnitTypeId.CYBERNETICSCORE) and not self.already_pending(UnitTypeId.CYBERNETICSCORE):
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
            # if self.can_afford(UnitTypeId.GATEWAY) and self.units(UnitTypeId.WARPGATE).amount < 4 and self.units(UnitTypeId.GATEWAY).amount < 4:
            if self.can_afford(UnitTypeId.GATEWAY) and self.units(
                        UnitTypeId.GATEWAY).amount < 7:
                    await self.build(UnitTypeId.GATEWAY, near=pylon)

        for nexus in self.units(UnitTypeId.NEXUS).ready:
            vgs = self.state.vespene_geyser.closer_than(20.0, nexus)
            for vg in vgs:
                if not self.can_afford(UnitTypeId.ASSIMILATOR):
                    break

                worker = self.select_build_worker(vg.position)
                if worker is None:
                    break

                if not self.units(UnitTypeId.ASSIMILATOR).closer_than(1.0, vg).exists:
                    await self.do(worker.build(UnitTypeId.ASSIMILATOR, vg))

        # if self.units(UnitTypeId.CYBERNETICSCORE).ready.exists and self.can_afford(UnitTypeId.RESEARCH_WARPGATE) and not self.warpgate_started:
        #     ccore = self.units(UnitTypeId.CYBERNETICSCORE).ready.first
        #     await self.do(ccore(UnitTypeId.RESEARCH_WARPGATE))
        #     self.warpgate_started = True

        # for gateway in self.units(UnitTypeId.GATEWAY).ready:
        #     abilities = await self.get_available_abilities(gateway)
        #     if AbilityId.MORPH_WARPGATE in abilities and self.can_afford(AbilityId.MORPH_WARPGATE):
        #         await self.do(gateway(UnitTypeId.MORPH_WARPGATE))

        # if self.proxy_built:
        # await self.warp_new_units(proxy)

        for warpgate in self.units(UnitTypeId.GATEWAY).ready.noqueue:
            if self.can_afford(UnitTypeId.STALKER):
                await self.do(warpgate.train(UnitTypeId.STALKER))


        if self.units(UnitTypeId.STALKER).amount > 8:
            for vr in self.units(UnitTypeId.STALKER).ready.idle:
                await self.do(vr.attack(self.select_target(self.state)))



        # if self.units(UnitTypeId.CYBERNETICSCORE).amount >= 1 and not self.proxy_built and self.can_afford(UnitTypeId.PYLON):
        #     p = self.game_info.map_center.towards(self.enemy_start_locations[0], 20)
        #     await self.build(UnitTypeId.PYLON, near=p)
        #     self.proxy_built = True

        # if not self.units(UnitTypeId.CYBERNETICSCORE).ready.exists:
        #     if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
        #         abilities = await self.get_available_abilities(nexus)
        #         if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
        #             await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
        # else:
        #     ccore = self.units(UnitTypeId.CYBERNETICSCORE).ready.first
        #     if not ccore.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
        #         abilities = await self.get_available_abilities(nexus)
        #         if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
        #             await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, ccore))


def main():
    sc2.run_game(sc2.maps.get("(2)CatalystLE"), [
        Bot(Race.Protoss, WarpGateBot()),
        Computer(Race.Protoss, Difficulty.Hard)
    ], realtime=True)

if __name__ == '__main__':
    main()
