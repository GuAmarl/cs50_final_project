# Spacia

#### Video Demo: <https://youtu.be/ZEdCLngQoYw>

#### Description:

_A smart flashcards app based on spaced repetition._

Spacia is a web application for studying with **intelligent flashcards**, using **scientifically backed spaced repetition algorithms** (inspired by SM-2).  
It helps users review information at the optimal time to maximize long-term retention.

---

## Features

- Deck-based flashcards system
- Smart scheduling (learning, review, relearning)
- Time-based reviews using spaced repetition
- Difficulty grading: Again / Hard / Good / Easy
- Automatic interval calculation
- Multi-user support
- SQLite database (simple and reliable)
- Web-based interface (Flask + HTML + Bootstrap 5)

---

## How It Works (Short Explanation)

Each flashcard follows a learning lifecycle:

1. **Learning** – short intervals (minutes/hours)
2. **Review** – long-term spaced repetition (days/weeks/months)
3. **Relearning** – triggered when a card is forgotten

After each review, the user grades the card:

| Grade | Meaning                  |
| ----- | ------------------------ |
| Again | Failed to recall         |
| Hard  | Recalled with difficulty |
| Good  | Correct recall           |
| Easy  | Effortless recall        |

Based on this feedback, Spacia recalculates:

- The next review time (`due`)
- The interval
- The ease factor
- The repetition count

All timestamps are stored in **UTC** for consistency.

---

## Tech Stack

- **Organization:** Uv, Ruff, Pywrigth
- **Backend:** Python, Flask
- **Database:** SQLite3
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Bootstrap 5
- **Scheduling Algorithm:** SM-2 inspired

---
