

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('barista_robot_description')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    urdf_file = os.path.join(pkg, 'urdf', 'barista_robot_model.urdf')
    world_file = os.path.join(pkg, 'worlds', 'empty.sdf')
    rviz_file = os.path.join(pkg, 'rviz', 'barista.rviz')

    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # --- Gazebo Harmonic via ros_gz_sim gz_sim.launch.py (gz_args -> gz sim) ---
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': [world_file, ' -r -v 4']}.items(),
    )

    # --- Publishes /robot_description + static TF for all fixed joints ---
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'robot_description': robot_desc}],
    )

    # --- Publishes /joint_states (default 0) so RViz can resolve wheel TFs ---
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    # --- Spawn the robot into Gazebo from the /robot_description topic ---
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-name', 'barista', '-topic', 'robot_description', '-z', '0.15'],
    )

    # --- ROS <-> Gazebo bridge ---------------------------------------------
    #   ] = ROS_TO_GZ   [ = GZ_TO_ROS   @ = BIDIRECTIONAL
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        parameters=[{'use_sim_time': True}],
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_file],
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        # let Gazebo resolve package:// mesh URIs
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(pkg, '..')),
        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        spawn,
        bridge,
        rviz,
    ])
