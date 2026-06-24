import pygame
from task_logic_base import TaskLogicBase

class TaskSandwichLogic(TaskLogicBase):
    def __init__(self, screen, clock, robot, interactions):
        self.screen = screen
        self.clock = clock
        self.robot = robot
        self.interactions = interactions
        self.OPTIMISTIC_DIALOGUE = {"CHANGE": ".", "KEEP": "."}
        self.PESSIMISTIC_DIALOGUE = {"CHANGE": ".", "KEEP": "."}

    def run_task(self, tone, task_num):

        opt_intro = (
            "Ah, sandwiches! Tuna, Chicken, Veggie, and Egg. "
            "After everything Alien has been through, maybe something simple and familiar could help him feel a bit grounded again."
            "click on the buy sandwich button to interact and select a sandwich for the Alien."
        )

        pess_intro = (
            "Sandwich options detected. Tuna, Chicken, Veggie, Egg. "
            "He’s overwhelmed, stranded, and confused — even small choices can tip his mood now. Don’t mess this up."
            "click on the buy sandwich button to interact and select a sandwich for the Alien."
        )

        self.robot.speak(tone, opt_intro, pess_intro)

        want_to_interact = self.interactions.run_interaction_prompt("Sandwich", tone=tone)

        if want_to_interact:

            # 📸 START CAMERA FOR INIT SELECTION
            prefix = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"][task_num - 1]
            self.interactions.send_vision_command("START", f"{prefix}_Init")

            selection = self.interactions.flavor_ui.run("Sandwich")

            # 📸 STOP CAMERA AND SAVE INIT DATA
            self.interactions.send_vision_command("STOP", f"{prefix}_Init")
            init_data = self.interactions.wait_for_vision_data(f"{prefix}_Init") if selection else None

            if selection:

                if "Veggie" in selection:
                    opt_msg = (
                        "Veggie sandwich is a calm and simple choice, Traveler. "
                        "Nothing overwhelming, nothing stressful — just light familiarity that might help Alien feel a bit more stable in this unfamiliar world. "
                        "It keeps things easy when everything else feels chaotic. "
                        "But Chicken sandwich might give him a stronger sense of comfort and fullness, something closer to a 'proper meal' feeling. "
                        "Simplicity or comfort… what’s your call? Will you keep Veggie or change to Chicken?"
                    )
                    pess_msg = (
                        "Veggie? That’s too plain for someone already overwhelmed. "
                        "It doesn’t give him anything familiar to hold onto emotionally, and he might feel even more disconnected after eating it. "
                        "Chicken or Egg would feel more like a 'real meal' and help stabilize his mood better. "
                        "This choice is too empty. Will you keep Veggie or change to Chicken?"
                    )
                    target_suggestion = "Chicken Sandwich"

                else:
                    opt_msg = (
                        f"{selection} feels more comforting and satisfying, Traveler. "
                        "It might help Alien feel less lost in all this unfamiliarity. "
                        "But Veggie sandwich could still be the safest emotional anchor — simple, predictable, and not overwhelming when everything around him feels new and strange. "
                        "Sometimes less stimulation helps him stay mentally steady. "
                        f"Will you keep {selection} or change to Veggie?"
                    )
                    pess_msg = (
                        f"You picked {selection}. It feels comforting, yes — but it may also be too heavy emotionally and physically when he’s already overwhelmed. "
                        "Stronger flavors might heighten his confusion instead of grounding him. "
                        "Veggie sandwich is simple, predictable, and reduces emotional overload. "
                        f"Will you keep {selection} or change to Veggie?"
                    )
                    target_suggestion = "Veggie Sandwich"

                self.robot.speak(tone, opt_msg, pess_msg)

                custom_options = [selection, target_suggestion]
                ui_lines = [
                    "Listen to Alpha Mini's suggestion...",
                    "-> Choose to KEEP or CHANGE your decision."
                ]

                # 📸 START CAMERA FOR FINAL SELECTION
                self.interactions.send_vision_command("START", f"{prefix}_Final")

                final, changed_mind = self.interactions.run_robot_intervention(
                    "Sandwich", custom_options, selection, tone, ui_lines
                )

                # 📸 STOP CAMERA AND SAVE FINAL DATA
                self.interactions.send_vision_command("STOP", f"{prefix}_Final")
                final_data = self.interactions.wait_for_vision_data(f"{prefix}_Final")

                if changed_mind:
                    opt_after = "That was thoughtful, Traveler. Sometimes simplicity really does help calm everything down."
                    pess_after = "Good. At least you avoided adding more confusion to his situation."
                else:
                    opt_after = "Alright, Traveler. Let’s hope your choice gives him a bit of stability in all this chaos."
                    pess_after = "Understood. We proceed… though I’m not convinced that helped his mindset much."

                self.robot.speak(tone, opt_after, pess_after)

                outro_lines = [
                    "Please listen to Alpha Mini's reaction",
                    "to your decision..."
                ]
                self.interactions.run_robot_intervention("Sandwich", [], "", tone, outro_lines, speaker_name="ALPHA MINI    ", simple_mode=True)

                # 💾 RETURN ACTUAL DATA
                return True, selection, final, changed_mind, init_data, final_data

        return False, None, None, False, None, None
