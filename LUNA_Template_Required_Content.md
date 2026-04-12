# LUNA Template-Only PPT Content

## Slide 1: Title of the Project

**LUNA - A Voice-Activated Emotional Support System Driven by Global Wisdom and Sonotherapy**

- Midterm Evaluation Presentation
- Department of Artificial Intelligence and Data Science
- Team Members:
  - Sandhya Shree
  - Ankitha S
  - Vaishnavi
  - Sri Praveen Challa
- Guide: Dr. Lakshmana

## Slide 2: Objective

- To build an emotional companion system that supports users through voice and text interaction.
- To detect the user’s mood from conversation and generate emotionally aligned responses.
- To integrate ancient/global wisdom into supportive AI dialogue.
- To provide calming sonotherapy based on the detected emotional state.
- To create an immersive user experience using voice, memory, and expressive interface design.

## Slide 3: Methodology

1. User interacts with LUNA through text or voice.
2. Voice input is converted into text using speech-to-text.
3. Backend processes the message and identifies the probable mood.
4. Relevant wisdom and response style are selected based on mood and context.
5. A supportive response is generated through the AI response pipeline.
6. The response is converted to speech and delivered back to the user.
7. Mood-based sonotherapy and interface changes are applied for a calming experience.
8. Conversation memory and diary continuity are stored for better personalization.

## Slide 4: Work Plan

- Requirement analysis and problem definition
- Frontend UI design for LUNA companion interface
- Backend API development using FastAPI
- Mood detection and wisdom-response integration
- Speech-to-text and text-to-speech integration
- Sonotherapy and mood-linked audio support
- Frontend-backend integration and testing
- Evaluation, tuning, and final enhancement phase

## Slide 5: Summary of Progress - Design

- Designed a full-stack architecture with React frontend and FastAPI backend.
- Built an immersive chat interface with animated LUNA visual experience.
- Added multilingual support flow for user interaction.
- Designed voice interaction pipeline for speech input and speech output.
- Added mood-aware sonotherapy concept into the interface flow.
- Included wisdom-based conversational support and memory continuity.

## Slide 6: Summary of Progress - Experiments and Results

- Implemented working `/chat`, `/stt`, `/tts`, `/wisdom`, `/voices`, and `/speech/token` endpoints.
- Implemented mood detection across six states: sad, anxious, overwhelmed, tired, hopeful, and neutral.
- Integrated Azure Speech for STT/TTS and ElevenLabs fallback for TTS.
- Completed frontend-backend interaction with mood updates and voice playback.
- Local backend evaluation achieved 30 correct predictions out of 30 benchmark cases.
- The current prototype shows that LUNA can provide emotionally aligned reply flow with voice and calming audio support.

## Slide 7: Science & Technology Component / Innovativeness / Novelty

- Combines emotional conversation, wisdom-based support, voice interaction, and sonotherapy in one platform.
- Moves beyond a normal chatbot by adapting reply style to detected emotional mood.
- Uses reflective wisdom as part of conversational support rather than generic responses.
- Creates a more human-centered emotional AI experience through calming audio and expressive UI.

## Slide 8: Prototype Development

- Functional React-based frontend is completed.
- FastAPI backend is actively connected to the UI.
- Mood-aware conversation flow is working.
- Voice input, voice output, and voice selection features are implemented.
- 3D/animated LUNA interface and emotional presentation layer are integrated.
- Local memory and whisper/wisdom continuity are available in the current prototype.

## Slide 9: Project Outcomes and Learnings

**Project outcomes**

- Developed a working emotional companion prototype.
- Achieved successful integration of chat, voice, mood detection, wisdom flow, and sonotherapy.
- Created a practical system that is more immersive than a text-only chatbot.

**Learnings**

- Learned full-stack integration of React and FastAPI.
- Gained experience in speech API integration and conversational AI workflow design.
- Understood the importance of emotional design, response tone, and user-centered interaction.

## Slide 10: Societal Benefit / Industry Relevance / Future Scope

**Societal benefit**

- Can support users seeking a calm, non-judgmental digital companion.
- Can help students and young adults with reflection, stress relief, and emotional comfort.

**Industry relevance**

- Relevant to AI wellness tools, voice assistants, digital mental wellness platforms, and empathetic conversational systems.

**Future scope**

- Improve mood detection using stronger ML/deep learning models.
- Add stronger privacy, authentication, and safety layers.
- Introduce crisis support and escalation guidance.
- Expand to mobile deployment and broader real-world use.

## Important note for presentation

While presenting, describe the current project as a **working prototype**. Do not strongly claim advanced modules like hybrid deep SER, FAISS retrieval, Whisper pipeline, or LoRA fine-tuning unless you have separate implementation proof for them. The safest and strongest presentation is to show what is already working in the current codebase.
