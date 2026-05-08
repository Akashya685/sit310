cmake_minimum_required(VERSION 3.0.2)
project(target_follower)

find_package(catkin REQUIRED COMPONENTS
  std_msgs
  rospy
  roscpp
  duckietown_msgs
)

catkin_package()
