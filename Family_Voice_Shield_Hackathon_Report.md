

**AI TRACK | HACKATHON REPORT** 

# **Family Voice Shield** 

Prove who is calling. A clone can copy a voice, but it cannot copy a secret. 

Idea review as senior developer and hackathon judge: problem, solution and market, competitors, technical review, architecture, tech stack, workflows, implementation plan, innovation angles and APIs, data, parameters and mathematics, ecosystem and pitch, agent rules (RULE.md) and a phase-by-phase build plan. 

Prepared Saturday, 14 November 2026 

## **Contents** 

|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**Executive Verdict (read this first)**|**.  .  .  .  .  .  .  .  .  .  .  .  . 5**|
|---|---|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>What is already excellent|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 5|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Top 10 changes that raise your score|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 5|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Scorecard (my estimate as a judge)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 6|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**1 The Problem**|**.  .  .  .  .  .  .  .  .  .  .  .  . 7**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>1.1 What is happening|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 7|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>1.2 Scale (with confidence levels)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 7|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>1.3 Anatomy of the attack (kill chain)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 7|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>1.4 Who suffers, and how|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 8|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>1.5 What people expect from a solution|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 8|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>1.6 Why the standard advice is not enough|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 8|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**2 Our Solution and Market Significance**|**.  .  .  .  .  .  .  .  .  .  .  .  . 9**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>2.1 The idea in one paragraph|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 9|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>2.2 Two layers plus a trigger|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 9|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>2.3 Why identity beats detection (the maths judges like)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 9|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>2.4 Market significance|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 9|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>2.5 Business models|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 10|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>2.6 Impact metrics to track|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 10|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**3 Competitive Landscape**|**.  .  .  .  .  .  .  .  .  .  .  . 11**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>3.1 Who is working on this|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 11|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>3.2 Feature comparison|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 11|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>3.3 Where we beat them, and where we lag|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 12|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>3.4 Positioning line|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 12|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>3.5 If a judge says “Truecaller already does this”|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 12|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**4 Technical Review of the Whole Project**|**.  .  .  .  .  .  .  .  .  .  .  . 13**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>4.1 Component review|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 13|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>4.2 Security analysis of the identity layer|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 13|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>4.3 The platform reality of call audio|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 14|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>4.4 Machine-learning honesty|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 14|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>4.5 Latency budget|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 15|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>4.6 Privacy and legal checklist|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 15|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>4.7 What a judge will probe, and your answer|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 15|
|**.  .  .  .  .  .  .  .  .  .  .  .  .**<br>**5 Architecture (Client Side and Server Side)**|**.  .  .  .  .  .  .  .  .  .  .  . 16**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>5.1 Design principles|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 16|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>5.2 System diagram|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 16|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>5.3 Client side (mobile app)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 17|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>5.4 Server side|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 17|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 2 

|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>5.5 Cryptographic design of the code (reference)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 18|
|---|---|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>5.6 Deployment|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 19|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**6 Tech Stack**|**.  .  .  .  .  .  .  .  .  .  . 20**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>6.1 Recommended stack (hackathon-minimum versus later)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 20|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>6.2 ML model options for anti-spoofing|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 21|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**7 Workflows**|**.  .  .  .  .  .  .  .  .  .  . 22**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>7.1 User workflows|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 22|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>7.2 Developer workflow|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 24|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**8 Implementation Plan (Short Time)**|**.  .  .  .  .  .  .  .  .  .  . 25**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>8.1 Team roles|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 25|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>8.2 Timeline|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 25|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>8.3 MoSCoW cut lines|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 25|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>8.4 Fallback ladder (if something breaks)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 26|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>8.5 Top risks|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 26|
|**.  .  .  .  .  .  .  .  .  .  .  .**<br>**9 Innovative Angles, Shortcuts and Helpful APIs**|**.  .  .  .  .  .  .  .  .  .  . 27**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>9.1 Angles that strengthen the idea (with effort and payoff)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 27|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>9.2 Services and APIs that save time|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 27|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>9.3 Shortcuts that save hours|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 28|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**10 Data Required**|**.  .  .  .  .  .  .  .  .  .  . 29**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>10.1 Data inventory|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 29|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>10.2 Scam techniques (taxonomy)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 29|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>10.3 Phrase lexicon (starter list for the classifier)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 30|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>10.4 Non-lexical signals (structural red flags)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 31|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>10.5 Labelling schema|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 31|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>10.6 Volumes, splits and quality checks|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 31|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>10.7 Data ethics|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 32|
|**.  .  .  .  .  .  .  .  .  .**<br>**11 Parameters, Training, Testing and Mathematics**|**.  .  .  .  .  .  .  .  .  .  . 33**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>11.1 Master parameter register|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 33|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>11.2 Features and signal processing|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 34|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>11.3 Training mathematics for the anti-spoof model|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 34|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>11.4 Scam-phrase engine mathematics|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 35|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>11.5 Fusion, thresholds and decision theory|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 35|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>11.6 Identity-layer mathematics|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 35|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>11.7 Test plan and acceptance targets|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 35|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**12 The Ecosystem and How to Pitch It**|**.  .  .  .  .  .  .  .  .  .  . 37**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>12.1 Ecosystem map|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 37|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>12.2 Roadmap|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 37|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>12.3 The 5-minute pitch (slide by slide)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 37|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>12.4 Demo script (about 75 seconds, with fallbacks)|.  .  .  .  .  .  .  .  .  .  .  .  .  .  . 38|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 3 

|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>12.5 Questions you will be asked|.  .  .  .  .  .  .  .  .  .  .  .  .  . 38|
|---|---|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>12.6 Claims discipline|.  .  .  .  .  .  .  .  .  .  .  .  .  . 39|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**13 RULE.md (Agent Working Rules)**|**.  .  .  .  .  .  .  .  .  . 40**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>0. Prime Directives|.  .  .  .  .  .  .  .  .  .  .  .  .  . 40|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>1. Branching Rules|.  .  .  .  .  .  .  .  .  .  .  .  .  . 40|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>2. Commit Rules|.  .  .  .  .  .  .  .  .  .  .  .  .  . 40|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>3. Permission Gates (STOP and ask)|.  .  .  .  .  .  .  .  .  .  .  .  .  . 41|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>4. Phase Protocol|.  .  .  .  .  .  .  .  .  .  .  .  .  . 41|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>5. Documentation System (mandatory)|.  .  .  .  .  .  .  .  .  .  .  .  .  . 41|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>6. Phase Report Template|.  .  .  .  .  .  .  .  .  .  .  .  .  . 42|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>7. Code Quality Rules|.  .  .  .  .  .  .  .  .  .  .  .  .  . 42|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>8. Security and Privacy Rules|.  .  .  .  .  .  .  .  .  .  .  .  .  . 43|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>9. Honesty and Evaluation Rules|.  .  .  .  .  .  .  .  .  .  .  .  .  . 43|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>10. Communication Rules|.  .  .  .  .  .  .  .  .  .  .  .  .  . 43|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>11. Hackathon Time-Box Rules|.  .  .  .  .  .  .  .  .  .  .  .  .  . 43|
|**.  .  .  .  .  .  .  .  .**<br>**14 Phase-by-Phase Implementation Plan for the Agent**|**.  .  .  .  .  .  .  .  .  . 44**|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>14.1 Phase overview and status board|.  .  .  .  .  .  .  .  .  .  .  .  .  . 44|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 0 Bootstrap and documentation scaffold|.  .  .  .  .  .  .  .  .  .  .  .  .  . 45|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 1 Crypto core: TOTP, HKDF, words, lockout|.  .  .  .  .  .  .  .  .  .  .  .  .  . 45|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 2 Pairing and secure storage|.  .  .  .  .  .  .  .  .  .  .  .  .  . 46|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 3 Verify-Caller flow and elderly UX|.  .  .  .  .  .  .  .  .  .  .  .  .  . 46|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 4 Backend skeleton and audio streaming|.  .  .  .  .  .  .  .  .  .  .  .  .  . 47|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 5 STT and scam-phrase engine|.  .  .  .  .  .  .  .  .  .  .  .  .  . 47|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 6 Anti-spoof module|.  .  .  .  .  .  .  .  .  .  .  .  .  . 48|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 7 Fusion, tiers and client alerts|.  .  .  .  .  .  .  .  .  .  .  .  .  . 48|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 8 Realistic demo path|.  .  .  .  .  .  .  .  .  .  .  .  .  . 49|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 9 Evaluation, hardening and privacy review|.  .  .  .  .  .  .  .  .  .  .  .  .  . 49|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Phase 10 Pitch assets and release|.  .  .  .  .  .  .  .  .  .  .  .  .  . 50|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>Stretch phases (only after Phase 10, each needs G1)|.  .  .  .  .  .  .  .  .  .  .  .  .  . 50|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>14.2 Documentation templates the agent must keep|.  .  .  .  .  .  .  .  .  .  .  .  .  . 50|
|.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .<br>14.3 Starter prompt for the coding agent|.  .  .  .  .  .  .  .  .  .  .  .  .  . 51|
|**.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .**<br>**Sources and Verification Notes**|**.  .  .  .  .  .  .  .  .  . 52**|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 4 

## **Executive Verdict (read this first)** 

**Judge’s one-line verdict:** a strong, well-reasoned idea whose core insight is correct: when a fake voice can be perfect, you stop trying to _hear_ the fake and instead _prove_ identity with something a clone cannot know. The weakest parts are not the idea but the engineering claims around it (call-audio access on phones, anti-spoof accuracy on compressed phone audio, a 4-digit code) and the fact that the “safe word” concept is already public advice and has at least one app competitor. Fix those and this is a top-tier submission. 

### **What is already excellent** 

- **Right problem, right framing.** Detection is an arms race; identity proof is not. Judges reward a team that explains _why_ the obvious approach is a trap. 

- **Honest about limits.** Your own note (“detection is a warning signal, the code is the protection”) is exactly the maturity judges look for. Keep it on a slide. 

- **Demoable in 60 seconds.** Clone a teammate, call a judge, watch the app react. High-emotion, easy to remember. 

- **India-relevant.** Surveys put India at the top of AI-voice-scam exposure and family-emergency scripts (“Papa, main musibat mein hoon”) are documented in news reports. 

### **Top 10 changes that raise your score** 

|**#**|**Change**|**Why it matters**|**Effort**|
|---|---|---|---|
|1|Make the AI layer the**trigger**for the identity<br>check (closed loop), not a standalone detector.|Real failure of safe words is that panicked people<br>forget to ask. Your AI layer fixes that. This is your true<br>novelty.|Low|
|2|Replace the 4-digit code with 6 digits or a 2-word<br>code; derive a different key per direction; add<br>lockout.|4 digits is only about 13 bits. Words are easier for<br>elderly users to hear and say correctly.|Low|
|3|Add a fallback for “my phone broke, I am calling<br>from a friend’s phone”.|This is the single most common scammer excuse. Use<br>backup passphrase, call-back, and family approval.|Low|
|4|Be explicit that phones restrict call-audio access;<br>demo through Twilio Media Streams or<br>speakerphone + mic.|A judge who knows Android/iOS will ask. Having the<br>answer ready wins trust.|Medium|
|5|Do not train an anti-spoof model from scratch.<br>Use a pretrained checkpoint, fine-tune with codec<br>augmentation, report cross-dataset error<br>honestly.|Time is short and generalisation, not training, is the<br>hard part.|Medium|
|6|Support Hindi and Hinglish scam phrases, not only<br>English.|Big differentiator versus Western tools. Your<br>scam-phrase table (Chapter 10) is ready.|Medium|
|7|Add a “Duress code” and a “Practice call” (scam<br>fire-drill) mode.|Cheap features that make the demo memorable and<br>show product thinking.|Low|
|8|Tell the ecosystem story: UPI/bank friction, telco<br>and family network (Chapter 12).|Moves you from “app” to “platform”, which scores<br>higher on impact and business.|Pitch only|
|9|Prepare a recorded fallback for the live demo and<br>a metrics slide with real numbers.|Live detection on a cloned voice over a phone line can<br>fail on stage. The code check will not.|Low|
|10|Do not claim you invented the safe word. Claim<br>you made it automatic, unforgettable and<br>triggered at the right moment.|FBI/FTC-style advice and an app called TrustWord<br>already exist. Overclaiming costs credibility.|Pitch only|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 5 

### **Scorecard (my estimate as a judge)** 

|**Criterion**|**Now**|**After**<br>**changes**|**Comment**|
|---|---|---|---|
|Problem significance|9|9|Large, growing, emotionally clear.|
|Innovation|7|8.5|Identity layer alone is known; closed-loop AI-triggered challenge plus<br>family network is new.|
|Technical depth|6|8|Add real evaluation (EER, codec tests) and a fusion model.|
|Feasibility in hackathon time|6|8|Cut scope using the MoSCoW list in Chapter 8.|
|Demo quality|8|9|Add fallback video and practice-call mode.|
|Business viability|6|7.5|B2B2C with banks, UPI apps and telcos is the credible path.|
|Ethics and privacy|6|8.5|On-device processing, no audio stored, consented cloning only.|



**Reading guide.** Chapters follow your numbered list: 1 Problem, 2 Solution and market, 3 Competitors, 4 Technical review, 5 Architecture, 6 Tech stack, 7 Workflows, 8 Implementation plan, 9 Innovation and APIs, 10 Data, 11 Parameters and mathematics, 12 Ecosystem and pitch, 13 RULE.md, 14 Phase-by-phase agent plan, then Sources. Statistics come from the web sources listed at the end; vendor accuracy claims are marked as vendor claims. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 6 

## **1 The Problem** 

### **1.1 What is happening** 

Voice-clone fraud is the modern form of the old “grandparent scam”. The attacker phones a parent or grandparent, sounds exactly like a son, daughter or grandchild, and says there is an accident, an arrest, a hospital bill or a kidnapping. The victim hears a loved one’s voice in panic and pays within minutes, usually through UPI, a bank transfer, gift cards or crypto. The technology barrier has collapsed: security firms and vendors say a few seconds of audio taken from an Instagram reel, a YouTube video or a WhatsApp voice note is enough to produce a convincing clone. 

Reported Indian incidents (secondary sources, treat as illustrative): 

- **Indore:** a play-school owner lost about Rs 97,500 after a caller using an apparently cloned voice posed as her cousin, a police employee (AI Incident Database; police called it a first of its kind in the state). 

- **Bhopal:** six AI-voice incidents were reported in 20 days in a single report (Free Press Journal). 

- **Delhi-NCR and Madhya Pradesh:** multiple “child in trouble / virtual kidnapping” cases where parents heard a child’s voice (Tabla, Lokmat Times). 

- **Corporate:** a claimed Rs 2.3 crore CEO-voice fraud at a Mumbai firm appears on a scam-awareness blog. Single-source and unverified, so do not put it on a slide as fact. 

### **1.2 Scale (with confidence levels)** 

|**Statistic**|**Value**|**Source**|**Confidence**|
|---|---|---|---|
|Indian adults who experienced, or<br>know someone who experienced, an<br>AI voice scam|47 percent (global<br>average about 25<br>percent)|McAfee 2023 “Artificial Impostor” survey,<br>7,054 adults in 7 countries; repeated by<br>Hindu BusinessLine, Cyber Secify, others|Medium:<br>self-reported online<br>survey, 2023 data|
|Indian victims who lost money|83 percent|Cyber Secify citing McAfee|Medium|
|Victims who lost over Rs 50,000|48 percent|Patrika citing survey data|Low to medium|
|Indian cyber-fraud losses, 2024|Rs 22,846 crore|Hindu BusinessLine (via ThreatCluster<br>summary)|Medium|
|Audio needed to clone a voice|About 3 seconds|McAfee, Truecaller press release, many<br>blogs|Medium: quality<br>varies with the tool|
|US: complaints about AI-voice scams<br>in Q1 2026|250,000 (claimed)|A single blog page|Low: do not use on<br>slides|



**Source discipline.** Quote surveys as “a McAfee survey found…” and put the year. Never present blog statistics as official data. Judges often check one number. 

### **1.3 Anatomy of the attack (kill chain)** 

|**Step**|**What the scammer does**|**Where our product acts**|
|---|---|---|
|1 Harvest|Collects voice from reels, videos, voice notes; collects<br>family links from social media or leaked data.|Awareness only (stretch: voice-exposure audit).|
|2 Clone|Feeds audio to a cloning tool; output in minutes.|None. Cannot be prevented.|
|3 Target|Picks parents and grandparents; often calls from a new or<br>hidden number.|Context score: unknown caller, new number<br>claim.|
|4 Hook|Cloned voice, crying, sirens, “don’t tell Mom”, “police are<br>here”.|**Scam-language score + anti-spoof warning.**|
|5 Pressure|Urgency, secrecy, authority (a “lawyer” or “inspector”<br>takes over the call).|**Challenge prompt: ask for the family code.**|
|6 Payment|Steers to UPI, QR scan, bank transfer, gift cards, crypto.|Identity check, call-back, family approval,<br>payment friction (roadmap).|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 7 

**Step What the scammer does** 

**Where our product acts** 

7 Cash-out Mule accounts, quick layering. Report to 1930 and cybercrime.gov.in (one tap). 

### **1.4 Who suffers, and how** 

|**Group**|**Why they are targeted**|**Harm**|
|---|---|---|
|Parents and grandparents|Trust voice, savings available, less familiar with|Direct financial loss, terror of a fake|
|(55+)|AI; emotional bond with children.|kidnapping, shame that stops reporting.|
|Parents of students or migrant<br>workers|Child lives far away, so a call from an unknown<br>number is plausible.|Panic payments; later guilt and<br>mistrust.|
|Small business owners|Voice of supplier, relative or “bank officer” used<br>to demand urgent transfers.|Working-capital loss; no insurance.|
|Corporate finance staff|CEO or CFO voice clone requests urgent wire (out<br>of our MVP scope but same mechanism).|Large losses; reputational damage.|
|The impersonated person|Their voice is stolen without consent.|Family trust damaged; harassment.|



Loss is made worse by speed: UPI payments are instant and effectively irreversible, and the “golden hour” advice from cybercrime authorities is to report within the first hour so that banks can try to freeze the receiving account. Many victims never report because of embarrassment, so real figures are higher than reported ones. 

### **1.5 What people expect from a solution** 

|**What the victim or family expects**|**Reality today**|**Gap we can fill**|
|---|---|---|
|“Tell me instantly whether this is really<br>my child.”|Humans cannot tell. Detection tools give<br>probabilities, not certainty, and degrade<br>on compressed phone audio.|Give a_proof_(code) instead of a guess.|
|“Stop the payment.”|UPI is instant; banks react after the fact.|Add friction before payment<br>(call-back, family approval); roadmap<br>with PSPs and banks.|
|“Something my parents can actually<br>use.”|Most security apps are too complex for<br>elderly users.|One big button, spoken prompts in<br>Hindi/English, no typing.|
|“Do not spy on my calls.”|Call-recording apps feel invasive and<br>raise legal questions.|On-device first, transient audio,<br>nothing stored by default.|
|“Work even if I panic.”|Safe-word advice fails when people are<br>terrified and forget to ask.|The app prompts at the right moment.|
|“Work for my language.”|Most tools are English-first.|Hindi and Hinglish scam-phrase<br>detection.|



### **1.6 Why the standard advice is not enough** 

The FBI (public service announcement, May 2025, as quoted by several outlets), the FTC and security writers all recommend a secret family word or phrase, and a call-back to a saved number. This is sound, but in practice it breaks in four ways: (1) families never get round to setting one, (2) a static word is forgotten, overheard or shared by accident, (3) a terrified person does not remember to ask, and (4) the real child, calling from a stranger’s phone, may not have the word to hand either. **Our opportunity is to turn good advice into a system that works under stress.** 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 8 

## **2 Our Solution and Market Significance** 

### **2.1 The idea in one paragraph** 

**Family Voice Shield** proves who is on the phone instead of guessing whether the voice is fake. Every family pair shares a secret, set up once in person, that generates a rotating code on both phones. When someone calls claiming to be a relative and asks for help or money, the app asks the caller to read out the current code. A cloned voice cannot produce it. A second, AI layer listens for synthetic-voice signs and scam language, and, crucially, **decides when to force the code challenge** so that a frightened parent does not have to remember. 

### **2.2 Two layers plus a trigger** 

|**Layer**|**Question it answers**|**Fails when**|**Backstop**|
|---|---|---|---|
|1 Identity proof (TOTP /<br>words)|Is this really my relative?|The parent forgets to ask; the<br>relative has no phone or app.|Layer 2 prompts; backup<br>passphrase; call-back; family<br>approval.|
|2 AI warning (anti-spoof +<br>scam language)|Does this call look or<br>sound like a scam?|Phone-line compression hides<br>artefacts; scammer uses new<br>wording or language.|Layer 1 does not depend on it.|
|3 Trigger (fusion engine)|When should the<br>challenge appear?|Threshold set badly (alert<br>fatigue or missed risk).|Calibrated thresholds, tiers,<br>hysteresis, user can always tap<br>“Verify now”.|



### **2.3 Why identity beats detection (the maths judges like)** 

Detection faces two structural problems. First, **arms race** : every improvement in synthesis is used to train the next evasion. Second, **base rates** : almost all calls are legitimate, so even a good detector produces mostly false alarms. By Bayes’ rule, the chance that a flagged call is really synthetic is: 

```
PPV = (sens * prev) / ( sens * prev + (1 - spec) * (1 - prev) )
```

```
Example: sens = 0.90, spec = 0.95, prevalence of cloned calls = 0.1 percent (0.001)
PPV = 0.0009 / (0.0009 + 0.05 * 0.999) = 0.0009 / 0.05085 = about 1.8 percent
=> 98 of every 100 alerts would be false.
```

Two consequences shape the design. (1) A detector alone must never be the decision-maker. (2) We raise the effective prevalence by only scoring calls that already look risky (unknown number, claim of being a relative, request for money or secrecy). In that narrower population the same detector becomes far more useful. A code check, by contrast, has a failure probability of about 1 in a million per attempt (Chapter 4) regardless of how good the clone is. 

### **2.4 Market significance** 

- **Urgency:** surveys place India among the most exposed countries; national fraud losses are in the tens of thousands of crores of rupees per year. 

- **Underserved:** existing tools detect fake audio (Truecaller, Hiya, Pindrop) or block spam; none of the big three offers a family identity protocol with an AI trigger. 

- **Advice exists, product does not:** FBI/FTC-style guidance recommends a safe word. Turning advice into an automatic product is a classic “vitamin to painkiller” move. 

- **Policy tailwind:** India’s data-protection law (DPDP Act 2023) rewards privacy-by-design, and regulators, banks and telcos are all under pressure to reduce digital fraud. 

- **Distribution:** families are natural networks. One adult child protects two or more parents; each install pulls in more members. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 9 

#### **Market sizing (method, with clearly labelled assumptions)** 

We do not have verified figures for the addressable market, so use a bottom-up method and show your assumptions on the slide: 

```
TAM  = households with at least one member aged 55+ and one smartphone-owning adult child
SAM  = TAM share that is reachable through Android and Play Store in year 1-3
SOM  = SAM share you can convert (family virality + bank/telco partnerships)
```

```
Illustrative only (ASSUMPTIONS, replace with sourced data before the final pitch):
```

```
  TAM  = 100 million households
  SAM  = 30 percent  = 30 million
  SOM  = 2 percent   = 600,000 households in 3 years
```

```
  B2C at Rs 99 per household per year, 5 percent paying  = about Rs 3 crore per year
  B2B2C at Rs 30 per protected household per year, 600,000 households = about Rs 1.8 crore per year
  (The real value is the avoided loss, not the subscription.)
```

### **2.5 Business models** 

|**Model**|**Who pays**|**Why they pay**|**Fit**|
|---|---|---|---|
|Freemium family plan|Adult child|Free: identity layer for up to 5 people. Paid:<br>AI warning, unlimited members, family<br>approval.|Good for adoption|
|B2B2C licence|Banks, UPI apps, telcos|Reduced fraud losses, fewer complaints,<br>regulatory goodwill.|**Best for scale**|
|Insurance bundle|Cyber or senior-care<br>insurers|Lower claim cost.|Medium term|
|Enterprise executive<br>verification|Companies|Same protocol for CEO-voice fraud.|Later; different<br>buyer|



### **2.6 Impact metrics to track** 

- Time to verify a caller (target under 15 seconds). 

- Share of challenged calls that were scams (precision of the trigger). 

- False-alert rate per 100 benign calls (target below 2). 

- Families activated per adult-child install. 

- Reported amounts prevented (with user consent). 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 10 

## **3 Competitive Landscape** 

Findings below come from public materials found during research. Check each product’s current status before the final presentation: the field moves quickly. 

### **3.1 Who is working on this** 

|**Player**<br>**Truecaller AI Call**<br>**Scanner**(launched May<br>2024)|**What they do**<br>User taps “Start AI Detection” during a<br>call; the call is merged with a secure<br>line, a voice sample is analysed and<br>the app shows human or AI voice.<br>Premium feature; Android; US first,<br>other markets planned.|**Strength**<br>Huge installed base,<br>consumer brand,<br>real-time on a live<br>call.|**Limit relative to us**<br>Detection only; the user must<br>already be suspicious; premium;<br>no identity proof; no family<br>protocol. If the clone passes, the<br>user is exposed.|
|---|---|---|---|
|**Pindrop Pulse**|Enterprise liveness / deepfake<br>detection for contact centres and<br>meetings (Zoom, Teams, Webex).<br>Vendor claims about 99 percent on<br>known engines and over 90 percent on<br>unseen engines with about 2 seconds<br>of audio, plus explainability.|Best-in-class<br>research depth (top<br>performer in<br>ASVspoof since<br>2017, per vendor).|B2B and call-centre focused; not<br>a family product; accuracy<br>figures are vendor-reported; still<br>detection, not identity.|
|**Hiya Deepfake Voice**<br>**Detector**(Oct 2024)|Free Chrome extension giving a 0 to<br>100 authenticity score for audio in web<br>pages; Hiya Protect serves carriers<br>and consumers; vendor claims up to<br>99 percent accuracy and analysis from<br>about 1 second of audio.|Free, fast, trusted by<br>fact-checkers.|Browser audio, not phone calls;<br>reviewers reported mixed or<br>uncertain results in some tests;<br>no identity layer.|
|**TrustWord**(iOS, early<br>stage)|App with rotating family code word,<br>free for up to 10 people; Android<br>“coming soon” according to its own<br>site.|**Closest to our**<br>**Layer 1.**Solves the<br>forgotten-static-word<br>problem.|No AI trigger, no scam-language<br>or synthetic-voice analysis, no<br>Indian languages, no UPI or<br>family-approval angle (per its<br>public page).|
|On-device and network<br>scam detection (e.g.<br>Google’s Pixel call scam<br>detection, operator<br>filters such as Airtel’s AI<br>spam filter)|Flag spam and scam patterns by<br>number reputation, conversation<br>patterns or network analytics.|Distribution through<br>OS or telecom.|Generic scam detection, usually<br>English-first or number-based;<br>not family identity. Verify current<br>availability in India.|
|Enterprise detection APIs<br>(Reality Defender,<br>Resemble Detect and<br>similar)|APIs that score audio for synthesis.|Good models, easy<br>to call.|Pure detection; paid; enterprise.|
|Static family safe word<br>(FBI, FTC, security press)|Free, low-tech advice.|Nothing to install.|Forgotten, overheard, never<br>asked under panic.|
|Government channels<br>(1930 helpline,<br>cybercrime.gov.in,<br>Sanchar Saathi /<br>Chakshu)|Reporting and blocking after the<br>event.|Official, free.|Reactive, not preventive.|



### **3.2 Feature comparison** 

|**Capability**|**Family Voice**|**Truecaller**|**Pindrop**|**Hiya DVD**|**TrustWord**|**Static safe**|
|---|---|---|---|---|---|---|
||**Shield**|**AI Scanner**|**Pulse**|||**word**|
|Detects synthetic voice|Yes (warning)|Yes|Yes|Yes|No|No|
|Still protects if clone is perfect|**Yes**|No|No|No|Yes|Yes|
|Prompts the check|**Yes**|No (user|Alerts agents|No|No|No|
|automatically at risk time||taps)|||||



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 11 

|**Capability**|**Family Voice**<br>**Shield**|**Truecaller**<br>**AI Scanner**|**Pindrop**<br>**Pulse**|**Hiya DVD**|**TrustWord**|**Static safe**<br>**word**|
|---|---|---|---|---|---|---|
|Scam-language analysis|Yes (Hindi/Hinglish/<br>English)|Not in this<br>feature|Not family-fo<br>cused|No|No|No|
|Rotating code|Yes|No|No|No|Yes|No|
|Identity check works offline|Yes|N/A|N/A|N/A|Likely|Yes|
|Family alert network|Yes (roadmap in<br>MVP)|No|No|No|Partial<br>(groups)|No|
|Indian languages|Yes (target)|Unknown|Multi-languag<br>e model|English<br>listed|Unknown|Any|
|Free tier for families|Yes|Premium|No<br>(enterprise)|Yes<br>(limited<br>credits)|Yes|Yes|



_Entries reflect public materials found in research (2024 to 2026). “Unknown” means not stated publicly. Verify before presenting._ 

### **3.3 Where we beat them, and where we lag** 

|**We beat them on**|**We lag on**|
|---|---|
|**Failure-mode independence:**works even with a perfect|**Detection accuracy:**Pindrop and Hiya train on huge|
|clone because it does not rely on detection.|corpora; we will use a small model.|
|**Closed loop:**AI decides when to challenge; the others stop|**Call-audio access:**Truecaller and carriers can reach the|
|at a score.|call; a normal app cannot on iOS and is restricted on Android.|
|**Family model:**pairing, roles, family approval, duress code.|**Distribution and brand:**no installed base; both parties|
|**India fit:**Hindi and Hinglish phrases, UPI-aware warnings,|must adopt (network effect).|
|1930 reporting.|**Maturity:**no field data, no adversarial testing yet.|
|**Offline identity check**and zero-knowledge secrets.|**Scale operations:**model updates against new generators.|
|**Price:**free core.||



### **3.4 Positioning line** 

**Others tell you what the voice is. We prove who the person is.** Detection is a smoke alarm that is sometimes wrong. The rotating family code is the lock on the door. We install both, and the alarm tells the lock when to engage. 

### **3.5 If a judge says “Truecaller already does this”** 

“Truecaller’s scanner is a good smoke alarm: the user has to be suspicious enough to press it, and if the clone is good the alarm stays quiet. We are the lock. Even if the detector says ‘human’, the caller still has to read a code only the real relative can produce, and our AI layer prompts that check automatically when the call has the shape of a scam. The two approaches are complementary, and a partner like Truecaller could ship our identity layer.” 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 12 

## **4 Technical Review of the Whole Project** 

This chapter reads the project as a senior engineer and as a skeptical judge. Each component is rated for hackathon feasibility and for the risk you must disclose or mitigate. 

### **4.1 Component review** 

|**Component**|**Feasibility**|**Main risk**|**Verdict and fix**|
|---|---|---|---|
|TOTP code engine|Easy (hours)|4 digits is weak; clock drift; code is<br>spoken aloud.|Use 6 digits or 2 to 3 words; window of 2 steps;<br>lockout; directional keys (4.2).|
|Pairing and secret<br>storage|Easy to<br>medium|Secret leakage; recovery when a<br>phone is lost; pairing at distance.|Pair by QR in person; store in<br>Keystore/Keychain; re-pair flow; optional<br>backup passphrase.|
|Call-audio capture|**Hard**|iOS gives apps no call audio;<br>Android restricts it; recording<br>consent.|Speakerphone + mic for demo; Twilio Media<br>Streams for scripted calls; production needs<br>dialer role or carrier partnership (4.3).|
|Anti-spoof model|Medium|Domain shift to 8 kHz compressed<br>phone audio; unseen generators;<br>calibration.|Pretrained SSL-based or AASIST-class model;<br>fine-tune with codec simulation; show EER per<br>condition; treat as warning.|
|Speech-to-text|Medium|Hinglish code-mixing; noisy calls;<br>latency.|faster-whisper small/base or Sarvam API; 3 s<br>chunks; keyword fallback if STT lags.|
|Scam-phrase classifier|Easy to<br>medium|Little labelled Indian-call data;<br>paraphrase evasion.|Noisy-OR rule lexicon + TF-IDF logistic<br>regression; optional multilingual transformer<br>or LLM; build 1,500+ synthetic labelled lines.|
|Fusion and alert<br>engine|Easy|Alert fatigue; threshold tuning.|Logistic fusion, three tiers, hysteresis,<br>cost-based thresholds (Chapter 11).|
|Family notify / push|Easy|Spam; privacy of events.|Send only “risky call, tier, time”; never audio.|
|Live demo|Medium risk|Detector may say “human” on the<br>clone; network or audio hiccups.|Make the_code challenge_the hero. Keep the<br>detector result as supporting evidence and<br>pre-record a fallback.|



### **4.2 Security analysis of the identity layer** 

The code must withstand three kinds of attack: guessing, live relaying, and social engineering. Probability of a lucky guess in one attempt, if the verifier accepts 3 consecutive codes (previous, current, next) to tolerate clock drift: 

|**Code format**|**Entropy**|**Combinations**|**Guess chance, 1 try**|**Guess chance, 3 tries**|
|---|---|---|---|---|
|4 digits|13.3 bits|10,000|0.030 percent|about 0.09 percent|
|6 digits|19.9 bits|1,000,000|0.00030 percent|about 0.0009 percent|
|2 words from a 2,048-word list|22 bits|4,194,304|0.000072 percent|about 0.00021 percent|
|3 words from a 2,048-word list|33 bits|8.6 billion|negligible|negligible|



|**Threat**|**How it works**|**Mitigation**|
|---|---|---|
|Blind guessing|Scammer says any four digits.|Lockout after 3 failed attempts per call; failure raises<br>risk to Red and notifies family.|
|Live relay (man in the<br>middle)|Scammer phones the real child, says “read<br>me the code, it is for verification”, and<br>forwards it to the parent.|Directional keys and on-screen warning “Never read<br>this code to anyone except Mom”; code shown to the<br>child only after choosing “I am calling Mom”; code<br>expires in 30 seconds; family notified on every code<br>view (optional).|
|Overheard or leaked<br>code|Attacker hears the code from a previous<br>call.|Code rotates every 30 seconds, so replay fails; each<br>direction has a different key.|
|Stolen phone|Thief opens the app.|Biometric or PIN gate to display the code; remote<br>revoke by the other family members.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 13 

|**Threat**|**How it works**|**Mitigation**|
|---|---|---|
|Clock drift|Phone clock off by more than a minute.|Accept previous and next steps; use network time<br>when available; show a “clock check” warning.|
|Secret exposure on<br>server|Database breach.|Zero-knowledge design: the server never sees the<br>secret.|
|Social engineering|“My phone is broken, I am using a friend’s<br>phone, no time!”|Policy: no code, no money. Offer backup passphrase,<br>call-back to the saved number, and family approval.<br>Make the policy visible in the UI.|
|Duress|Real child under coercion.|Duress code (a second valid code that silently alerts<br>the family).|



### **4.3 The platform reality of call audio** 

This is the most likely technical challenge from a judge, so be ready. A third-party app does **not** automatically get access to the other person’s voice during a normal phone call. 

|**Option**|**How it works**|**Pros**|**Cons**|**Use for**|
|---|---|---|---|---|
|Speakerphone +<br>microphone|Put the call on speaker; app<br>listens through the mic.|Works on any phone;<br>zero integration.|Echo, noise, degraded<br>audio; user must switch<br>to speaker.|**Hackathon**<br>**demo**|
|Twilio (or Exotel) Media<br>Streams|Calls routed through a cloud<br>number; call audio streams to<br>your server in real time over<br>WebSocket (8 kHz mu-law).|Realistic telephony<br>audio; no phone<br>restrictions;<br>scriptable.|Needs a cloud number<br>and cost; not the user’s<br>normal call path.|**Best**<br>**realistic**<br>**demo**|
|Be the default dialer /<br>call-merge|App becomes the phone app or<br>merges the call into a recorded<br>line (the approach Truecaller<br>describes).|Real call audio.|Heavy permissions; Play<br>Store policy; latency;<br>consent questions.|Production<br>Android|
|In-app VoIP family calls|Calls placed inside our app over<br>WebRTC.|Full audio control,<br>works on iOS.|Scammers do not call<br>you inside our app.|Family-to-fa<br>mily only|
|Carrier or PSP<br>integration|Network-level detection and<br>prompts.|Best coverage.|Needs partnership.|Roadmap|



**Say this out loud:** “On a normal phone the app cannot read the other side of a call, so our MVP runs on speakerphone, and our production plan is a dialer-role Android app plus carrier and bank partnerships. Our identity layer needs no call audio at all, so it works on every phone today.” 

### **4.4 Machine-learning honesty** 

- **Domain shift is the real enemy.** Models trained on clean 16 kHz studio data often degrade sharply on 8 kHz, codec-compressed audio and on generators they have not seen. Use datasets with codec conditions (ASVspoof 2021 and ASVspoof 5) and simulate telephony (Chapter 11). 

- **Narrowband removes evidence.** Many synthetic-speech artefacts live above 4 kHz, which phone audio discards. Expect the detector to be weaker on calls than on podcasts. 

- **Report generalisation, not only in-domain accuracy.** Train on one dataset, test on another (e.g. ASVspoof 2019 train, In-the-Wild test) and show the gap. 

- **Vendor claims are not your claims.** “99 percent” figures from companies depend on their data and conditions. Use them as context, not as benchmarks you match. 

- **Calibrate scores.** Raw network outputs are not probabilities; Platt scaling or isotonic regression on a dev set makes thresholds meaningful. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 14 

### **4.5 Latency budget** 

|**Stage**|**Target**|**Notes**|
|---|---|---|
|Chunk collection|3.0 s (sliding, 1.5 s hop)|Shorter chunks lower accuracy; longer chunks delay the<br>alert.|
|Transport (WSS)|under 150 ms|Send 16-bit PCM, 16 kHz mono.|
|STT|under 800 ms per chunk|faster-whisper small on a modest GPU or good CPU; or<br>streaming API.|
|Anti-spoof inference|under 300 ms per chunk|ONNX Runtime; quantise if needed.|
|Scam classifier + fusion|under 50 ms|Rules + linear model.|
|**Time to first Amber alert**|**under 8 s after speech**<br>**starts**|Acceptable because the typical scam script builds<br>pressure for 20 to 60 seconds.|



### **4.6 Privacy and legal checklist** 

- Process audio **transiently** ; store only scores, tier and reason codes by default. 

- Obtain clear consent from the app user for listening; explain that it analyses the call, not that it records it. Take legal advice before launch because call-recording and interception rules differ by jurisdiction and by whether both parties consent. 

- Follow data-minimisation and purpose-limitation principles under the DPDP Act 2023 and its rules; keep a privacy notice in plain Hindi and English. 

- Voice cloning for the demo: only with the written consent of the person cloned, label every sample “SYNTHETIC”, never use public figures’ voices. 

- Do not log codes, secrets, full phone numbers or transcripts. 

### **4.7 What a judge will probe, and your answer** 

|**Likely question**|**Strong answer**|
|---|---|
|“Isn’t this just a safe word?”|The safe word is the idea. The product is making it rotate, travel with the family,<br>stay secret, and appear automatically at the moment of risk.|
|“What if the relative has no phone?”|Backup passphrase, call-back to a saved number, family approval by a third<br>member. No code means no money.|
|“Can the scammer ask the child for<br>the code?”|Directional keys, warnings, and expiry reduce this; the code is only meaningful to<br>the one parent it was generated for.|
|“How accurate is your detector?”|Show real EER on telephony-simulated audio and say it is a warning signal. Our<br>protection does not depend on it.|
|“How do you listen to calls on iPhone?”|We do not need to for identity. For AI warnings, see 4.3: production path is Android<br>dialer role plus carrier partnerships.|
|“Will elderly users manage?”|One big button, spoken Hindi prompts, a practice-call mode, and the adult child<br>does the setup.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 15 

## **5 Architecture (Client Side and Server Side)** 

### **5.1 Design principles** 

- **Identity layer is offline and zero-knowledge.** The secret is generated on the guardian’s phone, handed to the member by QR in person, and never touches the server. 

- **Audio is transient.** Audio chunks live in memory for the length of inference; the server stores scores and reason codes only. 

- **Layers fail independently.** If the server is down, the code check still works. If the detector is wrong, the code check still works. 

- **Fail closed.** Any error in verification means “not verified”. 

- **Explainable alerts.** Every alert carries reason codes (for example urgency, secrecy, new_number, upi_request, synthetic_voice_likely) shown in plain language. 

- **Replaceable models.** Detector and classifier sit behind interfaces so a better model can be swapped in without touching the apps. 

### **5.2 System diagram** 



<!-- Start of picture text -->
CLIENT  (Guardian + Member phones, Flutter) SERVER  (FastAPI, stateless, no audio stored)<br>audio<br>Audio capture: mic / speakerphone, 16 kHz, 3 s WebSocket audio gateway /v1/stream<br>chunks<br>STT: faster-whisper / Sarvam (Hindi, English,<br>TOTP engine (offline): directional keys, 6 digits or 2 Hinglish)<br>words<br>Scam-phrase engine: rules + MuRIL / LR classifier<br>Verify-Caller UI: big buttons, Hindi/English voice<br>prompts<br>Anti-spoof: AASIST / XLS-R head via ONNX Runtime<br>Alert UI: Green / Amber / Red + family notify<br>risk<br>+ reasons<br>Fusion + alert engine: risk, tier, reasons, hysteresis<br>Pairing + Secure Storage (Keystore / Keychain), QR<br>in person<br>Push relay (FCM) + event log (scores only)<br>secret never leaves the device<br>identity check works with no internet<br><!-- End of picture text -->

_Figure 1. Client and server architecture. STT and anti-spoof run in parallel on every chunk; the vertical arrows show the order of data hand-off for readability._ 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 16 

### **5.3 Client side (mobile app)** 

Two roles share one codebase: a **Guardian** (usually the parent who receives risky calls) and a **Member** (the relative whose voice could be cloned). A person can be both in different pairs. 

|**Module**|**Responsibility**|**Key details**|
|---|---|---|
|Pairing|Create a pair; exchange the<br>secret in person.|Guardian generates 160-bit random secret and shows a QR (fvs://pair?...).<br>Member scans. Both store in secure storage. Show a 3-word “pairing<br>fingerprint” on both screens to confirm they match.|
|Secure storage|Keep secrets and settings.|flutter_secure_storage (Android Keystore, iOS Keychain). Biometric gate<br>via local_auth to reveal a code.|
|Code engine|Generate and verify codes<br>offline.|HKDF direction key, HOTP/TOTP (RFC 4226/6238), 30 s step, 6 digits or 2<br>words, window of 2 steps, 3-try lockout, duress code derivation.|
|Verify-Caller UI|Guide the guardian through<br>the check.|Large buttons: “Ask for the code”, “They said it” (enter digits or choose<br>words), “Hang up and call back”. Spoken prompts via text-to-speech in<br>Hindi or English.|
|Audio capture|Feed the AI layer.|Mic capture at 16 kHz mono PCM, 3 s windows with 1.5 s hop, foreground<br>service on Android; user starts it per call (explicit consent).|
|Stream client|Send audio, receive scores.|WebSocket (WSS) with auto-reconnect; heartbeat; exponential backoff;<br>local fallback to keyword rules if offline.|
|Alert UI|Show tiered warnings.|Green (silent), Amber (banner + “Ask for the code”), Red (full-screen<br>stop). Reasons listed in plain language.|
|Family notify|Tell other members.|FCM push: “Dad received a high-risk call at 14:03”. No content, only<br>metadata.|
|Practice mode|Training for elderly users.|App plays a harmless synthetic scam call (clearly labelled) and walks<br>through the challenge.|



#### **Call-session state machine (client)** 

```
IDLE --user taps "Protect this call"--> LISTENING
LISTENING --risk >= T1 for k of n chunks--> AMBER
AMBER     --risk >= T2--> RED
AMBER|RED --user/AI starts challenge--> CHALLENGE
CHALLENGE --code matches--> VERIFIED  (banner stays, remind: call back for big transfers)
CHALLENGE --3 wrong tries or refusal--> FAILED (alert family, offer report to 1930)
ANY --call ends--> IDLE  (audio buffers wiped)
```

#### **Data stored on the device** 

|**Item**|**Where**|**Retention**|
|---|---|---|
|Pair secrets (one per direction derived at runtime)|Secure storage|Until pair removed|
|Pair metadata (names, roles, language)|Local database (Hive or SQLite)|Until removed|
|Call-risk events (time, tier, reason codes)|Local database|30 days, user-clearable|
|Audio buffers|RAM only|Wiped at end of call|



### **5.4 Server side** 

A single stateless service is enough for the MVP. It exposes a WebSocket for audio and a few REST endpoints. Heavy components are loaded once at start-up. 

|**Service module**|**Responsibility**|**Implementation notes**|
|---|---|---|
|Gateway|Authenticate session, accept PCM<br>frames, buffer into chunks.|FastAPI + uvicorn; WebSocket; per-session ring buffer; session<br>token signed by the server.|
|STT worker|Transcribe chunks (EN, HI,<br>Hinglish).|faster-whisper (small or base, int8); VAD to skip silence;<br>language auto-detect; or Sarvam / Deepgram streaming.|
|Scam-phrase engine|Score transcript windows against<br>the lexicon and classifier.|Normalisation (lower-case, transliteration map), rules with<br>weights (noisy-OR) + TF-IDF logistic regression; optional<br>transformer.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 17 

|**Service module**|**Responsibility**|**Implementation notes**|
|---|---|---|
|Anti-spoof worker|Score chunk for synthetic speech.|ONNX Runtime; input 16 kHz mono 3 to 4 s; telephony pre-filter<br>option; output calibrated probability.|
|Fusion + alert engine|Combine scores, smooth, choose<br>tier, produce reasons.|Logistic fusion; EMA smoothing; hysteresis; config-driven<br>thresholds.|
|Push relay|Notify family.|Firebase Cloud Messaging; payload has no content.|
|Event log|Operational metrics.|SQLite or Postgres: session id (random), tier timeline, latency;<br>no audio, no transcripts.|
|Admin / eval|Offline evaluation scripts.|CLI that replays WAV files through the pipeline and prints EER,<br>latency, confusion matrices.|



#### **API contract (draft)** 

```
WebSocket  wss://<host>/v1/stream?token=<session_token>
```

```
client -> server (text):  {"type":"start","session":"b7f1...","lang":"auto","sr":16000,"channels":1}
client -> server (binary): raw 16-bit little-endian PCM frames (about 100 ms each)
client -> server (text):  {"type":"context","unknown_number":true,"claims_relative":true,"hour":14}
client -> server (text):  {"type":"end"}
```

```
server -> client (text):
{"type":"score","t":12.0,
 "s_a":0.71,         // synthetic-voice probability (calibrated)
 "s_t":0.64,         // scam-language probability
 "s_c":0.50,         // context score
 "risk":0.69,        // fused, smoothed
 "tier":"AMBER",
 "reasons":["urgency","secrecy","new_number"],
 "prompt":"ask_for_code"}
```

```
REST
```

```
  POST /v1/session            -> {"token":"...","expires_in":900}
  POST /v1/notify             -> push to paired family members (metadata only)
  GET  /v1/health             -> {"status":"ok","models":{"spoof":"v0.2","text":"v0.3"}}
```

### **5.5 Cryptographic design of the code (reference)** 

```
# Pairing (guardian phone)
K_pair = CSPRNG(20 bytes)                         # 160-bit secret, shown once as QR, stored in Keystore
```

```
# Direction keys so that "A proves to B" differs from "B proves to A"
K_A_to_B = HKDF-SHA256(K_pair, info="FVS1|A->B", len=20)
K_B_to_A = HKDF-SHA256(K_pair, info="FVS1|B->A", len=20)
```

```
# Code generation (RFC 6238 on top of RFC 4226)
T   = floor(unix_time / 30)
mac = HMAC-SHA1(K_dir, T as 8-byte big-endian)
o   = mac[19] & 0x0F
bin = ((mac[o] & 0x7F) << 24) | (mac[o+1] << 16) | (mac[o+2] << 8) | mac[o+3]
digits = bin mod 10^6
# words variant: w1 = bin mod 2048, w2 = (bin >> 11) mod 2048
```

```
# Verification (guardian side)
accept if digits == code(K_member_to_guardian, T) or == code(..., T-1)    # window of 2 steps
lockout after 3 failures per call; failure => Red + notify family
```

```
# Duress code: code(K_dir, T, tag="DURESS") - valid but silently alerts the family
```

Use a vetted library for HMAC and HKDF (Dart: cryptography or pointycastle; Python: cryptography). Validate the implementation against the RFC 4226 and RFC 6238 test vectors in a unit test before anything else is built. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 18 

### **5.6 Deployment** 

- **Hackathon:** one Docker container (FastAPI + models) on a laptop or small cloud VM, exposed with a tunnel (Cloudflare Tunnel or ngrok); mobile app points to it. Optional Twilio number for the realistic call path. 

- **Pilot:** managed container service (Cloud Run, Fly.io, Render), model files in object storage, Redis for session state, Postgres for event metrics, GPU only if transformer STT is needed. 

- **Production:** on-device inference for the detector and phrase engine (ONNX Runtime Mobile or TFLite), server only for push and optional heavy checks; partner APIs for banks and telcos. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 19 

## **6 Tech Stack** 

### **6.1 Recommended stack (hackathon-minimum versus later)** 

|**Layer**|**Hackathon choice**|**Alternatives**|**Why / notes**|
|---|---|---|---|
|Mobile client|**Flutter**(Dart), Android first|React Native (Expo); PWA for<br>a web-only demo|One codebase, solid audio and<br>secure-storage plugins. If nobody on<br>the team knows Dart, pick React<br>Native. A PWA is quickest but weaker<br>for secure storage and background<br>audio.|
|Secure storage|flutter_secure_storage +<br>local_auth|expo-secure-store (RN)|Keystore/Keychain backed.|
|QR pairing|qr_flutter + mobile_scanner|react-native-vision-camera|In-person only.|
|Audio capture|record package (PCM 16 kHz)|flutter_sound|Foreground service for Android.|
|Realtime<br>transport|WebSocket<br>(web_socket_channel)|gRPC streaming, WebRTC|Simplest to debug.|
|Backend|**Python 3.11, FastAPI,**<br>**uvicorn**|Node (NestJS)|Python hosts the ML stack natively.|
|Speech-to-text|faster-whisper (small/base,<br>int8)|Sarvam AI, Deepgram,<br>Google STT, AI4Bharat<br>models, Vosk (offline),<br>whisper.cpp|Check Hindi and Hinglish quality on<br>your own test lines before committing.|
|Anti-spoofing|Pretrained SSL front-end<br>(wav2vec2 / XLS-R) +<br>AASIST-style back-end, or a<br>pretrained Hugging Face<br>deepfake-audio checkpoint,<br>exported to ONNX|RawNet2, LCNN, ResNet on<br>LFCC; hosted detector APIs as<br>optional second opinion|Do not train from scratch. Fine-tune<br>with codec augmentation. Verify model<br>licence.|
|Scam classifier|Lexicon (noisy-OR) + TF-IDF +<br>logistic regression (scikit-learn)|MuRIL, IndicBERT, XLM-R<br>fine-tune; LLM zero-shot for<br>explanations|Start tiny, upgrade if time remains.|
|Fusion|Logistic regression on [s_a, s_t,<br>s_c], EMA + hysteresis|Gradient boosting|Few features; interpretable.|
|Code engine|RFC 6238 TOTP with HKDF<br>(cryptography / pointycastle)|pyotp (Python reference<br>tests)|Test against RFC vectors.|
|Telephony (demo)|Twilio Programmable Voice +<br>Media Streams|Exotel, Plivo, Vonage|Gives realistic 8 kHz call audio to your<br>WebSocket.|
|Voice cloning<br>(demo only)|ElevenLabs instant voice clone<br>(with teammate consent)|XTTS-v2 (check<br>non-commercial licence),<br>OpenVoice|Label every clip SYNTHETIC.|
|Push|Firebase Cloud Messaging|OneSignal|Free tier.|
|Data store|SQLite (MVP), Postgres later|Supabase|No audio ever stored.|
|DevOps|Docker, GitHub Actions,<br>pre-commit (ruff, black, dart<br>format)|-|Cheap quality gate.|
|Testing|pytest, flutter_test, Locust or<br>k6 for latency|-|Include RFC vectors and replay tests.|
|Docs|Markdown in /docs, Mermaid<br>diagrams|-|See RULE.md.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 20 

### **6.2 ML model options for anti-spoofing** 

|**Model family**|**Idea**|**Pros**|**Cons**|
|---|---|---|---|
|AASIST (graph attention on raw<br>waveform)|Spectro-temporal graph<br>attention; strong ASVspoof 2019<br>baseline.|Small, well documented,<br>open reference code.|Can overfit to training<br>attacks; weaker on<br>unseen conditions.|
|RawNet2|Raw waveform + sinc filters.|Classic baseline.|Older.|
|SSL front-end (wav2vec 2.0 /<br>XLS-R) + light back-end|Large self-supervised speech<br>model fine-tuned for spoof<br>detection.|Best generalisation in the<br>research literature;<br>multilingual (XLS-R).|Heavy; needs ONNX<br>export and possibly<br>quantisation.|
|LFCC + LCNN / GMM|Handcrafted features.|Fast, tiny, interpretable.|Weaker.|
|Hosted detector APIs|Send audio, get score.|Zero training.|Cost, privacy, rate limits,<br>dependency; use only as<br>optional second opinion.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 21 

## **7 Workflows** 

### **7.1 User workflows** 

#### **A. Onboarding and pairing (once per family pair, about 3 minutes)** 

1. Adult child (Member) installs the app and creates a profile. Parent (Guardian) installs it with help. 

2. Sitting together, the Guardian taps “Add family member”, enters the name and relationship, and the phone shows a QR code. 

3. The Member scans the QR. Both phones show the same 3-word pairing fingerprint; both confirm it matches. 

4. Both set the preferred language (English, Hindi, Hinglish) and a PIN or biometric. 

5. Each person writes a backup passphrase on paper (used if a phone is lost) and stores it at home. 

6. The Guardian runs the Practice Call once so the steps feel familiar. 

#### **B. Everyday use** 

1. Nothing to do. The app lives in the background. 

2. Members open the app only to show a code when they call. 

#### **C. Suspicious call (the core flow)** 

1. A call arrives. If it is unknown, or the caller says “It’s me, I need money”, the Guardian taps **Protect this call** and switches to speaker. 

2. The app listens and analyses chunks. Context signals (unknown number, urgency words) raise the risk. 

3. At Amber, the screen says in simple Hindi or English: _“Ask for the family code before anything else.”_ At Red, the app speaks it aloud. 

4. The Guardian says: “Please read me your code.” The caller reads digits or words. The Guardian enters or selects them. 

5. Match: green screen “Identity proven”. Reminder: still call back for large or first-time transfers. 

6. No match, refusal, or excuses: red screen “Treat as scam. Hang up.” Buttons: **Call back saved number** , **Alert family** , **Report to 1930** . 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 22 



<!-- Start of picture text -->
Call arrives: unknown number, or a “relative” asking for money<br>or urgent help<br>Anti-spoof score s_a (is the voice Scam-language score s_t (STT + Context score s_c (new number,<br>synthetic?) phrase classifier) urgency, time, payee)<br>Fusion: R = sigmoid(w0 + w1 s_a + w2 s_t + w3 s_c), smoothed<br>over chunks<br>RED: R at or above T2. Full-screen<br>GREEN: R below T1. Stay silent, keep AMBER: T1 to T2. Banner: “Ask for the<br>STOP + spoken prompt. Family<br>listening. family code before anything else.”<br>notified.<br>Caller reads the code aloud. App compares with its own offline<br>TOTP (window of 2 steps, 3 tries, then lockout).<br>MATCH: identity proven. Still call back for any large or NO MATCH or refuses: treat as scam. Alert family, offer<br>first-time transfer. one-tap report to 1930 / cybercrime.gov.in.<br><!-- End of picture text -->

_Figure 2. Call decision flow: three scores are fused into a tier, the tier triggers the code challenge, and the code decides._ 

#### **D. A real emergency** 

1. The real child calls from a borrowed phone. The parent asks for the code. 

2. The child opens the app on any trusted device (a friend’s phone with the web version, or a WhatsApp bot, see Chapter 9) and reads the code. 

3. If the child cannot reach any app: the child reads the backup passphrase, or the parent hangs up and calls the child’s saved number, or asks another family member to confirm. 

4. If the child is under coercion, the child reads the **duress code** ; the parent’s phone looks normal but silently alerts the family. 

#### **E. Lost or replaced phone** 

1. Member installs on the new phone and asks the Guardian to re-pair (new QR). 

2. Old pair is revoked from the Guardian’s phone or by another family member; the revoked device’s codes stop working. 

#### **F. False alarm** 

- If the call was fine, the user taps “This was safe”. The app stores a feedback flag (locally) so thresholds can be tuned and the user is not nagged about the same number. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 23 

### **7.2 Developer workflow** 

#### **Repository layout (monorepo)** 

```
family-voice-shield/
  RULE.md  HANDOFF.md  README.md
  docs/            00_PROJECT_BRIEF ... 08_DATA_AND_MODELS
  mobile/          Flutter app (lib/core/totp, lib/features/pairing, verify, alerts, practice)
  server/          FastAPI app (app/gateway, stt, scam, spoof, fusion, notify), tests/
  ml/              data scripts, training notebooks, export to ONNX, evaluation CLI
  data/            (gitignored) raw, interim, processed, synthetic
  demo/            scripts: clone-voice, twilio-call, replay, fallback video notes
  infra/           Dockerfile, compose, CI workflows
```

#### **Daily loop** 

1. Pull latest **main** . Read HANDOFF.md and the phase status board. 

2. Create or continue the phase branch **phase/NN-name** . 

3. Write a failing test, implement, make it pass, run linters. 

4. Commit small (Conventional Commits) and append to the progress log in the same commit. 

5. Before ending the session, update HANDOFF.md and the status board. 

6. Ask the developer for permission before pushing or starting a new phase. 

#### **ML loop** 

1. Fetch data to **data/raw** (never committed). Record source and licence in docs/08. 

2. Build deterministic splits: speaker-disjoint, attack-disjoint, codec-disjoint. Save split files. 

3. Create the telephony simulation (resample to 8 kHz, apply AMR-NB / G.711 / Opus, add noise). 

4. Train or fine-tune with seeds fixed; log hyper-parameters. 

5. Evaluate on in-domain and cross-dataset test sets; report EER, AUC, calibration. 

6. Export to ONNX; check numerical parity; measure latency; register model version. 

#### **Demo-day workflow** 

1. T-24h: freeze scope. Merge only demo-critical fixes. 

2. T-12h: full rehearsal with the actual phones, network and a hotspot as backup. 

3. T-2h: record a fallback video of the whole flow; charge phones; test audio levels. 

4. On stage: lead with the code challenge; show detector output as supporting evidence; keep fallback ready. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 24 

## **8 Implementation Plan (Short Time)** 

Assumes a **36-hour hackathon** and a team of four. If your window is shorter (for example 24 hours), apply the MoSCoW cuts in 8.3 first. Hour ranges are working hours, not wall-clock. 

### **8.1 Team roles** 

|**Role**|**Owns**|**Backup**|
|---|---|---|
|A. Mobile lead|Flutter app: pairing, code engine UI, verify flow, alerts, practice mode.|D|
|B. Backend and infra|FastAPI gateway, WebSocket, fusion engine, Docker, Twilio demo path, CI.|C|
|C. ML audio|Anti-spoof inference, telephony simulation, evaluation, cloning for the<br>demo (with consent).|B|
|D. ML text, data and pitch|Scam lexicon and classifier, STT integration, synthetic data, slides, demo<br>script.|A|



### **8.2 Timeline** 

|**Hours**|**Milestone**|**Who**|**Output**|
|---|---|---|---|
|0 to 2|Repo, docs skeleton, ADRs, task board, API contract frozen.|All|Phase 0 done|
|2 to 6|TOTP/HKDF engine with RFC vectors (Dart and Python parity).<br>Pairing by QR. Secure storage.|A, B|Two phones show matching codes|
|2 to 8|FastAPI skeleton, WebSocket, health, Docker. Start data<br>collection: lexicon v1, synthetic lines v1.|B, D|Server up; first labelled set|
|6 to 10|Verify-Caller UI, lockout, duress code, Hindi/English prompts,<br>practice mode.|A|**MVP of Layer 1 complete**|
|8 to 14|STT integration and scam-phrase engine with evaluation.|D, B|Transcript to s_t|
|8 to 16|Anti-spoof pretrained model in ONNX; chunking; telephony<br>simulation; baseline EER.|C|Transcript-independent s_a|
|14 to 18|Fusion engine, tiers, hysteresis, reason codes; client alert UI<br>wired to live scores.|B, A|**End-to-end loop on**<br>**speakerphone**|
|18 to 24|Realistic path: Twilio Media Streams or recorded-call replay;<br>teammate voice clone; scripted scam calls.|B, C|Demo-ready call path|
|24 to 28|Evaluation report (real numbers), red-team tests, privacy<br>review, bug fixing.|C, D|Metrics slide|
|28 to 32|Polish: UI, language, error states, fallback video, README,<br>docs.|All|Release candidate|
|32 to 36|Pitch rehearsal x3, Q and A drill, buffer.|All|Ready|



### **8.3 MoSCoW cut lines** 

|**Must have**|**Should have**|**Could have**|**Will not (this hackathon)**|
|---|---|---|---|
|TOTP + pairing + verify flow|Hindi prompts|Twilio realistic path|On-device model inference|
|Tier alerts from scam-phrase<br>engine|Duress code<br>Practice mode|2-word codes<br>Family approval for|Carrier or bank integration<br>iOS call-audio access|
|Anti-spoof score displayed with|Family push notification|payments (mock)|Training a model from scratch|
|honest caveat|Evaluation slide with real|WhatsApp code bot|Voice-exposure audit|
|Live demo + fallback video|EER|Dashboard||
|Docs and README||||



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 25 

### **8.4 Fallback ladder (if something breaks)** 

|**If this fails**|**Do this**|
|---|---|
|Live detector says “human” for the clone|Say “as expected, detection is a warning, not proof”. Show the code<br>challenge: the clone cannot answer.|
|STT is slow or wrong|Switch to keyword spotting on a short buffer; the demo script uses scripted<br>phrases the lexicon covers.|
|Server or Wi-Fi fails|Hotspot; then local laptop server; then recorded replay. Identity layer still<br>works offline.|
|Twilio path fails|Use speakerphone + laptop speaker playing the cloned audio.|
|App crash|Play the 90-second fallback video and continue with slides.|



### **8.5 Top risks** 

|**Risk**|**Probability**|**Impact**|**Mitigation**|
|---|---|---|---|
|Anti-spoof model performs poorly on phone<br>audio|High|Medium|Treat as warning; show honest metrics; rely on<br>code.|
|Hinglish STT quality|Medium|Medium|Test early; keyword fallback; scripted demo<br>phrases.|
|Mobile audio capture issues|Medium|High|Prototype capture in the first 8 hours; fallback<br>to laptop mic demo app.|
|Scope creep|High|High|Phase gates and RULE.md; cut list above.|
|Team member unavailable|Low|High|Backups listed; docs keep context.|
|Legal or ethics concern about cloning|Low|High|Written consent, SYNTHETIC labels, teammates<br>only.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 26 

## **9 Innovative Angles, Shortcuts and Helpful APIs** 

### **9.1 Angles that strengthen the idea (with effort and payoff)** 

|**#**|**Angle**|**What it is**|**Effort**|**Payoff**|
|---|---|---|---|---|
|1|**Closed loop trigger**|The AI layer decides when to demand the code, so<br>the parent need not remember.|Low|**Core novelty**|
|2|Directional keys + word<br>codes|A to B and B to A use different derived keys; codes<br>shown as two easy words for elderly users.|Low|Security and<br>usability|
|3|Duress code|A second valid code that silently alerts the family if<br>the real person is coerced.|Low|Very memorable in<br>a demo|
|4|Callback guard|One button: hang up and dial the saved contact.<br>FBI-style advice made one tap.|Low|Strong real<br>protection|
|5|Practice call (scam fire<br>drill)|App plays a harmless synthetic scam call and<br>coaches the parent through the challenge.|Low to<br>medium|Adoption and demo<br>wow|
|6|Family approval for<br>payments|First-time payee or amount above a limit needs a<br>second family member to approve (mock via push in<br>MVP).|Medium|Bridges to UPI and<br>banks|
|7|Randomised challenge<br>phrase|App gives the parent a random unpredictable phrase<br>to ask for; clone pipelines may show response delay<br>or artefacts; a delay feature feeds fusion.|Medium|Extra signal,<br>research flavour|
|8|WhatsApp or web code bot|Member can get the code through a bot or web page<br>when they have no app or a borrowed phone.|Medium|Removes the “no<br>app” objection|
|9|Scam number sharing|Opt-in anonymous sharing of scam numbers and<br>phrase patterns to a community list; link to 1930 and<br>cybercrime.gov.in reports.|Medium|Network effect,<br>civic angle|
|10|Lock-screen widget /<br>wearable|Show the current code without opening the app.|Low|Usability|
|11|Voice-exposure audit|Show a family how much of their voice is public<br>(counts of clips), to raise awareness.|Medium<br>(privacy<br>care)|Awareness; stretch|



### **9.2 Services and APIs that save time** 

Check current pricing, free-tier limits and licences before relying on any of these. 

|**Need**|**Service / library**|**How it helps**|**Notes**|
|---|---|---|---|
|Realistic call audio|Twilio Programmable Voice with<br>Media Streams (alternatives:<br>Exotel, Plivo, Vonage)|Place or receive a call on a cloud<br>number; stream raw call audio (8 kHz)<br>to your WebSocket in real time.|Solves the mobile<br>call-audio limitation for<br>the demo. Trial credit<br>may suffice.|
|Speech-to-text|faster-whisper (local); Sarvam AI<br>(Indian languages); Deepgram or<br>AssemblyAI streaming; Google<br>Speech-to-Text; AI4Bharat models;<br>Vosk offline|Transcripts for the scam-phrase<br>engine.|Test Hinglish early. Local<br>models avoid sending<br>audio to third parties.|
|Voice cloning<br>(demo)|ElevenLabs instant voice cloning;<br>open options such as XTTS-v2 or<br>OpenVoice|Create the teammate clone for the live<br>demo.|Consent and labelling<br>mandatory; XTTS licence<br>is non-commercial, so<br>check terms.|
|Optional detector<br>second opinion|Resemble Detect, Reality<br>Defender or similar APIs; Hugging<br>Face pretrained deepfake-audio<br>models|Compare against your own model; fall<br>back if your model underperforms.|Check privacy, latency<br>and licence.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 27 

|**Need**|**Service / library**|**How it helps**|**Notes**|
|---|---|---|---|
|Synthetic data<br>generation|An LLM (for example the Claude<br>API) to write scam and benign<br>dialogues in English, Hindi and<br>Hinglish; human review afterwards|Create the labelled text corpus quickly.|Always review a sample<br>by hand; deduplicate.|
|Alert explanations|LLM prompt that turns reason<br>codes into one plain sentence|Friendlier alerts.|Optional; keep rule-based<br>fallback.|
|Push notifications|Firebase Cloud Messaging|Family notify.|Free tier.|
|Phone-number<br>context|Local contacts list; carrier or<br>caller-ID APIs (production)|Unknown caller flag for the context<br>score.|Use local contacts for<br>MVP.|
|Payment friction<br>demo|UPI deep links (upi://pay) and a<br>mock “approval” screen|Show how family approval would gate<br>a payment.|No official partner API for<br>this; present as roadmap.|
|Reporting|National Cyber Crime Reporting<br>Portal (cybercrime.gov.in) and<br>helpline 1930; Sanchar Saathi /<br>Chakshu for suspicious numbers|One-tap deep link or call from the app.|Link only; do not file<br>automatically.|
|Mobile inference<br>(later)|ONNX Runtime Mobile, TFLite|On-device privacy.|Roadmap.|
|Hosting|Cloud Run, Fly.io, Render, Railway|Deploy the container quickly.|Cold starts affect demos;<br>keep one warm.|



### **9.3 Shortcuts that save hours** 

- Build the **code engine first** , because it is the guaranteed win and is testable with RFC vectors. 

- Use a **pretrained detector** ; spend your ML time on the telephony simulation and honest evaluation. 

- Begin with **keyword and regex rules** for scam language; add the classifier only when the rules work. 

- Create **scripted demo calls** that your lexicon and detector have been tested on, and keep a random unscripted call as a bonus, not the main act. 

- Write the **evaluation CLI** early; it doubles as your regression test and your metrics slide. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 28 

## **10 Data Required** 

### **10.1 Data inventory** 

Availability and licences change; confirm each one before use and record it in docs/08_DATA_AND_MODELS.md. 

|**Purpose**<br>Anti-spoof training|**Dataset / source**<br>ASVspoof 2019 LA|**What it provides**<br>Bona fide and spoofed speech from<br>TTS and voice conversion; standard<br>benchmark.|**Notes**<br>Clean; good for first<br>training; known to<br>generalise poorly alone.|
|---|---|---|---|
|Anti-spoof training<br>and test|ASVspoof 2021 (LA and DF)|Telephony-codec and<br>media-compression conditions.|Closest to phone audio in<br>the older series.|
|Anti-spoof training<br>and test|ASVspoof 5 (2024)|Larger, more diverse data with<br>codec conditions and adversarial<br>attacks.|Best modern benchmark;<br>check access terms.|
|Cross-dataset test|In-the-Wild deepfake audio (Müller<br>et al., 2022)|Real-world deepfakes of public<br>figures.|Use as unseen test to<br>expose generalisation<br>gaps.|
|Extra spoof<br>diversity|WaveFake, MLAAD<br>(multi-language), other open spoof<br>sets|Vocoder and multilingual TTS<br>outputs.|Mix carefully to avoid<br>leakage.|
|Bona fide speech|LibriSpeech, VCTK, Common Voice<br>(includes Hindi), AI4Bharat<br>IndicVoices / Kathbath|Real human speech in English and<br>Indian languages.|Required to keep Hindi<br>false alarms low.|
|Augmentation noise<br>and reverberation|MUSAN, OpenSLR room impulse<br>responses|Realistic noise, music, babble and<br>echo.|Used in training pipeline.|
|Own spoof data|Generate with open TTS and voice<br>conversion in English and Hindi;<br>plus teammate clones from a<br>commercial service (with consent)|2,000 to 5,000 clips, balanced<br>across generators and speakers.|Name with SYNTH_ prefix;<br>keep generator labels for<br>attack-disjoint splits.|
|Telephony<br>simulation|Your own pipeline: resample to 8<br>kHz, band-limit 300 to 3400 Hz,<br>apply AMR-NB, AMR-WB, G.711,<br>GSM, Opus; random packet loss;<br>noise|Makes every training clip look like a<br>phone call.|Single most valuable step<br>for this project.|
|Scam text|Own synthetic corpus<br>(LLM-generated + hand-reviewed);<br>public advisories from the Indian<br>Cyber Crime Coordination Centre<br>(I4C), RBI and NPCI awareness<br>material; UCI SMS Spam Collection<br>as a weak proxy|1,500 to 3,000 labelled utterances<br>in English, Hindi and Hinglish.|No large public corpus of<br>Indian scam-call transcripts<br>is known; build your own.|
|Benign text|Synthetic ordinary family calls,<br>delivery calls, bank service<br>notices, genuine requests for<br>money between family|2,000 or more utterances including<br>hard negatives.|Hard negatives prevent<br>over-flagging (“send me Rs<br>500 for the book”).|



### **10.2 Scam techniques (taxonomy)** 

|**Technique**|**Script in one line**|**Typical lines (Hinglish / English)**|**Payment**<br>**channel**|
|---|---|---|---|
|**Family emergency**<br>**impersonation**|A relative has had an accident, been<br>arrested, or needs urgent cash.|“Papa main musibat mein hoon”,<br>“Mummy plz paise bhejo abhi”,<br>“Accident ho gaya hai”|UPI, bank<br>transfer|
|**Virtual kidnapping**|Child is “held”; scammer or a second<br>voice demands ransom; victim told<br>not to hang up or call anyone.|“Aapka beta humare paas hai”, “Phone<br>mat kaatna”, “Police ko mat batana”|UPI, cash drop,<br>crypto|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 29 

|**Technique**|**Script in one line**|**Typical lines (Hinglish / English)**|**Payment**<br>**channel**|
|---|---|---|---|
|**Fake new number**|Relative says phone is lost or broken<br>and this is a new number or a<br>friend’s phone.|“Mera phone kharab ho gaya, ye naya<br>number hai”, “Dost ke phone se bol<br>raha hoon”|UPI (a “friend’s”<br>number)|
|**Authority and legal**<br>**threat (including**<br>**“digital arrest”)**|Claims of police, CBI, customs or a<br>court case; victim told to stay on a<br>video call and pay to “clear” the<br>case.|“Aapke naam par parcel mein drugs<br>mile hain”, “Aap digital arrest mein<br>hain”, “Case settle kar dijiye”|Bank transfer,<br>“safe account”|
|**Bail, lawyer or**<br>**hospital hand-off**|A second person takes over (“I am<br>the lawyer / doctor”) to collect the<br>money.|“Main vakeel bol raha hoon”, “Hospital<br>mein advance jama karna hai”|UPI, cash courier|
|**Bank, KYC and OTP**|Account will be blocked unless KYC is<br>updated; asks for OTP, PIN or card<br>details.|“Aapka account band ho jayega”, “KYC<br>update karna hai”, “OTP bataiye”|OTP theft, card<br>details|
|**UPI collect and QR**<br>**trick**|Victim told to scan a QR or approve a<br>collect request to “receive” or<br>“refund” money.|“QR scan karo paisa aayega”, “Request<br>approve karo”, “PIN daalo refund ke<br>liye”|UPI|
|**Remote-access**<br>**support scam**|Asks to install a screen-sharing app<br>to “fix” a problem.|“AnyDesk download karo”,<br>“TeamViewer ka code batao”|Account takeover|
|**Utility disconnection**|Electricity or gas will be cut tonight<br>unless a bill is paid now.|“Aaj raat bijli kat jayegi”, “Bill update<br>nahi hua”|UPI, link|
|**Boss, vendor or**<br>**client impersonation**|Voice of a manager or supplier<br>requests an urgent transfer.|“Urgent transfer chahiye”, “Account<br>change ho gaya hai”|Bank transfer|



### **10.3 Phrase lexicon (starter list for the classifier)** 

Weights express how strongly a signal suggests a scam on a 1 (weak) to 3 (strong) scale. They are starting points to be tuned on your data. Always handle misspellings, Roman-script Hindi variants and Devanagari forms (add Devanagari equivalents to the production lexicon). 

|**Signal**|**English examples**|**Hinglish examples**|**Weight**|
|---|---|---|---|
|**Urgency**|right now, immediately, in the next 10<br>minutes, no time, hurry, today only|abhi, turant, jaldi, abhi ke abhi, time nahi hai,<br>10 minute mein|2|
|**Secrecy and**<br>**isolation**|don’t tell anyone, keep this between us,<br>don’t tell mom or dad, don’t call the<br>police, don’t hang up|kisi ko mat batana, mummy papa ko mat<br>batana, police ko mat batana, phone mat<br>kaatna, line par bane rahiye|3|
|**Fear and authority**|you are under arrest, case registered, CBI,<br>customs, court, legal action, your account<br>will be blocked|giraftaar, case darj, digital arrest, parcel<br>mein drugs, account band ho jayega, kanooni<br>karwai|3|
|**Emotional distress**|I’m in trouble, accident, hospital, they<br>have me, please help, I’m scared, crying<br>sounds|musibat mein hoon, accident ho gaya,<br>hospital mein, mujhe bacha lo, bahut dar lag<br>raha hai|2|
|**Payment steering**|send via UPI, Google Pay, PhonePe, bank<br>transfer, gift card, crypto, wire, scan this<br>QR, approve the request|UPI karo, paise bhejo, GPay kar do, PhonePe,<br>QR scan karo, collect request approve karo,<br>gift card kharido|3|
|**Credential**<br>**harvesting**|share the OTP, tell me your PIN, card<br>number, CVV, Aadhaar, password|OTP batao, PIN batao, CVV batao, Aadhaar<br>number, password|3|
|**New number /**<br>**device excuse**|my phone broke, this is a new number,<br>calling from a friend’s phone, my phone is<br>dead|phone kharab ho gaya, naya number hai,<br>dost ke phone se, phone band hai|2|
|**Verification**<br>**avoidance**|I can’t talk, can’t video call, don’t call me<br>back, no time to explain, I’ll explain later|baat nahi kar sakta, video call nahi ho sakta,<br>wapas call mat karna, baad mein<br>samjhaunga|3|
|**Remote access**|install AnyDesk, TeamViewer, share your<br>screen, download this app|AnyDesk install karo, screen share karo, app<br>download karo|3|
|**Amount pressure**|fifty thousand, one lakh, bail amount,<br>advance, settlement|pachaas hazaar, ek lakh, zamanat, advance,<br>settlement|1 to 2|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 30 

|**Signal**|**English examples**|**Hinglish examples**|**Weight**|
|---|---|---|---|
|**Relationship claim**|it’s me, don’t you recognise my voice,|main bol raha hoon, pehchana nahi,|1|
|**without proof**|grandma, dad, uncle (opening line)|papa/mummy/chacha||



**Hard negatives matter.** Real family calls contain urgency and money too (“send Rs 2,000 for the exam fee today”). The scam engine must not call these scams on its own. They should instead trigger the _identity challenge_ because a money request from a family voice is exactly the case we protect. Build 500 or more such benign look-alikes. 

### **10.4 Non-lexical signals (structural red flags)** 

|**Signal**|**Why it matters**|**How to capture**|
|---|---|---|
|Unknown or new number; caller claims to<br>be a saved contact|Core of the family-emergency script.|Compare caller number with the<br>contacts list.|
|International prefix or VoIP-style number|Common in scams; also appears in<br>genuine calls.|Number-prefix feature (weak).|
|Call at unusual time or when the parent is<br>alone|Scammers choose moments of<br>confusion.|Time-of-day feature (weak).|
|Refusal to be called back or to switch to<br>video|Strong verification-avoidance signal.|Phrase engine plus explicit user tap.|
|Request for money in the first minute|Scripts monetise quickly.|Time-to-payment-keyword feature.|
|Second person takes over (“lawyer”,<br>“inspector”)|Known hand-off pattern.|Speaker-change detection (stretch).|
|Background crying, sirens, shouting|Used to heighten panic; may be<br>synthetic.|Audio event tagging (stretch).|
|Voice cues: unusually flat prosody, odd<br>breathing, response delays|May indicate synthetic or pipeline<br>latency.|Anti-spoof model plus<br>response-latency feature.|
|Payee is new and the amount is large|Strongest transaction-side signal.|Roadmap: bank and PSP signal.|



### **10.5 Labelling schema** 

```
{"id":"hin-0412",
```

```
 "text":"papa mera accident ho gaya hai abhi paise bhejo kisi ko mat batana",
```

```
 "lang":"hinglish",
 "speaker":"caller",                     // caller | receiver
 "labels":["family_emergency","urgency","secrecy","payment_steering"],  // multi-label
 "severity":3,                           // 0 benign ... 3 clear scam language
 "benign":false,
```

```
 "hard_negative":false,
 "template_id":"fam-emerg-17",           // for template-level splitting
 "source":"synthetic-llm-reviewed",
 "annotator":"A2"}
```

### **10.6 Volumes, splits and quality checks** 

|**Item**|**Minimum for hackathon**|**Good target**|**Rule**|
|---|---|---|---|
|Anti-spoof bona fide clips|5,000 (mix of EN and HI)|50,000+|Speaker-disjoint train, dev,<br>test.|
|Anti-spoof spoofed clips|5,000 across at least 4<br>generators|50,000+ across 10+<br>generators|Hold out at least one generator<br>entirely for testing.|
|Telephony-simulated copies|Each clip in at least 3<br>codec/noise variants|Random on-the-fly|Keep codec-disjoint test (train<br>on some codecs, test on<br>others).|
|Scam text positives|800|3,000|Split by template_id so<br>near-duplicates do not leak.|
|Benign text|1,200 incl. 300 hard negatives|6,000|Include family money requests.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 31 

|**Item**|**Minimum for hackathon**|**Good target**|**Rule**|
|---|---|---|---|
|Annotation agreement|Two reviewers on 200-sample<br>subset|Full double-annotation|Cohen’s kappa of at least 0.7.|



### **10.7 Data ethics** 

- Cloning only with written consent; never clone public figures or minors; label all synthetic audio. 

- Do not scrape social media or collect real victims’ recordings without explicit permission. 

- Anonymise any real transcripts (names, numbers, amounts) before storage. 

- Keep datasets and weights out of the repository; document source and licence for each. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 32 

**11 Parameters, Training, Testing and Mathematics** 

### **11.1 Master parameter register** 

Values are sensible starting points drawn from common practice in the anti-spoofing literature and typical speech pipelines. Tune on your dev set; record final values in docs/08. 

|**Group**|**Parameter**|**Start value**|**Range / note**|
|---|---|---|---|
|Audio|Sample rate for models|16 kHz mono|Telephony source is 8 kHz;<br>upsample after codec<br>simulation.|
|Audio|Bit depth on the wire|16-bit PCM|mu-law 8 kHz from Twilio is<br>decoded first.|
|Audio|Frame / hop for<br>spectrograms|25 ms / 10 ms|Window 400 samples, hop 160<br>at 16 kHz.|
|Audio|FFT size|512|1024 for finer resolution.|
|Audio|Mel bins or LFCC<br>coefficients|64 to 80 mel, or 20 LFCC + delta + delta-delta|Telephony band-limited to 300<br>to 3400 Hz.|
|Audio|VAD aggressiveness|Medium|Drop non-speech frames<br>before scoring.|
|Streaming|Chunk length|3.0 s|2 to 4 s; shorter reduces<br>accuracy.|
|Streaming|Hop|1.5 s|50 percent overlap.|
|Streaming|Smoothing factor (EMA<br>alpha)|0.5|0.3 to 0.7.|
|Streaming|Hysteresis|Raise tier after 2 of 3 chunks above threshold;<br>lower after 4 consecutive below|Avoid flicker.|
|Anti-spoof<br>model|Front-end|XLS-R 300M or wav2vec 2.0 (frozen early<br>layers) or raw-waveform AASIST|ONNX export and quantisation<br>for speed.|
|Anti-spoof<br>model|Back-end|AASIST-style graph attention or 2-layer MLP<br>over pooled features|Dropout 0.2 to 0.5.|
|Training|Optimiser|Adam or AdamW|Weight decay 1e-4 to 1e-2.|
|Training|Learning rate|1e-5 for SSL layers, 1e-4 for back-end|Cosine or step decay; warm-up<br>500 steps.|
|Training|Batch size|8 to 32|Limited by GPU memory.|
|Training|Epochs|10 to 30 with early stopping on dev EER|Patience 5.|
|Training|Loss|Weighted cross-entropy with class weights<br>about [0.1 bona fide, 0.9 spoof] (AASIST<br>default); or one-class softmax; or focal loss<br>gamma 2|See 11.3.|
|Training|Regularisation|Dropout, weight decay, SAM optimiser<br>optional|Helps generalisation.|
|Training|Seeds|3 seeds, report mean and spread|Reproducibility.|
|Augmentation|Codecs|AMR-NB, AMR-WB, G.711 (A-law, mu-law),<br>GSM, Opus, MP3; random bitrates|Apply with probability 0.7.|
|Augmentation|Noise|MUSAN noise/music/babble at SNR 5 to 30 dB|Probability 0.5.|
|Augmentation|Reverberation|Room impulse responses, RT60 0.2 to 0.8 s|Probability 0.3.|
|Augmentation|RawBoost-style|Linear and non-linear convolutive noise,<br>impulsive noise|Common in recent systems.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 33 

|**Group**|**Parameter**|**Start value**|**Range / note**|
|---|---|---|---|
|Augmentation|Speed and pitch|0.95 to 1.05|Small only; avoid destroying<br>artefacts.|
|Augmentation|Packet loss|0 to 5 percent random frame drops|Simulates VoIP.|
|Text|Tokenisation|Word and character n-grams (2 to 5) for<br>TF-IDF|Handles spelling variants.|
|Text|Normalisation|Lower-case, strip punctuation, Hinglish<br>spelling map, number words|Maintain a mapping table.|
|Text|Transformer (optional)|MuRIL or XLM-R base, max length 128, lr 2e-5,<br>3 to 5 epochs, batch 16 to 32|Use class weights.|
|Text|Rule weights|Per signal 0.2 (weight 1), 0.45 (2), 0.7 (3)|Tune on dev; combined by<br>noisy-OR.|
|Fusion|Features|s_a, s_t, s_c, plus optional response-delay|Standardise.|
|Fusion|Model|Logistic regression with L2|Calibrate with Platt scaling.|
|Decision|Tier thresholds T1 and T2|Set by cost: Amber at about 0.35, Red at<br>about 0.65 initially|Re-set on dev data (11.5).|
|Decision|Target false-alert rate|Under 2 Amber per 100 benign calls; under<br>0.5 Red per 100|Product requirement.|
|Identity|TOTP step|30 s|RFC 6238 default.|
|Identity|Digits / words|6 digits, or 2 words from a 2,048-word list|Configurable.|
|Identity|Window|Current and previous step|Add next step if clock drift is<br>common.|
|Identity|Max attempts|3 per call|Then Red + notify.|
|Identity|Hash|HMAC-SHA1 (RFC default) or SHA-256|HKDF-SHA256 for direction<br>keys.|
|Performance|End-to-end first Amber|Under 8 s|See Chapter 4.5.|
|Performance|Real-time factor of full<br>pipeline|Below 0.5|Processing time divided by<br>audio time.|



### **11.2 Features and signal processing** 

```
Short-time Fourier transform:  X[m,k] = sum_n x[n + mH] w[n] exp(-j 2 pi k n / N)
Power spectrum:               P[m,k] = |X[m,k]|^2
Log-mel spectrogram:          S[m,b] = log( sum_k Mel_b[k] * P[m,k] + eps )
LFCC (linear filter bank): c = DCT( log( sum_k Linear_b[k] * P[m,k] ) )
Delta features:               d[m] = ( sum_{n=1..N} n (c[m+n] - c[m-n]) ) / ( 2 sum n^2 )
Telephony band-limit:         x_tel = codec( resample_8k( bandpass_300_3400( x ) ) )
```

### **11.3 Training mathematics for the anti-spoof model** 

Let each chunk have a label y in {0 bona fide, 1 spoof} and let the network produce logits z_0, z_1 with softmax probabilities p_c = exp(z_c) / sum_j exp(z_j). 

```
Weighted cross-entropy:   L_WCE = - (1/N) sum_i  w_{y_i} * log p_{y_i}(x_i),   w = [0.1, 0.9]
```

```
Focal loss:              L_focal = - (1/N) sum_i  alpha_{y_i} (1 - p_{y_i})^gamma log p_{y_i},   gamma = 2
```

```
One-class softmax (OC-Softmax), embedding x_hat and target direction w_hat, margins m_0, m_1:
   L_OC = (1/N) sum_i log( 1 + exp( alpha * ( m_{y_i} - w_hat^T x_hat_i ) * (-1)^{y_i} ) )
   typical values from the original paper: alpha = 20, m_0 = 0.9, m_1 = 0.2   (verify when implementing)
```

```
Optimiser step (AdamW):  theta <- theta - lr * m_hat / (sqrt(v_hat) + eps) - lr * lambda * theta
```

```
Platt scaling (on dev set):   p_cal = sigmoid( a * s + b ),   (a, b) = argmin  - sum [ y log p + (1-y) log (1-p) ]
Expected calibration error:   ECE = sum_b ( |B_b| / N ) * | acc(B_b) - conf(B_b) |
```

**Why weighted or margin losses?** Spoof training sets are imbalanced and the test attack distribution differs. Margin-based and class-weighted losses reduce over-confidence on the training attacks and give a compact bona fide class, which tends to transfer better to unseen generators. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 34 

#### **Metrics** 

```
FAR(t) = fraction of spoof accepted as bona fide at threshold t;   FRR(t) = fraction of bona fide rejected
EER = value where FAR(t*) = FRR(t*)          (lower is better; report with confidence interval via bootstrap)
AUC = P( score(spoof) > score(bona fide) )
```

```
minDCF = min over t of  [ C_miss * P_miss(t) * pi + C_fa * P_fa(t) * (1 - pi) ]
```

```
Report EER separately for: in-domain, cross-dataset, each codec, each language, each held-out generator.
```

### **11.4 Scam-phrase engine mathematics** 

```
Rule score (noisy-OR over matched signals i with weights w_i in (0,1)):
   s_rule = 1 - prod_i (1 - w_i)
```

```
Classifier (logistic regression on TF-IDF vector x):   s_clf = sigmoid( w^T x + b )
   TF-IDF:  tfidf(t,d) = tf(t,d) * log( (1 + N) / (1 + df(t)) ) + 1
   Multi-label loss (BCE):  L = - sum_c [ y_c log p_c + (1 - y_c) log (1 - p_c) ]   with positive weights for rare classes
```

```
Combined text score:   s_t = max( s_rule, s_clf )   or a small learned blend
```

```
Metrics: precision, recall, F1 per category; PR-AUC; false alerts per 100 benign calls;
         macro-F1 across categories and across languages (EN / HI / Hinglish).
```

### **11.5 Fusion, thresholds and decision theory** 

```
Fusion:       R_t = sigmoid( w0 + w1 * s_a + w2 * s_t + w3 * s_c )
Smoothing:    R~_t = alpha * R_t + (1 - alpha) * R~_{t-1}
Evidence accumulation (optional): L_t = decay * L_{t-1} + logit(R_t) - logit(prior)
```

```
Cost-based threshold:  alert when  P(scam | evidence) >= C_fa / (C_fa + C_miss)
   example: false alert costs 1 unit (annoyance), a missed scam costs 50 units  =>  threshold = 1/51 = about 0.02
   an Amber alert only prompts a 10-second code check (cheap), so a low Amber threshold is acceptable;
   Red (full-screen stop) uses a higher cost ratio, e.g. C_miss / C_fa = 5 => threshold about 0.17;
   adjust to meet the false-Red target.
```

```
Choosing T1 and T2 empirically: sweep thresholds on dev data;
   pick T1 so Amber false rate on benign calls is at most 2 per 100,
   and T2 so Red false rate is at most 0.5 per 100; confirm on the test set.
```

### **11.6 Identity-layer mathematics** 

```
HOTP(K, C) = Truncate( HMAC-SHA1(K, C) ) mod 10^d                      (RFC 4226)
TOTP(K)    = HOTP( K, floor( (T - T0) / X ) ),   X = 30 s, T0 = 0          (RFC 6238)
Truncate: offset = last nibble of HMAC; take 4 bytes from offset; clear the top bit (31-bit integer)
Guess probability per attempt = (window size) / 10^d    -- see Chapter 4.2 table
Entropy bits = log2( 10^d ) or log2( 2048^w )  for d digits or w words
```

### **11.7 Test plan and acceptance targets** 

|**Test**|**Data / method**|**Pass target (aim, not a claim)**|
|---|---|---|
|Code engine correctness|RFC 4226 and RFC 6238 test vectors; Dart and Python<br>parity; clock-skew tests|100 percent of vectors pass|
|Anti-spoof in-domain|Held-out speakers and generators from training sets|EER below 5 percent|
|Anti-spoof cross-dataset|Train on ASVspoof-type data, test on In-the-Wild and<br>own clones|Report honestly; aim EER below 25<br>percent; show the gap|
|Anti-spoof telephony|Test set passed through AMR-NB / G.711 / Opus at 8<br>kHz|Report EER per codec; target within<br>2x of clean EER|
|Scam text|Held-out templates; Hinglish paraphrases; hard<br>negatives|Recall at least 0.85 for severity 3;<br>false alerts under 2 per 100 benign|
|Fusion end-to-end|20 scripted call scenarios (10 scam, 10 benign)<br>replayed through WebSocket|At least 9 of 10 scams reach Amber;<br>at most 1 of 10 benign reach Amber;<br>no benign Red|
|Latency|Replay with timing|First Amber within 8 s; real-time<br>factor below 0.5|
|Usability|5 volunteers (including at least 2 over 55) run the<br>challenge|Under 15 s to complete; at least 4 of<br>5 succeed unaided|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 35 

|**Test**|**Data / method**|**Pass target (aim, not a claim)**|
|---|---|---|
|Security|Red-team: guessing, relay attempt, replay, clock<br>manipulation|No successful bypass; lockout<br>verified|
|Privacy|Review logs and storage|No audio, transcripts, codes or<br>secrets persisted|



**Evaluation rules.** No speaker appears in two splits. No scam template appears in two splits. At least one generator and one codec are held out entirely. Report the number you got, the dataset it came from, and the date. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 36 

## **12 The Ecosystem and How to Pitch It** 

### **12.1 Ecosystem map** 

|**Stakeholder**|**Integration**|**Value to them**|**Effort**|**When**|
|---|---|---|---|---|
|Families (Guardians and<br>Members)|Mobile app, optional WhatsApp or web<br>code bot|Protection and peace of mind|Done in<br>MVP|Now|
|UPI apps and banks|API: “this user was on a flagged call in<br>the last 5 minutes” or “family approval<br>required for this payee”; SDK for in-app<br>challenge|Fewer fraud losses and<br>complaints; regulatory<br>goodwill|High (partn<br>ership)|6 to 12<br>months|
|Telecom operators|Network-level call tagging; SIM-level<br>family pairing; promote app|Churn reduction, trust, fraud<br>mitigation|High|12<br>months|
|Phone makers / OS dialer<br>teams|Dialer-role integration, native challenge<br>prompt|Differentiating safety feature|High|12+<br>months|
|Insurers|Premium reduction for protected seniors|Lower claims|Medium|12<br>months|
|Law enforcement and<br>cyber cells|One-tap report to 1930 and<br>cybercrime.gov.in; anonymised<br>scam-number sharing|Faster reporting; richer<br>intelligence|Medium|6 months|
|NGOs and senior-citizen<br>groups|Awareness workshops using Practice<br>Call|Reach and trust|Low|Now|
|Enterprises|Same protocol for executive-voice<br>verification|Stops CEO-voice fraud|Medium|12<br>months|



### **12.2 Roadmap** 

|**Stage**|**Scope**|
|---|---|
|**Hackathon MVP (now)**|Pairing, rotating code, verify flow, tiered alerts from scam-phrase engine and anti-spoof<br>score, practice mode, speakerphone demo.|
|**0 to 3 months (pilot)**|Android dialer-role build, on-device models, WhatsApp code bot, 500-family pilot with a<br>senior-citizen NGO, privacy audit.|
|**3 to 12 months**|Bank and UPI app SDK, family payment approval, community scam-number sharing, iOS<br>identity layer, more languages.|
|**12+ months**|Carrier partnerships, OEM dialer integration, enterprise executive-verification product.|



### **12.3 The 5-minute pitch (slide by slide)** 

|**#**|**Slide**|**Say (key points)**|**Time**|
|---|---|---|---|
|1|**Hook:**play the cloned voice|“Hello Papa, I’m in trouble, please send money.” Pause. “That voice is not<br>our teammate. It was cloned from 10 seconds of a video. Would you have<br>paid?”|0:30|
|2|Problem and scale|A McAfee survey found 47 percent of Indian adults experienced or knew<br>someone hit by an AI-voice scam. Parents lose lakhs in minutes. UPI is<br>instant.|0:30|
|3|Why current tools fail|Detection is an arms race and, on compressed phone audio, a coin you<br>cannot rely on. Even at 90 percent accuracy, most alerts would be false<br>(show the 1.8 percent number).|0:30|
|4|**Insight:**prove, don’t guess|“A clone can copy a voice. It cannot copy a secret.” Rotating family code,<br>like a bank authenticator, on both phones.|0:30|
|5|How it works (diagram)|Show Figure 2: scores, tiers, challenge, verdict. “The AI decides when to<br>ask; the maths decides who is real.”|0:40|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 37 

|**#**|**Slide**|**Say (key points)**|**Time**|
|---|---|---|---|
|6|**Live demo**|Teammate calls judge in the cloned voice; app turns Amber then Red;<br>parent asks for the code; clone fails; real teammate reads the code; green.<br>(see 12.4)|1:15|
|7|Honest metrics|Show real EER (clean versus telephony), cross-dataset gap, scam-phrase<br>precision/recall. “Detection is a warning signal; the code is the protection.”|0:30|
|8|Market and ecosystem|Families, banks and UPI apps, telcos. B2B2C model. India first.|0:30|
|9|Privacy and ethics|On-device first, no audio stored, consented cloning only, secrets never<br>leave the phone.|0:15|
|10|Ask and roadmap|Pilot with a senior-citizen NGO and one bank or UPI app; Android dialer build<br>next.|0:20|



### **12.4 Demo script (about 75 seconds, with fallbacks)** 

1. **Setup (before stage):** Guardian phone (parent role) on the table with the app open; teammate B (real) holds Member phone; teammate A has the cloned-voice call ready (Twilio number or recorded clip on a second device). 

2. **Call 1 (scam):** the “relative” phones the judge’s Guardian phone on speaker with a scripted request (urgent, secret, UPI). Within about 8 seconds the app goes Amber and the banner says “Ask for the family code”. 

3. The judge asks: “Please read me your code.” The clone stalls or invents digits. Screen goes **Red** : “Treat as scam”. Family receives a push. 

4. **Call 2 (real):** the real teammate calls, asks for help; judge asks for the code; teammate reads it from the Member app; screen goes **green: Identity proven** . 

5. Close: “Even if the detector had said ‘human’, the clone still could not read the code.” 

6. **Fallbacks:** no Twilio, use speaker + laptop; no server, show the code check alone (it is offline); everything fails, play the 90-second video. 

### **12.5 Questions you will be asked** 

|**Question**|**Answer**|
|---|---|
|Why should anyone trust your<br>detector?|They should not rely on it alone, and we say so. It is a warning that triggers a proof.<br>We report real error rates, including on phone audio.|
|What if the scammer calls the real<br>child as well?|Directional keys and on-screen warnings reduce it, codes expire in 30 seconds and<br>only work for that one parent. Education built into the practice mode.|
|How do you make money?|Free family plan for adoption; B2B2C licensing to banks, UPI apps and telcos who<br>bear the fraud cost.|
|Why would a parent install this?|The adult child installs and sets it up. The parent only needs the big “Protect this<br>call” button.|
|What about iPhone?|Identity layer works today. Real-time call analysis on iOS needs partner or network<br>integration.|
|Is this legal?|We process audio transiently with consent, store nothing by default, and plan a legal<br>review before launch.|
|Can attackers beat your scam-phrase<br>engine?|Yes, with paraphrase. That is why it only raises the prompt; it never decides identity.|
|What did you build versus mock?|State clearly: code engine, pairing, verify flow, live alerts, and detector are real;<br>family approval for payments is a labelled mock.|
|Is voice cloning your teammate<br>ethical?|Written consent, labelled SYNTHETIC, teammate only, and shown to illustrate the<br>risk.|
|What is your moat?|The closed loop, the family network, Indian-language scam intelligence, and<br>partnerships with banks and telcos.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 38 

### **12.6 Claims discipline** 

- Never say “our detector is 99 percent accurate” unless you measured it on your own held-out phone-audio test set. Say what you measured. 

- Never say “we invented the safe word”. Say “we made it automatic, rotating and triggered at the right moment”. 

- Attribute statistics to their source and year; avoid single-blog figures. 

- Label mocks as mocks on the slide. 

- Taglines: “Prove who’s calling.” / “A clone can copy a voice. It can’t copy a secret.” 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 39 

## **13 RULE.md (Agent Working Rules)** 

Save the text below as **RULE.md** in the repository root (a ready-made copy is delivered alongside this PDF). It is written for the coding agent: it forces phase-by-phase work, one branch per phase, many small commits, permission gates before pushes and new phases, and heavy documentation so that any new agent can resume without prior context. 

**How to use it.** Start every agent session with: “Read RULE.md, HANDOFF.md and all files in docs/. Summarise the current state in five lines, then propose the next phase brief and wait for my permission.” 

These rules are binding. Read this file, then every file in `docs/` , before touching any code. If a rule here conflicts with an instruction from the developer, stop and ask which one wins. 

### **0. Prime Directives** 

1. **Work phase by phase.** Only the current phase exists. Never implement, scaffold, stub or "quickly add" anything that belongs to a later phase. 

2. **Stay inside the phase scope.** Every phase has an _In scope_ list and an _Out of scope_ list in `docs/02_PHASE_PLAN.md` . If something outside scope seems necessary, do NOT do it. Write it to `docs/05_BACKLOG.md` and ask the developer. 

3. **Ask before you act on anything irreversible or shared** (see Section 3, Permission Gates). 

4. **Document as you build.** Code without matching documentation is unfinished work. A new agent with zero context must be able to resume from the docs alone. 

5. **Never fake results.** No invented metrics, no hard-coded "detections" presented as model output, no silent mocks. Every mock is labelled `MOCK` in code, docs and UI. 

### **1. Branching Rules** 

- `main` is protected. Never commit to `main` directly. Never force-push. Never rewrite pushed history. 

- Each phase gets exactly one branch, created from the latest approved `main` : 

- `phase/<NN>-<short-name>` (example: `phase/03-verify-ui` ). 

- Work only on the current phase branch. Do not switch branches to "borrow" code from another phase. 

- Merge to `main` happens only through a pull request that the developer approves. The agent never merges on its own. 

- After a phase is merged, tag it: `phase-<NN>-done` . 

### **2. Commit Rules** 

- **Many small commits.** One logical change per commit. A phase should normally contain 6 to 15 commits. A single giant commit is a violation. 

- Use Conventional Commits: `feat:` , `fix:` , `docs:` , `test:` , `refactor:` , `chore:` , `perf:` . 

- Subject line: 72 characters or fewer, imperative mood. 

- Body (for any non-trivial commit) answers: **What** changed, **Why** , **Decision** taken (if any) and **Next** step. 

- **Docs travel with code.** A commit that changes behaviour must also update the relevant file in `docs/` in the same commit (at minimum `docs/03_PROGRESS_LOG.md` ). 

- Tests travel with code. New logic needs a test in the same commit or the very next one. 

- Never commit secrets, API keys, `.env` , model weights, datasets, audio recordings or personal data. Use `.env.example` and `.gitignore` . 

- Commit trailers: follow whatever attribution instructions the environment provides for commits and pull requests; do not invent your own. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 40 

### **3. Permission Gates (STOP and ask)** 

The agent must stop and receive an explicit "yes" from the developer before: 

|**#**|**Action**|**What to say when asking**|
|---|---|---|
|G1|Starting any new phase (including Phase 0)|Phase brief: goal, scope, out of scope, planned commits, time-box,<br>risks|
|G2|Any`git push`|Branch name, commit list, test results, docs updated|
|G3|Opening or merging a pull request|PR title, summary, checklist|
|G4|Adding a new dependency, service, or<br>paid/external API|Name, why, licence, cost, alternatives considered|
|G5|Deleting or moving files, or changing the repo<br>layout|Exact paths and reason|
|G6|Changing an accepted decision in<br>`docs/04_DECISIONS.md`|Old decision, new proposal, impact|
|G7|Handling real voice recordings or any personal<br>data|Whose data, consent status, where stored, retention|
|G8|Exceeding the phase time-box by more than 50<br>percent|What is slow, what to cut|



Format for every permission request: 

```
PERMISSION REQUEST [G#]
Context: ...
Proposed action: ...
Impact / risk: ...
Alternatives: ...
Waiting for: yes / no / change
```

After asking, do nothing else on that topic until the developer answers. Silence is not consent. 

### **4. Phase Protocol** 

Run these steps in order, every phase: 

1. **Orient.** Read `RULE.md` , `docs/00` to `docs/08` , and `HANDOFF.md` . Summarise the current state in 5 lines. 

2. **Brief.** Write the phase brief into `docs/02_PHASE_PLAN.md` (status becomes `PROPOSED` ). Ask permission **G1** . 

3. **Branch.** After approval, create the phase branch. Status becomes `IN PROGRESS` . 

4. **Build** in small commits. After each commit, append an entry to `docs/03_PROGRESS_LOG.md` . 

5. **Verify.** Run the full test suite, linter and the phase's acceptance checks. Record the real results. 

6. **Document.** Update architecture, API contracts, runbook, decisions and backlog. Update `HANDOFF.md` . 

7. **Report.** Produce the Phase Report (template in Section 6). Ask permission **G2** to push. 

8. **Stop.** After pushing, ask permission **G3** for the PR. Do not start the next phase until **G1** is granted for it. Definition of Done for a phase: all acceptance criteria met with evidence, tests green, docs updated, Phase Report written, nothing out of scope added. 

### **5. Documentation System (mandatory)** 

All files live in `docs/` except `HANDOFF.md` and `RULE.md` , which live in the repo root. 

|**File**|**Purpose**|**Update rule**|
|---|---|---|
|`HANDOFF.md`|10-minute resume guide for a brand-new agent:<br>what this is, current phase, how to run, what to do<br>next, known traps|Rewritten at the end of<br>every phase and whenever<br>the plan changes|
|`docs/00_PROJECT_BRIEF.md`|Problem, solution, users, non-goals, success criteria,<br>demo script|Rarely; log changes in<br>decisions|
|`docs/01_ARCHITECTURE.md`|Components, data flow, diagrams (text/Mermaid),<br>module boundaries, security model|When structure changes|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 41 

|**File**|**Purpose**|**Update rule**|
|---|---|---|
|`docs/02_PHASE_PLAN.md`|Every phase: goal, in/out of scope, branch, planned<br>commits, acceptance criteria,**status board**(TODO /<br>PROPOSED / IN PROGRESS / DONE / BLOCKED)|Every phase start and end|
|`docs/03_PROGRESS_LOG.md`|Append-only log, one entry per commit|Every commit|
|`docs/04_DECISIONS.md`|Architecture Decision Records (ADR)|Every technical decision|
|`docs/05_BACKLOG.md`|Ideas, out-of-scope requests, tech debt, known bugs|Whenever something is<br>deferred|
|`docs/06_RUNBOOK.md`|Exact commands to install, run, test, demo, reset|Whenever commands<br>change|
|`docs/07_API_CONTRACTS.md`|REST/WebSocket schemas, message examples, error<br>codes|Whenever an interface<br>changes|
|`docs/08_DATA_AND_MODELS.md`|Datasets, licences, splits, model versions, metrics,<br>known limitations|Whenever data or models<br>change|



Progress log entry template (one per commit): 

```
### <short-hash> | <type>: <subject> | phase/<NN>
```

- `Built: ...` 

- `Why: ...` 

- `Decision: (link ADR-xxx or "none")` 

- `Tests: what ran, result` 

```
- Left off / next: ...
```

ADR template: 

```
### ADR-<nnn>: <title>   (status: proposed | accepted | superseded)
```

- `Date / phase:` 

- `Context: the problem and constraints` 

- `Options considered: A, B, C with pros and cons` 

- `Decision: what we chose` 

- `Consequences: what becomes easier, harder, or risky` 

- `Decided by: developer | agent (approved by developer)` 

The status board in `docs/02_PHASE_PLAN.md` must always answer four questions: **What is to be built? What is built? What is left off? What technical decisions were taken (with ADR links)?** 

### **6. Phase Report Template** 

```
PHASE REPORT: phase/<NN>-<name>
Goal: ...
Delivered: (bullets, each linked to a commit)
Not delivered / deferred: (and where it was logged)
Decisions taken: (ADR links)
Tests: commands run + real output summary
Metrics (if any): real numbers, dataset, split, caveats
Docs updated: (files)
Risks and surprises: ...
Time spent vs time-box: ...
Ready to push? Asking permission G2.
```

### **7. Code Quality Rules** 

- Small modules with one responsibility. No file over about 400 lines without a reason noted in the log. 

- Type hints (Python) and static typing (Dart or TypeScript) everywhere. Linter and formatter must pass before every commit. 

- Every public function has a docstring: purpose, inputs, outputs, failure modes. 

- Cryptography: use vetted libraries only. Never write your own HMAC, hash or random generator. TOTP must pass the RFC 4226 and RFC 6238 test vectors. 

- Configuration through environment variables. No magic numbers: thresholds, window sizes and weights live in one config file with comments. 

- Errors are handled explicitly. No empty `except` blocks. Fail closed on identity verification (failure means NOT verified). 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 42 

- Keep functions deterministic where possible. Seed all randomness in training and tests. 

### **8. Security and Privacy Rules** 

- The TOTP secret never leaves the device and is never sent to the server, logged or printed. 

- Audio is processed transiently. By default the server stores no audio and no transcripts. Logs may hold scores, tiers and reason codes only. 

- Never log OTP codes, secrets, phone numbers in full, or transcript text. 

- Voice cloning is allowed only with the explicit written consent of the person whose voice is used (teammates for the demo). Every synthetic clip is named with a `SYNTH_` prefix and recorded in `docs/08_DATA_AND_MODELS.md` . 

- Do not scrape social media or collect real victims' recordings. 

- Dependencies: check the licence before adding (Gate G4). Record the licence in `docs/08` . 

### **9. Honesty and Evaluation Rules** 

- Report only numbers produced by code that was actually run, with the dataset, split and date. 

- Always report cross-dataset or cross-codec results next to in-domain results. Never present lab accuracy as real-world accuracy. 

- Label every mock, stub, fixture and hard-coded demo path as `MOCK` or `DEMO-ONLY` . 

- The anti-spoofing score is a **warning signal** . The code check is the **protection** . The UI and the docs must never claim certainty from the detector. 

- If a requirement cannot be met, say so plainly in the Phase Report. Do not hide it. 

### **10. Communication Rules** 

- Keep messages short and structured. Lead with the outcome, then evidence, then the question. 

- State assumptions explicitly. If two reasonable interpretations exist and the cost of a wrong guess is high, ask. 

- If blocked after two genuine attempts, stop and report: what was tried, what failed, what is needed. 

- Never claim something works without having run it. 

- At the end of every working session, update `HANDOFF.md` so the next agent can continue without any chat history. 

### **11. Hackathon Time-Box Rules** 

- Every phase has a time-box in `docs/02_PHASE_PLAN.md` . At 100 percent of the time-box, report status. At 150 percent, trigger Gate G8 and propose what to cut. 

- Cut order when time runs out (cut first to last): stretch features, polish, secondary languages, model training, live telephony demo (fall back to recorded or speakerphone demo). **Never cut:** the TOTP identity layer, the verify-caller flow, and documentation. 

- Always keep `main` demo-able. The last approved merge must run end to end with the documented runbook. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 43 

## **14 Phase-by-Phase Implementation Plan for the Agent** 

Each phase has its own branch, an in-scope and out-of-scope list, planned commits, acceptance criteria and documentation duties. The agent works on one phase at a time, asks permission before starting it (G1) and before pushing (G2), and stops at the end of the phase. Time-boxes add up to about 26 hours of focused work and map to the 36-hour timeline in Chapter 8. Commit lists are guidance: split further if a commit grows. 

### **14.1 Phase overview and status board** 

|**Phas**<br>**e**|**Branch**|**Goal**|**Time-bo**<br>**x**|**Status**|
|---|---|---|---|---|
|0|phase/00-bootstrap|Repo, tooling, docs skeleton, first ADRs|1.5 h|TODO|
|1|phase/01-crypto-core|TOTP, HKDF, words, lockout, duress as tested pure<br>functions|2 h|TODO|
|2|phase/02-pairing|Flutter shell, QR pairing, secure storage, offline codes on<br>two phones|3 h|TODO|
|3|phase/03-verify-flow|Verify-Caller UX, callback guard, TTS prompts, practice<br>mode|2.5 h|TODO|
|4|phase/04-backend-stream|FastAPI, WebSocket streaming, chunker, mobile audio<br>capture and stream client|2.5 h|TODO|
|5|phase/05-scam-engine|STT wrapper, lexicon, classifier, synthetic dataset,<br>evaluation CLI|3 h|TODO|
|6|phase/06-antispoof|Telephony simulator, pretrained anti-spoof inference,<br>calibration, evaluation|3 h|TODO|
|7|phase/07-fusion-alerts|Fusion engine, tiers, hysteresis, client alert UI, family<br>notify|2 h|TODO|
|8|phase/08-demo-path|Twilio or replay path, teammate clone, scripted scenarios|3 h|TODO|
|9|phase/09-eval-hardening|End-to-end evaluation, red-team tests, privacy review|2 h|TODO|
|10|phase/10-release|Pitch assets, fallback video, README, final docs|2 h|TODO|



This table is the seed for the status board in **docs/02_PHASE_PLAN.md** . The agent updates the Status column (TODO, PROPOSED, IN PROGRESS, DONE, BLOCKED) at the start and end of every phase and adds columns for _Built_ , _Left off_ and _Decisions_ (ADR links). 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 44 

**Phase 0 Bootstrap and documentation scaffold** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/00-bootstrap`| 1.5 h|
|**Goal**|Create a clean monorepo with tooling and a complete documentation skeleton so every later phase<br>starts from shared context.|
|**In scope**|• Repository layout (mobile, server, ml, demo, infra, docs)<br>• .gitignore, .env.example, README skeleton<br>• Pre-commit hooks and CI lint workflow<br>• Copy RULE.md; create HANDOFF.md and docs/00 to docs/08<br>• Seed ADR-001 (stack), ADR-002 (code format), ADR-003 (demo audio path)|
|**Out of scope**|• Any application code<br>• Models, datasets, accounts or paid services|
|**Planned commits**|1. chore: initialise monorepo layout and gitignore<br>2. docs: add RULE.md and HANDOFF skeleton<br>3. docs: project brief from this report (problem, solution, non-goals)<br>4. docs: architecture overview and diagrams<br>5. docs: phase plan with status board and acceptance criteria<br>6. docs: ADR-001 stack, ADR-002 code format, ADR-003 demo audio path<br>7. chore: pre-commit hooks and CI lint workflow<br>8. docs: runbook skeleton and README|
|**Acceptance**<br>**criteria**|✓ Fresh clone plus HANDOFF.md tells a new agent what to do next in under 10 minutes<br>✓ CI lint passes on an empty project<br>✓ docs/00 to docs/08 exist with real content, not placeholders only|
|**Docs to update**|All docs created; HANDOFF.md written.|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



### **Phase 1 Crypto core: TOTP, HKDF, words, lockout** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/01-crypto-core`| 2 h|
|**Goal**|A tiny, heavily tested library that generates and verifies codes identically in Dart and Python.|
|**In scope**|• HOTP and TOTP per RFC 4226 and RFC 6238<br>• HKDF-SHA256 directional key derivation<br>• Digit and 2-word encodings (2,048-word list)<br>• Window verification, lockout counter, duress code derivation<br>• Shared JSON test-vector file used by both languages|
|**Out of scope**|• UI, storage, networking<br>• Anything that calls a server|
|**Planned commits**|1. feat: HOTP with RFC 4226 vectors<br>2. feat: TOTP with RFC 6238 vectors<br>3. feat: HKDF directional keys<br>4. feat: word-list encoding and decoding<br>5. feat: verification window and lockout state machine<br>6. feat: duress code derivation<br>7. test: cross-language parity fixtures (Dart and Python)<br>8. test: property tests for window and clock-skew handling<br>9. docs: crypto design, ADR for hash and window choices|
|**Acceptance**<br>**criteria**|✓ 100 percent of RFC vectors pass in both languages<br>✓ Parity test produces identical codes for 1,000 random (key, time) pairs<br>✓ Lockout fails closed|
|**Docs to update**|docs/01 (security model), docs/04 (ADR-004 code format), docs/06 (how to run tests).|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 45 

### **Phase 2 Pairing and secure storage** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/02-pairing`| 3 h|
|**Goal**|Two phones pair in person and display matching codes with no internet.|
|**In scope**|• Flutter shell, roles (Guardian, Member), navigation<br>• QR create and scan; pairing fingerprint words<br>• Secure storage; biometric or PIN gate<br>• Pair list, rename, revoke, re-pair<br>• Code display screen for Member with 30 s countdown|
|**Out of scope**|• Audio, server, alerts<br>• Push notifications|
|**Planned commits**|1. feat: Flutter shell with role model and navigation<br>2. feat: guardian creates pair and shows QR<br>3. feat: member scans QR and stores secret securely<br>4. feat: pairing fingerprint confirmation<br>5. feat: biometric gate and secure storage wrapper<br>6. feat: member code screen with countdown<br>7. feat: revoke and re-pair<br>8. test: widget and integration tests for pairing<br>9. docs: pairing protocol and user flow|
|**Acceptance**<br>**criteria**|✓ Two physical phones in airplane mode show valid matching codes<br>✓ Revoked pair stops verifying<br>✓ Secret is not present in logs or screenshots|
|**Docs to update**|docs/01, docs/04 (ADR on secure storage), docs/06.|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



### **Phase 3 Verify-Caller flow and elderly UX** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/03-verify-flow`| 2.5 h|
|**Goal**|A guardian can run the challenge in under 15 seconds with large buttons and spoken prompts.|
|**In scope**|• Verify screen with digit or word entry<br>• Result screens: verified, failed, locked<br>• Hang up and call back button; duress behaviour<br>• Text-to-speech prompts in English and Hindi<br>• Large-text and high-contrast accessibility<br>• Practice Call mode with a harmless labelled sample|
|**Out of scope**|• AI scoring<br>• Server communication|
|**Planned commits**|1. feat: verify screen and code entry<br>2. feat: verified and failed result screens<br>3. feat: lockout and notify-family stub (MOCK)<br>4. feat: callback guard action<br>5. feat: duress flow<br>6. feat: spoken prompts EN and HI<br>7. feat: accessibility pass (font scale, contrast)<br>8. feat: practice call mode<br>9. test: widget tests for every outcome<br>10. docs: UX flows and copy deck|
|**Acceptance**<br>**criteria**|✓ Usability check with two volunteers over 55 completes challenge unaided<br>✓ All outcome screens reachable by tests<br>✓ MOCK elements labelled in code and UI|
|**Docs to update**|docs/00 (user flows), docs/05 (backlog), docs/06.|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 46 

### **Phase 4 Backend skeleton and audio streaming** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/04-backend-stream`| 2.5 h|
|**Goal**|Phone microphone audio reaches the server as clean 3-second chunks and a dummy score returns.|
|**In scope**|• FastAPI app, health endpoint, session token<br>• WebSocket protocol per docs/07<br>• Chunker with ring buffer, VAD hook, config loader<br>• Structured logs without content<br>• Dockerfile and compose<br>• Mobile audio capture and stream client<br>• Python test client that replays WAV files|
|**Out of scope**|• Real models<br>• Push notifications<br>• Authentication beyond a session token|
|**Planned commits**|1. feat: FastAPI app with health and config<br>2. feat: session token endpoint<br>3. feat: WebSocket receive PCM and chunker<br>4. feat: dummy scorer returning fixed JSON (MOCK)<br>5. feat: Docker and compose<br>6. feat: mobile mic capture and WSS client<br>7. test: replay client and chunker unit tests<br>8. docs: API contracts and runbook|
|**Acceptance**<br>**criteria**|✓ Phone streams 60 s of speech; server logs correct chunk count; no audio is persisted<br>✓ Reconnect works<br>✓ Round-trip latency measured and recorded|
|**Docs to update**|docs/07 (API contracts), docs/06 (runbook), docs/01.|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



### **Phase 5 STT and scam-phrase engine** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/05-scam-engine`| 3 h|
|**Goal**|Transcripts become a scam-language score with reason codes and honest evaluation, including<br>Hinglish and hard negatives.|
|**In scope**|• STT wrapper (faster-whisper) with language auto-detect<br>• Versioned lexicon file from Chapter 10<br>• Normalisation and transliteration map<br>• Rule engine (noisy-OR)<br>• Synthetic dataset v1 with split by template_id<br>• TF-IDF plus logistic regression baseline<br>• Evaluation CLI: precision, recall, F1, false alerts per 100 benign|
|**Out of scope**|• Transformer fine-tuning (stretch)<br>• Anti-spoof<br>• Fusion|
|**Planned commits**|1. feat: STT wrapper and VAD<br>2. feat: lexicon v1 and normaliser<br>3. feat: rule engine with reason codes<br>4. data: synthetic dataset v1 generation script and review notes<br>5. feat: template-grouped splits<br>6. feat: TF-IDF logistic regression baseline<br>7. feat: evaluation CLI and report<br>8. test: hard-negative regression tests<br>9. docs: data card and model card for the text engine|
|**Acceptance**<br>**criteria**|✓ Report shows real precision and recall on held-out templates<br>✓ Hard negatives do not produce Red<br>✓ Hinglish results reported separately from English|
|**Docs to update**|docs/08 (data and models), docs/04, docs/05.|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 47 

**Phase 6 Anti-spoof module** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/06-antispoof`| 3 h|
|**Goal**|A calibrated synthetic-voice score on 3-second chunks, evaluated honestly on telephony-simulated<br>audio.|
|**In scope**|• Telephony simulator (8 kHz, band-limit, AMR, G.711, Opus, noise)<br>• Pretrained detector inference via ONNX Runtime<br>• Chunk scoring and calibration (Platt scaling)<br>• Evaluation: in-domain, cross-dataset, per codec, per generator<br>• Model card with limitations|
|**Out of scope**|• Training from scratch (stretch phase S3)<br>• Fusion<br>• UI|
|**Planned commits**|1. feat: telephony simulator with unit tests<br>2. feat: dataset loaders and speaker-disjoint splits<br>3. feat: pretrained model wrapper and ONNX export<br>4. feat: chunk scoring service<br>5. feat: calibration on dev set<br>6. feat: evaluation CLI (EER, AUC, per-condition)<br>7. docs: model card and honest limitations<br>8. test: latency and parity tests|
|**Acceptance**<br>**criteria**|✓ EER reported for clean and telephony conditions on held-out data<br>✓ First score within 300 ms per chunk on target hardware<br>✓ Model licence recorded|
|**Docs to update**|docs/08, docs/04 (model choice ADR), docs/05.|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



### **Phase 7 Fusion, tiers and client alerts** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/07-fusion-alerts`| 2 h|
|**Goal**|The live loop: scores are fused, tiered and shown, and Amber or Red launches the challenge.|
|**In scope**|• Fusion model (logistic), EMA, hysteresis<br>• Threshold configuration and sweep script<br>• Reason-code mapping to plain language<br>• Client alert UI (Green, Amber, Red)<br>• Auto-launch of verify flow<br>• Family notify via FCM (metadata only)|
|**Out of scope**|• Payment approval features<br>• Carrier or bank integration|
|**Planned commits**|1. feat: fusion model and config<br>2. feat: smoothing and hysteresis<br>3. feat: threshold sweep script and chosen values<br>4. feat: reason-code copy in EN and HI<br>5. feat: client alert banner and full-screen stop<br>6. feat: auto-launch challenge on Amber and Red<br>7. feat: FCM family notify<br>8. test: scripted scenario tests<br>9. docs: tuning notes and ADR on thresholds|
|**Acceptance**<br>**criteria**|✓ Scripted scam replay reaches Amber within 8 s<br>✓ Benign replays stay Green<br>✓ No audio or transcript in push payloads|
|**Docs to update**|docs/01, docs/04, docs/07, docs/08.|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 48 

### **Phase 8 Realistic demo path** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/08-demo-path`| 3 h|
|**Goal**|A repeatable demo that uses telephony-quality audio and a consented teammate clone.|
|**In scope**|• Twilio (or replay) path streaming call audio to the server<br>• Teammate clone created with written consent; SYNTH_ file naming<br>• Scripted scam and benign scenarios<br>• Demo runbook with fallbacks<br>• Fallback video recording plan|
|**Out of scope**|• New product features<br>• Production telephony integration|
|**Planned commits**|1. feat: Twilio Media Streams adapter (mu-law decode)<br>2. feat: replay adapter for recorded calls<br>3. data: consented teammate clone and SYNTH_ naming<br>4. demo: scripted scenarios and timing sheet<br>5. docs: consent record and demo runbook<br>6. test: end-to-end scenario run script<br>7. docs: fallback ladder|
|**Acceptance**<br>**criteria**|✓ Demo runs end to end three times in a row<br>✓ Fallbacks tested<br>✓ Consent record stored (outside repo if personal)|
|**Docs to update**|docs/06, docs/08, HANDOFF.md.|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



**Phase 9 Evaluation, hardening and privacy review** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/09-eval-hardening`| 2 h|
|**Goal**|Real numbers, security checks and privacy review ready for the metrics slide.|
|**In scope**|• Run full test plan from Chapter 11.7<br>• Red-team tests (guessing, relay, replay, clock)<br>• Log and storage privacy audit<br>• Dependency licence check<br>• Performance and reliability fixes|
|**Out of scope**|• New features|
|**Planned commits**|1. test: red-team scripts for identity layer<br>2. test: end-to-end scenario suite with metrics<br>3. fix: issues found in evaluation<br>4. chore: dependency licence audit<br>5. docs: evaluation report with datasets, splits and caveats<br>6. docs: privacy review checklist results|
|**Acceptance**<br>**criteria**|✓ Report lists every number with dataset, split and date<br>✓ No secrets, codes, audio or transcripts persisted<br>✓ No critical open bug|
|**Docs to update**|docs/08, docs/05, docs/00 (success criteria).|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 49 

### **Phase 10 Pitch assets and release** 

|**Item**|**Detail**|
|---|---|
|**Branch / time-box**|`phase/10-release`| 2 h|
|**Goal**|Everything needed to present and to hand the project to someone else.|
|**In scope**|• Slide deck and speaker notes<br>• Fallback demo video<br>• README with quick start<br>• Final HANDOFF.md<br>• Release tag|
|**Out of scope**|• Code changes except demo-blocking fixes|
|**Planned commits**|1. docs: README quick start and architecture summary<br>2. docs: pitch outline and Q and A sheet<br>3. demo: fallback video notes and checklist<br>4. docs: final HANDOFF.md and backlog triage<br>5. chore: release tag and version notes|
|**Acceptance**<br>**criteria**|✓ A new person can run the demo from the README in under 15 minutes<br>✓ Every claim on the slides is traceable to a number or a source|
|**Docs to update**|All docs; HANDOFF.md.|
|**Gates**|G1 before start; G4 for any new dependency; G2 before push; G3 for the pull request.|



### **Stretch phases (only after Phase 10, each needs G1)** 

|**Id**|**Idea**|**Notes**|
|---|---|---|
|S1|Family approval for payments (mock), UPI deep-link demo|Label as MOCK; never touch real money.|
|S2|WhatsApp or web code bot for members without the app|Server holds no secret; web page uses device-stored<br>secret.|
|S3|Fine-tune or train the anti-spoof model with codec<br>augmentation|GPU needed; report cross-dataset results.|
|S4|On-device inference (ONNX Runtime Mobile)|Privacy story for production.|
|S5|Transformer text classifier for Hinglish (MuRIL or XLM-R)|Compare against baseline with the same splits.|



### **14.2 Documentation templates the agent must keep** 

#### **HANDOFF.md (rewrite at the end of every phase)** 

- `# HANDOFF  (updated: <date>, phase <NN>, by <agent/developer>)` 

- `## What this project is (3 lines)` 

- `## Current state` 

- `Phase status: 0 DONE, 1 DONE, 2 IN PROGRESS ...` 

- `Built: <bullets with commit hashes>` 

- `Not built / left off: <bullets>` 

- `Known bugs and traps: <bullets>` 

- `## How to run and test (exact commands)` 

- `## Key decisions (links to ADR-xxx)` 

- `## Next step (the one thing to do first)` 

```
## Open questions for the developer
```

#### **docs/02_PHASE_PLAN.md status board (example row)** 

```
| Phase | Status      | Built                              | Left off                       | Decisions        |
|-------|-------------|------------------------------------|--------------------------------|------------------|
| 1     | DONE        | HOTP, TOTP, HKDF, words (a1b2c3d)  | duress parity test deferred #12| ADR-004, ADR-005 |
| 2     | IN PROGRESS | QR create, secure storage (e4f5a6b)| biometric gate, revoke         | ADR-006          |
```

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 50 

#### **Commit message example** 

```
feat: derive directional HKDF keys for pairs
```

```
What: add hkdf_direction(k_pair, "A->B") and "B->A" in core/crypto.
Why: prevents a code shown by one side being valid in the other direction (relay attack).
Decision: ADR-005 (HKDF-SHA256, info string FVS1|dir).
Tests: RFC vectors unchanged; new direction tests pass (14 tests).
Next: word-list encoding.
```

### **14.3 Starter prompt for the coding agent** 

```
You are the coding agent for Family Voice Shield. Read RULE.md, HANDOFF.md and every file in docs/ first.
Work strictly phase by phase using docs/02_PHASE_PLAN.md. Do not do anything outside the current phase.
Before starting a phase, post the phase brief and wait for my permission (G1).
Use one branch per phase and many small commits; update docs in the same commits.
Ask permission before any push, pull request, new dependency, deletion, or use of real voice data.
Never invent metrics; label every mock. At the end of each phase, send the Phase Report and update HANDOFF.md.
Start now with the orientation summary (5 lines) and propose Phase 0.
```

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 51 

## **Sources and Verification Notes** 

Collected during research for this report (14 November 2026). Product claims reflect each vendor’s public statements at the time and should be re-checked before the final presentation. Vendor accuracy figures are the vendor’s own. 

|**Topic**<br>India voice-clone cases<br>and scale|**Source (title or outlet)**<br>AI Voice Cloning Scams: Parents Tricked by<br>Synthetic Calls (Lokmat Times, March 2024)|**URL**<br>lokmattimes.com/national/ai-voice-cloning-sca<br>ms-parents-tricked-by-synthetic-calls-from-alleg<br>ed-kidnappers-a505|
|---|---|---|
|Delhi-NCR cases|Scammers use AI to clone kids’ voices (Tabla)|tabla.com.sg/news/india/scammers-use-ai-to-clo<br>ne-kids-voices|
|Bhopal incidents|Scammers Using AI To Clone Kids’ Voices To<br>Dupe Parents (Free Press Journal)|freepressjournal.in/bhopal/bhopal-aatifical-inteli<br>gence-scare-scammers-using-ai-to-clone-kids-v<br>oices-to-dupe-parents|
|Indore case|AI Incident Database, incident 1339|incidentdatabase.ai/reports/7000|
|McAfee survey, India 47<br>percent|AI voice scams more prevalent in India<br>(Business World); AI Voice Cloning Scams Surge<br>in India (Hindu BusinessLine summary)|businessworld.in/article/ai-voice-scams-more-pr<br>evalent-in-india-affects-almost-50-indians-mcaf<br>ee-report-475192; threatcluster.io/cluster/ai-voi<br>ce-cloning-scams-surge-in-india-124ab5b6|
|83 percent lost money;<br>targeted profiles|How a 3-Second Voice Sample Becomes a Scam<br>in India (Cyber Secify)|cybersecify.com/blog/ai-voice-cloning-scam-indi<br>a|
|Loss amounts|AI Voice Scam: Virtual Kidnapping (Patrika, June<br>2026)|patrika.com/en/latest-technology/ai-voice-scam-<br>learn-about-virtual-kidnapping-and-3-ways-to-id<br>entify-real-vs-fake-voices-in-10-seconds-stay-al<br>ert-20195605|
|Truecaller AI Call<br>Scanner|Truecaller press release (May 2024); Help Net<br>Security; Speech Technology Magazine|helpnetsecurity.com/2024/05/29/truecaller-ai-ca<br>ll-scanner; speechtechmag.com/Articles/News/S<br>peech-Technology-News/TrueCaller-Launches-AI<br>-Call-Scanner-164270.aspx|
|Pindrop Pulse|Pindrop Pulse articles and press release (2024<br>to 2025)|pindrop.com/article/pindrop-pulse-for-audio-dee<br>pfake-detection; helpnetsecurity.com/2024/08/1<br>6/pindrop-pulse-inspect|
|Hiya Deepfake Voice<br>Detector|Hiya blog and press release (Oct 2024);<br>Engadget; TechRadar|blog.hiya.com/hiyas-new-chrome-extension-ide<br>ntifies-deepfakes; engadget.com/ai/a-new-chro<br>me-extension-can-reliably-detect-ai-generated-<br>voices-130059842.html|
|Family code word<br>advice|PC Gamer summary of FBI advice; Scientific<br>American; Fortune (Oct 2026)|pcgamer.com/software/ai/fbi-recommends-comi<br>ng-up-with-a-secret-word-or-phrase...; scientific<br>american.com/article/a-safe-word-can-protect-a<br>gainst-ai-impostor-scams; fortune.com/2026/10/<br>24/ai-voice-cloning-scam-fake-kidnapping-safe-<br>word|
|TrustWord (competitor)|TrustWord blog page (self-description, early<br>stage)|trustword.pages.dev/blog/voice-cloning-scams|



**Not independently verified in this report:** datasets’ current licences and download terms; third-party API pricing; the exact current status of Google, Airtel and other operator or OS scam-detection features in India; legal position on call analysis. Confirm each before relying on it in the pitch or in production. 

Family Voice Shield  |  Hackathon Report  |  14 Nov 2026 

Page 52 

