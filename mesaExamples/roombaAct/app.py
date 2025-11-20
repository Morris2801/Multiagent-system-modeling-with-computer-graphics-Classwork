from random_agents.agent import ChargingStation, RandomAgent, ObstacleAgent, DirtyCell
from random_agents.model import RandomModel

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
    make_plot_component,
)

from mesa.visualization.components import AgentPortrayalStyle

AGENT_COLORS = {
    "exploring": "#000000",
    "returning": "#FF8C00",
    "charging": "#FFD700",
    "dead": "#FF0000",
}

CELL_COLORS = {
    "clean": "none",
    "dirty": "#8B4513",
    "obstacle": "#808080",
    "charging_station": "#00AA00",
}

CHART_COLORS = {
    "exploring": "black",
    "returning": "darkorange",
    "charging": "gold",
    "dead": "red",
    "clean": "lightgray",
    "dirty": "saddlebrown",
    "movements": "blue",
    "battery": "green",
}

def random_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o",
    )

    if isinstance(agent, RandomAgent):
        portrayal.color = AGENT_COLORS.get(agent.status, "#000000")
        portrayal.size = 60
    elif isinstance(agent, ObstacleAgent):
        portrayal.color = CELL_COLORS["obstacle"]
        portrayal.marker = "s"
        portrayal.size = 100
    elif isinstance(agent, ChargingStation):
        portrayal.color = CELL_COLORS["charging_station"]
        portrayal.marker = "D"
        portrayal.size = 80
    elif isinstance(agent, DirtyCell):
        portrayal.color = CELL_COLORS["clean"] if agent.is_clean else CELL_COLORS["dirty"]
        portrayal.size = 100
        portrayal.marker = "^"

    return portrayal

def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))

model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "simulation_mode": {
        "type": "Select",
        "value": "single",
        "values": ["single", "multiple"],
        "label": "Simulation Mode",
    },
    "max_steps": Slider("Maximum steps", 2500, 100, 10000, step=100),
    "num_agents": Slider("Number of agents [Sim 2]", 5, 1, 20, step=1),
    "dirty_percentage": Slider("Dirty cells (%)", 50, 0, 100, step=5),
    "obstacle_percentage": Slider("Obstacles (%)", 10, 0, 50, step=5),
    "width": Slider("Grid width", 28, 10, 50, step=2),
    "height": Slider("Grid height", 28, 10, 50, step=2),
}

model = RandomModel(
    simulation_mode=model_params["simulation_mode"]["value"],
    num_agents=model_params["num_agents"].value,
    width=model_params["width"].value,
    height=model_params["height"].value,
    dirty_percentage=model_params["dirty_percentage"].value,    
    obstacle_percentage=model_params["obstacle_percentage"].value,
    max_steps=model_params["max_steps"].value,
    seed=model_params["seed"]["value"]
)

space_component = make_space_component(
    random_portrayal,
    draw_grid=False,
    post_process=post_process_space
)

cleaning_chart = make_plot_component(
    {
        "Clean Percentage": CHART_COLORS["clean"],
    },
    post_process=post_process_lines,
)

agent_status_chart = make_plot_component(
    {
        "Exploring Agents": CHART_COLORS["exploring"],
        "Returning Agents": CHART_COLORS["returning"],
        "Charging Agents": CHART_COLORS["charging"],
        "Dead Agents": CHART_COLORS["dead"]
    },
    post_process=post_process_lines,
)

movements_chart = make_plot_component(
    {"Total Movements": CHART_COLORS["movements"]},
    post_process=post_process_lines,
)

battery_chart = make_plot_component(
    {
        "Average Battery Level": CHART_COLORS["battery"],
    },
    post_process=post_process_lines,
)

page = SolaraViz(
    model,
    components=[space_component, cleaning_chart, agent_status_chart, battery_chart, movements_chart],
    model_params=model_params,
    name="Roomba Cleaning Simulation",
)