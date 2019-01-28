from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
import random


class ProtossAgent(base_agent.BaseAgent):
    def __init__(self):
        super(ProtossAgent, self).__init__()

        self.attack_coordinates = None

    def unit_type_is_selected(self, obs, unit_type):
        if (len(obs.observation.single_select) > 0 and
                obs.observation.single_select[0].unit_type == unit_type):
            return True

        if (len(obs.observation.multi_select) > 0 and
                obs.observation.multi_select[0].unit_type == unit_type):
            return True

        return False

    def get_units_by_type(self, obs, unit_type):
        return [unit for unit in obs.observation.feature_units
                if unit.unit_type == unit_type]

    def can_do(self, obs, action):
        return action in obs.observation.available_actions

    def step(self, obs):
        super(ProtossAgent, self).step(obs)

        pylons = self.get_units_by_type(obs, units.Protoss.Pylon)
        if len(pylons) < 1:
            if self.unit_type_is_selected(obs, units.Protoss.Probe):
                if self.can_do(obs, actions.FUNCTIONS.Build_Pylon_screen.id):
                    x = random.randint(0, 83)
                    y = random.randint(0, 83)

                    return actions.FUNCTIONS.Build_Pylon_screen("now", (x, y))

            probes = self.get_units_by_type(obs, units.Protoss.Probe)



            if len(probes) > 0:
                probe = random.choice(probes)

                return actions.FUNCTIONS.select_point("select_all_type", (probe.x,
                                                                          probe.y))






        gateways = self.get_units_by_type(obs, units.Protoss.Gateway)
        if len(gateways) < 1:
            if self.unit_type_is_selected(obs, units.Protoss.Probe):
                if self.can_do(obs, actions.FUNCTIONS.Build_Gateway_screen.id):
                    x = random.randint(0, 83)
                    y = random.randint(0, 83)

                    # x = 60
                    # y = 54


                    return actions.FUNCTIONS.Build_Gateway_screen("now", (x, y))

        if self.can_do(obs, actions.FUNCTIONS.Train_Zealot_quick.id):
            return actions.FUNCTIONS.Train_Zealot_quick("now")
        elif len(gateways) > 0:
            gateway = gateways[0]
            print('gateway x is ' + str(gateway.x))
            print('gateway y is ' + str(gateway.y))

            return actions.FUNCTIONS.select_point("select_all_type", (gateway.x, gateway.y))


        # if self.unit_type_is_selected(obs, units.Protoss.Gateway):
        #     if self.can_do(obs, actions.FUNCTIONS.Train_Zealot_quick.id):
        #         return actions.FUNCTIONS.Train_Zealot_quick("now")

        zealots = self.get_units_by_type(obs, units.Protoss.Zealot)

        if len(zealots) >= 5:
            if self.unit_type_is_selected(obs, units.Protoss.Zealot):
                if self.can_do(obs, actions.FUNCTIONS.Attack_minimap.id):
                    return actions.FUNCTIONS.Attack_minimap("now",
                                                            self.attack_coordinates)

            if self.can_do(obs, actions.FUNCTIONS.select_army.id):
                return actions.FUNCTIONS.select_army("select")


        # larvae = self.get_units_by_type(obs, units.Protoss.Probe)
        # if len(larvae) > 0:
        #     larva = random.choice(larvae)
        #
        #     return actions.FUNCTIONS.select_point("select_all_type", (larva.x,
        #                                                               larva.y))

        return actions.FUNCTIONS.no_op()


def main(unused_argv):
    agent = ProtossAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                    map_name="16-BitLE",
                    players=[sc2_env.Agent(sc2_env.Race.protoss),
                             sc2_env.Bot(sc2_env.Race.random,
                                         sc2_env.Difficulty.very_easy)],
                    agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=84, minimap=64),
                        use_feature_units=True),
                    step_mul=16,
                    game_steps_per_episode=0,
                    visualize=True) as env:

                agent.setup(env.observation_spec(), env.action_spec())

                timesteps = env.reset()
                agent.reset()

                while True:
                    step_actions = [agent.step(timesteps[0])]
                    if timesteps[0].last():
                        break
                    timesteps = env.step(step_actions)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app.run(main)
