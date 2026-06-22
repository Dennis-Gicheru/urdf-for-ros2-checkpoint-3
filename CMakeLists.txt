cmake_minimum_required(VERSION 3.8)
project(barista_robot_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Install all resource directories into the package share folder.
# (xacro/ is created in Task 2; harmless if empty now.)
install(
  DIRECTORY urdf launch rviz worlds meshes xacro
  DESTINATION share/${PROJECT_NAME}
)

ament_package()