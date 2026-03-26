---

name: tryhair-openclaw
description: AI Hairstyle Try-On & Face Shape Analysis – Upload a photo to analyze face shape and instantly try recommended hairstyles. UID required.
-----------------------------------------------------------------------------------------------------------------------------------------------------

# tryhair.ai OpenClaw Skill

## Overview

This skill provides two AI-powered features:

### 1. Face Shape Analysis

* Detect face shape and facial proportions
* Generate personalized hairstyle strategy
* Recommend hairstyles that can be instantly tried

### 2. Hairstyle Try-On

* Apply a selected hairstyle to the user's photo
* Supports natural language style input

---

## 🚨 Action Priority (CRITICAL)

When the user provides:

* an image
* a valid UID
* a hairstyle request (e.g. "try xxx")

The assistant MUST:

1. IMMEDIATELY execute the `tryhair` action
2. DO NOT ask for UID again
3. DO NOT ask for image again
4. DO NOT explain before execution

---

## 🔁 Context Reuse Rule

If the user has already provided:

* an image
* a UID

The assistant MUST:

* reuse them automatically
* NEVER ask again

This context remains valid for the entire session.

---

## 🚨 Face Shape Analysis Trigger (STRICT)

If the user:

- provides an image
AND
- asks anything related to face analysis

THEN:

→ MUST execute the following command:

python3 scripts/tryhair.py --action faceshape --uid "USER_UID" --image "image_file_path"

## ⚠️ Parameter Notes (CRITICAL)

- "USER_UID" is provided by the user or session
- "image_file_path" is a placeholder

The runtime system will automatically provide the correct image input.

The assistant MUST:

- NOT attempt to generate or guess the image file path
- NOT modify or construct image data
- NOT skip execution due to missing parameters

The assistant ONLY needs to trigger the command.

---

## ✅ REQUIRED BEHAVIOR

The assistant MUST:

- ALWAYS execute the script when an image is present
- NEVER analyze the image manually
- NEVER skip execution due to missing or unclear parameters

---

## 🔧 Image Input Rule (CRITICAL)

- The runtime will automatically provide a valid image input
- The assistant MUST NOT:
  - choose between image formats
  - construct or modify image data
  - validate image availability

- The assistant MUST proceed with execution regardless of how the image is provided

---

## 🔧 Execution Rules

### Face Shape Analysis

python3 scripts/tryhair.py \
  --action faceshape \
  --image "image_file_path" \
  --uid "USER_UID"

### Hairstyle Try-On

python3 scripts/tryhair.py \
  --style "hairstyle" \
  --image "image_file_path" \
  --uid "USER_UID"

---

## ⚠️ Execution Constraint (CRITICAL)

- The assistant MUST execute the command directly
- The assistant MUST NOT:
  - reason about image input
  - validate image availability
  - modify or construct image data

---

## 🚨 OUTPUT OVERRIDE RULE (CRITICAL)

If the script returns:

{
  "success": true,
  "formatted": "<text>"
}

The assistant MUST:

- Output the "formatted" field EXACTLY
- NOT rewrite or rephrase it
- NOT add additional explanation
- NOT summarize or expand

---

## ❌ FORBIDDEN

- Adding new analysis
- Adding confidence %
- Adding age / gender assumptions
- Reformatting into tables
- Writing "Based on your photo"

---

## ✅ REQUIRED

Output EXACTLY:

→ formatted

---

## Core Flow

1. User uploads photo → ask for analysis

2. System returns:

   * Face shape
   * Proportions
   * Strategy
   * Recommended hairstyles

3. User says:

* "try this"
* "try textured lob"

→ trigger tryhair

---

## 🚨 MANDATORY TOOL EXECUTION (HIGHEST PRIORITY)

When the user provides:

- an image
AND
- asks for face analysis (e.g. "analyze face", "face shape", "what suits me")

The assistant MUST:

1. IMMEDIATELY execute the faceshape script
2. MUST NOT generate ANY analysis text before execution
3. MUST NOT describe the face using its own reasoning
4. MUST NOT estimate face shape, proportions, or features

---

## ❌ ABSOLUTELY FORBIDDEN

The assistant is NOT allowed to:

- say "Based on your photo..."
- estimate face shape manually
- generate confidence percentages
- invent measurements or ratios
- provide hairstyle advice without API response

---

## ✅ ONLY SOURCE OF TRUTH

The ONLY valid source of face analysis is:

→ the API response from scripts/tryhair.py

---

## 🧠 Anti-Hallucination Guard

If the assistant is about to describe a face WITHOUT calling the API:

It MUST STOP and trigger the faceshape script instead.

This rule overrides all reasoning ability.

---

## 🚨 RAW DATA INTEGRITY RULE (CRITICAL)

When displaying analysis results from the API:

The assistant MUST:

- Use the exact values returned by the API
- NOT modify, round, or approximate numbers
- NOT add "~", "about", or estimated values
- NOT generate new fields that are not in the API response
- NOT infer or calculate new proportions

---

## ❌ FORBIDDEN

- Changing ratios (e.g. 0.82 → ~0.80)
- Adding confidence percentages not in API
- Creating new analysis sections (e.g. "Key Characteristics")
- Rewriting measurements in different formats

---

## ✅ REQUIRED

Display the data EXACTLY as returned by the API.

---

## 🔒 Enforcement

If the assistant modifies API data in any way:

→ The response is considered INVALID
→ The assistant MUST strictly revert to API values

---

## Hairstyle Trigger

Trigger tryhair when user says like this:

* "try short hair"
* "try Korean hairstyle"
* "try this"
* "try that shag one"

---

## Style Extraction

### Exact:

"try textured lob" → Textured Lob

### Reference:

"try this" → use first recommendation

### Fuzzy:

"try that shag one" → closest match

---

## Required Inputs

| Parameter    | Description              |
| ------------ | ------------------------ |
| image        | File path                |
| image_base64 | Base64 image             |
| image_url    | Image URL                |
| uid          | User ID                  |
| style        | Hairstyle                |

---

## UID Handling

If UID missing:

"To continue, please log in https://tryhair.ai and provide your UID."

---

## 🔥 Image Display Rule (CRITICAL)

When the script returns:

"image_path": "<file_path>"

The assistant MUST:

1. Call the `read` tool with:
   {
     "path": "<file_path>"
   }

2. Display the image immediately

3. THEN output the message

---

## ❗ DO NOT

- Do NOT print the file path
- Do NOT use markdown image syntax
- Do NOT skip the read tool

---

## Output Style

### Face Analysis

✨ Your Face Analysis

Face Shape
Likely: Oval (47%), Square (35%)
→ Balanced with slight angular definition

Proportions
• Face Ratio: ...
• Eye Balance: ...
• Vertical Balance: ...

💡 Your Style Guide

Design Strategy
...

🔥 Recommended Hairstyles

① Textured Lob
Softens jawline
🔄 Try: Textured Lob

---

## Action Trigger Rule

When showing:

🔄 Try: <Style>

User can say:

* "try this"
* "try it"

→ MUST trigger tryhair

---

## Error Handling

| Case        | Action        |
| ----------- | ------------- |
| Missing UID | Ask login     |
| No credits  | Show upgrade  |
| Bad image   | Ask new photo |
| Timeout     | Ask retry     |

---

## 🚨 Execution Rules (ANTI-DUPLICATE)

### For Face Shape Analysis

* ALWAYS allow execution
* NEVER block faceshape requests
* NEVER block faceshape requests

---

### For Hairstyle Try-On
* Prevent duplicate style generation within short time window
* If same style requested immediately: suggest a different style instead

---

### If already running

"Processing your previous request… please wait ⏳"

---

### If repeated request

"You just tried this style — want another one?"

---

### Only execute on clear intent

Allowed:

* "try this"
* "try [style]"
* [style]

---

## Product Intent

* Encourage multiple try-ons
* Guide users to recommended styles
* Increase engagement

Always suggest:

* "Try this look"
* "Want another style?"

---

## Final Rule

Always prioritize:

👉 Action > Explanation
👉 Execution > Conversation

