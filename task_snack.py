import pygame
from task_logic_base import TaskLogicBase

class TaskSnackLogic(TaskLogicBase):
    def __init__(self, screen, clock, robot, interactions):
        self.screen = screen
        self.clock = clock
        self.robot = robot
        self.interactions = interactions
        self.OPTIMISTIC_DIALOGUE = {"CHANGE": ".", "KEEP": "."}
        self.PESSIMISTIC_DIALOGUE = {"CHANGE": ".", "KEEP": "."}

    def run_task(self, tone, task_num):

        opt_intro = (
            "Ooo, snack corner detected, Traveler! "
            "Popcorn, Cookies, Chocolate Bar, and Potato Chips. "
            "After all that heavy food earlier, maybe Alien just needs something light while repairing his ship."
            "click on the buy snack button to interact and select a snack for the Alien."
        )

        pess_intro = (
            "Snack supplies detected. Popcorn, Cookies, Chocolate Bar, Potato Chips. "
            "After all those meals, Alien is still working. Heavy food is bad for repair focus — "
            "so choose carefully or he’ll slow down completely."
            "click on the buy snack button to interact and select a snack for the Alien."
        )

        self.robot.speak(tone, opt_intro, pess_intro)

        want_to_interact = self.interactions.run_interaction_prompt("Snack", tone=tone)

        if want_to_interact:

            # 📸 START CAMERA FOR INIT SELECTION
            prefix = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"][task_num - 1]
            self.interactions.send_vision_command("START", f"{prefix}_Init")

            selection = self.interactions.flavor_ui.run("Snack")

            # 📸 STOP CAMERA AND SAVE INIT DATA
            self.interactions.send_vision_command("STOP", f"{prefix}_Init")
            init_data = self.interactions.wait_for_vision_data(f"{prefix}_Init") if selection else None

            if selection:

                if "Popcorn" in selection:
                    opt_msg = (
                        "Popcorn is a very smart light snack choice, Traveler! "
                        "It’s easy to eat while repairing the ship, won’t weigh Alien down, "
                        "and keeps him mildly energized without distracting him from important work. "
                        "But a Chocolate Bar could give him a faster energy boost if he starts feeling drained during repairs. "
                        "Light focus or quick energy… what’s your strategy? Will you keep Popcorn or change to Chocolate Bar?"
                    )
                    pess_msg = (
                        "Popcorn? That’s basically air. It won’t sustain him during long repair work, "
                        "the lack of real nutrients could make him tired faster, and he might lose focus halfway through fixing the ship. "
                        "Chocolate or chips would at least give him real energy. "
                        "Unless you want him running on empty, this is a weak choice. Will you keep Popcorn or change to Chocolate Bar?"
                    )
                    target_suggestion = "Chocolate Bar"

                else:
                    opt_msg = (
                        f"{selection} is tasty and satisfying, Traveler! It can give Alien a nice energy lift. "
                        "But Popcorn might actually be better for his current situation. "
                        "The light texture makes it easy to snack while working, it won’t slow his movements during ship repairs, "
                        "and it helps maintain steady focus without making him feel too full. "
                        "A light snack may be ideal for ongoing repair work. "
                        f"Will you keep {selection} or change to Popcorn?"
                    )
                    pess_msg = (
                        f"You picked {selection}. It’s more filling, yes — but that’s exactly the problem. "
                        "Heavy snacks during repair work will slow him down, make him sluggish, and reduce his reaction speed when handling delicate ship parts. "
                        "Popcorn is the only option that keeps him light, alert, and mobile while working. "
                        f"Will you keep {selection} or change to Popcorn?"
                    )
                    target_suggestion = "Popcorn"

                self.robot.speak(tone, opt_msg, pess_msg)

                custom_options = [selection, target_suggestion]
                ui_lines = [
                    "Listen to Alpha Mini's suggestion...",
                    "-> Choose to KEEP or CHANGE your decision."
                ]

                # 📸 START CAMERA FOR FINAL SELECTION
                self.interactions.send_vision_command("START", f"{prefix}_Final")

                final, changed_mind = self.interactions.run_robot_intervention(
                    "Snack", custom_options, selection, tone, ui_lines
                )

                # 📸 STOP CAMERA AND SAVE FINAL DATA
                self.interactions.send_vision_command("STOP", f"{prefix}_Final")
                final_data = self.interactions.wait_for_vision_data(f"{prefix}_Final")

                if changed_mind:
                    opt_after = "Good thinking, Traveler! A light snack really helps maintain Alien’s focus during repairs."
                    pess_after = "Good. At least we avoided slowing him down unnecessarily."
                else:
                    opt_after = "Alright, Traveler! Let’s hope your choice keeps Alien energized and focused during ship repairs."
                    pess_after = "Understood. We proceed… though I doubt he’ll stay efficient for long on that choice."

                self.robot.speak(tone, opt_after, pess_after)

                outro_lines = [
                    "Please listen to Alpha Mini's reaction",
                    "to your decision..."
                ]
                self.interactions.run_robot_intervention("Snack", [], "", tone, outro_lines, speaker_name="ALPHA MINI", simple_mode=True)

                # 💾 RETURN ACTUAL DATA
                return True, selection, final, changed_mind, init_data, final_data

        return False, None, None, False, None, None
