import rospy
import time
from std_msgs.msg import Bool
from std_msgs.msg import UInt16
from std_msgs.msg import String 
from std_msgs.msg import Int16


class hopp_coll_commands(object):
    """Determines the state of the collector, and the hopper."""

    def __init__(self):

        #IR Interrupt Distance Constants
        self.SAFE_DIST_MAX = 10 #CHANGE THIS VALUE
        self.SAFE_DIST_MIN = 12 #CHANGE THIS VALUE

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

        #Motor Command constants CHECK THESE VALUES!!!
        self.HOPPER_UP = 355
        self.HOPPER_DOWN = 385
        self.HOPPER_HALT = 370

        #Initializes the node
        rospy.init_node('hopp_coll_commands')

        # Initializes the hopper/collector angles to be considered in rest postion. This prevents log errors since the arduino 
        # does not immediatly send the angles. 
        self.hopper_angle = 80
        self.collector_angle = 250
        self.scoop_safe_dist = 10   #CHANGE THIS VALUE

        #Set up publishers to publish commands to command topic
        self.hopper_cmds_pub = rospy.Publisher("hopper_cmds", Int16, queue_size = 10)
        self.collector_spin_cmds_pub = rospy.Publisher("collector_spin_cmds", Int16, queue_size = 10)
        self.collector_tilt_cmds_pub = rospy.Publisher("collecter_tilt_cmds", Int16, queue_size = 10)

        #Sets up subscribers to get the angles of the collector/hopper
        rospy.Subscriber("hopper_pot", UInt16, self.hopper_callback)
        rospy.Subscriber("collector_pot", UInt16, self.collector_callback)
        rospy.Subscriber("scoop_safe", Bool, self.scoop_safe_callback)

        #Get states for current positions of hopper and collector
        rospy.Subscriber("hopper_state", String, self.hopper_state_callback)
        rospy.Subscriber("collector_state", String, self.collector_state_callback)
        rospy.Subscriber("scoop_safe_state", String, self.scoop_safe_state_callback)

    #Sets the data from the hopper_callback to data member
    def hopper_callback(self, angle):
        self.hopper_angle = angle.data

    #Sets the data from the collector_callback to data member
    def collector_callback(self, angle):
        self.collector_angle = angle.data

    #Sets the data from the IR distance interrupt to data member
    def scoop_safe_callback(self, dist):
        self.scoop_safe_dist = dist.data   
    
    #Sets the state from the hopper 
    def hopper_state_callback(self, state):
        self.hopper_state = state.data

    #Sets the state from the collector
    def collector_state_callback(self, state):
        self.collector_state = state.data

    #Sets the state for based on if the collector should spin
    def scoop_safe_state_callback(self, state):
        self.scoop_safe_state = state.data     

    def get_hopper_command(self, prev_command): #SHOULD WE PASS IN PREV ANGLE AND STATE HERE
        if self.hopper_state = "Resting":
            if self.HOPPER_MIN <= self.hopper_angle <= self.HOPPER_REST_MAX:
                command = HOPPER_UP
                state = "Resting"
            elif self.HOPPER_REST_MAX < self.hopper_angle <= self.HOPPER_DUMP_MIN:
                command = HOPPER_UP
                state = "Transitioning"
            else
                rospy.logerr("Inconsistent hopper angle reading, something went wrong...")
                state = "Warning"
        elif self.hopper_state = "Transitioning":
            if self.HOPPER_MIN <= self.hopper_angle <= self.HOPPER_REST_MAX:
                command = HOPPER_DOWN
                state = "Resting"
            elif self.HOPPER_REST_MAX < self.hopper_angle <= self.HOPPER_DUMP_MIN:
                command = prev_command
                state = "Transitioning"
            elif self.COLLECTOR_DUMP_MIN < self.collector_angle <= self.COLLECTOR_MAX:
                command = HOPPER_UP
                state = "Dumping"
            else
                rospy.logerr("Inconsistent hopper angle reading, something went wrong...")
                state = "Warning"
        elif self.hopper_state = "Dumping":
            if self.COLLECTOR_REST_MAX < self.collector_angle <= self.COLLECTOR_DUMP_MIN:
                command = HOPPER_DOWN
                state = "Transitioning"
            elif self.COLLECTOR_DUMP_MIN < self.collector_angle <= self.COLLECTOR_MAX:
                time.wait()
                command = HOPPER_DOWN
                state = "Dumping"
            else 
                rospy.logerr("Inconsistent hopper angle reading, something went wrong...")
                state = "Warning"

        return state, command  
        
        def publish_hopper_command(self, hopper_state, hopper_command):
            state_msg = String()
            command_msg = Int16()

            state_msg.data = hopper_state
            command_msg.data = hopper_command

            self.hopper_




if __name__ == "__main__":
    try:
        Hopp_Coll_Commands = hopp_coll_commands()
    except rospy.ROSInterruptException as er:
        rospy.logerr(str(er))
    else:
        Hopp_Coll_Commands.run()