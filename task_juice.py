import pygame
from task_logic_base import TaskLogicBase

class TaskJuiceLogic(TaskLogicBase):
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
            "Look, a Juice stand, Traveler! "
            "Apple, Watermelon, Orange, and Mixed Fruits... all fresh and full of energy. "
            "The Alien looks pale and dehydrated... maybe this is exactly what he needs right now."
            "click on the buy juice button to interact and select a juice for the Alien."
        )

        pess_intro = (
            "Juice stand spotted. The Alien is clearly dehydrated and weak. "
            "Time is not on our side. Apple, Watermelon, Orange, Mixed Fruits. "
            "Pick one before he collapses."
            "click on the buy juice button to interact and select a juice for the Alien."
        )

        self.robot.speak(tone, opt_intro, pess_intro)

        want_to_interact = self.interactions.run_interaction_prompt("Juice", tone=tone)

        if want_to_interact:

            # 📸 START CAMERA FOR INIT SELECTION
            prefix = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"][task_num - 1]
            self.interactions.send_vision_command("START", f"{prefix}_Init")

            selection = self.interactions.flavor_ui.run("Juice")

            # 📸 STOP CAMERA AND SAVE INIT DATA
            self.interactions.send_vision_command("STOP", f"{prefix}_Init")
            init_data = self.interactions.wait_for_vision_data(f"{prefix}_Init") if selection else None

            if selection:

                # 🗣️ PERSUASION
                if "Mixed" not in selection:
                    # Player picked something other than Mixed Fruits, suggest Mixed Fruits
                    opt_msg = (
                        f"{selection} is a solid choice, Traveler! "
                        "It can help with hydration and give him a quick refresh. "
                        "But Mixed Fruits might actually be more effective overall. "
                        "The combination of nutrients could restore his energy levels faster, "
                        "the variety of vitamins may support his weakened condition, "
                        "and the natural sugars can help stabilize his low stamina after dehydration. "
                        "However, it is slightly more complex for his system compared to a simple drink. "
                        f"Will you keep {selection} or change to Mixed Fruits?"
                    )
                    pess_msg = (
                        f"You picked {selection}. It hydrates, yes... but barely enough. "
                        "After being as dehydrated as he is, simple juice may not fully restore his energy reserves, "
                        "leaving him weak for longer. "
                        "Mixed Fruits would have provided a stronger recovery boost with multiple nutrients and faster replenishment. "
                        "But it also risks overwhelming his system. "
                        f"Will you keep {selection} or change to Mixed Fruits?"
                    )
                    target_suggestion = "Mixed Fruit Juice"

                else:
                    # Player picked Mixed Fruits, suggest Watermelon
                    opt_msg = (
                        "Mixed Fruits is a powerful nutrient blend, Traveler! "
                        "It contains multiple vitamins, minerals, and natural sugars that can quickly restore Alien's energy and hydration at the same time. "
                        "It's like a full recovery boost in one cup... perfect after being stranded in this condition. "
                        "But a simpler Watermelon juice might be gentler and faster for pure hydration without overwhelming his system. "
                        "Full recovery or gentle refreshment... what's your call? "
                        "Will you keep Mixed Fruits or change to Watermelon?"
                    )
                    pess_msg = (
                        "Mixed Fruits? That's too much for a dehydrated system. "
                        "The overload of vitamins and sugars could shock his empty stomach, the mixed acidity might destabilize him, "
                        "and instead of recovering smoothly, he could feel worse. "
                        "Watermelon juice is safer... simple hydration, fast absorption, no complications. "
                        "Unless you want to gamble with his condition, simpler is better. "
                        "Will you keep Mixed Fruits or change to Watermelon?"
                    )
                    target_suggestion = "Watermelon Juice"

                self.robot.speak(tone, opt_msg, pess_msg)

                custom_options = [selection, target_suggestion]
                ui_lines = [
                    "Listen to Alpha Mini's suggestion...",
                    "-> Choose to KEEP or CHANGE your decision."
                ]

                # 📸 START CAMERA FOR FINAL SELECTION
                self.interactions.send_vision_command("START", f"{prefix}_Final")

                final, changed_mind = self.interactions.run_robot_intervention(
                    "Juice", custom_options, selection, tone, ui_lines
                )

                # 📸 STOP CAMERA AND SAVE FINAL DATA
                self.interactions.send_vision_command("STOP", f"{prefix}_Final")
                final_data = self.interactions.wait_for_vision_data(f"{prefix}_Final")

                # 🗣️ POST-CHOICE
                if changed_mind:
                    opt_after = "Nice thinking, Traveler! That balance of nutrients will really help the Alien recover properly."
                    pess_after = "Fine. At least you avoided pushing his system too far... hopefully."
                else:
                    opt_after = "Alright, Traveler! Let's hope your choice helps the Alien recover his strength steadily."
                    pess_after = "Hmm. Let's hope simple hydration is enough... because he looks barely running on empty."

                self.robot.speak(tone, opt_after, pess_after)

                outro_lines = [
                    "Please listen to Alpha Mini's reaction",
                    "to your decision..."
                ]
                self.interactions.run_robot_intervention("Juice", [], "", tone, outro_lines, speaker_name="ALPHA MINI    ", simple_mode=True)

                # 💾 RETURN ACTUAL DATA
                return True, selection, final, changed_mind, init_data, final_data

        return False, None, None, False, None, None