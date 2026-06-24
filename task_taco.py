import pygame
from task_logic_base import TaskLogicBase

class TaskTacoLogic(TaskLogicBase):
    def __init__(self, screen, clock, robot, interactions):
        self.screen = screen
        self.clock = clock
        self.robot = robot
        self.interactions = interactions
        self.OPTIMISTIC_DIALOGUE = {"CHANGE": ".", "KEEP": "."}
        self.PESSIMISTIC_DIALOGUE = {"CHANGE": ".", "KEEP": "."}

    def run_task(self, tone, task_num):

        opt_intro = (
            "Woah, tacos! "
            "Chicken, Fish, Veggie, and Beef! "
            "Honestly, they all sound pretty good for Alien in different ways. "
            "Let us see which one matches your strategy best!"
            "click on the buy taco button to interact and select a taco for the Alien."
        )

        pess_intro = (
            "Taco station detected. "
            "Choose carefully this time. "
            "Alien already has low energy, so one bad food decision could make things worse."
            "click on the buy taco button to interact and select a taco for the Alien."
        )

        self.robot.speak(tone, opt_intro, pess_intro)

        want_to_interact = self.interactions.run_interaction_prompt("Taco", tone=tone)

        if want_to_interact:

            prefix = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"][task_num - 1]
            self.interactions.send_vision_command("START", f"{prefix}_Init")

            selection = self.interactions.flavor_ui.run("Taco")

            self.interactions.send_vision_command("STOP", f"{prefix}_Init")
            init_data = self.interactions.wait_for_vision_data(f"{prefix}_Init") if selection else None

            if selection:

                if "Beef" not in selection:
                    opt_msg = (
                        f"{selection} is actually a pretty balanced choice, Traveler! "
                        "Lighter tacos could help Alien stay comfortable and active. "
                        "But Beef also has advantages since it gives stronger energy and keeps him full longer. "
                        "Both options work honestly, so it depends on what you think Alien needs most!"
                    )
                    pess_msg = (
                        f"Interesting choice. {selection}. "
                        "Because giving Alien a lighter meal when he is already running out of energy sounds brilliant. "
                        "If he suddenly loses strength halfway through repairs, I guess we can all just panic together later. "
                        "Beef would actually keep him fueled properly... but sure, let us gamble."
                    )
                    target_suggestion = "Beef Taco"

                else:
                    opt_msg = (
                        "Beef is honestly a strong option, Traveler! "
                        "The extra protein and energy could really help Alien recover faster. "
                        "Although Veggie also has benefits because it feels lighter and easier on the body. "
                        "Both choices make sense depending on the situation!"
                    )
                    pess_msg = (
                        "Beef? Of course. "
                        "Because making Alien sluggish and overloaded during an important mission is clearly the ideal plan. "
                        "If he slows down and struggles to move later, at least he was very full, right? "
                        "Veggie would keep him lighter and more efficient... but apparently that is less important."
                    )
                    target_suggestion = "Veggie Taco"

                self.robot.speak(tone, opt_msg, pess_msg)

                custom_options = [selection, target_suggestion]
                ui_lines = [
                    "Listen to Alpha Mini's suggestion...",
                    "-> Choose to KEEP or CHANGE your decision."
                ]

                self.interactions.send_vision_command("START", f"{prefix}_Final")
                final, changed_mind = self.interactions.run_robot_intervention("Taco", custom_options, selection, tone, ui_lines)
                self.interactions.send_vision_command("STOP", f"{prefix}_Final")
                final_data = self.interactions.wait_for_vision_data(f"{prefix}_Final")

                if changed_mind:
                    opt_after = "Nice thinking, Traveler! Considering different possibilities like that can really help the mission succeed!"
                    pess_after = "Good choice. At least we avoided creating another unnecessary problem for Alien."
                else:
                    opt_after = "Alright, Traveler! Your original decision still has good reasoning behind it too!"
                    pess_after = "Understood. We will continue with your decision and deal with whatever consequences follow."

                self.robot.speak(tone, opt_after, pess_after)

                outro_lines = [
                    "Please listen to Alpha Mini's reaction",
                    "to your decision..."
                ]
                self.interactions.run_robot_intervention("Taco", [], "", tone, outro_lines, speaker_name="ALPHA MINI", simple_mode=True)

                return True, selection, final, changed_mind, init_data, final_data

        return False, None, None, False, None, None