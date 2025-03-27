#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Software emergency stop fro ros_control

import curses
import math

import rospy
from geometry_msgs.msg import Twist
from controller_manager_msgs.srv import *

import std_srvs

from std_srvs.srv import EmptyResponse, Empty as EmptyServiceMsg
from std_msgs.msg import Empty

class TextWindow():

    _screen = None
    _window = None
    _num_lines = None

    def __init__(self, stdscr, lines=11):
        self._screen = stdscr
        self._screen.nodelay(True)
        curses.curs_set(0)
        self._num_lines = lines
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    def read_key(self):
        keycode = self._screen.getch()
        return keycode if keycode != -1 else None

    def clear(self,color):
        self._screen.bkgd(curses.color_pair(color))
        self._screen.clear()
        
    def write_line(self, lineno, message):
        if lineno < 0 or lineno >= self._num_lines:
            raise ValueError, 'lineno out of bounds'
        height, width = self._screen.getmaxyx()
        y = (height / self._num_lines) * lineno
        x = 10
        for text in message.split('\n'):
            text = text.ljust(width)
            self._screen.addstr(y, x, text, curses.A_BOLD)
            y += 1

    def refresh(self):
        self._screen.refresh()

    def beep(self):
        curses.flash()


class SimpleKeyTeleop():
    def __init__(self, interface):
        self._interface = interface
        self._pub_cmd = rospy.Publisher('key_vel', Twist)
        self._hz = rospy.get_param('~hz', 10)
        self._last_pressed = {}
        self._angular = 0
        self._linear = 0
        self._keypressed = 'a'
        self._state = 3
        self._interface.clear(1)
        self._names = []
  
    def callstart_client(self):
        rospy.wait_for_service('/lip_walking_controller_ds_sim/generate_fixed_plan')
        try:
            emptySrv = rospy.ServiceProxy('/lip_walking_controller_ds_sim/generate_fixed_plan',std_srvs.srv.Empty)
            response = emptySrv()
            return True
        except rospy.ServiceException as e:
            print("Service call failed: %s"%e)
            return False

    def run(self):
        rate = rospy.Rate(self._hz)
        self._running = True
        while self._running:
            while True:
                keycode = self._interface.read_key()
                if keycode is None:
                    break
                self._key_pressed(keycode)
            self._publish()
            rate.sleep()

    def _key_pressed(self, keycode):
        if keycode == ord('q'):
            self._running = False
            rospy.signal_shutdown('Bye')
        self._keypressed = keycode

        if ((self._keypressed == 338) or (self._keypressed == 339) ) and (self._state==0):
            contrl_list = self._controller_list_srv()
            stop_list = SwitchControllerRequest()
            stop_list.strictness = 0
            for x in contrl_list.controller:
                contro = x
                self._names.append(contro.name)
            stop_list.stop_controllers = self._names
            resultsrv = self._controller_switch_srv(stop_list)
            self._state = 1
        
        if (self._keypressed == 114) and (self._state==1):
            stop_list = SwitchControllerRequest()
            stop_list.strictness = 0
            stop_list.start_controllers = self._names
            resultsrv = self._controller_switch_srv(stop_list)
            self._state = 2
        
        if (self._keypressed == 100) and ( (self._state==2) or (self._state==0) ) :
            self._state = 4

        if (self._keypressed == 338) and (self._state==4):
            check = self.callstart_client()
            if(check == True):
                self._state = 0
            else:
                self._state = 2

        if (self._keypressed == 339) and (self._state==4):
            contrl_list = self._controller_list_srv()
            stop_list = SwitchControllerRequest()
            stop_list.strictness = 0
            for x in contrl_list.controller:
                contro = x
                self._names.append(contro.name)
            stop_list.stop_controllers = self._names
            resultsrv = self._controller_switch_srv(stop_list)
            self._state = 1


    def _publish(self):
        if self._state == 0:
            self._interface.clear(2)
            self._interface.write_line(2, 'pressed: %s' % (self._keypressed))
            self._interface.write_line(5, 'Page up/down --> Stop')
            self._interface.write_line(6, 'Press d to reseet.')
            self._interface.write_line(7, 'Press q to exit.')
            self._interface.refresh()
            
        if self._state == 1:
            self._interface.clear(1)
            self._interface.write_line(2, 'pressed: %s' % (self._keypressed))
            self._interface.write_line(4, 'Stopped: %s' %(self._names))
            self._interface.write_line(8, 'Press r to restart controllers')
            self._interface.write_line(9, 'Remember to unmount your controller first')
            self._interface.write_line(10, 'Press q to exit.')
            self._interface.refresh()
            
        if self._state == 2:
            self._interface.clear(3)
            self._interface.write_line(2, 'pressed: %s' % (self._keypressed))
            self._interface.write_line(5, 'Press d after seting home')
            self._interface.write_line(7, 'Press q to exit.')
            self._interface.refresh()
            
        if self._state == 3:
            self._interface.clear(3)
            self._interface.write_line(2, 'Waiting for controller_manager services...')
            self._interface.refresh()
            rospy.wait_for_service('controller_manager/list_controllers')
            self._controller_list_srv = rospy.ServiceProxy('controller_manager/list_controllers', ListControllers)
            rospy.wait_for_service('controller_manager/switch_controller')
            self._controller_switch_srv = rospy.ServiceProxy('controller_manager/switch_controller', SwitchController)
            self._state = 4
            
        if self._state == 4:
            self._interface.clear(3)
            self._interface.write_line(2, 'pressed: %s' % (self._keypressed))
            self._interface.write_line(4, 'Page up   --> Stop')
            self._interface.write_line(5, 'Page down --> Start')
            self._interface.write_line(7, 'Press q to exit.')
            self._interface.refresh()

        twist = Twist()
        self._pub_cmd.publish(twist)


def main(stdscr):
    rospy.init_node('remote_emg_stop')
    app = SimpleKeyTeleop(TextWindow(stdscr))
    app.run()

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except rospy.ROSInterruptException:
        pass
