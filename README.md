# Investigation of Robot Humour Styles on User Acceptance in a Gamified HRI Environment

**Author:** Noramira Husna Norkhairani

**Supervisors:** Dr. Aimi Shazwani Ghazali and Dr. Afif Husman

**Institution:** Department of Mechatronics Engineering, International Islamic University Malaysia

## 📌 Project Overview
Social humanoid robots require natural communication tools like humour to ensure seamless and intuitive interactions with human users. This project evaluates the impact of a humanoid robot's optimistic and pessimistic humour styles on human behavioral compliance and subjective user experience. The proposed mechatronic framework utilizes a rule-based conversational model to influence decisions, emotional arousal, and overall acceptance without requiring wearable sensors.

## 🛠️ System Architecture
The framework integrates both software and hardware components to create a unified Human-Robot Interaction (HRI) environment.

* **Gamified Narrative Simulation:** A custom Pygame simulation titled "Foodie Adventure" engages users in digital navigation and food-preparation decision nodes.
* **Humanoid Robot Intervention:** A physical UBTECH Alpha Mini robot delivers rule-based persuasive scripts featuring optimistic or pessimistic humour. The robot is actuated directly via a WebSocket bridge.
* **Vision-Based Affect Tracking:** A concurrent, non-contact computer vision pipeline estimates real-time arousal and facial valence. It utilizes OpenCV, DeepFace neural networks, bounding box localization, and Haar Cascades.

### Arousal Calculation Formula
Physiological arousal is calculated using normalized Eye Blink Rates (EBR) and average blink duration. The real-time approximation of emotional intensity is computed as follows:

$$Arousal=0.7\times br_{norm}+0.3\times bd_{norm}-0.15$$

## 🧪 Methodology
* **Participants:** 30 Mechatronics Engineering students participated in a highly controlled laboratory session.
* **Design:** The study adopted a rule-based conversational model utilizing a between-subjects experimental design.
* **Procedure:** Users were engaged with a "Brain Lock" protocol for pair-wise choice tasks while the system prioritized the robot's auditory intervention.
* **Evaluation:** Subjective user acceptance was measured using a 24-item, 5-point Likert scale questionnaire integrated directly into the Pygame interface.

## 📊 Key Findings
* **Pessimistic Humour Style:** Triggered a moderate increase in behavioral compliance, causing users to yield to the robot and change their decisions more frequently. This yielding was driven by emotional detachment, risk aversion, and a significantly higher frequency of neutral facial states.
* **Optimistic Humour Style:** Encouraged users to resist persuasion and retain their original choices. It successfully fostered a significantly happier sustained emotional state and yielded notably higher post-game user experience ratings.
* **Conclusion:** While a pessimistic humour style is effective at forcing immediate task compliance, an optimistic humour style demonstrates a much stronger practical effect on long-term user acceptance, trust, and positive social judgment.
