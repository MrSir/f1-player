# F1 Player
A tool for watching F1 races from a data perspective.

![f1p](https://github.com/user-attachments/assets/7cacf4fc-ed9e-4d39-a288-fac5600926f3)

## Purpose
With every day busyness there isn't always enough time to sit down and watch a 2 hour F1 race, and the 10min F1 race highlights tend to miss a lot of the more detailed data. So I set out to build a tool that can solve this problem. An F1 Player that can allow me to watch the full race at a sped up pace, while still giving me as much data as possible. Rendering the circuit and representations of the cars going around it for visual aid and track position. Showing individual car telemetry for those more indepth glimpses. Lap, sector, and interval times, and many more things.

## Requirements
- poetry v2.2.1
- python 3.14

## Installation
`poetry install`

## Starting the Player
`f1p`

## Contributing with AI

Use the following as a prefix to your prompts. Make sure to also include the `ai/patterns.md` file into the context for more deterministic results.
```
Analyze and follow the instructions in the `./ai/patterns.md` file first. Then ...
```