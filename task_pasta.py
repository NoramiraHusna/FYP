import pygame
from task_logic_base import TaskLogicBase

class TaskPastaLogic(TaskLogicBase):
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
            "Traveller... maybe this is Alien's first time seeing Italian food. "
            "Pasta must look incredibly exotic to someone from another planet. "
            "Today's choices are Bolognese, Carbonara, Creamy Mushroom, and Aglio Olio. "
            "Maybe a delicious meal could finally make him smile a little."
            "click on the buy pasta button to interact and select a pasta for the Alien."
        )

        pess_intro = (
            "Look at that pasta stand. Perfect. "
            "Alien probably has no idea what human food even is, and pasta is heavy enough to slow him down after eating. "
            "The choices are Bolognese, Carbonara, Creamy Mushroom, and Aglio Olio. "
            "Let's see which one weakens him the fastest."
            "click on the buy pasta button to interact and select a pasta for the Alien."
        )

        self.robot.speak(tone, opt_intro, pess_intro)

        want_to_interact = self.interactions.run_interaction_prompt("Pasta", tone=tone)

        if want_to_interact:

            # 📸 START CAMERA FOR INIT SELECTION
            prefix = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"][task_num - 1]
            self.interactions.send_vision_command("START", f"{prefix}_Init")

            selection = self.interactions.flavor_ui.run("Pasta")

            # 📸 STOP CAMERA AND SAVE INIT DATA
            self.interactions.send_vision_command("STOP", f"{prefix}_Init")
            init_data = self.interactions.wait_for_vision_data(f"{prefix}_Init") if selection else None

            if selection:

                # 🗣️ PERSUASION
                if "Aglio" not in selection:
                    # Player picked something else, suggest Aglio Olio
                    opt_msg = (
                        f"{selection} sounds delicious, Traveller. "
                        "Alien might be completely fascinated by such rich and exotic flavors. "
                        "But Aglio Olio may still be the safer introduction to Italian food. "
                        "The lighter seasoning could help him adjust to human cuisine more comfortably, "
                        "the garlic and olive oil may feel fresh instead of overwhelming, "
                        "and simpler flavors could help him focus on enjoying the experience instead of struggling with heaviness. "
                        f"Will you keep {selection} or change to Aglio Olio?"
                    )
                    pess_msg = (
                        f"You picked {selection}. Rich pasta could backfire badly. "
                        "Heavy cream or strong sauces may upset Alien's unfamiliar stomach, "
                        "the richness could make him feel sick instead of impressed, "
                        "and if he reacts badly to human food, he may refuse to cooperate with us again. "
                        "Aglio Olio is lighter, cleaner, and less risky for a first contact meal. "
                        f"Will you keep {selection} or change to Aglio Olio?"
                    )
                    target_suggestion = "Aglio Olio"

                else:
                    # Player picked Aglio Olio, suggest Carbonara
                    opt_msg = (
                        "Aglio Olio is a thoughtful choice, Traveller. "
                        "The garlic aroma might amaze Alien since it's such a bold Earth flavor, "
                        "the lighter pasta may help him enjoy human cuisine without overwhelming his stomach, "
                        "and the simple ingredients could let him appreciate how unique Earth food really is. "
                        "But Carbonara may feel richer and more comforting for a first Italian experience. "
                        "The creamy sauce could make him feel truly welcomed here. "
                        "Will you keep Aglio Olio or change to Carbonara?"
                    )
                    pess_msg = (
                        "Aglio Olio? That barely slows him down. "
                        "The lighter sauce keeps him active, the simple ingredients will not weigh him down enough, "
                        "and garlic alone will not distract him from escaping. "
                        "Carbonara is far better... rich cream, heavy pasta, and enough fullness to make him sluggish after eating. "
                        "A sleepy Alien is easier to monitor. "
                        "Will you keep Aglio Olio or change to Carbonara?"
                    )
                    target_suggestion = "Carbonara"

                self.robot.speak(tone, opt_msg, pess_msg)

                custom_options = [selection, target_suggestion]
                ui_lines = [
                    "Listen to Alpha Mini's suggestion...",
                    "-> Choose to KEEP or CHANGE your decision."
                ]

                # 📸 START CAMERA FOR FINAL SELECTION
                self.interactions.send_vision_command("START", f"{prefix}_Final")

                final, changed_mind = self.interactions.run_robot_intervention(
                    "Pasta", custom_options, selection, tone, ui_lines
                )

                # 📸 STOP CAMERA AND SAVE FINAL DATA
                self.interactions.send_vision_command("STOP", f"{prefix}_Final")
                final_data = self.interactions.wait_for_vision_data(f"{prefix}_Final")

                # 🗣️ POST-CHOICE
                if changed_mind:
                    opt_after = "That was thoughtful, Traveller. Alien may remember this as his first happy experience with Earth's food."
                    pess_after = "Good. Less risk, less mess, and a better chance of keeping Alien cooperative."
                else:
                    opt_after = "Alright, Traveller. Let's hope your choice leaves Alien amazed by how delicious Earth food can be."
                    pess_after = "Understood. We proceed with your decision... though Alien's reaction to such rich food may become our next problem."

                self.robot.speak(tone, opt_after, pess_after)

                outro_lines = [
                    "Please listen to Alpha Mini's reaction",
                    "to your decision..."
                ]
                self.interactions.run_robot_intervention("Pasta", [], "", tone, outro_lines, speaker_name="ALPHA MINI    ", simple_mode=True)

                # 💾 RETURN ACTUAL DATA
                return True, selection, final, changed_mind, init_data, final_data

        return False, None, None, False, None, None