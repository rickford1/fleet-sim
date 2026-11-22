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

## Running the sim

Requires ROS 2 Humble and `ros-humble-gazebo-ros-pkgs` installed. Build the workspace first:

```
cd ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

**Terminal 1 — launch the sim** (Gazebo + robot_state_publisher + spawns the robot):
```
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
ros2 launch fleet_sim_gazebo fleet_sim.launch.py
```
Leave this running — `Ctrl+C` shuts down Gazebo and all the nodes cleanly.

**Terminal 2 — drive it:**
```
source /opt/ros/humble/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
Click into this terminal (it needs keyboard focus) and use `i`/`,`/`j`/`l` etc. to drive.

**Terminal 3 (optional) — watch odometry:**
```
source /opt/ros/humble/setup.bash
ros2 topic echo /odom --field pose.pose.position
```
