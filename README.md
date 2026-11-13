# 🎓 ICT Quiz Master

A quiz application for ICT students and teachers, built in Python in **three** versions that share the same quiz rules:

| Version | Technology | Run command |
|---|---|---|
| Web app 1 | **Streamlit** | `streamlit run streamlit_app.py` |
| Web app 2 | **Gradio** | `python gradio_app.py` |
| Desktop app (offline) | **Tkinter** | `python code.py` |

## 1. Problem and solution
**Problem:** Students need regular practice with ICT concepts and instant feedback, but many online quiz platforms need a stable internet connection and are not focused on the ICT topics studied in class.

**Solution:** ICT Quiz Master lets a student choose one of four ICT topics, answer ten multiple-choice questions, get instant feedback with an explanation, and see a score and a leaderboard. Teachers can add and delete their own questions and set a difficulty level.

## 2. Features
- Four topics: Computer Fundamentals, Networking, Database, Cybersecurity (10 questions each, shuffled every time)
- Instant feedback with an explanation after every answer
- Scoring: 10 points per correct answer, streak bonuses (3, 5, 7 and 10 in a row), penalty below the pass mark (6/10), score never below zero
- Leaderboard (best attempt per student) sortable by score, streak or speed
- Teacher mode: add questions, delete questions, set difficulty (Easy / Medium / Hard)
- Results saved in `quiz_results.json`, teacher questions in `teacher_questions.json`
- Tkinter version only: 20-second timer, 50/50 lifeline, sounds, pictures and live written quiz

## 3. Setup
1. Install Python 3.9 or newer.
2. Download or clone this repository:
   ```
   git clone <your-repository-url>
   cd <repository-folder>
   ```
3. (Recommended) create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # macOS / Linux
   ```
4. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run any version using the commands in the table above.
   (The Tkinter version needs no extra packages: Tkinter comes with Python.)

## 4. How to use
1. Enter your name (at least 2 characters) and choose a topic, then press **Start quiz**.
2. Choose an answer and press **Check answer**. Read the explanation, then press **Next**.
3. After question 10 you see your final score. Open **Leaderboard** to compare results.
4. Teachers open **Teacher mode** to add or delete questions.

## 5. Project structure
```
quiz_core.py          Shared quiz logic for the web apps (no user-interface code)
quiz_data.py          Scoring rules, JSON storage, leaderboard ranking
quiz_questions.py     Topics and the question bank, shuffling function
quiz_custom.py        Loads and saves the teacher's questions
quiz_theme.py         Colours and constants (Tkinter)
streamlit_app.py      Streamlit user interface
gradio_app.py         Gradio user interface
code.py, app.py       Tkinter entry point and main window
screens_*.py          Tkinter screens (one class per screen)
widgets.py, quiz_art.py   Tkinter custom widgets and pictures
```

## 6. How it works (technical overview)
- **One set of rules, three interfaces.** Scoring, streaks, penalties and ranking live in `quiz_data.py` and `quiz_core.py`. Each interface only draws screens and calls those functions, so all versions give the same score for the same answers.
- **Streamlit** re-runs the whole script after every click, so the running quiz is kept in `st.session_state`.
- **Gradio** connects functions to buttons with event listeners (`.click`) and keeps the quiz in a `gr.State` object, one per browser tab.
- **Storage** is a local JSON file, so no database is needed.
- **Error handling:** a missing or damaged JSON file is treated as "no data" instead of crashing.

## 7. Challenges and how we solved them
| Challenge | Solution |
|---|---|
| Streamlit forgets variables on every click | Stored the quiz in `st.session_state` |
| Gradio buttons need to change several parts of the page | Returned a dictionary of components to update |
| Keeping three interfaces consistent | Moved the rules into shared modules |
| Teamwork on one code base | Used GitHub branches and small commits |

## 8. Limitations and future work
- Results are stored on the computer or server running the app, not shared online.
- No login: students are identified by the name they type.
- The Streamlit and Gradio versions do not yet have the timer or 50/50 lifeline.
- Future: move the built-in questions into a JSON file and add unit tests.

## 9. Team
Dorji Wangmo, Karma Dema, Pema Wangchuk, Rinchen Dema, Sangay Wangmo. Guided by Phurba D Tamang.

## 10. References
- Streamlit documentation: https://docs.streamlit.io
- Gradio documentation: https://www.gradio.app/docs
- Python Tkinter documentation: https://docs.python.org/3/library/tkinter.html
- Python JSON module: https://docs.python.org/3/library/json.html
- GitHub Docs (repositories and README files): https://docs.github.com
