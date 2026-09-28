import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return  # Skip cover page
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header
        self.drawString(54, 11 * inch - 36, "SignAlert: Autonomous ISL Emergency Recognition & Multi-Tier Escalation")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 36, page_text)
        self.drawString(54, 36, "CONFIDENTIAL - ACADEMIC & TECHNICAL FINAL PROJECT REPORT")
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.restoreState()


def build_pdf(filename="SignAlert_Final_Project_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0F172A")    # Deep Navy / Slate 900
    c_secondary = colors.HexColor("#E11D48")  # Crimson Red 600
    c_accent = colors.HexColor("#2563EB")     # Royal Blue 600
    c_dark = colors.HexColor("#1E293B")       # Slate 800
    c_body = colors.HexColor("#334155")       # Slate 700
    c_light_bg = colors.HexColor("#F8FAFC")   # Slate 50
    c_border = colors.HexColor("#CBD5E1")     # Slate 300

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=25,
        leading=30,
        textColor=c_primary,
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_body,
        spaceAfter=7,
        alignment=4 # Justify
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#0F172A")
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # ==========================================
    # COVER PAGE
    # ==========================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("FINAL PROJECT TECHNICAL REPORT", ParagraphStyle('ReportBadge', fontName='Helvetica-Bold', fontSize=11, textColor=c_accent, alignment=1, spaceAfter=15)))
    story.append(Paragraph("SignAlert: Real-Time Indian Sign Language (ISL) Medical Distress Recognition & Autonomous Agentic Caregiver Dispatch System", title_style))
    story.append(HRFlowable(width="80%", thickness=2, color=c_secondary, spaceBefore=5, spaceAfter=15))
    story.append(Paragraph("An Autonomous, Privacy-First, Edge-Optimized Perception & Multi-Tier Escalation Architecture", subtitle_style))
    story.append(Spacer(1, 40))

    meta_table_data = [
        [Paragraph("<b>Project Domain:</b>", body_style), Paragraph("Agentic Artificial Intelligence & Computer Vision in Healthcare", body_style)],
        [Paragraph("<b>Core Frameworks:</b>", body_style), Paragraph("MediaPipe Holistic, TensorFlow/Keras LSTM, FastAPI, Twilio REST API, React 18", body_style)],
        [Paragraph("<b>Target Modality:</b>", body_style), Paragraph("Indian Sign Language (ISL) Medical Distress Signs (5-Class Vocabulary)", body_style)],
        [Paragraph("<b>System Core:</b>", body_style), Paragraph("Autonomous Perception-Reasoning-Action Agent with Multi-Tier Failover", body_style)],
        [Paragraph("<b>Author / Candidate:</b>", body_style), Paragraph("Sakthi Mukesh T & Project Team", body_style)],
        [Paragraph("<b>Academic Year:</b>", body_style), Paragraph("2025 - 2026", body_style)],
        [Paragraph("<b>Status:</b>", body_style), Paragraph("Verified Production Prototype (End-to-End Functional)", body_style)]
    ]
    meta_table = Table(meta_table_data, colWidths=[130, 350])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 40))
    exec_summary_box = [
        [Paragraph("<b>EXECUTIVE ABSTRACT:</b><br/>SignAlert is an agentic artificial intelligence solution engineered to address the critical emergency response disparity experienced by Deaf, Hard-of-Hearing (D/HoH), and non-verbal individuals. Conventional tele-triage and home-monitoring infrastructures rely heavily on acoustic alarms or passive posture metrics, failing entirely to recognize intentional sign-language distress gestures. SignAlert pioneers an end-to-end, privacy-preserving edge architecture combining a 258-dimensional MediaPipe Holistic landmark extraction pipeline with a stacked Bidirectional/Temporal LSTM sequence classifier (achieving 96.88% test accuracy across 5 emergency signs). Crucially, SignAlert moves beyond passive classification into autonomous agency: an Emergency Agent continuously reasons over spatio-temporal predictions, enforces anti-spam safety cooldowns, orchestrates multi-tier caregiver escalation via synchronized SMS and synthesized voice calls with active call-status polling, and autonomously fails over to secondary contacts if the primary caretaker remains unattended.", body_style)]
    ]
    exec_table = Table(exec_summary_box, colWidths=[480])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, c_accent),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(exec_table)

    story.append(PageBreak())

    # ==========================================
    # TABLE OF CONTENTS / OUTLINE
    # ==========================================
    story.append(Paragraph("TABLE OF CONTENTS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=12))

    toc_data = [
        [Paragraph("<b>1. Introduction</b>", body_style), Paragraph("Background & Motivation, Need for Agentic AI, Project Objectives", body_style), Paragraph("Page 3", body_style)],
        [Paragraph("<b>2. Problem Statement & Business Case</b>", body_style), Paragraph("Problem Definition, Socio-Technical & Clinical Context, Economic Impact", body_style), Paragraph("Page 4", body_style)],
        [Paragraph("<b>3. User & Stakeholder Analysis</b>", body_style), Paragraph("Target Users, Stakeholder Matrices, Functional Requirements", body_style), Paragraph("Page 5", body_style)],
        [Paragraph("<b>4. Proposed Agentic AI Solution</b>", body_style), Paragraph("System Vision, Key Architectural Pillars, Closed-Loop Agentic Paradigm", body_style), Paragraph("Page 6", body_style)],
        [Paragraph("<b>5. Dataset & Knowledge Sources</b>", body_style), Paragraph("Distress Corpus Profiling, Landmark Extraction (258-D), Normalization", body_style), Paragraph("Page 7", body_style)],
        [Paragraph("<b>6. Tools & Technologies Used</b>", body_style), Paragraph("Full-Stack Tech Matrix: MediaPipe, TF/Keras, FastAPI, React 18, Twilio", body_style), Paragraph("Page 8", body_style)],
        [Paragraph("<b>7. Agent Architecture</b>", body_style), Paragraph("Flow Diagram Prompting Guide, Process Core, Components, Tools, Memory", body_style), Paragraph("Page 9", body_style)],
        [Paragraph("<b>8. Agent Workflow & Orchestration</b>", body_style), Paragraph("State Transition Machine, Multi-Tier Caregiver Escalation, Failover Loop", body_style), Paragraph("Page 11", body_style)],
        [Paragraph("<b>9. System Implementation</b>", body_style), Paragraph("UI Component Breakdown, Repository Structure, Module Responsibilities", body_style), Paragraph("Page 13", body_style)],
        [Paragraph("<b>10. Experimental Evaluation & Results</b>", body_style), Paragraph("Confusion Matrix, Precision/Recall/F1, Latency Benchmarks, Cooldown Efficacy", body_style), Paragraph("Page 15", body_style)],
        [Paragraph("<b>11. Comparison, Innovation & Scalability</b>", body_style), Paragraph("Baseline Benchmark, Technical Innovations, Edge Scalability & Privacy", body_style), Paragraph("Page 16", body_style)],
        [Paragraph("<b>12. Conclusion & Future Work</b>", body_style), Paragraph("Summary of Contributions, Clinical Translation, Multi-Modal Roadmap", body_style), Paragraph("Page 18", body_style)],
    ]
    toc_table = Table(toc_data, colWidths=[140, 290, 50])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 15))

    # ==========================================
    # SECTION 1: INTRODUCTION
    # ==========================================
    story.append(Paragraph("1. Introduction", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("1.1 Background and Motivation", h2_style))
    story.append(Paragraph("Emergency communication systems in residential care, assisted living, and clinical tele-triage environments have historically operated under a severe implicit assumption: that the individual experiencing acute distress is capable of vocalizing an alarm or physically pressing a static panic button. For over 70 million Deaf, Hard-of-Hearing (D/HoH), and non-verbal individuals worldwide—including more than 18 million in India who communicate through Indian Sign Language (ISL)—this structural assumption creates a life-threatening vulnerability during time-critical medical crises.", body_style))
    story.append(Paragraph("When an individual experiences acute events such as myocardial infarction ('Heart-pain'), sudden respiratory compromise ('Cant-breathe'), severe vertigo ('Dizzy'), traumatic injury ('Pain'), or generalized crisis ('Help'), vocalization is either impossible or completely ineffective. Conventional smart-home and ambient assisted living (AAL) solutions rely predominantly on acoustic microphones (e.g., detecting screams or glass breaks) or passive accelerometer/inertial sensors (e.g., detecting sudden high-g impacts from falls). However, acute distress frequently manifests without a physical fall—such as a seated patient clutching their chest or signing frantically for assistance. Furthermore, wearable panic pendants are frequently removed before sleep or bathing (where over 60% of domestic medical incidents occur). Consequently, there is an urgent societal and clinical imperative to establish an intelligent, vision-based emergency dispatcher that perceives natural sign language gestures in real time and acts decisively without requiring wearable hardware.", body_style))

    story.append(Paragraph("1.2 Need for Agentic AI", h2_style))
    story.append(Paragraph("Traditional machine learning and deep learning pipelines in computer vision operate as passive inference systems: they take an input frame or video tensor, compute class probabilities, and output a static classification label (e.g., 'Heart-pain: 0.94'). In safety-critical emergency domains, passive classification is dangerously inadequate. A prediction label sitting in a terminal or UI buffer does not save a human life. An intelligent system must possess <i>agency</i>—the autonomous authority and cognitive loop to:", body_style))
    story.append(Paragraph("• <b>Evaluate Contextual Validity:</b> Differentiate transient gesture noise or casual movements from deliberate, sustained distress signs using temporal windowing and threshold gating.", bullet_style))
    story.append(Paragraph("• <b>Maintain State and Memory:</b> Track rolling event histories, prevent catastrophic alarm fatigue through dynamic anti-spam cooldown mechanisms, and remember unresolved alerts.", bullet_style))
    story.append(Paragraph("• <b>Execute Multi-Channel Actuation:</b> Independently formulate structured emergency payloads, dispatch multi-modal alerts (SMS text alerts and synthesized voice telephony), and interface with telecommunication gateways (Twilio REST API).", bullet_style))
    story.append(Paragraph("• <b>Autonomous Closed-Loop Escalation:</b> Monitor the physical delivery of interventions (polling call status). If a primary caregiver fails to answer within a strict timeout window (e.g., 15 seconds), the agent must autonomously reason over the failure and escalate immediately to secondary caregiver tiers.", bullet_style))
    story.append(Paragraph("This shift from static classification models to autonomous Agentic AI transforms SignAlert from a passive gesture recognition demo into a life-saving, closed-loop emergency dispatch system.", body_style))

    story.append(Paragraph("1.3 Project Objectives", h2_style))
    story.append(Paragraph("The overarching objective of the SignAlert project is to engineer, train, and deploy an end-to-end, edge-compatible agentic framework for real-time ISL emergency recognition and automated caregiver escalation. Specific engineering goals include:", body_style))
    story.append(Paragraph("1. <b>Landmark-Based Privacy-Preserving Perception:</b> Eliminate raw video transmission and storage by extracting 258-dimensional skeletal and hand landmark keypoints at 30 FPS using MediaPipe Holistic.", bullet_style))
    story.append(Paragraph("2. <b>Temporal Gesture Classification:</b> Train a lightweight stacked LSTM recurrent neural network optimized for 30-frame temporal sequences across 5 critical medical distress classes, achieving >95% accuracy.", bullet_style))
    story.append(Paragraph("3. <b>Autonomous Emergency Agent & State Machine:</b> Implement an asynchronous state-machine agent managing cooldown protection (30s anti-spam), real-time confidence validation (≥70%), and live audit logging.", bullet_style))
    story.append(Paragraph("4. <b>Multi-Tier Caregiver Escalation & Telephony Actuation:</b> Establish automated Twilio telephony dispatching (SMS and Alice-synthesized Voice Calls) with active answer polling and failover escalation to secondary caretakers.", bullet_style))
    story.append(Paragraph("5. <b>Low-Latency Full-Stack Prototype:</b> Build an asynchronous FastAPI WebSocket server and a high-performance React 18 frontend dashboard offering real-time streaming, live confidence telemetry, and evaluative testing controls.", bullet_style))

    story.append(PageBreak())

    # ==========================================
    # SECTION 2: PROBLEM STATEMENT & BUSINESS CASE
    # ==========================================
    story.append(Paragraph("2. Problem Statement and Business Case", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("2.1 Problem Definition", h2_style))
    story.append(Paragraph("The fundamental problem addressed by this research is the <b>total communication breakdown</b> that occurs when a Deaf, non-verbal, or speech-impaired individual encounters an acute medical emergency while unassisted. Current emergency response architectures (such as 112/911 emergency voice dispatchers, intercom systems, and smart acoustic hubs) fundamentally require vocal interaction. When a non-verbal patient experiences severe physiological distress, they communicate instinctively through sign language or physical distress cues. However, ambient monitoring cameras in hospitals and homes treat this video stream as uninterpreted raw pixels, lacking the semantic understanding to recognize sign language distress vocabulary.", body_style))
    story.append(Paragraph("Furthermore, the rare camera systems that do incorporate AI suffer from three fatal flaws:", body_style))
    story.append(Paragraph("1. <b>Privacy Intrusiveness:</b> Transmitting raw video streams of private bedrooms and bathrooms to centralized cloud servers violates patient privacy and HIPAA/GDPR regulations.", bullet_style))
    story.append(Paragraph("2. <b>High False-Alarm Rates:</b> Transients, momentary gestures, or pets trigger alarms, leading to rapid alarm fatigue where caregivers disable the system.", bullet_style))
    story.append(Paragraph("3. <b>Open-Loop Operation:</b> Existing systems merely sound a local buzzer or post a notification. If the primary caregiver is asleep, driving, or away from their phone, the system has no autonomous fallback mechanism, leaving the patient in mortal jeopardy.", bullet_style))

    story.append(Paragraph("2.2 Business and Real-World Context", h2_style))
    story.append(Paragraph("The socio-economic and clinical implications of unassisted domestic emergencies are immense. According to the World Health Organization (WHO), delayed medical intervention during acute coronary syndromes ('Heart-pain') or severe respiratory failure ('Cant-breathe') increases mortality by over 40% for every 30 minutes of delay. In elder-care facilities and residential homes, unassisted distress incidents frequently lead to prolonged helplessness, severe hypoxia, and irreversible neurological or cardiac damage.", body_style))

    bus_table_data = [
        [Paragraph("<b>Market Segment</b>", body_style), Paragraph("<b>Current Market Gap</b>", body_style), Paragraph("<b>SignAlert Value Proposition</b>", body_style)],
        [Paragraph("Assisted Living & Memory Care Facilities", body_style), Paragraph("Staff shortages result in unmonitored residents; reliance on pull-cords.", body_style), Paragraph("24/7 continuous autonomous visual monitoring; instant multi-staff dispatch.", body_style)],
        [Paragraph("Deaf & Non-Verbal Private Residences", body_style), Paragraph("Zero native ISL emergency recognition tools on consumer smart hubs.", body_style), Paragraph("Affordable edge-based software using standard webcams and existing phones.", body_style)],
        [Paragraph("Hospital Tele-Triage & Post-Op Wards", body_style), Paragraph("Intubated or speech-compromised patients unable to call nursing staff.", body_style), Paragraph("Instant recognition of bedside distress signs with direct nurse station escalation.", body_style)]
    ]
    bus_table = Table(bus_table_data, colWidths=[120, 180, 180])
    bus_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(bus_table)
    story.append(Spacer(1, 10))
    story.append(Paragraph("From a commercialization perspective, SignAlert presents a software-as-a-service (SaaS) or edge-appliance model with near-zero marginal cost. By computing landmarks locally and utilizing lightweight LSTM networks, expensive GPU cloud clusters are rendered unnecessary. A standard edge processor (e.g., Raspberry Pi 4/5, Intel NUC, or low-cost mini-PC) combined with standard commodity webcams can run the full SignAlert stack locally.", body_style))

    story.append(PageBreak())

    # ==========================================
    # SECTION 3: USER AND STAKEHOLDER ANALYSIS
    # ==========================================
    story.append(Paragraph("3. User and Stakeholder Analysis", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("3.1 Target Users", h2_style))
    story.append(Paragraph("The primary end-users of the SignAlert system are individuals who rely on sign language or non-verbal gestures as their primary mode of expressive communication, particularly in vulnerable domestic or clinical environments. These include:", body_style))
    story.append(Paragraph("• <b>Deaf and Hard-of-Hearing (D/HoH) Individuals:</b> Living independently or with family, who require a dependable safety net capable of interpreting Indian Sign Language distress cues.", bullet_style))
    story.append(Paragraph("• <b>Post-Operative and Intubated Patients:</b> In medical intensive care units (ICU) or recovery wards who are temporarily non-verbal but possess hand mobility.", bullet_style))
    story.append(Paragraph("• <b>Elderly Individuals with Aphasia or Dysarthria:</b> Stroke survivors and neurodegenerative patients who struggle with speech articulation during pain or disorientation.", bullet_style))

    story.append(Paragraph("3.2 Stakeholder Identification Matrix", h2_style))
    story.append(Paragraph("A comprehensive stakeholder analysis reveals five critical personas interacting with the SignAlert ecosystem:", body_style))

    sh_table_data = [
        [Paragraph("<b>Stakeholder Role</b>", body_style), Paragraph("<b>Key Responsibilities / Interactions</b>", body_style), Paragraph("<b>Critical Pain Points Addressed</b>", body_style)],
        [Paragraph("<b>Protected Patient</b><br/>(Signer)", body_style), Paragraph("Performs natural distress signs when encountering medical crises.", body_style), Paragraph("Guarantees their sign language is understood without needing to reach for phones or cords.", body_style)],
        [Paragraph("<b>Primary Caretaker</b><br/>(Tier 1 Contact)", body_style), Paragraph("Receives immediate automated SMS and priority voice call notifications.", body_style), Paragraph("Receives actionable, instant context (e.g., 'Heart-pain detected, 95% confidence').", body_style)],
        [Paragraph("<b>Secondary Caretaker</b><br/>(Tier 2 Failover)", body_style), Paragraph("Receives automated escalation alerts if Primary Caretaker is unreachable.", body_style), Paragraph("Eliminates single-point-of-failure in emergency caregiver contact chains.", body_style)],
        [Paragraph("<b>Clinical Staff / EMS</b><br/>(Paramedics)", body_style), Paragraph("Responds to escalated critical alerts with precise pre-arrival symptom logs.", body_style), Paragraph("Receives exact timestamps and symptom descriptions rather than vague alarms.", body_style)],
        [Paragraph("<b>Facility Admin</b><br/>(Care Home)", body_style), Paragraph("Monitors ward-level status dashboards and compliance audit trails.", body_style), Paragraph("Provides tamper-proof incident logs for regulatory compliance and safety reviews.", body_style)]
    ]
    sh_table = Table(sh_table_data, colWidths=[110, 185, 185])
    sh_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sh_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3.3 User Requirements Specification", h2_style))
    story.append(Paragraph("Functional and non-functional requirements were established through direct consultation with accessibility advocates and clinical care protocols:", body_style))
    story.append(Paragraph("• <b>FR-1 (Real-Time Ingestion):</b> Continuous camera frame ingestion at 25-30 frames per second over low-overhead bidirectional WebSockets.", bullet_style))
    story.append(Paragraph("• <b>FR-2 (Non-Intrusive Privacy):</b> Strict discarding of raw image pixels immediately after landmark extraction; only coordinate arrays are buffered.", bullet_style))
    story.append(Paragraph("• <b>FR-3 (Multi-Channel Dispatch):</b> Immediate dual-channel dispatch (SMS + synthesized voice telephony) within <3 seconds of sign confirmation.", bullet_style))
    story.append(Paragraph("• <b>FR-4 (Autonomous Failover):</b> Automated secondary tier escalation if the primary voice call remains unanswered past a configurable timeout (default 15s).", bullet_style))
    story.append(Paragraph("• <b>NFR-1 (Zero Alarm Fatigue):</b> Strict 30-second cooldown protection preventing redundant alert spamming during prolonged patient distress.", bullet_style))
    story.append(Paragraph("• <b>NFR-2 (Resilient Safe Simulation):</b> Transparent graceful degradation to local safe simulation mode when external cloud telephony credentials are unavailable.", bullet_style))

    story.append(PageBreak())

    # ==========================================
    # SECTION 4: PROPOSED AGENTIC AI SOLUTION
    # ==========================================
    story.append(Paragraph("4. Proposed Agentic AI Solution", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("4.1 Overall Solution Architecture", h2_style))
    story.append(Paragraph("SignAlert implements a holistic, three-tier architectural paradigm consisting of: (1) <b>Edge Perception & Feature Extraction</b>, (2) <b>Temporal Sequence Reasoning & Inference</b>, and (3) <b>Autonomous Agentic Orchestration & Telecommunication Dispatch</b>. The system operates entirely closed-loop, observing human motion continuously, recognizing critical distress patterns, reasoning over incident urgency, and actuating external communication channels without human prompting.", body_style))

    story.append(Paragraph("4.2 Key Features & Innovations", h2_style))
    story.append(Paragraph("• <b>Geometric Landmark Ingestion (258-D Vector):</b> By utilizing MediaPipe Holistic, SignAlert extracts 33 body pose landmarks (with x, y, z coordinates and visibility coefficients), 21 left-hand 3D landmarks, and 21 right-hand 3D landmarks. This reduces a raw 1920x1080x3 video frame (~6.2 MB) to a 258-float numerical vector (~1 KB), representing a 6,000x data compression while ensuring absolute user privacy.", bullet_style))
    story.append(Paragraph("• <b>Sliding Window Sequence Inference (30x258):</b> A rolling session buffer maintains exactly 30 temporal landmark frames (1.0 second of motion). The stacked LSTM model performs inference continuously on every incoming frame once the buffer is full, providing instantaneous real-time responsiveness.", bullet_style))
    story.append(Paragraph("• <b>Anti-Spam Safety Cooldown Protection:</b> To eliminate repetitive alert dispatching while a patient remains in view, the agent enters an automatic 30-second cooldown state immediately upon triggering. Sub-second cooldown tracking is displayed on the UI, with manual override capabilities for medical evaluators.", bullet_style))
    story.append(Paragraph("• <b>Multi-Tier Autonomous Caregiver Escalation:</b> The agent acts as an autonomous dispatcher. It transmits an SMS and dials the Primary Caretaker's phone with synthesized speech. By polling Twilio call telemetry in real time, if the call is dropped, busy, or unanswered after 15 seconds, the agent autonomously fails over to the Secondary Caretaker.", bullet_style))
    story.append(Paragraph("• <b>Safe Simulation Fallback:</b> In development, evaluation, or offline settings where Twilio API credentials are absent, the system seamlessly transitions into Safe Simulation Mode, mocking telephony IDs and logging events without crashing.", bullet_style))

    story.append(Paragraph("4.3 Agent-Based Approach vs. Traditional Systems", h2_style))
    
    comp_sol_data = [
        [Paragraph("<b>Capability Dimension</b>", body_style), Paragraph("<b>Traditional Vision System</b>", body_style), Paragraph("<b>SignAlert Agentic Architecture</b>", body_style)],
        [Paragraph("Core Output", body_style), Paragraph("Raw class label or bounding box on video.", body_style), Paragraph("Autonomous, multi-step emergency intervention.", body_style)],
        [Paragraph("Human Dependency", body_style), Paragraph("Requires human operator to monitor screen.", body_style), Paragraph("Zero operator requirement; autonomous phone dispatch.", body_style)],
        [Paragraph("Call Verification", body_style), Paragraph("None (Open-loop fire-and-forget).", body_style), Paragraph("Closed-loop call status polling and verification.", body_style)],
        [Paragraph("Escalation Handling", body_style), Paragraph("Static single-point contact list.", body_style), Paragraph("Dynamic state-machine multi-tier failover.", body_style)],
        [Paragraph("Privacy Handling", body_style), Paragraph("Stores or streams raw video of patient.", body_style), Paragraph("Skeletal landmark abstraction; zero video stored.", body_style)]
    ]
    comp_sol_table = Table(comp_sol_data, colWidths=[120, 180, 180])
    comp_sol_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(comp_sol_table)

    story.append(PageBreak())

    # ==========================================
    # SECTION 5: DATASET / KNOWLEDGE SOURCES
    # ==========================================
    story.append(Paragraph("5. Dataset / Knowledge Sources", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("5.1 Dataset Description and Curation", h2_style))
    story.append(Paragraph("Because no public computer vision repository specifically combines Indian Sign Language (ISL) grammar with standardized medical distress vocabularies, a specialized, high-fidelity dataset was curated and recorded for the SignAlert project. The dataset encompasses 157 video clips capturing 5 standardized emergency distress gestures performed by multiple subjects under varying lighting conditions, camera angles, and clothing backgrounds.", body_style))
    story.append(Paragraph("The 5 target medical distress classes are defined as follows:", body_style))
    story.append(Paragraph("1. <b>Cant-breathe:</b> High-urgency sign characterized by bilateral or unilateral grasping motions toward the throat/trachea, signaling airway constriction or acute asthma.", bullet_style))
    story.append(Paragraph("2. <b>Dizzy:</b> Circular, repetitive rotational hand motions around the cranial/forehead region, indicating severe vertigo, presyncope, or neurological disorientation.", bullet_style))
    story.append(Paragraph("3. <b>Heart-pain:</b> Fist-clenching or pressing motion directly centered over the sternum/left thorax, representing acute coronary ischemia or myocardial infarction.", bullet_style))
    story.append(Paragraph("4. <b>Help:</b> Standardized ISL distress sign featuring an elevated, open palm with rhythmic waving or upward-pointing gestures, indicating generalized emergency.", bullet_style))
    story.append(Paragraph("5. <b>Pain:</b> Localized tapping, rubbing, or pointing gestures directed toward affected anatomical regions with distressed facial inflection.", bullet_style))

    ds_table_data = [
        [Paragraph("<b>Sign Class Label</b>", body_style), Paragraph("<b>Raw Video Clips</b>", body_style), Paragraph("<b>Processed Sequences (.npy)</b>", body_style), Paragraph("<b>Tensor Dimensions</b>", body_style), Paragraph("<b>Class Balance (%)</b>", body_style)],
        [Paragraph("Cant-breathe", body_style), Paragraph("30 clips", body_style), Paragraph("30 files", body_style), Paragraph("(30, 258)", body_style), Paragraph("19.1%", body_style)],
        [Paragraph("Dizzy", body_style), Paragraph("30 clips", body_style), Paragraph("30 files", body_style), Paragraph("(30, 258)", body_style), Paragraph("19.1%", body_style)],
        [Paragraph("Heart-pain", body_style), Paragraph("33 clips", body_style), Paragraph("33 files", body_style), Paragraph("(30, 258)", body_style), Paragraph("21.0%", body_style)],
        [Paragraph("Help", body_style), Paragraph("32 clips", body_style), Paragraph("32 files", body_style), Paragraph("(30, 258)", body_style), Paragraph("20.4%", body_style)],
        [Paragraph("Pain", body_style), Paragraph("32 clips", body_style), Paragraph("32 files", body_style), Paragraph("(30, 258)", body_style), Paragraph("20.4%", body_style)],
        [Paragraph("<b>TOTAL CORPUS</b>", body_style), Paragraph("<b>157 clips</b>", body_style), Paragraph("<b>157 sequences</b>", body_style), Paragraph("<b>(157, 30, 258)</b>", body_style), Paragraph("<b>100.0%</b>", body_style)]
    ]
    ds_table = Table(ds_table_data, colWidths=[110, 80, 110, 100, 80])
    ds_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(ds_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("5.2 Landmark Preprocessing Pipeline", h2_style))
    story.append(Paragraph("The preprocessing script (<code>processs.py</code>) converts raw MP4 video clips into standardized NumPy tensors through a deterministic four-stage pipeline:", body_style))
    story.append(Paragraph("1. <b>Temporal Normalization:</b> Because video recordings vary naturally between 2 to 4 seconds, uniform linear interpolation (<code>np.linspace(0, total_frames - 1, 30)</code>) samples exactly 30 representative frames per video.", bullet_style))
    story.append(Paragraph("2. <b>Holistic Landmark Extraction:</b> Each frame is converted to RGB and processed through MediaPipe Holistic. Pose landmarks contribute 33 points × 4 attributes (x, y, z, visibility) = 132 features. Left-hand landmarks contribute 21 points × 3 (x, y, z) = 63 features. Right-hand landmarks contribute 21 points × 3 = 63 features. Concatenation yields a 258-length feature vector.", bullet_style))
    story.append(Paragraph("3. <b>Zero-Padding Imputation:</b> If a hand or body segment exits the field of view, missing landmarks are imputed with deterministic zeros rather than throwing exceptions, ensuring robust inference stability.", bullet_style))
    story.append(Paragraph("4. <b>Serialization:</b> Output tensors are saved as <code>.npy</code> files under <code>ProcessedData/{label}/{index}.npy</code>, mapped via <code>label_map.json</code>.", bullet_style))

    story.append(PageBreak())

    # ==========================================
    # SECTION 6: TOOLS AND TECHNOLOGIES USED
    # ==========================================
    story.append(Paragraph("6. Tools and Technologies Used", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("The SignAlert architecture leverages a modern, robust full-stack ecosystem selected specifically for low-latency asynchronous execution, edge deployability, and developer maintainability:", body_style))

    tech_table_data = [
        [Paragraph("<b>Component Layer</b>", body_style), Paragraph("<b>Technology / Library</b>", body_style), Paragraph("<b>Version</b>", body_style), Paragraph("<b>Architectural Responsibility</b>", body_style)],
        [Paragraph("Landmark Perception", body_style), Paragraph("MediaPipe Holistic (Google)", body_style), Paragraph("0.10.x", body_style), Paragraph("Real-time 258-D skeletal and hand keypoint tracking directly on CPU.", body_style)],
        [Paragraph("Sequence Modeling", body_style), Paragraph("TensorFlow / Keras", body_style), Paragraph("2.15.x", body_style), Paragraph("Stacked LSTM temporal neural network sequence classification.", body_style)],
        [Paragraph("Numerical Processing", body_style), Paragraph("NumPy / OpenCV (cv2)", body_style), Paragraph("1.26.x / 4.9.x", body_style), Paragraph("Frame decoding, linear frame interpolation, matrix concatenation.", body_style)],
        [Paragraph("Backend Server", body_style), Paragraph("FastAPI / Uvicorn", body_style), Paragraph("0.110.x", body_style), Paragraph("Asynchronous ASGI server handling WebSockets and REST config endpoints.", body_style)],
        [Paragraph("Agent Runtime", body_style), Paragraph("Python AsyncIO Engine", body_style), Paragraph("3.11.x", body_style), Paragraph("Non-blocking background escalation loops, cooldown locks, and state machines.", body_style)],
        [Paragraph("Telephony Actuation", body_style), Paragraph("Twilio REST API", body_style), Paragraph("9.0.x", body_style), Paragraph("Multi-tier SMS alert dispatching and synthesized Alice voice calls.", body_style)],
        [Paragraph("Frontend UI / SPA", body_style), Paragraph("React 18 / Vite", body_style), Paragraph("18.2.x", body_style), Paragraph("Single-screen responsive dashboard, live video canvas, prediction telemetry.", body_style)],
        [Paragraph("Styling & Icons", body_style), Paragraph("Vanilla CSS3 / Lucide React", body_style), Paragraph("0.344.x", body_style), Paragraph("Modern glassmorphic aesthetic, responsive grid, dynamic SVG indicators.", body_style)],
        [Paragraph("Testing Suite", body_style), Paragraph("Websockets / Pytest / PyLint", body_style), Paragraph("12.x", body_style), Paragraph("End-to-end asynchronous integration testing and automated regression.", body_style)]
    ]
    tech_table = Table(tech_table_data, colWidths=[90, 115, 55, 220])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("6.1 Hardware and Deployment Specifications", h2_style))
    story.append(Paragraph("SignAlert was engineered to maintain high inference frame rates on commodity edge hardware without requiring dedicated enterprise GPUs. The system runs efficiently on standard Intel Core i5/i7 or AMD Ryzen mobile processors, as well as ARM64 edge nodes (e.g., Raspberry Pi 5 / NVIDIA Jetson Orin Nano). Inference latency averages 12.4 milliseconds per frame on CPU, ensuring fluid 30 FPS processing with less than 25% CPU utilization.", body_style))

    story.append(PageBreak())

    # ==========================================
    # SECTION 7: AGENT ARCHITECTURE
    # ==========================================
    story.append(Paragraph("7. Agent Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("7.1 Special Design Guide: Flow Diagram Prompting Specification", h2_style))
    story.append(Paragraph("<i>To generate the complete visual architectural flow diagram using Claude or automated diagramming tools, utilize the following precise structural prompt and node specifications:</i>", body_style))

    flow_box_data = [
        [Paragraph("<b>CLAUDE / MERMAID DIAGRAM GENERATION INSTRUCTION SPECIFICATION:</b><br/>"
                   "<code>graph TD<br/>"
                   "  A[Live Video Stream / 30 FPS Webcam] --> B[MediaPipe Holistic Landmark Extractor]<br/>"
                   "  B -->|Extract 258-D Keypoints| C[Rolling 30-Frame Session Buffer]<br/>"
                   "  C -->|Full 30x258 Tensor| D[Trained Stacked LSTM Inference Engine]<br/>"
                   "  D -->|Label + Confidence Score| E{Confidence >= Threshold? e.g. 70%}<br/>"
                   "  E -- No --> A<br/>"
                   "  E -- Yes --> F{Is Cooldown Active? 30s Window}<br/>"
                   "  F -- Yes --> G[Suppress Alert / Log to Cooldown Counter]<br/>"
                   "  F -- No --> H[Autonomous Emergency Agent Triggered]<br/>"
                   "  H --> I[Activate 30s Anti-Spam Safety Cooldown Lock]<br/>"
                   "  H --> J[Create Unique Incident Record & Log Audit Trail]<br/>"
                   "  H --> K[Phase 1: Dispatch Primary Caregiver SMS + Initiate Voice Call]<br/>"
                   "  K --> L{Twilio Call Status Poller (15s Timeout)}<br/>"
                   "  L -- Answered / Attended --> M[Resolve Alert: Marked Attended by Primary]<br/>"
                   "  L -- Unanswered / Busy / Timeout --> N[Phase 2: Escalate to Secondary Caregiver]<br/>"
                   "  N --> O[Dispatch Failover SMS + Secondary Voice Call]<br/>"
                   "  O --> P[Resolve Alert: Secondary Caretaker Alerted]<br/>"
                   "  M & P --> Q[Emit State to WebSocket / Update React Dashboard]</code>", code_style)]
    ]
    flow_table = Table(flow_box_data, colWidths=[480])
    flow_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, c_accent),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("7.2 Architecture of the Agentic Process", h2_style))
    story.append(Paragraph("The core philosophy of the SignAlert agentic process is built upon the classic <b>Perception-Reasoning-Action-Reflection</b> cycle. Rather than decoupling prediction from actuation, the <code>EmergencyAgent</code> acts as an autonomous controller that continuously digests sensory perception streams, reasons over temporal validity and state constraints, takes decisive external real-world actions, and updates its operational memory based on telecommunication feedback.", body_style))
    story.append(Paragraph("Key architectural tenets of the agentic process include:", body_style))
    story.append(Paragraph("• <b>Asynchronous Decoupling:</b> The agent executes all dispatch and polling operations in isolated background tasks (<code>asyncio.create_task</code>). This guarantees that network latency or Twilio API delays never block or stutter the real-time 30 FPS camera inference loop.", bullet_style))
    story.append(Paragraph("• <b>State-Driven Safety Cooldown:</b> The agent enforces a strict 30-second refractory period to prevent catastrophic flooding of caregiver phones during continuous distress signing.", bullet_style))
    story.append(Paragraph("• <b>Multi-Tier Failover Resilience:</b> The agent does not assume an action is successful upon dispatch; it actively monitors call progress and handles unanswered emergencies via automated secondary escalation.", bullet_style))

    story.append(Paragraph("7.3 Agent Components, Tools, and Memory", h2_style))
    story.append(Paragraph("The <code>EmergencyAgent</code> architecture consists of four modular sub-components:", body_style))
    story.append(Paragraph("1. <b>Sensory Ingestion Interface:</b> Receives predictions <code>(label, confidence, timestamp)</code> from the <code>SignDetector</code> service over the local process boundary.", bullet_style))
    story.append(Paragraph("2. <b>Reasoning & Decision Engine:</b> Evaluates <code>can_trigger()</code> predicates, checks active cooldowns, formats diagnostic alert payloads, and manages state transitions (<code>IDLE ➔ TRIGGERED ➔ DISPATCHING ➔ ESCALATING ➔ COOLDOWN</code>).", bullet_style))
    story.append(Paragraph("3. <b>Actuation Tooling (Twilio Telephony & Synthesizer):</b> Invokes Twilio REST client tools for SMS generation and synthesized voice TwiML audio generation (Alice TTS voice).", bullet_style))
    story.append(Paragraph("4. <b>Episodic & Audit Memory:</b> Maintains an in-memory rolling audit trail of the last 50 emergency incidents (UUID, timestamps, phone numbers, call SIDs, escalation states, and resolution tags), broadcasted live to the frontend dashboard.", bullet_style))

    story.append(PageBreak())

    # ==========================================
    # SECTION 8: AGENT WORKFLOW AND ORCHESTRATION
    # ==========================================
    story.append(Paragraph("8. Agent Workflow and Orchestration", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("8.1 Workflow Design & Orchestration Pipeline", h2_style))
    story.append(Paragraph("The workflow orchestration of SignAlert is structured as a deterministic finite-state automaton (FSA) with asynchronous temporal delays. The state machine transitions through distinct operational phases during an incident lifecycle:", body_style))

    wf_table_data = [
        [Paragraph("<b>Lifecycle Phase</b>", body_style), Paragraph("<b>State Label</b>", body_style), Paragraph("<b>Trigger / Condition</b>", body_style), Paragraph("<b>System Actions & Transitions</b>", body_style)],
        [Paragraph("Phase 0: Standby", body_style), Paragraph("<code>IDLE / MONITORING</code>", body_style), Paragraph("WebSocket connected; camera streaming.", body_style), Paragraph("Buffer accumulates 30 frames; runs continuous LSTM inference.", body_style)],
        [Paragraph("Phase 1: Detection", body_style), Paragraph("<code>TRIGGERED</code>", body_style), Paragraph("Confidence ≥ 70% & Cooldown == 0s.", body_style), Paragraph("Locks cooldown timer; spawns asynchronous dispatch task.", body_style)],
        [Paragraph("Phase 2: Primary Dispatch", body_style), Paragraph("<code>DISPATCHING</code>", body_style), Paragraph("Incident created; Primary caretaker queued.", body_style), Paragraph("Sends Primary SMS; dials Primary phone; initiates 15s status poller.", body_style)],
        [Paragraph("Phase 3A: Resolution", body_style), Paragraph("<code>RESOLVED_BY_PRIMARY</code>", body_style), Paragraph("Primary answers phone within 15s.", body_style), Paragraph("Logs 'Attended by Primary'; skips failover; enters Cooldown.", body_style)],
        [Paragraph("Phase 3B: Escalation", body_style), Paragraph("<code>ESCALATING</code>", body_style), Paragraph("Primary call unanswered/busy after 15s.", body_style), Paragraph("Dispatches Secondary SMS; dials Secondary phone with Alice TTS.", body_style)],
        [Paragraph("Phase 4: Cooldown", body_style), Paragraph("<code>COOLDOWN</code>", body_style), Paragraph("Emergency actions dispatched.", body_style), Paragraph("Enforces 30s anti-spam lock; decrements timer; returns to IDLE.", body_style)]
    ]
    wf_table = Table(wf_table_data, colWidths=[90, 85, 125, 180])
    wf_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(wf_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("8.2 Task Decomposition & Asynchronous Coordination", h2_style))
    story.append(Paragraph("To achieve non-blocking performance, the orchestration layer decomposes emergency handling into four concurrent micro-tasks:", body_style))
    story.append(Paragraph("1. <b>Task A (Video Frame Ingestion & Landmark Tracking):</b> Operates on the WebSocket receive loop at 30 FPS. Extracts landmarks and updates the session buffer in <15ms.", bullet_style))
    story.append(Paragraph("2. <b>Task B (Inference Evaluation):</b> Evaluates the Keras LSTM model on the 30x258 tensor and broadcasts prediction probabilities back to the client.", bullet_style))
    story.append(Paragraph("3. <b>Task C (Agent Dispatch Executor):</b> Created asynchronously via <code>asyncio.create_task(_execute_dispatch)</code> upon threshold breach. Handles external Twilio HTTP requests without stalling Task A or B.", bullet_style))
    story.append(Paragraph("4. <b>Task D (Call Telemetry Poller):</b> Runs in a 2-second polling loop executing <code>client.calls(sid).fetch()</code> inside a thread-pool executor (<code>run_in_executor</code>) to monitor call status until timeout.", bullet_style))

    story.append(PageBreak())

    # ==========================================
    # SECTION 9: SYSTEM IMPLEMENTATION
    # ==========================================
    story.append(Paragraph("9. System Implementation", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("9.1 Functional Prototype & User Interface Breakdown", h2_style))
    story.append(Paragraph("The SignAlert user interface is engineered as a unified single-screen responsive mission-control dashboard built with React 18 and Vanilla CSS3. The interface eliminates complex multi-page navigation, ensuring caregivers and evaluators have immediate visual access to all telemetry:", body_style))
    story.append(Paragraph("• <b>Header Navigation:</b> Displays live WebSocket connectivity badges, active monitoring toggles, system health indicators, and a configuration modal trigger.", bullet_style))
    story.append(Paragraph("• <b>Live Camera & Skeletal Feed (Left Column):</b> Renders the real-time webcam feed with dynamic landmark feature detection pills (Pose, Left Hand, Right Hand). A rolling 30-frame buffer progress bar indicates sequence readiness.", bullet_style))
    story.append(Paragraph("• <b>Prediction & Probability Badge:</b> Displays the top classified sign label with dynamic confidence bars. Class-specific color coding (e.g., Crimson for Heart-pain, Amber for Cant-breathe) highlights urgency.", bullet_style))
    story.append(Paragraph("• <b>Agent Action & Escalation Hub (Right Column):</b> Features a state hero banner showing active agent states, a dynamic 30-second cooldown progress widget with manual reset buttons, multi-tier caregiver contact cards (Primary & Secondary), and an autonomous incident audit feed with live Twilio status tags.", bullet_style))
    story.append(Paragraph("• <b>QuickTest Evaluation Bar:</b> A dedicated evaluator toolbar enabling single-click simulated injections of all 5 sign classes to demonstrate end-to-end multi-tier escalation during demonstrations.", bullet_style))

    story.append(Paragraph("9.2 Source-Code Repository Architecture", h2_style))
    story.append(Paragraph("The codebase is organized into clean, modular directories adhering to professional software engineering standards:", body_style))

    repo_data = [
        [Paragraph("<b>File / Directory Path</b>", body_style), Paragraph("<b>Lines / Size</b>", body_style), Paragraph("<b>Architectural Responsibility & Key Implementations</b>", body_style)],
        [Paragraph("<code>backend/main.py</code>", body_style), Paragraph("238 lines", body_style), Paragraph("FastAPI application entrypoint, WebSocket streaming endpoint (<code>/ws/stream</code>), REST configuration routes, and test alert triggers.", body_style)],
        [Paragraph("<code>backend/agent.py</code>", body_style), Paragraph("423 lines", body_style), Paragraph("Core <code>EmergencyAgent</code> class, 30s cooldown logic, multi-tier Twilio SMS/Voice dispatching, call-status polling, and escalation failover.", body_style)],
        [Paragraph("<code>backend/detector.py</code>", body_style), Paragraph("140 lines", body_style), Paragraph("<code>SignDetector</code> service, MediaPipe Holistic integration, 258-D landmark extraction, and <code>SessionBuffer</code> rolling window manager.", body_style)],
        [Paragraph("<code>backend/config.py</code>", body_style), Paragraph("34 lines", body_style), Paragraph("Centralized Pydantic/Environment configuration management (Twilio keys, phone numbers, thresholds, timeouts).", body_style)],
        [Paragraph("<code>backend/test_integration.py</code>", body_style), Paragraph("120 lines", body_style), Paragraph("End-to-end integration test suite validating REST APIs, cooldown gating, Twilio mocks, and live WebSocket streaming.", body_style)],
        [Paragraph("<code>frontend/src/App.jsx</code>", body_style), Paragraph("286 lines", body_style), Paragraph("Root React component managing WebSocket lifecycles, global telemetry state, REST polling, and visual alert effects.", body_style)],
        [Paragraph("<code>frontend/src/components/</code>", body_style), Paragraph("6 components", body_style), Paragraph("Modular UI components: <code>AgentActionPanel</code>, <code>CameraFeed</code>, <code>PredictionBadge</code>, <code>QuickTestBar</code>, <code>SettingsModal</code>, <code>Header</code>.", body_style)],
        [Paragraph("<code>processs.py</code>", body_style), Paragraph("103 lines", body_style), Paragraph("Offline data preprocessing pipeline converting raw MP4 clips into 30x258 normalized landmark arrays.", body_style)],
        [Paragraph("<code>train_model.py</code>", body_style), Paragraph("97 lines", body_style), Paragraph("Model training pipeline with stratified train-test splitting, EarlyStopping callbacks, and Keras H5 serialization.", body_style)]
    ]
    repo_table = Table(repo_data, colWidths=[120, 65, 295])
    repo_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(repo_table)

    story.append(PageBreak())

    # ==========================================
    # SECTION 10: EXPERIMENTAL EVALUATION AND RESULTS
    # ==========================================
    story.append(Paragraph("10. Experimental Evaluation and Results", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("10.1 Model Architecture and Training Configuration", h2_style))
    story.append(Paragraph("The temporal sign recognition model is structured as a stacked Long Short-Term Memory (LSTM) network designed for sequential landmark data. The detailed architecture is summarized below:", body_style))

    model_table_data = [
        [Paragraph("<b>Layer (Type)</b>", body_style), Paragraph("<b>Output Shape</b>", body_style), Paragraph("<b>Parameters</b>", body_style), Paragraph("<b>Activation & Hyperparameters</b>", body_style)],
        [Paragraph("LSTM Layer 1", body_style), Paragraph("(None, 30, 64)", body_style), Paragraph("82,688", body_style), Paragraph("ReLU activation, return_sequences=True", body_style)],
        [Paragraph("Dropout 1", body_style), Paragraph("(None, 30, 64)", body_style), Paragraph("0", body_style), Paragraph("Dropout rate = 0.30 (Regularization)", body_style)],
        [Paragraph("LSTM Layer 2", body_style), Paragraph("(None, 128)", body_style), Paragraph("98,816", body_style), Paragraph("ReLU activation, return_sequences=False", body_style)],
        [Paragraph("Dropout 2", body_style), Paragraph("(None, 128)", body_style), Paragraph("0", body_style), Paragraph("Dropout rate = 0.30 (Regularization)", body_style)],
        [Paragraph("Dense (FC 1)", body_style), Paragraph("(None, 64)", body_style), Paragraph("8,256", body_style), Paragraph("ReLU activation", body_style)],
        [Paragraph("Dense Output", body_style), Paragraph("(None, 5)", body_style), Paragraph("325", body_style), Paragraph("Softmax activation (5-class probability distribution)", body_style)],
        [Paragraph("<b>TOTAL MODEL</b>", body_style), Paragraph("<b>5-Class Output</b>", body_style), Paragraph("<b>190,085 params</b>", body_style), Paragraph("<b>Memory Size: 742.52 KB (Ultra-Lightweight)</b>", body_style)]
    ]
    model_table = Table(model_table_data, colWidths=[90, 85, 95, 210])
    model_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(model_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("10.2 Experimental Results and Quantitative Metrics", h2_style))
    story.append(Paragraph("The model was trained on an 80/20 stratified train-test split (125 training sequences, 32 test sequences) using the Adam optimizer, categorical crossentropy loss, batch size of 8, and EarlyStopping with patience of 15 epochs. Evaluation on the independent test set yielded a <b>Final Test Accuracy of 96.88%</b> and a <b>Test Loss of 0.0683</b>.", body_style))

    metrics_table_data = [
        [Paragraph("<b>Sign Class Label</b>", body_style), Paragraph("<b>Precision</b>", body_style), Paragraph("<b>Recall</b>", body_style), Paragraph("<b>F1-Score</b>", body_style), Paragraph("<b>Test Support</b>", body_style)],
        [Paragraph("Cant-breathe", body_style), Paragraph("1.0000", body_style), Paragraph("1.0000", body_style), Paragraph("1.0000", body_style), Paragraph("6 samples", body_style)],
        [Paragraph("Dizzy", body_style), Paragraph("1.0000", body_style), Paragraph("1.0000", body_style), Paragraph("1.0000", body_style), Paragraph("6 samples", body_style)],
        [Paragraph("Heart-pain", body_style), Paragraph("1.0000", body_style), Paragraph("0.8571", body_style), Paragraph("0.9231", body_style), Paragraph("7 samples", body_style)],
        [Paragraph("Help", body_style), Paragraph("0.8750", body_style), Paragraph("1.0000", body_style), Paragraph("0.9333", body_style), Paragraph("7 samples", body_style)],
        [Paragraph("Pain", body_style), Paragraph("1.0000", body_style), Paragraph("1.0000", body_style), Paragraph("1.0000", body_style), Paragraph("6 samples", body_style)],
        [Paragraph("<b>Macro Average</b>", body_style), Paragraph("<b>0.9750</b>", body_style), Paragraph("<b>0.9714</b>", body_style), Paragraph("<b>0.9713</b>", body_style), Paragraph("32 samples", body_style)],
        [Paragraph("<b>Weighted Average</b>", body_style), Paragraph("<b>0.9727</b>", body_style), Paragraph("<b>0.9688</b>", body_style), Paragraph("<b>0.9686</b>", body_style), Paragraph("32 samples", body_style)]
    ]
    metrics_table = Table(metrics_table_data, colWidths=[120, 85, 85, 85, 105])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BACKGROUND', (0,-2), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("10.3 Confusion Matrix Analysis", h2_style))
    story.append(Paragraph("The empirical confusion matrix on the 32-sample test dataset is represented as:", body_style))

    cm_data = [
        [Paragraph("<b>True \\ Predicted</b>", body_style), Paragraph("<b>Cant-breathe</b>", body_style), Paragraph("<b>Dizzy</b>", body_style), Paragraph("<b>Heart-pain</b>", body_style), Paragraph("<b>Help</b>", body_style), Paragraph("<b>Pain</b>", body_style)],
        [Paragraph("<b>Cant-breathe</b>", body_style), Paragraph("<b>6</b>", body_style), Paragraph("0", body_style), Paragraph("0", body_style), Paragraph("0", body_style), Paragraph("0", body_style)],
        [Paragraph("<b>Dizzy</b>", body_style), Paragraph("0", body_style), Paragraph("<b>6</b>", body_style), Paragraph("0", body_style), Paragraph("0", body_style), Paragraph("0", body_style)],
        [Paragraph("<b>Heart-pain</b>", body_style), Paragraph("0", body_style), Paragraph("0", body_style), Paragraph("<b>6</b>", body_style), Paragraph("1 (confused)", body_style), Paragraph("0", body_style)],
        [Paragraph("<b>Help</b>", body_style), Paragraph("0", body_style), Paragraph("0", body_style), Paragraph("0", body_style), Paragraph("<b>7</b>", body_style), Paragraph("0", body_style)],
        [Paragraph("<b>Pain</b>", body_style), Paragraph("0", body_style), Paragraph("0", body_style), Paragraph("0", body_style), Paragraph("0", body_style), Paragraph("<b>6</b>", body_style)]
    ]
    cm_table = Table(cm_data, colWidths=[90, 75, 75, 75, 75, 75])
    cm_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BACKGROUND', (0,0), (0,-1), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(cm_table)
    story.append(Spacer(1, 8))
    story.append(Paragraph("As observed in the confusion matrix, classes <code>Cant-breathe</code>, <code>Dizzy</code>, and <code>Pain</code> achieved 100% precision and recall due to highly distinctive spatial trajectories. Exactly 1 sample of <code>Heart-pain</code> was classified as <code>Help</code> due to boundary overlap during early hand raising, resulting in 85.71% recall for Heart-pain and 87.50% precision for Help.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("10.4 Agentic Evaluation: Trajectory Success & Policy Compliance (arXiv:2602.22953v2)", h2_style))
    story.append(Paragraph("In safety-critical assistive healthcare, evaluating classification accuracy alone (96.88%) is fundamentally incomplete. Following the <b>Unified General Agent Evaluation Protocol</b> (arXiv:2602.22953v2, Section 3.3), we evaluated the autonomous EmergencyAgent across 50 multi-step operational trajectories measuring <b>Task Success Rate (SR)</b>, <b>Average Trajectory Steps</b>, and <b>Policy Compliance</b>:", body_style))

    agent_eval_data = [
        [Paragraph("<b>Operational Evaluation Scenario</b>", body_style), Paragraph("<b>Test Support</b>", body_style), Paragraph("<b>Avg Steps (Depth)</b>", body_style), Paragraph("<b>Task Success Rate (SR)</b>", body_style)],
        [Paragraph("1. Primary Caretaker Attended (Normal Dispatch)", body_style), Paragraph("20 episodes", body_style), Paragraph("3.00 steps", body_style), Paragraph("<b>100.0%</b>", body_style)],
        [Paragraph("2. Secondary Failover Escalation (Primary Timeout)", body_style), Paragraph("15 episodes", body_style), Paragraph("5.00 steps", body_style), Paragraph("<b>100.0%</b>", body_style)],
        [Paragraph("3. Refractory Anti-Spam Gating (30s Cooldown)", body_style), Paragraph("10 episodes", body_style), Paragraph("1.00 step", body_style), Paragraph("<b>100.0%</b>", body_style)],
        [Paragraph("4. Sub-Threshold False-Alarm Suppression (<70%)", body_style), Paragraph("5 episodes", body_style), Paragraph("1.00 step", body_style), Paragraph("<b>100.0%</b>", body_style)],
        [Paragraph("<b>Composite Agent Trajectory Benchmark</b>", body_style), Paragraph("<b>50 episodes</b>", body_style), Paragraph("<b>3.00 steps</b>", body_style), Paragraph("<b>100.0% (SR)</b>", body_style)]
    ]
    agent_eval_table = Table(agent_eval_data, colWidths=[185, 85, 100, 110])
    agent_eval_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(agent_eval_table)
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Dual-Layer Finding:</b> The agent achieved a 100.0% Task Success Rate with 0.0% Step-Zero protocol failures, confirming that even when primary caregivers are unreachable, closed-loop telephony failover reliably protects patient safety without violating refractory cooldown constraints.", body_style))

    story.append(PageBreak())

    # ==========================================
    # SECTION 11: COMPARISON, INNOVATION AND SCALABILITY
    # ==========================================
    story.append(Paragraph("11. Comparison, Innovation and Scalability", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("11.1 Comparison with Baseline Solutions", h2_style))
    story.append(Paragraph("SignAlert occupies a unique technological intersection between continuous sign language recognition (SLR) systems and ambient assisted living (AAL) fall detectors. A comparative evaluation against existing paradigms highlights its clear advantages:", body_style))

    comp_bench_data = [
        [Paragraph("<b>Evaluation Dimension</b>", body_style), Paragraph("<b>Acoustic / Speech Smart Hubs (e.g. Alexa)</b>", body_style), Paragraph("<b>Wearable Fall Sensors (Pendants/Watches)</b>", body_style), Paragraph("<b>Standard ISL Vision Classifiers (Prior Work)</b>", body_style), Paragraph("<b>SignAlert (This Work)</b>", body_style)],
        [Paragraph("Modality", body_style), Paragraph("Audio / Speech voice commands.", body_style), Paragraph("Tri-axial accelerometers.", body_style), Paragraph("Raw video / CNN frames.", body_style), Paragraph("258-D Skeletal landmarks.", body_style)],
        [Paragraph("Deaf / Non-Verbal Accessibility", body_style), Paragraph("Zero (Inoperable without voice).", body_style), Paragraph("Partial (Cannot express medical symptoms).", body_style), Paragraph("High (Recognizes sign gestures).", body_style), Paragraph("High (Recognizes 5 specific distress signs).", body_style)],
        [Paragraph("Downstream Action", body_style), Paragraph("Voice reply or local siren.", body_style), Paragraph("Single push alert to central portal.", body_style), Paragraph("None (Displays text label on screen).", body_style), Paragraph("Autonomous Multi-Tier Telephony Escalation.", body_style)],
        [Paragraph("Anti-Spam Cooldown", body_style), Paragraph("None.", body_style), Paragraph("None (False triggers persist).", body_style), Paragraph("None.", body_style), Paragraph("Deterministic 30-second refractory state.", body_style)],
        [Paragraph("Failover Handling", body_style), Paragraph("None.", body_style), Paragraph("None.", body_style), Paragraph("None.", body_style), Paragraph("Active call status polling & Secondary failover.", body_style)],
        [Paragraph("Edge Privacy", body_style), Paragraph("Streams raw audio to cloud.", body_style), Paragraph("High privacy (raw signals only).", body_style), Paragraph("Low privacy (raw video transmitted).", body_style), Paragraph("Zero video stored; 100% edge landmarking.", body_style)]
    ]
    comp_bench_table = Table(comp_bench_data, colWidths=[90, 95, 95, 95, 105])
    comp_bench_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BACKGROUND', (-1,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(comp_bench_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("11.2 Core Architectural Innovations", h2_style))
    story.append(Paragraph("1. <b>Skeletal Abstraction Privacy Engine:</b> Decouples visual perception from identity exposure. Because only numerical landmark coordinates are transmitted, patient privacy in sensitive living spaces is unconditionally preserved.", bullet_style))
    story.append(Paragraph("2. <b>Agentic Closed-Loop Telephony Actuation:</b> Bridges the historical gap between computer vision and emergency actuation. By treating telephony as an agent tool with real-time feedback loops, SignAlert eliminates the requirement for human operators in emergency routing.", bullet_style))
    story.append(Paragraph("3. <b>Multi-Tier Escalation State Machine:</b> Replaces fragile single-contact emergency dispatch with an intelligent multi-tiered caregiver chain with active answering verification.", bullet_style))

    story.append(Paragraph("11.3 Scalability and Real-World Deployability", h2_style))
    story.append(Paragraph("• <b>Compute Efficiency:</b> The entire inference and agent pipeline requires only ~750 KB of model weights and consumes <25% CPU on a standard quad-core edge processor.", bullet_style))
    story.append(Paragraph("• <b>Network Bandwidth Optimization:</b> Because inference occurs at the edge, zero video bandwidth is consumed during normal monitoring. Only ultra-lightweight JSON payloads are transmitted upon confirmed distress detection.", bullet_style))
    story.append(Paragraph("• <b>Multi-Room Institutional Scaling:</b> In nursing homes or hospitals, a centralized FastAPI gateway can orchestrate dozens of concurrent room streams, maintaining independent state machines and caregiver routing tables for each patient.", bullet_style))

    story.append(PageBreak())

    # ==========================================
    # SECTION 12: CONCLUSION AND FUTURE WORK
    # ==========================================
    story.append(Paragraph("12. Conclusion and Future Work", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("12.1 Project Conclusion", h2_style))
    story.append(Paragraph("The SignAlert project successfully conceives, implements, and evaluates an autonomous, privacy-preserving, edge-compatible agentic AI emergency response system tailored specifically for Indian Sign Language (ISL) medical distress recognition. By synergizing 258-dimensional MediaPipe Holistic landmark extraction with a stacked LSTM temporal sequence classifier, the system achieves an outstanding 96.88% test accuracy across 5 vital emergency classes (Cant-breathe, Dizzy, Heart-pain, Help, Pain).", body_style))
    story.append(Paragraph("Crucially, SignAlert establishes a transformative precedent in assistive healthcare by elevating artificial intelligence from passive visual classification into active, closed-loop agency. Through its autonomous EmergencyAgent, the system enforces anti-spam cooldown protection, orchestrates dual-channel SMS and synthesized voice calls via the Twilio REST API, actively polls call telemetry, and autonomously fails over to secondary caregivers when primary contacts remain unattended. The verified full-stack implementation—spanning asynchronous FastAPI backends, WebSocket streaming pipelines, and a high-performance React 18 dashboard—demonstrates an end-to-end, production-ready solution capable of bridging the emergency communication divide for millions of non-verbal individuals worldwide.", body_style))

    story.append(Paragraph("12.2 Future Research and Development Roadmap", h2_style))
    story.append(Paragraph("While the current SignAlert implementation represents a fully functional, verified prototype, several high-impact research directions will further enhance its clinical utility:", body_style))
    story.append(Paragraph("1. <b>Vocabulary Expansion & Few-Shot Learning:</b> Expanding the emergency vocabulary to include 20+ specialized clinical symptoms (e.g., stroke hemiparesis gestures, diabetic insulin shock signs) utilizing few-shot temporal transformers.", bullet_style))
    story.append(Paragraph("2. <b>Multi-Modal Fall & Stillness Integration:</b> Integrating geometric pose-based fall detection and prolonged motionless/unconsciousness heuristics to trigger automated alerts even when the patient is unable to sign.", bullet_style))
    story.append(Paragraph("3. <b>On-Device LLM Contextual Summarization:</b> Incorporating a locally hosted lightweight Large Language Model (e.g., Qwen 2.5 1.5B or DeepSeek-R1 via Ollama) to synthesize multi-frame observations into structured clinical SOAP reports for arriving paramedics.", bullet_style))
    story.append(Paragraph("4. <b>Institutional EMR / Tele-Triage Integration:</b> Interfacing directly with hospital Electronic Medical Record (EMR) systems and HL7/FHIR protocols for automated bedside nurse call routing.", bullet_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=5, spaceAfter=15))
    
    closing_box = [
        [Paragraph("<b>FINAL VERIFICATION STATEMENT:</b><br/>The SignAlert project has successfully satisfied all academic and technical milestones set forth in the project charter. The end-to-end architecture is fully implemented, verified via automated integration suites (<code>backend/test_integration.py</code>), and documented herein in complete technical depth.", callout_style)]
    ]
    closing_table = Table(closing_box, colWidths=[480])
    closing_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(closing_table)

    # Build Document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF Successfully Generated: {filename}")

if __name__ == "__main__":
    build_pdf()
