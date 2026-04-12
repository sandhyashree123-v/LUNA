# LUNA Judge-Facing Explanation Scripts

These scripts are written for presentation in front of judges. They are detailed, technically grounded, and aligned with the current working prototype.

## Slide 1: Title of the Project

**Script**

Good morning respected judges. Our project is titled **"LUNA - A Voice-Activated Emotional Support System Driven by Global Wisdom and Sonotherapy."**

The core idea behind LUNA is to build an AI companion that goes beyond a normal chatbot. Instead of only answering user questions, our system tries to understand the emotional tone of the interaction and respond in a more supportive, calming, and human-centered way.

We approached this as a full-stack AI application. The frontend is built using **React with Vite**, which gives us a fast and responsive interface. For the emotional visual layer, we use **React Three Fiber** and **Drei** to render an expressive 3D LUNA experience. The backend is built using **FastAPI in Python**, where we manage mood detection, wisdom selection, response generation flow, speech services, and memory continuity.

In addition to text chat, the system also supports voice-based interaction. For this, we integrated **Azure Speech Services** for speech-to-text and text-to-speech, and we also kept **ElevenLabs** as a fallback text-to-speech option. The overall goal is to create a digital emotional companion that feels calm, reflective, and supportive rather than purely transactional.

From a judge’s perspective, we would like to position this project as a **working intelligent wellness prototype** that combines conversational AI, voice AI, emotional adaptation, and therapeutic interface design in one integrated system.

## Slide 2: Objective

**Script**

The main objective of our project is to create an emotionally aware AI companion that can interact with users through both **text and voice**, while adapting its response style based on the user’s emotional condition.

More specifically, our first objective was to design a system that can take user input and identify a probable emotional state such as sadness, anxiety, tiredness, hopefulness, overwhelm, or a neutral mood. This emotional estimation is important because a single generic response style is usually not effective for emotionally sensitive interaction.

Our second objective was to integrate a **wisdom-guided response layer**. We wanted LUNA’s replies to feel more reflective and grounded rather than sounding like generic chatbot outputs. So we added a curated wisdom flow that blends emotional support with short reflective lines in a modern conversational style.

Our third objective was to make the interaction **multimodal**. Instead of restricting the system to typed chat, we added speech input and speech output. This improves accessibility and also makes the interaction more immersive and natural.

Another important objective was to introduce **sonotherapy**, meaning mood-linked calming audio support. The idea is that emotional comfort can be enhanced not only through words, but also through sound ambience and therapeutic frequency-inspired audio design.

Finally, from a software engineering perspective, our objective was to deliver an integrated prototype with a usable interface, backend APIs, memory continuity, and real interaction flow, not just a conceptual model.

## Slide 3: Methodology

**Script**

Our methodology follows a clear end-to-end pipeline from user input to emotionally aligned output.

The process begins when the user interacts with LUNA either through **typed text** or **voice input**. If the user speaks, the speech signal is captured on the frontend and routed to the backend speech pipeline. We use **Azure Speech Services** to convert that audio into text. This gives us a textual representation of the user’s message, which becomes the input for the main conversational logic.

Once the input text is available, the backend performs **mood detection**. In the current active prototype, this is implemented using a rule-based and keyword-driven classification approach. Although it is not yet a deep-learning speech emotion model, it is fast, transparent, and easy to validate in a prototype stage. The system maps the message into one of six emotional categories: **sad, anxious, overwhelmed, tired, hopeful, or neutral**.

After mood detection, the backend prepares the **response-generation context**. This includes:

- the detected mood
- the selected reply language
- recent memory context
- wisdom threads relevant to the emotional situation
- a response archetype that guides tone and conversational behavior

For response generation, the backend constructs a structured prompt and sends it through a **Hugging Face powered language-model workflow** to generate a supportive, emotionally aligned reply. This reply is not random text generation; it is guided by multiple internal rules such as language consistency, emotional tone, memory continuity, and wisdom blending.

Once the reply is created, the system converts it into voice through **Azure TTS**, with **ElevenLabs** as a fallback when needed. At the same time, the frontend updates the **visual mood state**, the **wave label**, and the **background sonotherapy track** based on the returned emotion.

The final step in the methodology is persistence. The system stores conversational snippets and mood-linked diary entries locally, which allows continuity and a more personalized feel in future interactions.

So overall, our methodology combines **frontend interaction design, backend emotional logic, speech AI integration, response generation, and adaptive media feedback** into one coherent pipeline.

## Slide 4: Work Plan

**Script**

We structured the project as a staged development plan rather than trying to build everything at once.

In the first phase, we focused on **problem understanding and system planning**. We studied the gap between conventional chatbots and emotionally supportive systems, and from that we defined the core modules we needed: interface, backend, mood analysis, wisdom flow, voice support, and sonotherapy.

In the second phase, we moved to **frontend development**. We built the LUNA interface using **React**, because component-based architecture helped us manage a chat interface, mood indicators, voice controls, and visual layers in a modular way. We used **Vite** as the build tool for faster development and iteration.

The third phase was **backend API development** with **FastAPI**. We selected FastAPI because it is lightweight, asynchronous, and suitable for API-first AI systems. This allowed us to define routes such as `/chat`, `/stt`, `/tts`, `/wisdom`, `/voices`, and `/speech/token` in a clean and scalable way.

The fourth phase was **AI behavior integration**. Here we added mood detection, response-style control, ancient wisdom routing, language normalization, and memory continuity.

The fifth phase was **speech pipeline integration**, where we connected Azure STT and TTS, and implemented voice selection and preview features.

The sixth phase was **mood-based audio and sonotherapy integration**, where we linked emotional state to background sound profiles.

The final phase was **testing and evaluation**, where we checked flow consistency, backend performance, mood classification accuracy on our local benchmark set, and the overall user experience.

This structured work plan helped us treat the project not just as an AI idea, but as a proper software product with layered development.

## Slide 5: Summary of Progress - Design

**Script**

In terms of design progress, we have completed the major architectural direction of the project.

The first key design achievement is the **full-stack separation of concerns**. We kept the frontend and backend independent but tightly connected through APIs. This is useful from a product engineering perspective because it improves maintainability and allows future scaling.

On the frontend side, we designed the application around a **conversational emotional interface** instead of a plain form-based chatbot. The interface includes mood presentation, animated visual feedback, voice controls, whisper history, sound controls, and a dedicated voice studio experience. This gives the system a more immersive identity.

We also designed the visual layer around an expressive LUNA persona. Using **React Three Fiber**, we created a mood-responsive visual environment that changes based on the active emotional state and speech activity. For judges, this is important because it shows that our project is not only NLP-oriented, but also focuses on human-computer interaction and emotional UX.

On the backend side, the design includes several modular layers:

- input processing
- mood detection
- wisdom-thread selection
- reply-generation control
- memory handling
- speech processing
- voice management

This modular design means each capability can later be upgraded independently. For example, the current rule-based mood classifier can later be replaced by a stronger machine-learning model without changing the entire system architecture.

So in the design phase, our major contribution was creating a **cohesive emotional AI architecture** rather than a single isolated chatbot function.

## Slide 6: Summary of Progress - Experiments and Results

**Script**

At the implementation and results level, we now have a functional prototype with real interaction flow.

Currently, the backend supports key API routes such as:

- `/chat` for primary conversation
- `/stt` for speech-to-text
- `/tts` for text-to-speech
- `/wisdom` for reflective wisdom retrieval
- `/voices` for voice listing
- `/voices/select` and `/voices/preview` for voice customization
- `/speech/token` for Azure speech session support

This means the prototype is not a static demo. It is a working integrated conversational system.

For evaluation, we performed a local backend benchmark focused on the active mood-classification logic. On our current benchmark set, the system achieved **30 correct predictions out of 30 cases**, which is **100% accuracy on that local evaluation sample**. We also measured core function timings, where mood detection and language normalization were extremely fast, showing that the backend-side emotional routing logic adds very little local overhead.

At the same time, we want to present the result honestly. This benchmark is specifically for our **current implemented backend logic**, not for a generalized real-world clinical emotional classification claim. The full end-to-end user experience still depends on network-based providers such as Azure and the response generation service.

From a prototype perspective, however, the result is strong because we have validated:

- successful chat flow
- successful voice flow
- successful mood-linked adaptation
- successful sonotherapy switching
- successful memory continuity
- successful frontend-backend synchronization

So the project has crossed the stage of idea validation and reached working system integration.

## Slide 7: Science & Technology Component / Innovativeness / Novelty

**Script**

The science and technology component of LUNA lies in the way multiple AI and interaction technologies are combined into one emotionally adaptive system.

The first innovative aspect is that our project is not limited to response generation. It combines:

- conversational AI
- voice AI
- emotional state adaptation
- wisdom-guided content shaping
- calming audio feedback
- expressive interface design

Usually, student chatbot projects stop at text interaction. In our case, we intentionally designed a richer human-centered stack.

The second novel aspect is the **wisdom integration layer**. Rather than generating purely generic comfort replies, LUNA tries to bring in concise reflective wisdom in a controlled and contextual way. This gives the interaction a unique identity compared to standard FAQ bots or task bots.

The third innovation is the **adaptive sonotherapy layer**. Once the mood is identified, the system shifts the audio ambience and wave label accordingly. This allows emotional support to happen not only through text content, but through a broader sensory experience.

From the technical stack perspective, the novelty comes from the orchestration of:

- **React + Vite** for a fast modern UI
- **React Three Fiber + Drei** for immersive visual presentation
- **FastAPI** for API orchestration
- **Azure Speech Services** for speech AI
- **ElevenLabs fallback TTS** for robustness
- **Hugging Face based generation workflow** for supportive text generation
- local persistence for memory and diary continuity

So if we describe the novelty in judge-facing terms, LUNA is best understood as an **integrated multimodal emotional companion prototype**, not just a chatbot with extra styling.

## Slide 8: Prototype Development

**Script**

Our prototype development is already at a functional stage.

On the frontend, we have implemented a live LUNA interface where the user can type or speak, receive responses, hear the reply in voice form, and observe mood-linked interface changes. The system also supports language selection, voice volume control, and voice personalization through a voice studio.

On the backend, we have implemented the major service layer in **Python FastAPI**. This layer handles incoming requests, processes emotional context, routes wisdom support, generates responses, stores conversation memory, and returns structured outputs to the UI.

A strong point of our prototype is the **voice workflow**. The user is not limited to typing. They can interact through speech, and LUNA can answer back with synthesized voice. This makes the system closer to a companion interface than a normal chat app.

Another strong point is the **prototype completeness** across modules. Many student projects implement separate components independently, but our system already demonstrates end-to-end connection between:

- input capture
- backend reasoning
- emotional adaptation
- response generation
- voice synthesis
- mood-based sound environment
- UI feedback

In judge terms, the project can be seen as a **working demonstrable prototype with clear upgrade paths**, which is valuable because it shows both implementation maturity and future extensibility.

## Slide 9: Project Outcomes and Learnings

**Script**

The first major outcome of this project is that we successfully developed a working emotional companion prototype that combines multiple technologies into a single user experience.

Technically, the project outcome is not only a frontend or only a backend. It is a complete integrated system with:

- conversational AI flow
- mood-aware adaptation
- voice interaction
- wisdom support
- sonotherapy-linked ambience
- interface-level emotional presentation

A second important outcome is the practical understanding we gained in **full-stack AI system design**. We learned how to connect UI state management, backend APIs, cloud speech services, prompt-based response control, and local persistence in one application.

We also learned an important product-design lesson: in emotionally sensitive applications, correctness alone is not enough. Tone, pacing, wording, and sensory presentation matter a lot. That means emotional AI is not just an NLP problem; it is also a UX, systems, and ethics problem.

Another learning is about architectural honesty. During development, we understood the difference between a conceptual research pipeline and a production-facing prototype. So for evaluation, we are careful to present implemented features as implemented, and future enhancements as future scope. We believe judges appreciate that clarity.

Overall, this project taught us technical integration, AI workflow design, multimodal interaction, and responsible presentation of system capability.

## Slide 10: Societal Benefit / Industry Relevance / Future Scope

**Script**

From a societal perspective, LUNA addresses a very relevant modern problem: people are surrounded by technology, but not always by emotionally supportive technology. Students, young adults, and working individuals often face stress, overthinking, loneliness, and emotional fatigue. LUNA is designed as a non-judgmental digital companion that can offer gentle conversational comfort and reflective support.

It is important to clarify that our system is not being presented as a replacement for mental health professionals. Instead, we see it as a **supportive wellness-oriented companion tool** that can help users with emotional reflection, calmness, and accessible interaction.

In terms of industry relevance, this project fits strongly into areas such as:

- AI wellness products
- empathetic chat systems
- voice-first assistants
- digital companionship platforms
- mental wellness support tools
- emotionally adaptive UX systems

The project also demonstrates industry-relevant skills such as API design, cloud speech integration, frontend-backend architecture, multimodal interaction design, and AI orchestration.

For future scope, we see several clear technical upgrades.

First, the current mood detection can be replaced with a **stronger machine-learning or deep-learning emotion model**.

Second, we can improve privacy and trust through stronger authentication, encrypted storage, and safer user data management.

Third, we can introduce **crisis detection and escalation guidance**, which is very important for real-world emotional AI systems.

Fourth, we can extend the system to **mobile platforms and wearable ecosystems**, which would make it more accessible for everyday use.

Finally, we can further improve personalization through long-term memory, adaptive recommendations, and stronger real-world evaluation frameworks.

So our final message to the judges is that LUNA is already a solid prototype today, and it also has a strong roadmap toward becoming a more advanced emotionally intelligent platform tomorrow.

## Quick tips for presenting before judges

- Say "working prototype" often. It sounds strong and honest.
- Do not claim medical diagnosis or therapy.
- If asked about AI depth, explain that the strength of the project is **system integration**, **emotional UX**, and **multimodal design**.
- If asked about limitations, say that the current mood detector is rule-based and can be upgraded to learned models in future work.
- If asked about originality, focus on the combination of wisdom support, voice AI, sonotherapy, and expressive interface in one system.
