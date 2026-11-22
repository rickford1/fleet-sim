# fleet-sim

A small fleet of robots that pick tasks off a priority queue: moving boxes,
going to designated areas. Central ROS 2 scheduler assigns tasks to robots
based on a weighted priority score, with an override that preempts everything
else.

## Plan
1. Simulate in Gazebo first, then Isaac Sim.
2. Get a single robot driving around in sim.
3. Build out the fleet scheduler and multi-robot coordination.
4. 3D print and build a small real fleet.

See [fleet-notes.md](fleet-notes.md) for the full design notes and open questions.

## Stack
- ROS 2 Humble
- Gazebo (sim), Isaac Sim (later)
- Nav2
