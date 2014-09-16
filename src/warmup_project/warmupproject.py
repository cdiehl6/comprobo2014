#!/usr/bin/env python
import rospy
import math
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan

def getch():
    """ Return the next character typed on the keyboard """
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def teleop():
    turn_vel = .5
    linear_vel = 1
    r=rospy.Rate(10)
    key=getch()
    while not rospy.is_shutdown():
        if key=='w':
            pub.publish(Twist(linear=Vector3(x=linear_vel)))
        elif key=='d':
            pub.publish(Twist(angular=Vector3(z=-turn_vel)))
        elif key=='s':
            pub.publish(Twist(linear=Vector3(x=-linear_vel)))
        elif key=='a':
            pub.publish(Twist(angular=Vector3(z=turn_vel)))
        elif key=='q':
            break
        else:
            pub.publish(Twist())

def valid_scan(msg):
    valid_ranges = []
    #print msg
    for i in range(len(msg.ranges)):
        if msg.ranges[i]!=0 and msg.ranges[i]<8:
            valid_ranges.append(msg.ranges[i])
        else:
            valid_ranges.append(10)
    return valid_ranges

def wallfollow(msg,pub,wall,wall_dist):
    linear = 0
    angular=0
    scan=valid_scan(msg)
    if len(wall)>0 and len(wall_dist)>0:
        #print wall
        wall_angle=sum(wall)/float(len(wall))
        wall_distance=sum(wall_dist)/float(len(wall_dist))
        #print wall_angle
        diff_from_wall=wall_angle-90
        angular=diff_from_wall/100
        print angular
        if diff_from_wall<10 and diff_from_wall>-10:
            angular=diff_from_wall/5
            linear=math.fabs(diff_from_wall)/10
            print linear
        if wall_distance<.8:
            angular=angular+((1-wall_distance)/2)
            print angular
        pub.publish(Twist(linear=Vector3(x=linear),angular=Vector3(z=angular)))

def obstacle(msg,pub,obst,obst_dist):
    linear=0
    angular=0
    if len(obst)>0 and len(obst_dist)>0:
        obst_angle=sum(obst)/float(len(obst))
        wall_distance=sum(wall_dist)/float(len(wall_dist))
        #print wall_angle
        heading_from_obst=obst_angle-180
        angular=math.fabs(heading_from_obst)/100
        print angular
        if heading_from_obst>10 and heading_from_obst<-10:
            angular=heading_from_obst/5
            linear=math.fabs(heading_from_obst)/10
            print linear
        if wall_distance<.8:
            angular=angular+((1-obst_distance)/2)
            print angular
        pub.publish(Twist(linear=Vector3(x=linear),angular=Vector3(z=angular)))

def switcher():
    pub=rospy.Publisher('cmd_vel',Twist,queue_size=10)
    sub=rospy.Subscriber('scan', LaserScan, wallfollow,pub)
    rospy.init_node('warmupproject',anonymous=True)
    while not rospy.is_shutdown():
        msg=LaserScan
        scan=valid_scan(msg)
        wall=[]
        wall_dist=[]
        for i in range(len(scan)):
            if scan[i]<=1:
                #print scan[i]
                wall_dist.append(scan[i])
                #print wall_dist
        for i in scan:
            wall.append(scan.index(i))
        if len(wall)>30:
            wallfollow(msg,pub,wall,wall_dist)
        elif len(wall)<30 and len(wall)>0:
            obstacle(msg,pub,wall,wall_dist)
        else:
            teleop()

if __name__=="__main__":
    try:
        switcher()
    except rospy.ROSInterruptException: Pas