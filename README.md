# Attention Drift Detector
### Personal Project (Work in Progress)

This is a personal project I'm developing in my free time.  
The idea is to build a web app that measures attention stability using reading tasks, reaction-time tasks, and simple coding exercises.  
The project is still in progress, and I keep adding features as I go.

---

## Current Features

### Reading Task
- Splits text into short segments
- Measures reading time for each one
- Checks consistency and variability

### Reaction-Time Task
- Simple cognitive questions
- Measures reaction time + accuracy
- Looks at changes over time

### Code-Writing Task
- User writes a small code snippet
- Measures typing speed, delay before starting, and correctness
- Tracks consistency between exercises

---

## Concentration Score (Early Version)

The backend calculates an early version of a “Concentration Score” based on:
- Reading stability
- Reaction-time variability
- Accuracy changes
- Typing metrics

This is an early prototype and will be improved as I gather more data.

---

## Tech Stack

### Frontend
- React (Vite)

### Backend
- FastAPI (Python)

---

## How to Run

### Backend
```
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Frontend
```
cd frontend
npm install
npm run dev
```

---

## Work in Progress / Next Steps
- Better UI and flow between tasks
- Graphs for visualizing results
- Improving typing-task editor
- Moving from JSON storage to a database
- Deploying the project online

---

This project is mainly for learning and exploring ideas that interest me.
