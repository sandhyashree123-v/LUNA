# LUNA Midterm PPT Content

## Important alignment note

Use the current running project as the primary truth source for the midterm presentation.

The written proposal/report describes some advanced research components such as:

- hybrid CNN-LSTM-Transformer speech emotion recognition
- OpenAI Whisper transcription
- FAISS-based semantic retrieval
- LoRA fine-tuned Mistral model

These are **not clearly present in the current active codebase**. The current implementation is better presented as:

- React + Vite frontend
- FastAPI backend
- keyword/rule-based mood detection
- Hugging Face powered empathetic reply generation
- Azure Speech based STT/TTS with ElevenLabs fallback for TTS
- mood-based sonotherapy
- multilingual interaction
- local memory and wisdom continuity
- animated 3D emotional companion UI

For the midterm PPT, this means:

- keep the original vision from the SPP
- present the current implemented system honestly
- label advanced research ideas as future enhancement unless you have separate experimental artifacts to prove them

## Suggested slide order

### Slide 1: Title Slide

**LUNA - A Voice-Activated Emotional Support System Driven by Global Wisdom and Sonotherapy**

- Midterm Evaluation Presentation
- Department of Artificial Intelligence and Data Science
- Team members:
  - Sandhya Shree
  - Ankitha S
  - Vaishnavi
  - Sri Praveen Challa
- Guide: Dr. Lakshmana

### Slide 2: Problem Statement

- Most AI assistants are task-oriented but emotionally disconnected.
- Users experiencing stress, loneliness, anxiety, or emotional fatigue often need a calm and non-judgmental support space.
- Existing systems usually do not combine emotional awareness, voice interaction, reflective wisdom, and calming audio in one platform.

**Problem statement:**
There is a need for an emotionally aware AI companion that can listen, respond with empathy, provide reflective wisdom, and create a soothing user experience through voice and sonotherapy.

### Slide 3: Motivation

- Students and young adults often face stress, overthinking, burnout, and loneliness.
- Many people need support in the moment, but do not always have immediate human availability.
- A digital companion can offer gentle conversational support, emotional reflection, and a calming experience.
- LUNA aims to make AI interaction feel warmer, more human, and more emotionally supportive.

### Slide 4: Objectives

- To develop a multimodal emotional companion supporting text and voice interaction.
- To identify the user’s emotional state and adapt the response style.
- To provide multilingual speech input and natural voice output.
- To integrate ancient/global wisdom in a contextual and gentle way.
- To use sonotherapy and an expressive interface to improve emotional comfort.

### Slide 5: Literature Survey

- Conversational systems like ELIZA showed early human-like interaction.
- Mental health chatbots such as Woebot highlighted the value of accessible support systems.
- Transformer-based language models improved contextual and coherent dialogue generation.
- Modern speech APIs enabled practical speech-to-text and text-to-speech interaction.
- LUNA extends this by combining empathetic conversation, wisdom guidance, voice interaction, and calming sound support.

### Slide 6: Proposed System vs Current Implementation

**Proposed in SPP**

- emotion-aware AI companion
- wisdom-based response generation
- therapeutic sound integration
- voice-driven interaction
- emotionally supportive interface

**Current implementation status**

- Implemented: React frontend and FastAPI backend
- Implemented: `/chat`, `/tts`, `/stt`, `/wisdom`, `/voices`, `/speech/token`
- Implemented: mood detection for sad, anxious, overwhelmed, tired, hopeful, neutral
- Implemented: multilingual response flow
- Implemented: Azure voice selection and preview
- Implemented: sonotherapy linked to mood
- Implemented: local memory and wisdom continuity
- Pending/Not evidenced in active code: hybrid deep SER model, FAISS retrieval, Whisper-based transcription pipeline, fine-tuned Mistral

### Slide 7: System Architecture

**Flow**

1. User gives text or voice input
2. Speech input is converted to text
3. Backend detects mood from user message
4. Relevant wisdom thread and conversational style are selected
5. Hugging Face based model generates empathetic reply
6. Reply is converted to speech
7. Frontend updates avatar, mood visuals, and sonotherapy audio
8. Memory and diary data are saved for continuity

**Suggested figure:** `LUNA_Figure1_System_Architecture.png`

### Slide 8: Major Modules

**Frontend**

- React + Vite interface
- animated LUNA scene
- login screen
- chat interface
- voice studio
- language selection
- mood-based audio ambience

**Backend**

- FastAPI endpoints
- mood detection
- wisdom thread selection
- contextual response prompting
- speech-to-text and text-to-speech
- local memory and diary logging

### Slide 9: Key Features Implemented

- Emotion-aware conversation flow
- Six mood classes: sad, anxious, overwhelmed, tired, hopeful, neutral
- Ancient wisdom integration in modern conversational tone
- Voice interaction with Azure Speech
- ElevenLabs fallback for TTS
- Sonotherapy profiles matched to mood
- User memory and whisper/wisdom continuity
- 3D expressive UI and voice customization

### Slide 10: Current Results / Progress

**What has been completed**

- Working frontend-backend integration
- Chat endpoint running with mood-aware response generation
- TTS and STT integration completed
- Mood-linked sonotherapy and voice playback completed
- Wisdom retrieval and continuity logic completed
- Voice selection studio implemented

**Current local evaluation**

- Backend mood-classification benchmark: 30/30 correct cases
- Overall benchmark accuracy: 100% on local evaluation set
- Average `detect_mood` time: 0.0023 ms
- Average `normalize_language_choice` time: 0.0006 ms
- Average `detect_smalltalk_intent` time: 0.0059 ms

**Suggested visuals**

- `LUNA_Evaluation_Table.png`
- `LUNA_Evaluation_Graph.png`

### Slide 11: Example Output

**Sample test input**

"I feel stressed and nervous and I keep overthinking everything tonight."

**Detected mood**

- anxious

**Wave label**

- 528 Hz breath field - easing the mind back into clarity

**What this demonstrates**

- mood detection
- adaptive calming layer
- emotionally aligned response flow

### Slide 12: Challenges and Gaps

- The current mood detection is rule/keyword based, so it is simpler than a full deep-learning SER model.
- Some claims in the proposal/report are broader than what the active code currently proves.
- End-to-end latency also depends on external APIs such as Hugging Face and speech providers.
- Privacy, emotional safety, and crisis handling still need stronger real-world deployment safeguards.

### Slide 13: Future Work

- Replace rule-based mood detection with stronger learned emotion models
- Add richer personalization and safer long-term memory handling
- Introduce stronger privacy and authentication layers
- Add crisis detection and escalation guidance
- Expand mobile support and wearable integration
- If desired, evolve toward true multimodal SER and retrieval-augmented wisdom pipelines

### Slide 14: Conclusion

- LUNA demonstrates a practical emotional companion system that combines empathetic conversation, voice support, wisdom guidance, and sonotherapy.
- The current project already delivers a functional full-stack prototype with real interaction flow.
- The midterm outcome shows strong implementation progress, while some research ambitions remain future enhancements.
- LUNA has clear scope to grow into a richer and more robust emotionally aware support platform.

## Short version for viva explanation

We aligned the PPT with both the proposal and the current project status. The core vision remains the same: an emotional AI companion that combines empathy, wisdom, voice, and calming audio. However, to keep the presentation academically safe, the PPT should describe the active codebase truthfully. The current working system uses FastAPI, React, Azure speech services, Hugging Face response generation, local memory, wisdom routing, and sonotherapy. Advanced items mentioned in the report, such as hybrid deep SER, FAISS, Whisper, and LoRA fine-tuning, should be presented as future scope unless separately implemented and demonstrated.
