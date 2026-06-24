# [cite_start]Investigation of Robot Humour Styles on User Acceptance in a Gamified HRI Environment [cite: 1, 2]

[cite_start]**Author:** Noramira Husna Norkhairani [cite: 3]
[cite_start]**Supervisors:** Dr. Aimi Shazwani Ghazali and Dr. Afif Husman [cite: 9, 15, 167]
[cite_start]**Institution:** Department of Mechatronics Engineering, International Islamic University Malaysia [cite: 10, 11, 12, 13]

## 📌 Project Overview
[cite_start]Social humanoid robots require natural communication tools like humour to ensure seamless and intuitive interactions with human users[cite: 20]. [cite_start]This project evaluates the impact of a humanoid robot's optimistic and pessimistic humour styles on human behavioral compliance and subjective user experience[cite: 22]. [cite_start]The proposed mechatronic framework utilizes a rule-based conversational model to influence decisions, emotional arousal, and overall acceptance without requiring wearable sensors[cite: 37, 59].

## 🛠️ System Architecture
[cite_start]The framework integrates both software and hardware components to create a unified Human-Robot Interaction (HRI) environment[cite: 71, 73].

* [cite_start]**Gamified Narrative Simulation:** A custom Pygame simulation titled "Foodie Adventure" engages users in digital navigation and food-preparation decision nodes[cite: 77].
* [cite_start]**Humanoid Robot Intervention:** A physical UBTECH Alpha Mini robot delivers rule-based persuasive scripts featuring optimistic or pessimistic humour[cite: 82, 83]. [cite_start]The robot is actuated directly via a WebSocket bridge[cite: 83, 107].
* [cite_start]**Vision-Based Affect Tracking:** A concurrent, non-contact computer vision pipeline estimates real-time arousal and facial valence[cite: 24]. [cite_start]It utilizes OpenCV, DeepFace neural networks, bounding box localization, and Haar Cascades[cite: 24, 86].

### Arousal Calculation Formula
[cite_start]Physiological arousal is calculated using normalized Eye Blink Rates (EBR) and average blink duration[cite: 87]. The real-time approximation of emotional intensity is computed as follows:

[cite_start]$$Arousal=0.7\times br_{norm}+0.3\times bd_{norm}-0.15$$ [cite: 88]

## 🧪 Methodology
* [cite_start]**Participants:** 30 Mechatronics Engineering students participated in a highly controlled laboratory session[cite: 63, 64].
* [cite_start]**Design:** The study adopted a rule-based conversational model utilizing a between-subjects experimental design[cite: 70].
* [cite_start]**Procedure:** Users were engaged with a "Brain Lock" protocol for pair-wise choice tasks while the system prioritized the robot's auditory intervention[cite: 91, 92].
* [cite_start]**Evaluation:** Subjective user acceptance was measured using a 24-item, 5-point Likert scale questionnaire integrated directly into the Pygame interface[cite: 67, 68].

## 📊 Key Findings
* [cite_start]**Pessimistic Humour Style:** Triggered a moderate increase in behavioral compliance, causing users to yield to the robot and change their decisions more frequently[cite: 26, 120]. [cite_start]This yielding was driven by emotional detachment, risk aversion, and a significantly higher frequency of neutral facial states[cite: 26, 127].
* [cite_start]**Optimistic Humour Style:** Encouraged users to resist persuasion and retain their original choices[cite: 27, 119]. [cite_start]It successfully fostered a significantly happier sustained emotional state and yielded notably higher post-game user experience ratings[cite: 27, 137].
* [cite_start]**Conclusion:** While a pessimistic humour style is effective at forcing immediate task compliance, an optimistic humour style demonstrates a much stronger practical effect on long-term user acceptance, trust, and positive social judgment[cite: 137, 159].
