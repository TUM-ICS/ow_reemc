#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Software emergency stop for ros_control

import rospy
import math
import evdev

from std_msgs.msg import String
from std_srvs.srv import Empty
from evdev import ecodes
from controller_manager_msgs.srv import *

class EmergencyStop():

    def __init__(self, devic):
        self.state_pub = rospy.Publisher('/h1_emg_stop/state', String, queue_size=10)
   
        self.key = 'a'
        self.prev_key = 'a'
        self.names = []
        self.restart_server = rospy.Service('/h1_emg_stop/restartControllers', Empty, self.restart_controllers)

        print('Waiting for controller_manager/list_controllers service')    
        rospy.wait_for_service('controller_manager/list_controllers')
        self.controller_list_srv = rospy.ServiceProxy('controller_manager/list_controllers', ListControllers)
    
        print('Waiting for controller_manager/switch_controller service')
        rospy.wait_for_service('controller_manager/switch_controller')
        self.controller_switch_srv = rospy.ServiceProxy('controller_manager/switch_controller', SwitchController)

        #self.device = evdev.InputDevice('/dev/input/event15')
        self.device = evdev.InputDevice(devic)
        print(self.device)

    def restart_controllers(self,req):        
        contrl_list = self.controller_list_srv()
        stop_list = SwitchControllerRequest()
        stop_list.strictness = 0
        self.names = []
        for x in contrl_list.controller:
            contro = x
            self.names.append(contro.name)
        stop_list.start_controllers = self.names
        resultsrv = self.controller_switch_srv(stop_list)
        hello_str = "Restarting controllers %s" % self.names
        rospy.loginfo(hello_str)
        self.state_pub.publish(hello_str)

        return 

    def run(self):
        rate = rospy.Rate(10) # 10hz    
        while not rospy.is_shutdown():
            for event in self.device.read_loop():
                if event.type == evdev.ecodes.EV_KEY:
                                                
                    print(event.code)

                    if (event.value == 1) and ((event.code == 104) or (event.code == 109)):
                        contrl_list = self.controller_list_srv()
                        stop_list = SwitchControllerRequest()
                        stop_list.strictness = 0
                        self.names = []
                        for x in contrl_list.controller:
                            contro = x
                            self.names.append(contro.name)
                        stop_list.stop_controllers = self.names
                        resultsrv = self.controller_switch_srv(stop_list)
                        
                        hello_str = "Stoping controllers %s" % self.names
                        rospy.loginfo(hello_str)
                        self.state_pub.publish(hello_str)      
        rate.sleep()
    
    
if __name__ == '__main__':

    print 'Argument List:', str(sys.argv)

    if len(sys.argv) < 2:
        print("usage: rosrun tum_ics_h1_walking_tools emg_stop_background.py /dev/input/event")
    else:
        rospy.init_node('h1_emergency_stop', anonymous=True)
        app = EmergencyStop(sys.argv[1])    

        try:
            app.run()
        except rospy.ROSInterruptException:
            pass

