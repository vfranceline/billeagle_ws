#!/usr/bin/env python3
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    # Diretório do pacote
    pkg_bill = get_package_share_directory('bill_description')

    # Arquivo xacro
    xacro_file = os.path.join(pkg_bill, 'models/myBill', 'bill.urdf.xacro')
    doc = xacro.process_file(xacro_file)
    robot_description_config = doc.toxml()

    # Configuração do uso do tempo simulado
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Arquivo de parâmetros do Gazebo
    gazebo_params_file_dir = os.path.join(pkg_bill, 'config', 'gazebo_params.yaml')

    # Declaração de argumentos
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Usar tempo simulado (Gazebo)'
    )

    # Lançar o Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'params_file': gazebo_params_file_dir}.items()
    )

    # Nó robot_state_publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'use_sim_time': use_sim_time,
                     'robot_description': robot_description_config}],
        output='screen'
    )

    # Spawn do robô no Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'robot'],
        output='screen'
    )

    # spawner do joint_state_broadcaster
    spawn_joints = TimerAction(
        period=2.0,
        actions=[Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
            output='screen'
        )]
    )

    # spawner do mecanum_controller
    spawn_mecanum = TimerAction(
        period=4.0,
        actions=[Node(
            package='controller_manager',
            executable='spawner',
            arguments=['mecanum_controller',    '--controller-manager', '/controller_manager'],
            output='screen'
        )]
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        parameters=[{'use_gui': False}],
        output="screen",
    )

    # Criar descrição do launch
    ld = LaunchDescription()

    # Adicionar ações
    ld.add_action(declare_use_sim_time)
    ld.add_action(gazebo)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(spawn_entity)
    ld.add_action(spawn_joints)
    ld.add_action(spawn_mecanum)
    ld.add_action(joint_state_publisher)

    return ld
