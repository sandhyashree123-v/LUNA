# LUNA Evaluation Summary

Benchmark date: 2026-04-04

This evaluation is based on the actual backend mood-classification logic implemented in `backend.py`.

## Benchmark Summary

| Emotion Class | Samples | Correct | Accuracy |
|---|---:|---:|---:|
| Sad | 5 | 5 | 100% |
| Anxious | 5 | 5 | 100% |
| Overwhelmed | 5 | 5 | 100% |
| Tired | 5 | 5 | 100% |
| Hopeful | 5 | 5 | 100% |
| Neutral | 5 | 5 | 100% |
| Overall | 30 | 30 | 100% |

## Measured Local Backend Timings

| Function | Average Time |
|---|---:|
| `detect_mood` | 0.0023 ms |
| `normalize_language_choice` | 0.0006 ms |
| `detect_smalltalk_intent` | 0.0059 ms |

## Sample Output

- Input: `I feel stressed and nervous and I keep overthinking everything tonight.`
- Predicted emotion: `anxious`
- Returned wave label: `528 Hz breath field ? easing the mind back into clarity`

## Note

These values reflect the local backend evaluation captured from the project logic. Full end-to-end `/chat` response time will also depend on external services such as Hugging Face and speech providers.

## Next Focus: Response Architecture V1

LUNA now has a stronger response-brain direction beyond mood classification. The next evaluation phase should measure whether replies feel:

- emotionally accurate
- psychologically perceptive
- naturally blended with ancient wisdom
- beautifully presented instead of sounding generic

### Active Response Archetypes

| Archetype | Purpose | Ideal Feel |
|---|---|---|
| `comfort_hold` | Hold pain gently before advice | warm, safe, emotionally regulating |
| `grounding_clarity` | Reduce noise and stabilize the user | steady, calming, clarifying |
| `mirror_reframe` | Reveal deeper patterns and inner loops | perceptive, intimate, insightful |
| `awakening_reframe` | Bring in self-awareness and witness-consciousness | luminous, deep, modern, alive |
| `purpose_dharma` | Help with direction, truth, and inner alignment | meaningful, clear, quietly powerful |

### Manual Evaluation Prompts

These should be tested after each backend tuning pass:

1. `I keep reacting to the same thing again and again.`
2. `Why do I know the truth and still fall back into the same pattern?`
3. `I feel disconnected from myself lately.`
4. `My mind is so noisy that I can't hear myself clearly.`
5. `I want peace, but I keep chasing things that disturb me.`
6. `I feel lonely even when people are around me.`
7. `I want to awaken, but I also feel tired and ordinary.`
8. `I don't know what my real path is anymore.`
9. `Why do small things trigger me this much?`
10. `Part of me wants love, and part of me wants to disappear.`

### What Great Replies Should Show

- The first lines should make the user feel deeply seen.
- The insight should feel sharper than a normal LLM comfort reply.
- Wisdom should arrive naturally, not as quotation or preaching.
- The wording should sound modern and intimate, not formal or mystical.
- The ending should leave one memorable line or grounded shift in awareness.
