

import rospy
from std_msgs.msg import Bool
from std_msgs.msg import UInt16
from std_msgs.msg import String 
from std_msgs.msg import Int16


class hopp_coll_states(object):
    """Determines the state of the collector, and the hopper."""

    def __init__(self):


        #Hopper Angle Constansts
        self.HOPPER_MAX = 180
        self.HOPPER_MIN = 75

        self.HOPPER_REST_MAX = 85
        self.HOPPER_DUMP_MIN = 175

        #Collector Angle Constants
        self.COLLECTOR_MAX = 300
        self.COLLECTOR_MIN = 245

        self.COLLECTOR_REST_MAX = 255
        self.COLLECTOR_DUMP_MIN = 295

        #Initializes the node
        rospy.init_node('hopp_coll_state')

        #Sets up publisher to publish states onto a topics
        self.hopper_state_pub = rospy.Publisher("hopper_state", String, queue_size = 10)
        self.collector_state_pub = rospy.Publisher("collector_state", String, queue_size = 10)
	self.scoop_safe_state_pub = rospy.Publisher("scoop_safe_state", String, queue_size = 10)

        # Initializes the hopper/collector angles to be considered in rest postion. This prevents log errors since the arduino 
        # does not immediatly send the angles. 
        self.hopper_angle = 80
        self.collector_angle = 250
	self.scoop_safe_bool = 1


        #Sets up subsribers to get the angles of the collector/hopper
        rospy.Subscriber("hopper_pot", UInt16, self.hopper_callback)
        rospy.Subscriber("collector_pot", UInt16, self.collector_callback)
	rospy.Subscriber("scoop_safe", Bool, self.scoop_safe_callback)

        

    #Sets the data from the hopper_callback to data member
    def hopper_callback(self, angle):
        self.hopper_angle = angle.data

    #Sets the data from the collector_callback to data member
    def collector_callback(self, angle):
        self.collector_angle = angle.data

    #Sets the data from the IR distance interrupt to data member
    def scoop_safe_callback(self, info):
	self.scoop_safe_bool = info.data

    #Checks the hopper's current angle and determines what state it is in and tell hopper what to do.
    def check_hopper(self):
        if self.HOPPER_MIN <= self.hopper_angle <= self.HOPPER_REST_MAX: 
            state = "Resting"
        elif self.HOPPER_REST_MAX < self.hopper_angle <= self.HOPPER_DUMP_MIN:
            state = "Transitioning"
        elif self.HOPPER_DUMP_MIN < self.hopper_angle <= self.HOPPER_MAX:
            state = "Dumping"
        else:
            state = "Warning"
            #print self.hopper_angle
            rospy.logerr("Hopper Angle: Out of Bounds. Hopper may be in dangerous position.")

        return state

    #Publishes the hopper state to it's respective topic
    def publish_hopper_state(self, hopper_state):
        state_msg = String()
        state_msg.data = hopper_state
        self.hopper_state_pub.publish(state_msg)

    #Checks the collector's current angle and determines what state it is in and tell collector what to do.
    def check_collector(self):
        if self.COLLECTOR_MIN <= self.collector_angle <=self.COLLECTOR_REST_MAX: 
            state = "Resting"
        elif self.COLLECTOR_REST_MAX < self.collector_angle <= self.COLLECTOR_DUMP_MIN:
            state = "Transitioning"
        elif self.COLLECTOR_DUMP_MIN < self.collector_angle <= self.COLLECTOR_MAX:
            state =  "Dumping"
        else:
            print self.collector_angle
            state = "Warning"
            rospy.logerr("Collector Angle: Out of Bounds. Collector may be in dangerous position.")

        return state

    #Publishes the collector state to it's respective topic    
    def publish_collector_state(self, collector_state):
        state_msg = String()
        state_msg.data = collector_state
        self.collector_state_pub.publish(state_msg)

    #Check IR Interrupt distance to see whether we can drive
    def check_scoop_safe(self):
	if self.scoop_safe_bool == 1:
	    state = "Safe"
	else:
	    state = "Warning"
	    rospy.logerr("IR Interrupt Sensor: Bucket not detected, cannot drive yet")

    #Publish the interrupt state to it's respective topic
    def publish_scoop_safe_state(self, scoop_safe_state):
	state_msg = String()
	state_msg.data = scoop_safe_state
	self.scoop_safe_state_pub.publish(state_msg)



    #Main Function. 
    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
	    #get string states for hopper, collect, and scoop_safe, and publish
            hopper_state = self.check_hopper()
            collector_state = self.check_collector()
	    scoop_safe_state = self.check_scoop_safe()
	    
            self.publish_hopper_state(hopper_state)
            self.publish_collector_state(collector_state)
	    self.publish_scoop_safe_state(scoop_safe_state)

            rate.sleep()

if __name__ == "__main__":
    try:
        Hopp_Coll_State = hopp_coll_states()
    except rospy.ROSInterruptException as er:
        rospy.logerr(str(er))
    else:
        Hopp_Coll_State.run()


