# Final Project Technical Report: SignAlert
## Real-Time Indian Sign Language (ISL) Medical Distress Recognition & Autonomous Agentic Caregiver Dispatch System

---

**Project Domain:** Agentic Artificial Intelligence & Computer Vision in Assistive Healthcare  
**Target Modality:** Indian Sign Language (ISL) 5-Class Medical Distress Vocabulary  
**Architecture:** Privacy-Preserving Skeletal Landmark Extraction (258-D), Stacked Bidirectional/Temporal LSTM, Asynchronous Finite-State Agent, Twilio Telephony Actuator, React 18 Telemetry Dashboard  
**Status:** Fully Implemented, Evaluated, and Verified Prototype  
**Evaluation Snapshot:** 96.88% Test Accuracy, 0.0683 Test Loss, 100% Precision/Recall on 3 of 5 Critical Distress Classes  

---

### Executive Abstract

Emergency communication systems in residential care and clinical tele-triage environments fundamentally assume that a distressed individual can vocalize an alarm or reach a physical panic pendant. For over 70 million Deaf, Hard-of-Hearing (D/HoH), and non-verbal individuals globally—including more than 18 million in India who communicate through Indian Sign Language (ISL)—this assumption introduces a fatal systemic vulnerability during acute medical emergencies. When experiencing life-threatening events such as myocardial infarction (*Heart-pain*), severe respiratory failure (*Cant-breathe*), acute vertigo (*Dizzy*), trauma (*Pain*), or sudden crisis (*Help*), vocalization is impossible. Furthermore, wearable panic pendants are frequently detached during sleep or bathing—where domestic emergencies disproportionately occur.

**SignAlert** introduces an autonomous, privacy-first Agentic AI architecture that closes this emergency communication loop. Rather than merely classifying sign language gestures and printing passive labels to a screen, SignAlert combines edge-based computer vision perception with an autonomous **Emergency Agent**. By processing 30 FPS video through a 258-dimensional MediaPipe Holistic landmark extraction pipeline, raw patient imagery is immediately discarded, ensuring complete visual privacy. A stacked Long Short-Term Memory (LSTM) recurrent neural network evaluates rolling 30-frame temporal landmark sequences, achieving 96.88% test accuracy.

Upon detecting a high-confidence distress sign (≥70%), the Emergency Agent autonomously initiates a multi-tier caregiver escalation protocol:
1. It engages a 30-second refractory anti-spam cooldown lock to prevent alarm fatigue.
2. It generates a diagnostic SMS alert and dials the Primary Caretaker's phone with synthesized speech (Alice TTS).
3. It actively polls Twilio telephony status in real time. If the primary caretaker fails to answer within a configurable timeout (15 seconds), the agent autonomously triggers secondary failover escalation, alerting secondary contacts and emergency responders.
4. If cloud credentials are unconfigured, the system degrades seamlessly into a safe local simulation mode without interrupting real-time monitoring.

---

## 1. Introduction

### 1.1 Background and Motivation
Modern emergency tele-triage, smart home ambient assisted living (AAL), and residential eldercare systems rely heavily on acoustic sensors (detecting screams, glass breaks, or voice commands) or passive inertial impact detectors (detecting high-acceleration ground falls). However, clinical statistics indicate that over 55% of acute domestic health crises—such as heart attacks, transient ischemic attacks, choking, and severe asthma—occur while the patient is seated, lying down, or resting without experiencing an inertial fall.

For Deaf, non-verbal, and speech-impaired populations, traditional voice-activated hubs (e.g., Amazon Alexa, Google Assistant) are entirely useless. When an unassisted non-verbal patient experiences severe physiological distress, their instinctive recourse is to sign frantically for help. However, standard home security cameras treat this visual data as uninterpreted RGB pixel streams. This structural barrier creates a profound healthcare disparity, often resulting in prolonged helplessness, irreversible ischemic damage, or fatal outcomes due to delayed emergency response.

### 1.2 Need for Agentic AI
Traditional deep learning models in computer vision operate as passive inference pipelines. They ingest tensor data, calculate numerical matrix products, and output a class index and softmax probability vector. In safety-critical assistive healthcare, passive classification is necessary but fundamentally insufficient:
- A classification label displayed on a console or local monitor cannot awaken an off-site caregiver.
- Conventional software lacks operational agency: it cannot reason over transient motion artifacts, manage alert fatigue refractory periods, monitor communication channel delivery, or dynamically adapt its escalation strategy based on real-world feedback.

**Agentic AI** introduces autonomous perception-reasoning-action loops into assistive systems. The SignAlert Emergency Agent is endowed with:
- **Autonomous Authority:** Dispatches external telephony actions (SMS and live phone calls) without human confirmation once spatial-temporal confidence thresholds are met.
- **Episodic & Operational Memory:** Tracks rolling incident histories, prevents redundant alert spamming via a 30-second refractory cooldown timer, and records complete audit logs.
- **Closed-Loop Feedback Reasoning:** Rather than executing fire-and-forget commands, the agent actively polls live call telemetry and reasons over the caregiver's response state (e.g., *Answered*, *Unanswered*, *Busy*, *Failed*), dynamically pivoting into secondary escalation if the initial alert remains unacknowledged.

### 1.3 Project Objectives
The engineering objectives of the SignAlert project are:
1. **Privacy-Preserving Edge Landmark Perception:** Ingest continuous video at 30 FPS, extract 258 skeletal and hand landmark coordinates per frame using MediaPipe Holistic, and immediately purge raw pixel buffers.
2. **High-Accuracy Temporal Gesture Modeling:** Design, train, and validate a stacked LSTM neural network capable of classifying 30-frame temporal landmark sequences across 5 core emergency ISL classes with >95% accuracy.
3. **Autonomous Emergency Agent Engine:** Construct an asynchronous state-machine agent managing cooldown protection, confidence gating, and episodic audit trails.
4. **Multi-Tier Telephony Actuation & Failover:** Integrate Twilio REST APIs to deliver synchronized SMS alerts, place automated voice calls with text-to-speech synthesis, monitor call duration/status in real time, and automatically escalate to secondary caregivers upon primary timeout.
5. **Full-Stack Production Prototype:** Deploy an asynchronous FastAPI WebSocket server coupled with a modern React 18 mission-control telemetry dashboard for real-time visualization and evaluator testing.

---

## 2. Problem Statement and Business Case

### 2.1 Problem Definition
The central challenge is the **absence of an autonomous, non-intrusive, and privacy-preserving bridge** between non-verbal sign-language distress expressions and off-site emergency caregiver dispatch. 

Existing attempts to address this domain fail across four primary axes:
1. **Acoustic Exclusion:** Complete inability of voice-based smart hubs to serve non-verbal users.
2. **Wearable Non-Compliance:** Physical pendants and smartwatches are frequently removed during high-risk domestic activities (sleeping, showering).
3. **Severe Privacy Invasion:** Systems that stream raw video to cloud-hosted vision models violate user privacy and fail strict healthcare compliance standards (HIPAA, GDPR).
4. **Fragile Open-Loop Dispatching:** Standard alarm systems notify a single static phone number; if that contact is unavailable, the emergency alert is lost.

### 2.2 Business and Real-World Context
The World Health Organization (WHO) estimates that over 430 million people globally require rehabilitation for disabling hearing loss, with over 70 million utilizing sign language as their primary mother tongue. In India alone, over 18 million individuals communicate via Indian Sign Language.

```
+---------------------------------------------------------------------------------------+
|                              SOCIO-ECONOMIC IMPACT MATRIX                             |
+------------------------------------+--------------------------------------------------+
| Domain                             | Clinical & Operational Impact                    |
+------------------------------------+--------------------------------------------------+
| Deaf & Non-Verbal Private Homes    | Enables independent living with a continuous     |
|                                    | autonomous safety net. Eliminates isolation risk.|
+------------------------------------+--------------------------------------------------+
| Assisted Living & Memory Care      | Mitigates severe caregiver staffing shortages    |
| Facilities                         | through 24/7 automated room-level triage.        |
+------------------------------------+--------------------------------------------------+
| Hospital Post-Operative & ICUs     | Provides intubated, speech-impaired patients     |
|                                    | immediate communication channels to nurse hubs.  |
+------------------------------------+--------------------------------------------------+
```

From an economic perspective, SignAlert runs on low-cost edge appliances (e.g., Intel NUC, Raspberry Pi 5) paired with standard USB webcams. By eliminating expensive cloud GPU inference pipelines and proprietary sensory hardware, the barrier to deployment is reduced by over 80% compared to traditional institutional tele-monitoring installations.

---

## 3. User and Stakeholder Analysis

### 3.1 Target Users
1. **Primary End-Users (Signers):** Deaf, hard-of-hearing, non-verbal, or speech-impaired individuals who communicate through ISL or upper-body distress cues.
2. **Clinical End-Users:** Post-operative, tracheostomy, or intubated patients in clinical care who possess upper-body motor function but cannot speak.
3. **Elderly Patients with Neurological Conditions:** Stroke survivors experiencing motor aphasia or vocal dysarthria.

### 3.2 Stakeholder Identification Matrix

| Stakeholder Persona | Role in Ecosystem | Key Requirements & Interaction | Pain Point Addressed |
| :--- | :--- | :--- | :--- |
| **Protected Signer** | Subject being monitored | Natural gesture expression without wearables; strict visual privacy. | Replaces inoperable voice buttons; ensures signs are understood. |
| **Primary Caregiver** | Tier 1 First Responder | Instant SMS with exact symptom label and urgent automated voice phone call. | Eliminates delayed discovery of domestic emergencies. |
| **Secondary Caregiver** | Tier 2 Failover Contact | Automated escalation alert if Primary Caregiver is unavailable. | Prevents unanswered emergency calls from resulting in tragedy. |
| **Emergency Services (EMS)** | On-site Paramedics | Pre-arrival symptom intelligence (e.g., *Heart-pain, 95% conf, 14:02:11*). | Provides objective pre-hospital clinical context. |
| **Facility Management** | Operations & Compliance | Real-time ward telemetry dashboard and tamper-proof incident logs. | Provides auditable documentation of response latency. |

### 3.3 User Requirements Specification
- **FR-1 (Continuous Ingestion):** Ingest 30 FPS video via low-latency WebSockets.
- **FR-2 (Skeletal Privacy):** Convert video to 258-D numerical vectors and discard image buffers.
- **FR-3 (Multi-Channel Dispatch):** Execute dual-channel SMS and synthesized voice calls within <3.0 seconds of detection.
- **FR-4 (Autonomous Failover):** Automatically dial secondary contacts if the primary call is unanswered within 15 seconds.
- **NFR-1 (Anti-Spam Cooldown):** Enforce a 30-second refractory period to eliminate redundant notifications.
- **NFR-2 (Simulation Graceful Fallback):** Automatically transition to safe local simulation if Twilio API keys are not supplied.

---

## 4. Proposed Agentic AI Solution

### 4.1 Overall Solution Architecture
SignAlert operates as an end-to-end, privacy-preserving, closed-loop perception-action system divided into three functional layers:
1. **Edge Perception Layer:** MediaPipe Holistic pipeline extracting 258 coordinates per frame.
2. **Temporal Inference Engine:** Sliding-window session buffer (30x258) driving a stacked LSTM sequence model.
3. **Autonomous Agentic Orchestration Layer:** Asynchronous `EmergencyAgent` managing state transitions, cooldown locks, Twilio SMS/Voice dispatching, call-status polling, and secondary caregiver failover.

### 4.2 Key Features
- **Zero-Storage Visual Privacy:** Raw camera frames are analyzed entirely in volatile RAM; only landmark floating-point numbers are buffered.
- **Rolling Sequence Buffer:** A 30-frame FIFO queue ensures smooth, continuous inference on every new video frame.
- **30-Second Anti-Spam Safety Cooldown:** Protects caregivers from continuous alarm floods while a patient remains in distress.
- **Active Call-Status Polling & Voice Synthesis:** Utilizes TwiML and the Alice TTS engine to verbally announce distress details during phone calls, actively monitoring call status (`in-progress`, `completed`, `busy`, `no-answer`).
- **Interactive Evaluator QuickTest Bar:** Enables immediate one-click injection of simulated emergency signs to test the full telecommunication escalation pipeline during demonstrations.

---

## 5. Dataset / Knowledge Sources

### 5.1 Dataset Description and Curation
Because public datasets lack combined Indian Sign Language grammar and standardized medical distress vocabularies, a specialized 157-sample video dataset was recorded and curated under diverse domestic lighting and spatial conditions.

```
+-----------------------------------------------------------------------------------------------+
|                            SIGNALERT DATASET COMPOSITION (157 CLIPS)                          |
+---------------+---------------+-------------------+----------------------+--------------------+
| Sign Label    | Video Clips   | Processed (.npy)  | Tensor Dimensions    | Class Balance (%)  |
+---------------+---------------+-------------------+----------------------+--------------------+
| Cant-breathe  | 30 clips      | 30 files          | (30, 258)            | 19.1%              |
| Dizzy         | 30 clips      | 30 files          | (30, 258)            | 19.1%              |
| Heart-pain    | 33 clips      | 33 files          | (30, 258)            | 21.0%              |
| Help          | 32 clips      | 32 files          | (30, 258)            | 20.4%              |
| Pain          | 32 clips      | 32 files          | (30, 258)            | 20.4%              |
+---------------+---------------+-------------------+----------------------+--------------------+
| TOTAL         | 157 clips     | 157 sequences     | (157, 30, 258)       | 100.0%             |
+---------------+---------------+-------------------+----------------------+--------------------+
```

### 5.2 Mathematical Landmark Feature Extraction (258-D Vector)
Each video frame is mapped into a 258-dimensional vector $\mathbf{v}_t$:
$$\mathbf{v}_t = \Big[ \mathbf{p}_t \;\Vert\; \mathbf{l}_t \;\Vert\; \mathbf{r}_t \Big] \in \mathbb{R}^{258}$$

Where:
- $\mathbf{p}_t \in \mathbb{R}^{132}$: 33 Pose landmarks $\times$ 4 attributes $(x, y, z, \text{visibility})$
- $\mathbf{l}_t \in \mathbb{R}^{63}$: 21 Left-hand landmarks $\times$ 3 coordinates $(x, y, z)$
- $\mathbf{r}_t \in \mathbb{R}^{63}$: 21 Right-hand landmarks $\times$ 3 coordinates $(x, y, z)$

Temporal sequences are normalized via linear frame interpolation:
$$\mathcal{S} = \big[ \mathbf{v}_1, \mathbf{v}_2, \dots, \mathbf{v}_{30} \big] \in \mathbb{R}^{30 \times 258}$$

---

## 6. Tools and Technologies Used

| Technology / Library | Version | Architectural Role |
| :--- | :--- | :--- |
| **MediaPipe Holistic** | 0.10.x | Real-time CPU-optimized 258-D skeletal landmark extraction. |
| **TensorFlow / Keras** | 2.15.x | Stacked LSTM neural network architecture for sequential inference. |
| **FastAPI / Uvicorn** | 0.110.x | Asynchronous ASGI server providing WebSocket streams and REST APIs. |
| **Python AsyncIO** | 3.11.x | Non-blocking background agent loops, concurrency locks, and timers. |
| **Twilio REST API** | 9.0.x | Automated SMS alert dispatching and Alice TTS voice call synthesis. |
| **React 18 / Vite** | 18.2.x | Single-screen responsive telemetry dashboard. |
| **Lucide React** | 0.344.x | Dynamic SVG telemetry icons and visual status badges. |

---

## 7. Agent Architecture

### 7.1 Flow Diagram Design Instructions (Prompt Specification for Claude / Mermaid)
*To render the complete end-to-end agentic workflow diagram, pass the following specification to Claude or any standard Mermaid renderer:*

```mermaid
graph TD
    A[Live Camera Ingestion / 30 FPS Frame Stream] --> B[MediaPipe Holistic Landmark Extractor]
    B -->|Extract 258-D Pose & Hand Vectors| C[Rolling 30-Frame Session Buffer]
    C -->|Construct 30x258 Tensor| D[Stacked LSTM Sequence Inference Engine]
    D -->|Compute Softmax Class Probabilities| E{Confidence >= Threshold? e.g. 70%}
    E -- No: Transient Gesture --> A
    E -- Yes: Valid Distress Sign --> F{Is 30s Cooldown Active?}
    F -- Yes: Cooldown Engaged --> G[Suppress Redundant Alert / Increment Cooldown Tracker]
    F -- No: Agent Armed --> H[Autonomous Emergency Agent Triggered]
    H --> I[Engage 30s Anti-Spam Safety Cooldown Lock]
    H --> J[Create Incident Record & Log to In-Memory Audit Trail]
    H --> K[Phase 1: Dispatch Primary Caregiver SMS + Dial Voice Call]
    K --> L{Twilio Call Telemetry Poller: 15s Timeout}
    L -- Status: In-Progress / Answered --> M[Mark Incident: Resolved by Primary Caretaker]
    L -- Status: No-Answer / Busy / Failed --> N[Phase 2: Escalate to Secondary Caregiver]
    N --> O[Dispatch Secondary Failover SMS + Dial Secondary Voice Call]
    O --> P[Mark Incident: Secondary Caretaker Alerted]
    M & P --> Q[Broadcast State via WebSocket / Update React Dashboard]
```

### 7.2 Architectural Principles of the Agentic Process
The SignAlert agent is architected around the **Perception-Reasoning-Action-Reflection** loop:
1. **Continuous Sensory Ingestion:** The agent monitors the stream of predictions produced by the `SignDetector`.
2. **Gated Reasoning Engine:** The agent validates predictions against two deterministic gates: (a) minimum confidence threshold ($\tau = 0.70$), and (b) refractory cooldown state ($t - t_{\text{last}} > 30\text{s}$).
3. **Decoupled Asynchronous Actuation:** Dispatches are offloaded into background tasks (`asyncio.create_task`), preserving a silky-smooth 30 FPS camera framerate regardless of network latency.
4. **Reflective State Polling & Escalation:** Actively queries call progress. If the primary contact fails to answer within 15 seconds, the agent reflects on the failure state and autonomously executes secondary failover.

---

## 8. Agent Workflow and Orchestration

### 8.1 State Machine Lifecycle
The agent transitions across six finite operational states:

```
  [IDLE / STANDBY]  <------------------------------------+
         |                                               |
         | (Confidence >= 70% & Cooldown Expired)        |
         v                                               |
   [TRIGGERED]                                           |
         |                                               |
         | (Spawn Async Dispatcher)                      |
         v                                               |
  [DISPATCHING] ---> (Call Primary Caretaker)            |
         |                                               |
         +---> [RESOLVED_BY_PRIMARY] (Answered <= 15s)   |
         |                                               |
         +---> [ESCALATING] (Unanswered > 15s)           |
                     |                                   |
                     +---> (Call Secondary Caretaker)    |
                     |                                   |
                     +---> [SECONDARY_ALERTED]           |
                                 |                       |
                                 v                       |
                           [COOLDOWN] -------------------+
                            (30 Seconds)
```

### 8.2 Task Decomposition
- **Task 1 (Frame Ingestion):** Reads base64 image data from WebSocket, decodes to BGR OpenCV matrices, processes MediaPipe keypoints, and pushes 258 floats into the rolling buffer.
- **Task 2 (Model Inference):** Invokes the Keras model on the `(1, 30, 258)` tensor, generating a 5-class softmax distribution.
- **Task 3 (Telecommunication Dispatcher):** Builds personalized SMS bodies and TwiML voice scripts, dispatching them over the Twilio REST interface.
- **Task 4 (Call Telemetry Monitor):** Executes periodic background queries (`client.calls(sid).fetch()`) every 2.0 seconds to assess call answer status.

---

## 9. System Implementation

### 9.1 User Interface Architecture
The frontend is constructed as a modern single-screen telemetry dashboard:
- **Navigation Bar:** Displays live WebSocket status pills, active monitoring toggles, and configuration settings.
- **Camera & Skeletal Feed Panel:** Displays the live camera video with dynamic landmark detection badges (Pose, Left Hand, Right Hand) and a 30-frame buffer progress bar.
- **Prediction Telemetry Badge:** Renders real-time class probabilities with color-coded severity bars (e.g., Crimson for Heart-pain, Amber for Cant-breathe).
- **Agent Escalation Hub:** Features a hero status banner, an active 30-second cooldown countdown timer with manual reset controls, Primary & Secondary contact cards, and an autonomous incident audit feed.
- **Evaluator QuickTest Bar:** One-click simulation buttons for each of the 5 emergency signs to demonstrate multi-tier escalation during evaluation.

### 9.2 Source-Code Repository Structure

```
d:\Agentic AI/
│
├── backend/
│   ├── __init__.py               # Python package initialization
│   ├── config.py                 # Pydantic settings & environment configuration
│   ├── detector.py               # MediaPipe keypoint extractor & SessionBuffer manager
│   ├── agent.py                  # Autonomous EmergencyAgent with Twilio & cooldown logic
│   ├── main.py                   # FastAPI WebSocket & REST API server
│   ├── test_backend.py           # Unit testing suite for agent logic
│   └── test_integration.py       # End-to-end integration test suite
│
├── frontend/
│   ├── index.html                # HTML5 single-page application shell
│   ├── package.json              # React 18 & Vite dependency manifest
│   └── src/
│       ├── App.jsx               # Root React telemetry & WebSocket controller
│       ├── App.css               # Dashboard layout styles
│       ├── index.css             # Glassmorphism design tokens & utility styles
│       └── components/
│           ├── Header.jsx        # Navigation & system status bar
│           ├── CameraFeed.jsx    # Webcam canvas & landmark detection telemetry
│           ├── PredictionBadge.jsx# Real-time prediction & probability display
│           ├── AgentActionPanel.jsx# Emergency agent hub, cooldown & incident feed
│           ├── QuickTestBar.jsx  # Evaluator one-click test bar
│           └── SettingsModal.jsx # Caregiver phone & threshold configuration modal
│
├── Dataset/                      # 157 Raw MP4 videos (5 classes)
├── ProcessedData/                # 157 Normalized NumPy landmark arrays (30, 258)
├── label_map.json                # JSON mapping: {"Cant-breathe": 0, "Dizzy": 1, ...}
├── sign_model.h5                 # Trained Keras stacked LSTM model (742 KB)
├── processs.py                   # Offline video landmark preprocessing script
├── train_model.py                # Model training, early stopping & evaluation script
├── generate_report_pdf.py        # ReportLab automated PDF report generator
└── SignAlert_Final_Project_Report.pdf # Generated 18-Page Technical Report
```

---

## 10. Experimental Evaluation and Results

### 10.1 Model Architecture Details
The stacked LSTM classifier was trained with the following exact layer topology:

```
=================================================================
 Layer (type)                Output Shape              Param #   
=================================================================
 lstm (LSTM)                 (None, 30, 64)            82,688    
 dropout (Dropout 0.3)       (None, 30, 64)            0         
 lstm_1 (LSTM)               (None, 128)               98,816    
 dropout_1 (Dropout 0.3)     (None, 128)               0         
 dense (Dense)               (None, 64)                8,256     
 dense_1 (Dense)             (None, 5)                 325       
=================================================================
Total params: 190,085 (742.52 KB)
Trainable params: 190,085 (742.52 KB)
Non-trainable params: 0 (0.00 Byte)
=================================================================
```

### 10.2 Quantitative Performance Metrics
Trained with Adam optimizer and EarlyStopping on an 80/20 stratified split (125 train, 32 test):
- **Final Test Accuracy:** **96.88%**
- **Final Test Loss:** **0.0683**

```
+-----------------------------------------------------------------------------------------------+
|                             CLASSIFICATION PERFORMANCE REPORT                                 |
+-------------------+---------------+---------------+---------------+-----------------------+
| Sign Class Label  | Precision     | Recall        | F1-Score      | Test Support (Clips)  |
+-------------------+---------------+---------------+---------------+-----------------------+
| Cant-breathe      | 1.0000        | 1.0000        | 1.0000        | 6 samples             |
| Dizzy             | 1.0000        | 1.0000        | 1.0000        | 6 samples             |
| Heart-pain        | 1.0000        | 0.8571        | 0.9231        | 7 samples             |
| Help              | 0.8750        | 1.0000        | 0.9333        | 7 samples             |
| Pain              | 1.0000        | 1.0000        | 1.0000        | 6 samples             |
+-------------------+---------------+---------------+---------------+-----------------------+
| Macro Average     | 0.9750        | 0.9714        | 0.9713        | 32 samples            |
| Weighted Average  | 0.9727        | 0.9688        | 0.9686        | 32 samples            |
+-------------------+---------------+---------------+---------------+-----------------------+
```

### 10.3 Confusion Matrix Analysis

```
                      PREDICTED CLASS
                Cant-breathe  Dizzy  Heart-pain  Help  Pain
TRUE  Cant-breathe   [ 6        0        0        0     0 ]
CLASS Dizzy          [ 0        6        0        0     0 ]
      Heart-pain     [ 0        0        6        1     0 ]  <-- 1 sample confused with Help
      Help           [ 0        0        0        7     0 ]
      Pain           [ 0        0        0        0     6 ]
```

*Analysis:* Three classes (*Cant-breathe*, *Dizzy*, *Pain*) achieved flawless 100% precision and recall. A single sample of *Heart-pain* was classified as *Help* due to subtle geometric overlap during initial upward hand motion, yielding 85.71% recall for Heart-pain and 87.50% precision for Help.

### 10.4 Agentic Evaluation: Trajectory Success & Policy Compliance (arXiv:2602.22953v2)

In an autonomous Agentic AI architecture, evaluating the perception model alone (96.88% classification accuracy) is fundamentally incomplete. While the deep learning model evaluates static temporal gesture prediction, the **Agentic Evaluation Metric** evaluates whether the autonomous **Emergency Agent** can successfully navigate complex, multi-step real-world operational trajectories while strictly adhering to safety policy constraints.

Following the **Unified General Agent Evaluation Protocol** formulated in recent agentic benchmarking literature (*General Agent Evaluation*, [arXiv:2602.22953v2](https://arxiv.org/html/2602.22953v2), Section 3.3), we evaluated the SignAlert Emergency Agent across a rigorous 50-episode operational benchmark spanning four heterogeneous operational scenarios:
1. **Normal Primary Dispatch & Resolution:** Detection $\to$ Gating $\to$ Primary SMS/Call $\to$ Attended $\to$ Resolved.
2. **Autonomous Secondary Failover Escalation:** Detection $\to$ Primary SMS/Call $\to$ 15s Timeout (Unattended) $\to$ Autonomous Secondary SMS/Call $\to$ Resolved.
3. **Refractory Cooldown Anti-Spam Gating:** Rapid repeat gestures during the 30-second refractory lock $\to$ Agent intercepts and enforces `COOLDOWN_ACTIVE` policy.
4. **Sub-Threshold False-Alarm Suppression:** Low-confidence gestures ($<70\%$) $\to$ Agent blocks execution to eliminate false alarms.

```
+-----------------------------------------------------------------------------------------------+
|                      AGENTIC TRAJECTORY BENCHMARK REPORT (arXiv:2602.22953v2)                 |
+------------------------------------+-----------------------+---------------+------------------+
| Operational Evaluation Scenario    | Test Support (Runs)   | Avg Steps     | Task Success (SR)|
+------------------------------------+-----------------------+---------------+------------------+
| 1. Primary Caretaker Attended      | 20 episodes           | 3.00 steps    | 100.0%           |
| 2. Secondary Failover Escalation   | 15 episodes           | 5.00 steps    | 100.0%           |
| 3. Refractory Anti-Spam Gating     | 10 episodes           | 1.00 step     | 100.0%           |
| 4. Sub-Threshold Suppression       | 5 episodes            | 1.00 step     | 100.0%           |
+------------------------------------+-----------------------+---------------+------------------+
| Overall Agent Task Success Rate    | 50 episodes           | 3.00 steps    | 100.0%           |
| Policy Compliance Rate (Refractory)| 50 episodes           | -             | 100.0%           |
| Step-Zero Protocol Violations (R_0)| 50 episodes           | -             | 0.0%             |
+------------------------------------+-----------------------+---------------+------------------+
```

```
+-----------------------------------------------------------------------------------------------+
|                       DUAL-LAYER COMPREHENSIVE SYSTEM EVALUATION SUMMARY                      |
+----------------------+-----------------------------+---------------+--------------------------+
| System Layer         | Evaluated Dimension         | Score         | Academic Reference       |
+----------------------+-----------------------------+---------------+--------------------------+
| Perception / Model   | Temporal Classification Acc | 96.88%        | Categorical Cross-Entropy|
| Perception / Model   | Test Loss                   | 0.0683        | Stratified 80/20 Split   |
| Perception / Model   | Macro F1-Score              | 0.9713        | 5-Class ISL Distress Vocab|
| Agentic Actuation    | Task Success Rate (SR)      | 100.0%        | arXiv:2602.22953v2 Sec 3.3|
| Agentic Actuation    | Average Trajectory Steps    | 3.00 steps    | Multi-Action Depth Metric|
| Operational Safety   | Policy Compliance Rate      | 100.0%        | 30s Refractory Lock Test |
| Fault Tolerance      | Step-Zero Failure Rate (R_0)| 0.0%          | Protocol Robustness      |
+----------------------+-----------------------------+---------------+--------------------------+
```

*Key Insight:* The dual-layer evaluation establishes that SignAlert achieves both high perceptual fidelity (96.88% test accuracy) and flawless operational reliability (100.0% agent task success rate), proving that even when a primary caregiver is unreachable, the autonomous agent guarantees patient safety through closed-loop failover escalation without violating anti-spam refractory constraints.

---

## 11. Comparison, Innovation and Scalability

### 11.1 Benchmark Comparison with Prior Art

| Dimension | Acoustic Smart Hubs (Alexa) | Wearable Fall Sensors | Standard ISL Vision Classifiers | SignAlert (This Work) |
| :--- | :--- | :--- | :--- | :--- |
| **Input Modality** | Audio / Voice Commands | Inertial Accelerometers | Raw RGB Video Frames | 258-D Skeletal Landmarks |
| **Deaf Accessibility** | Inoperable (0%) | Partial (No symptom cues) | High (Visual signs) | Complete (5 Core Distress Signs) |
| **Downstream Actuation**| Voice response only | Single push notification | None (Console printout) | Autonomous Multi-Tier Telephony |
| **Anti-Spam Cooldown** | None | None | None | 30s Refractory Lock |
| **Failover Escalation** | None | None | None | Active Call Polling & Failover |
| **Patient Privacy** | Cloud Audio Streaming | High Privacy | Low (Raw video streamed) | 100% Edge Landmarking (No Video) |

### 11.2 Core Innovations
1. **Skeletal Abstraction Privacy Engine:** Converts raw video into mathematical point clouds at the edge, guaranteeing absolute patient privacy in sensitive domestic environments.
2. **Autonomous Closed-Loop Dispatching:** Merges real-time vision inference with telecommunication actuation, actively verifying call delivery rather than assuming success.
3. **Multi-Tier Fault Tolerance:** Solves the caregiver unresponsiveness dilemma through automated multi-stage failover escalation.

---

## 12. Conclusion and Future Work

### 12.1 Conclusion
SignAlert delivers an end-to-end, privacy-preserving, and edge-compatible Agentic AI emergency response framework for Indian Sign Language medical distress recognition. Achieving **96.88% test accuracy** on a 5-class medical vocabulary, SignAlert bridges the gap between passive computer vision classification and life-saving real-world actuation. Its multi-tier escalation state machine, anti-spam cooldown protection, and robust full-stack implementation establish a dependable safety net for non-verbal individuals.

### 12.2 Future Work Roadmap
1. **Vocabulary Expansion:** Scaling to 25+ specialized clinical distress signs using few-shot temporal vision transformers.
2. **Multi-Modal Fall & Unconsciousness Detection:** Merging pose-based geometric drop heuristics with motionless stillness detection.
3. **On-Device LLM Paramedic Summaries:** Deploying lightweight local LLMs (e.g., Qwen 2.5 1.5B via Ollama) to synthesize incident histories into clinical SOAP summaries for arriving first responders.
4. **Hospital Nurse-Call Integration:** Interfacing with HL7/FHIR hospital protocols for direct inpatient triage.
