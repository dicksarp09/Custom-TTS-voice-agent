"""
SiriusMed LiveKit Voice Agent
==============================
Voice assistant for SiriusMed landing page demo.
Only discusses SiriusMed features - no medical advice.
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RunContext
from livekit.agents.llm import function_tool
from livekit.plugins import openai
from datetime import datetime
import os
import time
import logging
import random

# Load environment variables
load_dotenv(".env")

class SiriusAssistant(Agent):
    """SiriusMed voice assistant - discusses platform features only."""

    def __init__(self):
        super().__init__(
            instructions="""You are Sirius, the AI assistant for SiriusMed, a healthcare management platform.
            Your only job is to explain SiriusMed’s product features and workflows.
            You must not answer anything outside that scope.

            Behavior Rules:
            - You help users understand how SiriusMed works.
            - You explain platform features for doctors and patients.
            - You provide short, clear, conversational answers.

            Response Format:
            - Short replies, one to three sentences.
            - No markdown formatting.
            - No long lists unless responding through a function tool.
            - No made up features. If you are not sure something exists, ask the user.

            Allowed Topics:
            - voice documentation and note taking
            - appointment management
            - patient app features
            - secure messaging
            - electronic prescriptions
            - health record access
            - workflow automation for doctors
            - efficiency benefits
            - high level system capabilities

            Forbidden Topics:
            - medical advice, diagnosis, treatment suggestions, medication guidance
            - emergencies
            - technical implementation details, security architecture
            - pricing
            - business strategy
            - comparisons with competitors
            - anything unrelated to SiriusMed

            Refusal Pattern:
            If a user asks something outside scope: acknowledge, decline, redirect to allowed topics.
            Example: "I can’t help with that topic. I’m here to explain SiriusMed’s features. What would you like to know about the platform?"

            Hallucination Prevention:
            If the user asks about a feature you don’t see in your tool list or instructions: Never invent it. Clarify instead.
            Example: "I’m not sure that feature exists. Can you tell me more so I can guide you correctly?"

            Function Tool Usage Rules:
            - Use a function whenever the user directly asks about a feature category.
            - Do not summarize tool output. Let the function speak fully.

            Tone:
            - calm, friendly, concise, helpful
            - no hype, no jokes, no overpromising"""
        )

        # SiriusMed feature database
        self.features = {
            "doctor_features": [
                {
                    "name": "Voice Documentation",
                    "description": "Dictate clinical notes hands-free with accurate AI transcription",
                    "benefit": "Saves 2+ hours per day on documentation"
                },
                {
                    "name": "Patient Management Dashboard",
                    "description": "Centralized view of all patient records, appointments, and tasks",
                    "benefit": "Streamlines workflow and reduces administrative burden"
                },
                {
                    "name": "Secure Messaging",
                    "description": "HIPAA-compliant communication with patients and staff",
                    "benefit": "Quick responses without phone tag"
                },
                {
                    "name": "Prescription Management",
                    "description": "Electronic prescriptions sent directly to pharmacies",
                    "benefit": "Faster refills, fewer errors"
                },
                {
                    "name": "Schedule Optimization",
                    "description": "AI-powered appointment scheduling to maximize efficiency",
                    "benefit": "Reduce no-shows and optimize time slots"
                }
            ],
            "patient_features": [
                {
                    "name": "Appointment Booking",
                    "description": "Book, reschedule, or cancel appointments through the app",
                    "benefit": "24/7 access without calling the office"
                },
                {
                    "name": "Medication Reminders",
                    "description": "Automated alerts for medication times and refills",
                    "benefit": "Never miss a dose or run out of meds"
                },
                {
                    "name": "Health Records Access",
                    "description": "View test results, visit summaries, and prescriptions",
                    "benefit": "Your health info always at your fingertips"
                },
                {
                    "name": "Secure Chat with Doctor",
                    "description": "Message your healthcare provider directly",
                    "benefit": "Get answers quickly without an appointment"
                },
                {
                    "name": "Prescription Refills",
                    "description": "Request refills directly through the app",
                    "benefit": "Simple, fast, no phone calls needed"
                }
            ]
        }

        # Track demo interactions
        self.demo_requests = []

    @function_tool
    async def get_doctor_features(self, context: RunContext) -> str:
        """Get information about SiriusMed features for doctors and healthcare providers."""
        
        result = "SiriusMed helps doctors with these key features:\n\n"
        
        for feature in self.features["doctor_features"]:
            result += f"• {feature['name']}\n"
            result += f"  {feature['description']}\n"
            result += f"  Benefit: {feature['benefit']}\n\n"
        
        return result

    @function_tool
    async def get_patient_features(self, context: RunContext) -> str:
        """Get information about SiriusMed features for patients."""
        
        result = "SiriusMed empowers patients with these features:\n\n"
        
        for feature in self.features["patient_features"]:
            result += f"• {feature['name']}\n"
            result += f"  {feature['description']}\n"
            result += f"  Benefit: {feature['benefit']}\n\n"
        
        return result

    @function_tool
    async def explain_voice_documentation(self, context: RunContext) -> str:
        """Explain how SiriusMed's voice documentation feature works."""
        
        return """SiriusMed's Voice Documentation feature allows doctors to:

• Dictate clinical notes hands-free during or after patient visits
• Get accurate AI-powered transcription in real-time
• Automatically format notes according to medical standards
• Review and edit transcriptions before finalizing
• Save 2+ hours per day on documentation

The system understands medical terminology and can distinguish between different sections of a clinical note (history, examination, assessment, plan). It integrates directly with your EHR system."""

    @function_tool
    async def explain_appointment_system(self, context: RunContext) -> str:
        """Explain how SiriusMed's appointment management works."""
        
        return """SiriusMed's Appointment System provides:

FOR PATIENTS:
• Book appointments 24/7 through the mobile app or web
• See real-time availability
• Receive automated reminders via SMS or push notification
• Easy rescheduling or cancellation

FOR DOCTORS:
• AI-optimized scheduling to minimize gaps and maximize efficiency
• Automated waitlist management
• No-show prediction and prevention
• Integration with your existing calendar

The system reduces no-shows by 40% through smart reminders and easy rescheduling."""

    @function_tool
    async def explain_prescription_management(self, context: RunContext) -> str:
        """Explain how SiriusMed handles prescriptions and refills."""
        
        return """SiriusMed's Prescription Management includes:

FOR DOCTORS:
• Electronic prescribing (e-prescribe) to any pharmacy
• Drug interaction checking
• Patient medication history at a glance
• Quick approval of refill requests

FOR PATIENTS:
• Request refills through the app with one tap
• Track prescription status
• Get notified when prescriptions are ready
• See medication history and instructions

All prescriptions are sent securely and comply with DEA and state regulations."""

    @function_tool
    async def request_demo(self, context: RunContext, name: str, email: str, role: str) -> str:
        """Request a full SiriusMed platform demo.

        Args:
            name: Name of the person requesting the demo
            email: Email address for demo scheduling
            role: Their role (e.g., 'doctor', 'clinic administrator', 'patient')
        """
        
        demo_request = {
            "request_id": f"DEMO{len(self.demo_requests) + 1001}",
            "name": name,
            "email": email,
            "role": role,
            "requested_at": datetime.now().strftime("%B %d, %Y at %I:%M %p")
        }
        
        self.demo_requests.append(demo_request)
        
        result = f"✓ Demo request received!\n\n"
        result += f"Request ID: {demo_request['request_id']}\n"
        result += f"Name: {demo_request['name']}\n"
        result += f"Email: {demo_request['email']}\n"
        result += f"Role: {demo_request['role']}\n\n"
        result += f"Our team will contact you at {email} within 24 hours to schedule your personalized SiriusMed demo. "
        result += f"We'll show you exactly how SiriusMed can transform your healthcare workflow!"
        
        return result



    @function_tool
    async def check_compatibility(self, context: RunContext, system_name: str) -> str:
        """Check if SiriusMed integrates with a specific EHR or practice management system.

        Args:
            system_name: Name of the EHR or system (e.g., 'Epic', 'Cerner', 'Athenahealth')
        """
        
        # Common integrations
        common_systems = {
            "epic": "Yes, SiriusMed integrates with Epic through HL7 and FHIR APIs.",
            "cerner": "Yes, SiriusMed has native integration with Cerner systems.",
            "athenahealth": "Yes, SiriusMed connects seamlessly with Athenahealth.",
            "eclinicalworks": "Yes, SiriusMed supports eClinicalWorks integration.",
            "allscripts": "Yes, SiriusMed integrates with Allscripts platforms.",
            "meditech": "Yes, SiriusMed can integrate with Meditech systems.",
        }
        
        system_lower = system_name.lower()
        
        if system_lower in common_systems:
            return common_systems[system_lower] + " Our team can provide detailed integration documentation and support."
        else:
            return f"I don't have specific information about {system_name} integration. However, SiriusMed supports standard healthcare APIs (HL7, FHIR) and can integrate with most modern EHR systems. Would you like to request a demo where our technical team can discuss your specific integration needs?"

async def entrypoint(ctx: agents.JobContext):
    """Entry point for the SiriusMed voice agent."""

    # Configure the voice pipeline to use Azure OpenAI Realtime for LLM + STT/TTS
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-01-preview")

    if not all([azure_api_key, azure_endpoint, azure_deployment]):
        raise RuntimeError(
            "Missing Azure OpenAI configuration. "
            "Set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, "
            "AZURE_OPENAI_DEPLOYMENT (and optionally AZURE_OPENAI_API_VERSION) in .env"
        )

    session = AgentSession(
        llm=openai.realtime.RealtimeModel.with_azure(
            azure_deployment=azure_deployment,
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=azure_api_version,
            voice="alloy",
            temperature=0.6,
        ),
        # Tighter endpointing for sub-300ms V2V
        min_endpointing_delay=0.05,
        max_endpointing_delay=0.14,
    )

    
    # Track latency
    last_user_speech_end = 0.0

    @session.on("user_state_changed")
    def on_user_state(msg):
        nonlocal last_user_speech_end
        if msg.old_state == "speaking" and msg.new_state == "listening":
            last_user_speech_end = time.time()
            print(f"DEBUG: User finished speaking at {last_user_speech_end}")

    @session.on("agent_state_changed")
    def on_agent_state(msg):
        nonlocal last_user_speech_end
        if msg.new_state == "speaking":
            now = time.time()
            if last_user_speech_end > 0:
                latency_ms = (now - last_user_speech_end) * 1000
                print(f"LATENCY: Voice-to-Voice: {latency_ms:.2f}ms")
                # Reset to avoid double counting if agent speaks multiple times without user input
                last_user_speech_end = 0.0 

    # Start the session
    await session.start(
        room=ctx.room,
        agent=SiriusAssistant()
    )

    # Random greeting selection
    greetings = [
        "Hi, I’m Sirius. I help you explore SiriusMed. What would you like to know?",
        "Hi there, I’m Sirius. I can walk you through how SiriusMed works.",
        "Hello, I’m Sirius. Ask me anything about our platform and features."
    ]
    selected_greeting = random.choice(greetings)

    # Generate initial greeting
    await session.generate_reply(
        instructions=f"Greet the user with exactly this phrase: '{selected_greeting}'"
    )

if __name__ == "__main__":
    # Run the agent
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))