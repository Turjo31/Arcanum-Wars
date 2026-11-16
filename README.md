# Arcanum Wars

A 2D fantasy game built for the AI lab (CSE 3210). Explore a village and a forest, challenge rivals,
and watch AI agents battle each other. The game is a testbed for **Minimax, Alpha-Beta pruning, MCTS and A\***.

## Run

```
pip install -r requirements.txt
python main.py
```

Run everything from the project root folder. Python 3.9+ and pygame 2.x are required.
Sounds are generated automatically on the first start if `assets/sounds/` is empty.

## Game modes

| Menu item | What it does |
|---|---|
| Adventure Mode | Walk through the village, forest and arena. Talk to villagers (Enter), read the notice board, fight the forest rivals, step on the arena emblem for free matches. |
| AI Battle Mode | Set up any match: choose 2 fighters per team, an agent for each side, and who moves first. |
| Tournament Mode | Fair mirrored matches between Minimax, Alpha-Beta, Alpha-Beta+, MCTS and Random, with live statistics. |
| Help | Controls, element chart, fighter stats and the agents. |

Controls: arrow keys move, Enter/Space talks, ESC pauses or goes back, M mutes sound.

## Progression

Five forest rivals (Scout Rex, Hunter Vale, Warden Kael, Sage Mora, Champion Ash) use stronger agents each time.
You pick your team from your unlocked fighters (4 at the start). Beating a rival unlocks a new fighter.
Progress is saved in `save.json` (delete it to start over).

## Battle rules

Teams of 2 fighters, one active at a time. Each turn a team attacks or switches.
`damage = max(1, round(Attack × multiplier) − Defense)`, multiplier 1.5 / 1.0 / 0.75 by element.
Fire > Earth > Lightning > Water > Fire. Damage is deterministic, so every move can be simulated exactly.

## The AI

| Agent | Where it is used | Idea |
|---|---|---|
| Minimax | Tournament baseline | Full search to a fixed depth, no pruning. |
| Alpha-Beta | Battles, rivals | Same result as Minimax, skips branches that cannot matter. |
| Alpha-Beta+ | Battles, final rival | Alpha-Beta with a smarter heuristic and best-move-first ordering. |
| MCTS | Battles, rivals | Simulates many battles with element-aware playouts, plays the most visited move. |
| Greedy / Random | Baselines | Rule-based and random players for comparison. |
| A* | Forest rival movement | Shortest path around obstacles on the tile map. |

The battle screen shows each agent's reasoning (action scores, nodes searched, pruned branches, MCTS visit counts).

## Project layout

```
main.py             launcher
ai/                 battle.py (rules, heuristics, Minimax / Alpha-Beta), mcts.py, agents.py (agent registry),
                    teams.py (fighters, rivals), tournament.py (fair tournament)
ui/                 menu, match setup, battle, tournament and help screens
world/              maps.py (tile maps), npcs.py (villagers, signs, dialogue), overworld.py (game loop, rivals, pause)
core/               audio.py, synth.py (generated sounds), save.py
experiments/        scripts for the report (results are written to results/)
assets/sounds/      generated sound effects and music
```

## Experiments for the report

```
python -m ai.tournament                         # fair tournament table + tournament.png
python experiments/mcts_experiment.py 100       # smart vs random playouts, simulations, exploration constant
python experiments/heuristic_experiment.py 100  # basic vs smart heuristic, Greedy and Random baselines
python experiments/depth_experiment.py 60       # nodes by depth (Minimax vs Alpha-Beta), strength by depth
```

The number is the number of games per row. Larger numbers give less noisy results but take longer.
