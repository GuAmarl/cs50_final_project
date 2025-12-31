# Spacia

#### Video Demo: <https://youtu.be/ZEdCLngQoYw>

#### Description

**Spacia** is a smart flashcards web application designed to help users learn more efficiently using **spaced repetition** and **active recall**.

The app is built around **scientifically proven memory principles**, inspired by the **SM-2 algorithm**, and automatically schedules reviews at the optimal moment—right before information is likely to be forgotten. This approach improves long-term retention while minimizing unnecessary repetitions.

Spacia adapts to each user’s performance, dynamically adjusting review intervals based on how difficult each flashcard feels during study sessions.

---

## Features

- Deck-based flashcard organization
- Intelligent scheduling system with clear learning states:
  - **Learning**
  - **Review**
  - **Relearning**
- Time-based reviews using spaced repetition
- Difficulty grading after each review:
  - Again
  - Hard
  - Good
  - Easy
- Automatic calculation of:
  - Next review time
  - Review interval
  - Ease factor
  - Repetition count
- Multi-user support with isolated decks
- SQLite database for simplicity and reliability
- Clean, responsive web interface
- Fully web-based (no desktop installation required)

---

## How It Works

Each flashcard in Spacia follows a **learning lifecycle** that adapts to the user’s memory strength.

### Learning States

1. **Learning**  
   New cards start with short review intervals (minutes or hours) to reinforce initial memory formation.

2. **Review**  
   Once a card is learned, it enters long-term spaced repetition with increasing intervals (days, weeks, or months).

3. **Relearning**  
   If a card is forgotten, it temporarily re-enters short review steps to rebuild memory strength.

---

### Grading System

After reviewing a card, the user grades how difficult it was to recall:

| Grade | Meaning                  |
| ----- | ------------------------ |
| Again | Failed to recall         |
| Hard  | Recalled with difficulty |
| Good  | Correct recall           |
| Easy  | Effortless recall        |

This feedback directly influences the scheduling algorithm.

---

### What Gets Recalculated

Based on the user’s grade, Spacia updates:

- **Next review timestamp (`due`)**
- **Review interval**
- **Ease factor**
- **Repetition count**
- **Learning step (when applicable)**

All timestamps are stored in **UTC** to ensure consistency across systems and time zones.

---

## Scheduling Algorithm

Spacia uses a **custom scheduling algorithm inspired by SM-2**, adapted for modern web applications and time-based scheduling.

Unlike the original SM-2 (which operates strictly in days), Spacia supports **minute-, hour-, and day-level intervals**, allowing smoother transitions between learning and long-term review.

Key characteristics of the algorithm:

- **Learning steps**  
  New and relearning cards progress through predefined short intervals before entering long-term review.

- **Ease factor (EF)**  
  Each card has an ease factor that represents how easy it is for the user.

  - EF increases when cards are graded _Good_ or _Easy_
  - EF decreases when cards are graded _Hard_ or _Again_
  - A minimum EF prevents intervals from collapsing too aggressively

- **Repetition counter**  
  Only increments once a card reaches the review phase, ensuring that early learning steps do not artificially inflate long-term intervals.

- **Adaptive intervals**  
  Review intervals grow proportionally based on the card’s ease factor and repetition count, creating personalized review schedules.

- **Failure recovery (Relearning)**  
  When a card is forgotten, it temporarily re-enters short intervals instead of restarting entirely, preserving learning progress.

This approach provides a balance between algorithmic rigor and practical usability.

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite3
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Bootstrap 5
- **Scheduling Algorithm:** SM-2 inspired spaced repetition
- **Tooling & Quality:**
  - Uv (environment and dependency management)
  - Ruff (linting and code quality)
  - Playwright (end-to-end testing)

---

## Project Goals

Spacia aims to be:

- Simple to use
- Easy to self-host
- Educational and transparent
- A solid foundation for experimenting with spaced repetition algorithms

---

## Status

**Work in progress**

Spacia is actively being developed and refined. Features, structure, and scheduling behavior may evolve over time.

---
