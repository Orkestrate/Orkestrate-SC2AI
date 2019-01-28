from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
import random


class ProtossAgent(base_agent.BaseAgent):

    def select_one_probe(self, obs):
        probes = self.get_units_by_type(obs, units.Protoss.Probe)
        if len(probes) > 0:
            probe = probes[0]

            return actions.FUNCTIONS.select_point("select", (probe.x,
                                                             probe.y))

    pass
