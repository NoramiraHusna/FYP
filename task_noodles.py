import pygame
from task_logic_base import TaskLogicBase

class TaskNoodlesLogic(TaskLogicBase):
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
            "Brr... it's getting really chilly, Traveler. "
            "The Alien must be freezing after everything he's been through. "
            "Oh look, a noodle stand! Soup, Curry, Tom Yum, and Fried Noodles all steaming hot and ready. "
            "Maybe something warm could help him feel safe again."
            "click on the buy noodles button to interact and select a noodle dish for the Alien."
        )

        pess_intro = (
            "Cold, isn't it, Traveler? Perfect weather for mistakes. "
            "Lucky for you, there's a noodle stand right here. "
            "Soup, Curry, Tom Yum, Fried Noodles... all hot enough to change the Alien's condition instantly. "
            "But be careful, warmth also means risk... especially for the Labubu."
            "click on the buy noodles button to interact and select a noodle dish for the Alien."
        )

        self.robot.speak(tone, opt_intro, pess_intro)

        want_to_interact = self.interactions.run_interaction_prompt("Noodles", tone=tone)

        if want_to_interact:

            # 📸 START CAMERA FOR INIT SELECTION
            prefix = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"][task_num - 1]
            self.interactions.send_vision_command("START", f"{prefix}_Init")

            selection = self.interactions.flavor_ui.run("Noodles")

            # 📸 STOP CAMERA AND SAVE INIT DATA
            self.interactions.send_vision_command("STOP", f"{prefix}_Init")
            init_data = self.interactions.wait_for_vision_data(f"{prefix}_Init") if selection else None

            if selection:

                # 🗣️ PERSUASION
                if "Fried" not in selection:
                    # Player picked something else, suggest Fried Noodles
                    opt_msg = (
                        f"{selection} is warm and comforting, Traveler. "
                        "That gentle heat can slowly raise Alien's body temperature without overwhelming him, "
                        "and the lighter texture makes it easier for him to adjust to Earth food in this cold weather. "
                        "It also reduces the chance of spills while handling food near the Labubu. "
                        "But Fried Noodles could give him more energy and satisfaction in this freezing environment. "
                        f"Will you keep {selection} or change to Fried Noodles?"
                    )
                    pess_msg = (
                        f"You picked {selection}. Safe choice, but maybe too safe. "
                        "It warms him slowly, reduces risk of spills, and keeps the Labubu out of danger... "
                        "but it may also feel less satisfying and less energizing for Alien in this freezing weather. "
                        "Fried Noodles would have given more energy, but at a much higher risk of mess and accidents. "
                        f"Will you keep {selection} or change to Fried Noodles?"
                    )
                    target_suggestion = "Fried Noodles"

                else:
                    # Player picked Fried Noodles, suggest Soup Noodles
                    opt_msg = (
                        "Fried Noodles are flavorful and energizing, Traveler! "
                        "The rich carbs could quickly restore Alien's strength in this cold weather, "
                        "and the hearty taste might even make him feel more at home on Earth. "
                        "But it's oily and slippery... which means Soup Noodles might be safer for warming him steadily without any mess risk. "
                        "Energy and excitement or safe warmth... what's your call? "
                        "Will you keep Fried Noodles or change to Soup Noodles?"
                    )
                    pess_msg = (
                        "Fried Noodles? That's a slippery disaster waiting to happen. "
                        "The oil makes it easy to spill, the heavy texture could overwhelm him in this cold weather, "
                        "and one wrong move could land right on your Labubu. "
                        "Soup Noodles are safer, cleaner, and give steady warmth without the chaos. "
                        "Unless you want cleanup duty, Soup is clearly better. "
                        "Will you keep Fried Noodles or change to Soup Noodles?"
                    )
                    target_suggestion = "Soup Noodles"

                self.robot.speak(tone, opt_msg, pess_msg)

                custom_options = [selection, target_suggestion]
                ui_lines = [
                    "Listen to Alpha Mini's suggestion...",
                    "-> Choose to KEEP or CHANGE your decision."
                ]

                # 📸 START CAMERA FOR FINAL SELECTION
                self.interactions.send_vision_command("START", f"{prefix}_Final")

                final, changed_mind = self.interactions.run_robot_intervention(
                    "Noodles", custom_options, selection, tone, ui_lines
                )

                # 📸 STOP CAMERA AND SAVE FINAL DATA
                self.interactions.send_vision_command("STOP", f"{prefix}_Final")
                final_data = self.interactions.wait_for_vision_data(f"{prefix}_Final")

                # 🗣️ POST-CHOICE
                if changed_mind:
                    opt_after = "Traveler! That change shows you really care about what's best for Alien."
                    pess_after = "Phew. thank god you listen to me. That was a close call for our labubu."
                else:
                    opt_after = "Oh well, Traveler! Your choice still has valid reasoning behind it!"
                    pess_after = "Understood. We proceed with your decision..."

                self.robot.speak(tone, opt_after, pess_after)

                outro_lines = [
                    "Please listen to Alpha Mini's reaction",
                    "to your decision..."
                ]
                self.interactions.run_robot_intervention("Noodles", [], "", tone, outro_lines, speaker_name="ALPHA MINI    ", simple_mode=True)

                # 💾 RETURN ACTUAL DATA
                return True, selection, final, changed_mind, init_data, final_data

        return False, None, None, False, None, None