from setuptools import find_packages, setup

package_name = 'task_nav'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vfran',
    maintainer_email='vitorianascimentomatos@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'init_pose = task_nav.init_pose:main',
            'goal_pose = task_nav.goal_pose:main',
            'mecanum_drive = task_nav.mecanum_drive:main',
            'inspection_routine = task_nav.inspection:main',
            'object_avoidance = task_nav.object_avoidance:main',
            'turn_around = task_nav.turn_around:main',
            'pub_turned = task_nav.pub_turn_around:main',
            'fake_node = task_nav.fake_node:main'
        ],
    },
)
