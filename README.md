# billeagle_ws

## Mapping
For mapping the environment launch the following launch files each in a separate terminal:
```bash
# Launch rviz, gazebo and robot state and joint publishers
ros2 launch bill_description robot.launch.py
```
```bash
# Launch mapping with slamtoolbox
ros2 launch bill_slam mapping.launch.py use_saved_map:=false
```
```bash
# Use teleop Twist keyboard to navigate in the map
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Localization
After creating a map and saving it, you can use the saved map to localize the robot using amcl
```bash
# Launch rviz, gazebo and robot state and joint publishers
ros2 launch bill_description robot.launch.py 
```
```bash
# Launch localization with amcl
ros2 launch bill_slam amcl.launch.py 
```
```bash
# Use teleop Twist keyboard to navigate in the map
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Navigation
To pass a target location to the robot and make it autonomously plan the path and move to it use the following
```bash
# Launch rviz, gazebo and robot state and joint publishers
ros2 launch bill_description robot.launch.py 
```
```bash
# Launch localization with amcl to load the saved map
ros2 launch bill_slam amcl.launch.py 
```
```bash
# Launch navigation stack of nav2
ros2 launch bill_nav navigation_launch.py
```
