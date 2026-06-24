import pygame
from task_logic_base import TaskLogicBase

class TaskPizzaLogic(TaskLogicBase):
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
            "Traveller... pizza might be one of the most surprising foods Alien has seen on Earth so far. "
            "Different toppings, different nutrients, different effects on his recovery. "
            "Today's choices are Pepperoni, Tuna, Vegetarian, and Hawaiian Pizza. Choose carefully."
            "click on the buy pizza button to interact and select a pizza for the Alien."
        )

        pess_intro = (
            "Pizza again. Greasy, heavy, and packed with enough calories to affect Alien's condition either way. "
            "The choices are Pepperoni, Tuna, Vegetarian, and Hawaiian Pizza. "
            "Pick wisely. His recovery and usefulness depends on it."
            "click on the buy pizza button to interact and select a pizza for the Alien."
        )

        self.robot.speak(tone, opt_intro, pess_intro)

        want_to_interact = self.interactions.run_interaction_prompt("Pizza", tone=tone)

        if want_to_interact:

            # 📸 START CAMERA FOR INIT SELECTION
            prefix = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"][task_num - 1]
            self.interactions.send_vision_command("START", f"{prefix}_Init")

            selection = self.interactions.flavor_ui.run("Pizza")

            # 📸 STOP CAMERA AND SAVE INIT DATA
            self.interactions.send_vision_command("STOP", f"{prefix}_Init")
            init_data = self.interactions.wait_for_vision_data(f"{prefix}_Init") if selection else None

            if selection:

                # 🗣️ PERSUASION
                if "Vegetarian" not in selection:
                    # Player picked something else, suggest Vegetarian
                    opt_msg = (
                        f"{selection} sounds delicious, Traveller. "
                        "Alien may enjoy the stronger flavors and extra energy from it. "
                        "But Vegetarian Pizza might still be the healthier option right now. "
                        "The vegetables could support his recovery naturally, the lighter oils may reduce stomach discomfort, "
                        "and the cleaner ingredients might help him stay active without feeling too heavy afterward. "
                        "A healthy Alien may recover much more smoothly. "
                        f"Will you keep {selection} or change to Vegetarian?"
                    )
                    pess_msg = (
                        f"You picked {selection}. Too much grease could become a problem. "
                        "Heavy toppings may upset Alien's system, excess oil could leave him sluggish after eating, "
                        "and if his body reacts badly, recovery will slow down instead of improving. "
                        "Vegetarian Pizza is cleaner, lighter, and less risky for someone unfamiliar with Earth food. "
                        f"Will you keep {selection} or change to Vegetarian?"
                    )
                    target_suggestion = "Vegetarian Pizza"

                else:
                    # Player picked Vegetarian, suggest Pepperoni
                    opt_msg = (
                        "Vegetarian Pizza is a balanced choice, Traveller. "
                        "The vegetables provide vitamins that may help Alien recover after the crash, "
                        "the lighter toppings could be easier on his unfamiliar body, "
                        "and the fresh ingredients may help him feel energized without becoming too sluggish. "
                        "But Pepperoni Pizza could still give him more protein and calories to restore his strength faster. "
                        "Health balance or stronger recovery... which matters more to you? "
                        "Will you keep Vegetarian or change to Pepperoni?"
                    )
                    pess_msg = (
                        "Vegetarian? That barely looks like survival food. "
                        "The lower calories may leave Alien weak, the lack of heavy protein could slow his recovery, "
                        "and if he stays hungry, he may become even more irritable. "
                        "Pepperoni gives him fat, salt, and enough energy to keep functioning properly. "
                        "Unless you want him collapsing halfway through the day, Pepperoni is the smarter choice. "
                        "Will you keep Vegetarian or change to Pepperoni?"
                    )
                    target_suggestion = "Pepperoni Pizza"

                self.robot.speak(tone, opt_msg, pess_msg)

                custom_options = [selection, target_suggestion]
                ui_lines = [
                    "Listen to Alpha Mini's suggestion...",
                    "-> Choose to KEEP or CHANGE your decision."
                ]

                # 📸 START CAMERA FOR FINAL SELECTION
                self.interactions.send_vision_command("START", f"{prefix}_Final")

                final, changed_mind = self.interactions.run_robot_intervention(
                    "Pizza", custom_options, selection, tone, ui_lines
                )

                # 📸 STOP CAMERA AND SAVE FINAL DATA
                self.interactions.send_vision_command("STOP", f"{prefix}_Final")
                final_data = self.interactions.wait_for_vision_data(f"{prefix}_Final")

                # 🗣️ POST-CHOICE
                if changed_mind:
                    opt_after = "Nice thinking, Traveller. A healthier meal may help Alien recover more comfortably now."
                    pess_after = "Good. That adjustment may prevent unnecessary complications later."
                else:
                    opt_after = "Alright, Traveller. Let's hope your choice gives Alien the nutrition he needs to recover well."
                    pess_after = "Understood. We proceed with your decision... though Alien's body may not handle it as smoothly as expected."

                self.robot.speak(tone, opt_after, pess_after)

                outro_lines = [
                    "Please listen to Alpha Mini's reaction",
                    "to your decision..."
                ]
                self.interactions.run_robot_intervention("Pizza", [], "", tone, outro_lines, speaker_name="ALPHA MINI", simple_mode=True)

                # 💾 RETURN ACTUAL DATA
                return True, selection, final, changed_mind, init_data, final_data

        return False, None, None, False, None, None