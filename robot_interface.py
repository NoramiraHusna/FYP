from robot_controller import RobotController

# 🔌 Fire up the ONE physical connection for the entire game!
alpha_mini_hardware = RobotController()
alpha_mini_hardware.connect()

class RobotInterface:
    def __init__(self):
        pass

    def speak(self, tone, message_optimistic, message_pessimistic):
        if tone == "Optimistic":
            final_msg = str(message_optimistic)
            safe_tone = "Optimistic"
        else:
            final_msg = str(message_pessimistic)
            safe_tone = "Pessimistic" 
            
        alpha_mini_hardware.speak(safe_tone, final_msg)