# Simulated Robotics Fleet — Project Notes

Status: early, scope not locked yet. This file just tracks the idea as it develops.

## Concept
A small fleet of robots that pick up tasks from a priority queue: moving boxes,
going to designated areas. Need to work out how tasks get prioritized and
assigned across multiple robots.

## Planned path
1. Simulate in Gazebo and Isaac Sim first.
2. Once the logic works in sim, 3D print and build a small real fleet.

## Decisions so far

**Task / scheduling logic**
- Priority = weighted total of factors (deadline, distance, etc.), with an override
  flag that preempts the weighted score entirely.
- Central scheduler (avoids network timing / race condition / latency issues of
  decentralized bidding).
- A robot finishes its current task before taking a new one, unless an override
  interrupts it.
- Positions are arbitrary coordinates, not fixed waypoints. Resolved through a
  generic position registry/API (hashmap-style: label -> coords, e.g. pos a, b,
  c...) so any map can be uploaded and just needs its positions defined.

**Fleet / robot capabilities**
- Robot count: start small, but design for an expandable fleet (not hardcoded to N).
- Capability for now: nav-to-waypoint only, no manipulation yet.
- Robots are identical.
- Collision avoidance: central coordinator handles robot-vs-robot conflicts;
  onboard LiDAR or RGB-D handles local/dynamic obstacle avoidance.

**Software stack**
- ROS 2 (Humble, already installed) is the nav + comms layer, not just sim bridging.
- Sim order: Gazebo first, Isaac Sim after.
- Nav stack: Nav2.
- Scheduler is a ROS 2 node.

**Sim-to-real**
- Real platform: diff-drive, fully custom. Details (microcontroller/compute,
  how much code ports unchanged) TBD once sim is working.

## Still open
- Exact priority weighting formula (which factors, what weights).
- Fleet size target for first sim pass.
- Microcontroller/compute choice for the real robots.
- How much of the Nav2/scheduler code is expected to carry over to real hardware
  vs. needing a hardware abstraction layer.