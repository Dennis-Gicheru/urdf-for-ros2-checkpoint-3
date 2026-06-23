
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('barista_robot_description')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(pkg, 'xacro', 'barista_robot_model.urdf.xacro')
    world_file = os.path.join(pkg, 'worlds', 'empty.sdf')
    rviz_file = os.path.join(pkg, 'rviz', 'barista.rviz')

    include_laser = LaunchConfiguration('include_laser')

    # Process the xacro at launch, forwarding the include_laser argument.
    robot_desc = ParameterValue(
        Command(['xacro ', xacro_file, ' include_laser:=', include_laser]),
        value_type=str,
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': [world_file, ' -r -v 4']}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'robot_description': robot_desc}],
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-name', 'barista', '-topic', 'robot_description', '-z', '0.15'],
    )

    # Core bridge: always on. ] = ROS_TO_GZ, [ = GZ_TO_ROS
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        parameters=[{'use_sim_time': True}],
    )

    # Scan bridge: only when the laser is included -> no /scan when disabled.
    scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=['/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(include_laser),
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_file],
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(pkg, '..')),
        DeclareLaunchArgument(
            'include_laser', default_value='true',
            description='Spawn the laser scanner and bridge /scan (true/false)'),
        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        spawn,
        bridge,
        scan_bridge,
        rviz,
    ])
