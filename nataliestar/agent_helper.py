from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
import random





def select_one_probe(pagent, obs):
    probes = pagent.get_units_by_type(obs, units.Protoss.Probe)
    if len(probes) > 0:
        probe = probes[0]

    return actions.FUNCTIONS.select_point("select", (probe.x,
                                                     probe.y))


def build_pylon(obs, x, y):
    player_y, player_x = (obs.observation.feature_minimap.player_relative ==
                          features.PlayerRelative.SELF).nonzero()
    xmean = player_x.mean()
    ymean = player_y.mean()

    if xmean <= 40 and ymean >= 20:
        x = random.randint(70, 83)
        y = random.randint(0, 20)
    else:
        x = random.randint(0, 20)
        y = random.randint(70, 83)

        # x = random.randint(70, 83)
        # y = random.randint(0, 20)

        # x = 50
        # y = 50
        cameraPosX = x
        cameraPosY = y

    return actions.FUNCTIONS.Build_Pylon_screen("now", (77, 77))


pass
