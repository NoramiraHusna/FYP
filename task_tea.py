import pygame
from task_logic_base import TaskLogicBase

class TaskTeaLogic(TaskLogicBase):
    def __init__(self, screen, clock, robot, interactions):
        self.screen = screen
        self.clock = clock
        self.robot = robot
        self.interactions = interactions
        self.OPTIMISTIC_DIALOGUE = {"CHANGE": ".", "KEEP": "."}
        self.PESSIMISTIC_DIALOGUE = {"CHANGE": ".", "KEEP": "."}

    def run_task(self, tone, task_num):

        opt_intro = (
            "Welcome to the tea house, Traveler! "
            "Milk Tea, Green Tea, Lemon Tea, and Black Tea all ready to go. "
            "The Alien looks stressed and stranded… maybe something calming is exactly what he needs right now. "
            "So feel free to choose what you think helps Alien most!"
            "click on the buy tea button to interact and select a tea for the Alien."
        )

        pess_intro = (
            "The tea house. Four drinks. Milk Tea, Green Tea, Lemon Tea, Black Tea. "
            "Don’t overthink it — or worse, underthink it. Alien is stressed, stranded, and running on fumes. "
            "Your choice matters more than it should."
            "click on the buy tea button to interact and select a tea for the Alien."
        )

        self.robot.speak(tone, opt_intro, pess_intro)

        want_to_interact = self.interactions.run_interaction_prompt("Tea", tone=tone)

        if want_to_interact:

            # 📸 START CAMERA FOR INIT SELECTION
            prefix = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"][task_num - 1]
            self.interactions.send_vision_command("START", f"{prefix}_Init")

            selection = self.interactions.flavor_ui.run("Tea")

            # 📸 STOP CAMERA AND SAVE INIT DATA
            self.interactions.send_vision_command("STOP", f"{prefix}_Init")
            init_data = self.interactions.wait_for_vision_data(f"{prefix}_Init") if selection else None

            if selection:

                if "Green" in selection:
                    opt_msg = (
                        "Green Tea is an excellent calming choice, Traveler. "
                        "It contains natural compounds that can help reduce stress and stabilize his racing thoughts after being stranded. "
                        "The warm, light drink may also help him focus better on repairing his ship without feeling overwhelmed. "
                        "In this condition, calmness could be more valuable than energy. "
                        "But Milk Tea might improve his mood and give him extra calories for recovery. "
                        "Calm mind or emotional comfort… what’s your call? Will you keep Green Tea or change to Milk Tea?"
                    )
                    pess_msg = (
                        "Green Tea? It’s basically just warm bitterness. "
                        "It won’t give him enough energy, the calories are almost nonexistent, and if he stays stressed and underfed, he’ll still struggle with repairs. "
                        "Milk Tea would at least give sugar and dairy to stabilize his condition and keep him going. "
                        "Calm is useless if he collapses. Will you keep Green Tea or change to Milk Tea?"
                    )
                    target_suggestion = "Milk Tea"

                else:
                    opt_msg = (
                        f"{selection} is a comforting choice, Traveler. "
                        "It may help lift Alien’s spirits and provide some energy for recovery. "
                        "But Green Tea might actually be more suitable for his current condition. "
                        "The natural calming effect could help reduce stress from being stranded, support clearer thinking during ship repairs, "
                        "and keep his body from overreacting to pressure or exhaustion. "
                        "A calm Alien may repair things more safely and efficiently. "
                        f"Will you keep {selection} or change to Green Tea?"
                    )
                    pess_msg = (
                        f"You picked {selection}. It may comfort him briefly, but it doesn’t solve the real problem. "
                        "Too much sugar or dairy could make him sluggish, slow his reaction time, and worsen his focus while repairing the ship. "
                        "Green Tea is the only option that keeps him mentally sharp and emotionally stable under stress. "
                        f"Will you keep {selection} or change to Green Tea?"
                    )
                    target_suggestion = "Green Tea"

                self.robot.speak(tone, opt_msg, pess_msg)

                custom_options = [selection, target_suggestion]
                ui_lines = [
                    "Listen to Alpha Mini's suggestion...",
                    "-> Choose to KEEP or CHANGE your decision."
                ]

                # 📸 START CAMERA FOR FINAL SELECTION
                self.interactions.send_vision_command("START", f"{prefix}_Final")

                final, changed_mind = self.interactions.run_robot_intervention(
                    "Tea", custom_options, selection, tone, ui_lines
                )

                # 📸 STOP CAMERA AND SAVE FINAL DATA
                self.interactions.send_vision_command("STOP", f"{prefix}_Final")
                final_data = self.interactions.wait_for_vision_data(f"{prefix}_Final")

                if changed_mind:
                    opt_after = "That was a thoughtful choice, Traveler. A calmer Alien will handle everything much better now."
                    pess_after = "Good. At least you corrected it before stress turned into failure."
                else:
                    opt_after = "Alright, Traveler. Let’s hope your decision still helps Alien manage his stress and recovery."
                    pess_after = "Understood. We proceed… though an unstable mind on a stranded Alien is rarely a good sign."

                self.robot.speak(tone, opt_after, pess_after)

                outro_lines = [
                    "Please listen to Alpha Mini's reaction",
                    "to your decision..."
                ]
                self.interactions.run_robot_intervention("Tea", [], "", tone, outro_lines, speaker_name="ALPHA MINI", simple_mode=True)

                # 💾 RETURN ACTUAL DATA
                return True, selection, final, changed_mind, init_data, final_data

        return False, None, None, False, None, None
