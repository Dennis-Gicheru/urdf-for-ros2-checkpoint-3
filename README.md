# barista_robot_description

URDF / Xacro description of the **Barista robot** — a differential-drive mobile base with a cup-holder tray on standoff rods and a planar laser scanner. Spawns in Gazebo with RViz. (The Construct, Checkpoint 3.)

## Environment

- **ROS 2 Jazzy**
- **Gazebo Harmonic** (`gz sim`) via `ros_gz_sim` / `ros_gz_bridge`

## Layout

```
urdf/    barista_robot_model.urdf          # Task 1: raw URDF
xacro/   barista_robot_model.urdf.xacro    # Task 2: main file
         drive_wheel / caster_wheel / standoff_rod / cup_holder_tray / laser_scanner .xacro
launch/  barista_urdf.launch.py            # Task 1 launch
         barista_xacro.launch.py           # Task 2 launch
worlds/  empty.sdf      meshes/  (laser mesh)      rviz/  barista.rviz
```

## Build

```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select barista_robot_description
source install/setup.bash
```

## Run

```bash
# Task 1 (raw URDF)
ros2 launch barista_robot_description barista_urdf.launch.py

# Task 2 (xacro)
ros2 launch barista_robot_description barista_xacro.launch.py

# Task 2 without the laser (no /scan published)
ros2 launch barista_robot_description barista_xacro.launch.py include_laser:=false
```

## Topics

| Topic | Type | Direction |
|-------|------|-----------|
| `/cmd_vel` | `geometry_msgs/Twist` | command in |
| `/odom` | `nav_msgs/Odometry` | published |
| `/scan` | `sensor_msgs/LaserScan` | published (laser on) |

## Notes

- Set the real laser mesh filename in `urdf/…urdf` and `xacro/laser_scanner.xacro` (replace `LASER_MESH.dae`).
- Git tags: `initial-tag`, `task1`, `task2`.
