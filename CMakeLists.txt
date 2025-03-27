cmake_minimum_required(VERSION 3.11)
project(ow_reemc)

###################
## Configuration ##
###################

## Compile as C++11, supported in ROS Kinetic and newer
add_compile_options(-std=c++11)

# ROS dependecies
find_package(catkin REQUIRED COMPONENTS
    ow_core
    ow_hw_interface
    ow_fk
    ow_zmp
    ow_balancer
    ow_com
    ow_com_tg
    ow_ftg
    ow_fcm
    ow_ik
    ow_cmd_gen
    ow_controller
)


# Package configuration (this information is passed to projects/packages that
# depend on this package)
catkin_package(
    INCLUDE_DIRS 
    LIBRARIES ow_devel_tests
    CATKIN_DEPENDS
        ow_core
        ow_hw_interface
        ow_fk
        ow_zmp
        ow_balancer
        ow_com
        ow_com_tg
        ow_ftg
        ow_fcm
        ow_ik
        ow_cmd_gen
        ow_controller
#    DEPENDS ${DEPENDS_VAR}
)

###########
## Build ##
###########


foreach( dir config launch scripts )
  install(DIRECTORY ${dir}
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION} 
  )
endforeach(dir)

