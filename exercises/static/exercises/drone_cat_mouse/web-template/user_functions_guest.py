from shared.image import SharedImage
from shared.value import SharedValue
import numpy as np
import cv2

# Define HAL functions
class HALFunctions:
    def __init__(self):
        # Initialize image variable
        self.shared_frontal_image = SharedImage("halfrontalimageguest")
        self.shared_ventral_image = SharedImage("halventralimageguest")
        self.shared_x = SharedValue("xguest")
        self.shared_y = SharedValue("yguest")
        self.shared_z = SharedValue("zguest")
        self.shared_takeoff_z = SharedValue("sharedtakeoffzguest")
        self.shared_az = SharedValue("azguest")
        self.shared_azt = SharedValue("aztguest")
        self.shared_vx = SharedValue("vxguest")
        self.shared_vy = SharedValue("vyguest")
        self.shared_vz = SharedValue("vzguest")
        self.shared_landed_state = SharedValue("landedstateguest")
        self.shared_position = SharedValue("positionguest",3)
        self.shared_velocity = SharedValue("velocityguest",3)
        self.shared_orientation = SharedValue("orientationguest",3)
        self.shared_yaw_rate = SharedValue("yawrateguest")

        self.shared_CMD =  SharedValue("CMDguest")


    # Get image function
    def get_frontal_image(self):
        image = self.shared_frontal_image.get()
        return image
    
    # Get left image function
    def get_ventral_image(self):
        image = self.shared_ventral_image.get()
        return image

    def takeoff(self, height):
        self.shared_takeoff_z.add(height)

        self.shared_CMD.add(3) #TAKEOFF

    def land(self):
        self.shared_CMD.add(4) #LAND
    
    def set_cmd_pos(self, x, y , z, az):
        self.shared_x.add(x)
        self.shared_y.add(y)
        self.shared_z.add(z)
        self.shared_az.add(az)

        self.shared_CMD.add(0) #POS
    
    def set_cmd_vel(self, vx, vy, vz, az):
        self.shared_vx.add(vx)
        self.shared_vy.add(vy)
        self.shared_vz.add(vz)
        self.shared_azt.add(az)

        self.shared_CMD.add(1) #VEL
    
    def set_cmd_mix(self, vx, vy, z, az):
        self.shared_vx.add(vx)
        self.shared_vy.add(vy)
        self.shared_z.add(z)
        self.shared_azt.add(az)

        self.shared_CMD.add(2) #MIX
    
    
    def get_position(self):
        position = self.shared_position.get()
        return np.array(position)

    def get_velocity(self):
        velocity = self.shared_velocity.get()
        return np.array(velocity)

    def get_yaw_rate(self):
        yaw_rate = self.shared_yaw_rate.get()
        return yaw_rate

    def get_orientation(self):
        orientation = self.shared_orientation.get()
        return np.array(orientation)

    def get_roll(self):
        roll = self.shared_orientation.get()[0]
        return roll

    def get_pitch(self):
        pitch = self.shared_orientation.get()[1]
        return pitch
    
    def get_yaw(self):
        yaw = self.shared_orientation.get()[2]
        return yaw 

    def get_landed_state(self):
        landed_state = self.shared_landed_state.get()
        return landed_state

# Define GUI functions
class GUIFunctions:
    def __init__(self):
        # Initialize image variable
        self.shared_image = SharedImage("guifrontalimageguest")
        self.shared_left_image = SharedImage("guiventralimageguest")

    # Show image function
    def showImage(self, image):
        # Reshape to 3 channel if it has only 1 in order to display it
        if (len(image.shape) < 3):
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        self.shared_image.add(image)
    
    # Show left image function
    def showLeftImage(self, image):
        # Reshape to 3 channel if it has only 1 in order to display it
        if (len(image.shape) < 3):
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        self.shared_left_image.add(image)