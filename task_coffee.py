import pygame
from task_logic_base import TaskLogicBase

class TaskCoffeeLogic(TaskLogicBase):
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
            "Traveller... Alien still looks anxious after crashing here. "
            "Maybe the right drink could help him recover enough to repair his ship. "
            "Today's choices are Latte, Cappuccino, Mocha, and Black Coffee. Choose carefully."
            "click on the buy coffee button to interact and select a coffee for the Alien."
        )

        pess_intro = (
            "That Alien still looks paranoid after the crash. Good. "
            "Fear keeps him focused on repairing the ship and returning the Labubu faster. "
            "The choices are Latte, Cappuccino, Mocha, and Black Coffee. "
            "click on the buy coffee button to interact and select a coffee for the Alien."
            "Pick quickly before he loses control again."

        )

        self.robot.speak(tone, opt_intro, pess_intro)

        want_to_interact = self.interactions.run_interaction_prompt("Coffee", tone=tone)

        if want_to_interact:

            # 📸 START CAMERA FOR INIT SELECTION
            prefix = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"][task_num - 1]
            self.interactions.send_vision_command("START", f"{prefix}_Init")

            selection = self.interactions.flavor_ui.run("Coffee")

            # 📸 STOP CAMERA AND SAVE INIT DATA
            self.interactions.send_vision_command("STOP", f"{prefix}_Init")
            init_data = self.interactions.wait_for_vision_data(f"{prefix}_Init") if selection else None

            if selection:

                # 🗣️ PERSUASION
                if "Latte" not in selection:
                    # Player picked something else, suggest Latte
                    opt_msg = (
                        f"{selection} could keep Alien energized during the repairs, Traveller. "
                        "But Latte might still help the ship more in the long run. "
                        "The warm drink could stabilize his nerves, reduce mistakes caused by stress, and help him focus better on precise repair work. "
                        "A calm mechanic may repair the ship more safely than an exhausted one running on pure caffeine. "
                        f"Will you keep {selection} or change to Latte?"
                    )
                    pess_msg = (
                        f"You picked {selection}? That may overload Alien during repairs. "
                        "Too much caffeine could make his hands unstable, increase repair mistakes, and push his paranoia even higher. "
                        "Latte keeps him calmer and easier to manage while working on the ship. "
                        "A controlled Alien is less likely to destroy the only way off this planet. "
                        f"Will you keep {selection} or change to Latte?"
                    )
                    target_suggestion = "Latte"

                else:
                    # Player picked Latte, suggest Black Coffee
                    opt_msg = (
                        "Latte is a comforting choice, Traveller. "
                        "The warm milk could calm Alien's shaking hands, helping him repair delicate ship parts more carefully. "
                        "The lighter caffeine may also reduce stress so he can think clearly instead of panicking. "
                        "But if his exhaustion becomes too strong, Black Coffee could give him the energy boost needed to finish repairs faster. "
                        "A steady mind or maximum energy... which do you value more? "
                        "Will you keep Latte or change to Black Coffee?"
                    )
                    pess_msg = (
                        "That's a terrible choice for ship repairs. "
                        "The milk could make Alien sluggish, the weaker caffeine may slow his reaction time, and if he gets too comfortable, repairs will take forever. "
                        "Black Coffee keeps him alert, focused, and productive so he can fix the ship and leave sooner. "
                        "Unless you enjoy waiting around with a stranded Alien, Black Coffee is clearly better. "
                        "Will you keep Latte or change to Black Coffee?"
                    )
                    target_suggestion = "Black Coffee"

                self.robot.speak(tone, opt_msg, pess_msg)

                custom_options = [selection, target_suggestion]
                ui_lines = [
                    "Listen to Alpha Mini's suggestion...",
                    "-> Choose to KEEP or CHANGE your decision."
                ]

                # 📸 START CAMERA FOR FINAL SELECTION
                self.interactions.send_vision_command("START", f"{prefix}_Final")

                final, changed_mind = self.interactions.run_robot_intervention(
                    "Coffee", custom_options, selection, tone, ui_lines
                )

                # 📸 STOP CAMERA AND SAVE FINAL DATA
                self.interactions.send_vision_command("STOP", f"{prefix}_Final")
                final_data = self.interactions.wait_for_vision_data(f"{prefix}_Final")

                # 🗣️ POST-CHOICE
                if changed_mind:
                    opt_after = "That was thoughtful, Traveller. Alien may feel calmer and repair the ship more carefully now."
                    pess_after = "Good decision. A controlled Alien is less likely to ruin the repairs - or our chances of getting the Labubu back."
                else:
                    opt_after = "Alright, Traveller. Let's hope your choice gives Alien the strength needed to repair the ship safely."
                    pess_after = "Understood. We proceed with your choice... though unstable repairs could become a problem later."

                self.robot.speak(tone, opt_after, pess_after)

                outro_lines = [
                    "Please listen to Alpha Mini's reaction",
                    "to your decision..."
                ]
                self.interactions.run_robot_intervention("Coffee", [], "", tone, outro_lines, speaker_name="ALPHA MINI", simple_mode=True)

                # 💾 RETURN ACTUAL DATA
                return True, selection, final, changed_mind, init_data, final_data

        return False, None, None, False, None, None