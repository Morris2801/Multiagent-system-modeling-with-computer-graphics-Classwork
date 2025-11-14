from random_agents.agent import ChargingStation, RandomAgent, ObstacleAgent, DirtyCell
from random_agents.model import RandomModel

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
)

from mesa.visualization.components import AgentPortrayalStyle
import solara

def random_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o",
    )

    if isinstance(agent, RandomAgent):
        portrayal.color = "black"
        portrayal.size=60
        portrayal.zorder=1
    elif isinstance(agent, ObstacleAgent):
        portrayal.color = "gray"
        portrayal.marker = "s"
        portrayal.size = 100
    elif isinstance(agent, ChargingStation):
        portrayal.color = "green"
        portrayal.marker = "D"
        portrayal.size = 80
    elif isinstance(agent, DirtyCell):
        if agent.is_clean:
            portrayal.color = "none"
        else:
            portrayal.color = "brown"
        portrayal.marker = "s"
        portrayal.size = 100
        portrayal.border_color = "black"

    return portrayal

def post_process(ax):
    ax.set_aspect("equal")

model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "max_steps": Slider("Maximum steps", 1000, 1, 10000),
    "num_agents": Slider("Number of agents", 10, 1, 50),
    "dirty_cells": Slider("Number of dirty cells", 50, 0, 100),
    "num_obstacles": Slider("Number of obstacles", 60,0,100),
    "width": Slider("Grid width", 28, 1, 50),
    "height": Slider("Grid height", 28, 1, 50),
}

# Create the model using the initial parameters from the settings
model = RandomModel(
    num_agents=model_params["num_agents"].value,
    width=model_params["width"].value,
    height=model_params["height"].value,
    dirty_cells=model_params["dirty_cells"].value,
    seed=model_params["seed"]["value"]
)

space_component = make_space_component(
        random_portrayal,
        draw_grid = False,
        post_process=post_process
)

page = SolaraViz(
    model,
    components=[space_component],
    model_params=model_params,
    name="Random Model",
)
