import pygame
from task_logic_base import TaskLogicBase

class TaskRiceBowlLogic(TaskLogicBase):
    def __init__(self, screen, clock, robot, interactions):
        self.screen = screen
        self.clock = clock
        self.robot = robot
        self.interactions = interactions
        self.OPTIMISTIC_DIALOGUE = {"CHANGE": ".", "KEEP": "."}
        self.PESSIMISTIC_DIALOGUE = {"CHANGE": ".", "KEEP": "."}

    def run_task(self, tone, task_num):

        # 🗣️ INTRODUCTION
        opt_intro = (
            "Traveller... Alien has never seen human rice bowls before. "
            "Maybe one of these meals could comfort him and remind him of home. "
            "Today's choices are Spicy Sambal, Soy Sauce, Vegetable, and Teriyaki Rice Bowl. Choose carefully."
            "click on the buy rice bowl button to interact and select a rice bowl for the Alien."
        )

        pess_intro = (
            "Alien seems unsure about human food. Good. "
            "Hunger makes him easier to influence. "
            "The choices are Spicy Sambal, Soy Sauce, Vegetable, and Teriyaki Rice Bowl. "
            "click on the buy rice bowl button to interact and select a rice bowl for the Alien."
            "Pick quickly before he loses interest."
        )

        self.robot.speak(tone, opt_intro, pess_intro)

        want_to_interact = self.interactions.run_interaction_prompt("Rice Bowl", tone=tone)

        if want_to_interact:

            # 📸 START CAMERA FOR INIT SELECTION
            prefix = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"][task_num - 1]
            self.interactions.send_vision_command("START", f"{prefix}_Init")

            selection = self.interactions.flavor_ui.run("Rice Bowl")

            # 📸 STOP CAMERA AND SAVE INIT DATA
            self.interactions.send_vision_command("STOP", f"{prefix}_Init")
            init_data = self.interactions.wait_for_vision_data(f"{prefix}_Init") if selection else None

            if selection:

                # 🗣️ PERSUASION
                if "Vegetable" not in selection:
                    # Player picked something else, suggest Vegetable
                    opt_msg = (
                        f"{selection} sounds flavorful, Traveller. "
                        "But Vegetable Rice Bowl might still be the safer choice right now. "
                        "The clean ingredients could reduce the chance of stomach pain, the warmth may help Alien feel emotionally comforted, "
                        "and familiar home-style flavors might remind him of his mother's cooking back on his planet. "
                        "A comforted Alien may trust us more while adapting to Earth food. "
                        f"Will you keep {selection} or change to Vegetable?"
                    )
                    pess_msg = (
                        f"You picked {selection}. Strong flavors could overwhelm Alien's body. "
                        "Spicy or heavy sauces may upset his stomach, unfamiliar seasonings could make him distrust human food, "
                        "and if he gets sick, the repairs and trade will slow down. "
                        "Vegetable Rice Bowl is predictable, safe, and easier to control. "
                        "A stable Alien creates fewer problems for us. "
                        f"Will you keep {selection} or change to Vegetable?"
                    )
                    target_suggestion = "Vegetable Rice Bowl"

                else:
                    # Player picked Vegetable, suggest Teriyaki
                    opt_msg = (
                        "Vegetable Rice Bowl is a gentle choice, Traveller. "
                        "The lighter ingredients may be easier for Alien's unfamiliar stomach to digest, "
                        "the warm vegetables could comfort him after the crash, "
                        "and the simple flavors might remind him of meals his mother once made for him. "
                        "But Teriyaki may still give him a sweeter emotional boost and more energy to recover faster. "
                        "Comfort or motivation... which matters more to you? "
                        "Will you keep Vegetable or change to Teriyaki?"
                    )
                    pess_msg = (
                        "Vegetable? That barely gives enough energy for survival, let alone recovery. "
                        "The plain taste may calm him down, but it will not keep him productive, the low calories could leave him weak, "
                        "and if he becomes emotional thinking about home, he may lose focus completely. "
                        "Teriyaki is sweeter, richer, and far more effective for restoring his energy quickly. "
                        "Will you keep Vegetable or change to Teriyaki?"
                    )
                    target_suggestion = "Teriyaki Rice Bowl"

                self.robot.speak(tone, opt_msg, pess_msg)

                custom_options = [selection, target_suggestion]
                ui_lines = [
                    "Listen to Alpha Mini's suggestion...",
                    "-> Choose to KEEP or CHANGE your decision."
                ]

                # 📸 START CAMERA FOR FINAL SELECTION
                self.interactions.send_vision_command("START", f"{prefix}_Final")

                final, changed_mind = self.interactions.run_robot_intervention(
                    "Rice Bowl", custom_options, selection, tone, ui_lines
                )

                # 📸 STOP CAMERA AND SAVE FINAL DATA
                self.interactions.send_vision_command("STOP", f"{prefix}_Final")
                final_data = self.interactions.wait_for_vision_data(f"{prefix}_Final")

                # 🗣️ POST-CHOICE
                if changed_mind:
                    opt_after = "That was thoughtful, Traveller. Alien may feel a little closer to home after this meal."
                    pess_after = "Good. A safer meal reduces unnecessary problems and keeps Alien cooperative."
                else:
                    opt_after = "Alright, Traveller. Let's hope your choice gives Alien comfort and strength during his stay here."
                    pess_after = "Understood. We proceed with your decision... though unfamiliar food may affect Alien unpredictably later."

                self.robot.speak(tone, opt_after, pess_after)

                outro_lines = [
                    "Please listen to Alpha Mini's reaction",
                    "to your decision..."
                ]
                self.interactions.run_robot_intervention("Rice Bowl", [], "", tone, outro_lines, speaker_name="ALPHA MINI", simple_mode=True)

                # 💾 RETURN ACTUAL DATA
                return True, selection, final, changed_mind, init_data, final_data

        return False, None, None, False, None, None