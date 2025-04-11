# Adaptive Perspective Learning System (APLS)

## 📌 Overview

The **Adaptive Perspective Learning System (APLS)** is a smart agent that evolves its understanding of a client's content preferences by learning from feedback and approved edits. It uses OpenAI's managed AI services to generate content, detect tone, and recognize patterns in client-approved revisions.

---

## ⚙️ Features

- ✅ AI-generated drafts based on learned client style
- ✅ Pattern recognition between AI output and client-approved content
- ✅ Detection of stylistic vs. substantive changes
- ✅ Vocabulary and tone adaptation per client
- ✅ JSON-based persistent client profiles

---

## 🧠 How It Works

1. **Draft Generation**  
   Generates an initial draft based on client preferences (tone, vocabulary).

2. **Feedback Loop**  
   Compares the AI draft with the client-approved version using `difflib`.

3. **Pattern Recognition**  
   Identifies replaced terms and classifies them as either:
   - *Stylistic*: minor changes (e.g. wording)
   - *Substantive*: major perspective shifts

4. **Model Evolution**  
   Updates a `PerspectiveProfile` with:
   - New preferred vocabulary
   - Learned tone
   - Repeated edit patterns

---

## 🧪 Example Usage

Run the main script:

```bash
python assessment4.py
