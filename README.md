# 🧬 PROJECT-ORDIS — DEVELOPMENT EVOLUTION MAP
*A bottom-up organism architecture inspired by real neurobiology.*

```
        ┌───────────────────────────────────────────────────┐
        │                    ORDIS GROWTH                   │
        │     (Foetus → Infant → Child → Adolescent → Adult)│
        └───────────────────────────────────────────────────┘
```

---

# 🌱 **WEEK 1–2: THE BODY (FOUNDATION)**  
> *Equivalent to: zygote → embryo → newborn*  
These stages create **existence**, **time continuity**, and **sensation**.  
No intelligence. No personality. No autonomy.

---

## **WEEK 1 — Kernel / Brainstem Formation**
**Purpose:** Lay down the “life support” systems.

### 🧠 Subcomponents
- `identity.yaml` → **DNA / genetic header**
- tick loop → **heartbeat + circadian rhythm generator**
- kernel.py → **brainstem (autonomic systems)**
- episodic.db → **hippocampus (raw memory tape)**
- tool router → **motor neuron registry**

### Why this step MUST come first
Without continuity, memory, and autonomic stability,  
**nothing intelligent can exist later.**

---

## **WEEK 2 — Sensory Organs + Input Normalization**
**Purpose:** Give Ordis the ability to *perceive*.

### 👁️ Subcomponents
- unified `Event` schema → **neural spike format**
- chat ingest → **hearing nerve**
- file ingest → **vision nerve**
- ingest_event() → **sensory → memory pipeline**
- inbox folder → **retinal surface**

### Why this step MUST come second
You cannot build a mind with zero sensory data.  
A world model without perception is hallucination.

---

# 🧩 **WEEK 3–4: THE MIND (WORLD MODEL + SEMANTICS)**  
> *Equivalent to: infant → child learning object permanence & facts*

---

## **WEEK 3 — World Model v0 (Object Permanence)**
**Purpose:** Turn raw events into objects + relationships.

### 🧱 Subcomponents
- entities (Person, File, Project…)  
- relationships (owned_by, mentions, linked_to…)  
- WorldModel graph store  
- deterministic update rules (Event → Graph update)

### Why this step MUST come third
Experience without structure is chaos.  
Perception must “settle” into entities or Ordis can’t accumulate meaning.

---

## **WEEK 4 — Semantic Memory (Fact Extraction)**
**Purpose:** Convert episodic tape into **stable facts**.

### 📚 Subcomponents
- entity merging (duplicate resolution)  
- contradiction handling  
- confidence scoring  
- fact persistence  
- semantic cleanup + consolidation cycle

### Why this step MUST come fourth
You can’t plan or reason without **semantic stability**.  
Facts must survive beyond moments.

---

# 🧭 **WEEK 5–8: THE SELF (SANITY → HANDS → VOICE → AUTONOMY)**  
> *Equivalent to: adolescence → early adulthood*

---

## **WEEK 5 — Evaluator / Sanity System**
**Purpose:** Make Ordis self-consistent over time.

### 🧩 Subcomponents
- output evaluation  
- world-model checking  
- hallucination prevention  
- drift scoring  
- rule enforcement

### Why this must come fifth
Without sanity, autonomy becomes dangerous spaghetti.

---

## **WEEK 6 — Tool-Use + Intent Skeleton**
**Purpose:** Let Ordis *do things* deterministically.

### 🛠 Subcomponents
- tool registry expansion  
- safe action selection logic  
- kernel-level boundaries  
- success/failure logging

### Why sixth?
Tools require a stable world model + sanity checks.  
Otherwise the system acts blindly.

---

## **WEEK 7 — Personality / Userland Layer**
**Purpose:** Give Ordis a “voice” without corrupting the kernel.

### 🎭 Subcomponents
- expression wrapper  
- tone/personality mode (Ordis-style)  
- safe disagreement layer  
- emotional simulation layer (cosmetic only)

### Why seventh?
Personality must never touch kernel logic.  
It sits **on top**, not inside.

---

## **WEEK 8 — Scheduler + Autonomy v0**
**Purpose:** Introduce limited, safe initiative.

### ⏳ Subcomponents
- periodic tasks  
- background processes  
- daily cycles  
- priority queue  
- goal evaluation stub

### Why last?
Autonomy without:
- perception  
- world model  
- semantics  
- sanity  
is how AGI disasters happen.

---

# ⚡ FULL EVOLUTION SUMMARY (ONE GLANCE)

```
W1 — Body: Existence (tick, identity, memory)
W2 — Body: Sensation (events, perception)
W3 — Mind: Object permanence (world graph)
W4 — Mind: Semantic stability (facts)
W5 — Self: Coherence (evaluators)
W6 — Self: Actions (tool-use)
W7 — Persona: Expression (voice)
W8 — Autonomy: Scheduler (initiative)
```

This order mirrors **real biological development** AND **distributed system architecture.**

**Skipping steps = corruption, drift, collapse, instability.**

Building them in order =  
a stable artificial organism with continuity, memory, personality, and safe autonomy.
