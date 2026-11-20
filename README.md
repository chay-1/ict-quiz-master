# 🎓 ICT Quiz Master

An offline ICT quiz game for students, built in Python with **Tkinter**. Students choose an ICT topic, answer 10 questions against a timer, get instant feedback and explanations, earn streak bonuses and compete on a leaderboard. Teachers can add their own open-ended questions.

## 1. Problem and solution
**Problem:** Students need regular practice with ICT concepts and quick feedback, but many online quiz tools need a stable internet connection and are not based on the ICT topics studied in class.

**Solution:** ICT Quiz Master runs on one computer without internet. The student picks a topic, answers 10 multiple-choice questions, sees the correct answer with a short explanation after each one, and finishes with a score, a review of every answer and a performance summary.

## 2. Features
- Four topics: Computer Fundamentals (Easy), Networking (Medium), Database (Medium) and Cybersecurity (Hard). Each topic has 10 questions, and the questions and answer choices are shuffled every attempt.
- A drawn picture for every question, made on a Tkinter canvas (no internet or image files needed).
- 20 seconds per question, plus a timer for the whole quiz.
- One **50/50 lifeline** per quiz.
- Keyboard shortcuts: **A–D** choose an answer, **Enter** checks the answer or continues, **F** uses the 50/50, **R** tries a wrong question again, **S** skips and continues. Tab moves between buttons and Enter or Space presses the selected one.
- Scoring: 10 points per correct answer, streak bonuses at 3, 5, 7 and 10 correct in a row (+5, +10, +15, +25), a penalty when the score is below the pass mark (6/10), and the final score never goes below 0.
- Sound effects for choosing an answer, correct, wrong, streak, the last 5 seconds, and passing or failing the quiz, with a sound on/off button (small WAV tones on Windows, the system bell on other computers).
- A modern dark theme: **charcoal background, lime and purple buttons, teal for correct answers**. All colours are kept in one file, `core/quiz_theme.py`.
- Confetti and a motivation message when the student passes.
- Result screen, **review of all answers** and a **performance** screen.
- **Certificate for every student** who finishes a quiz, as a token of appreciation: a *Certificate of Achievement* for a pass and a *Certificate of Participation* otherwise. The student can **download** it (landscape A4 page that opens in any browser; press *Print / Save as PDF* to get a PDF).
- Leaderboard that shows each student's best result, sorted by score, streak or speed, for all topics or one topic.
- Teacher mode: create open-ended questions with a model answer and a difficulty level, then let a student answer them and compare with the model answer.

## 3. Project structure
```text
ict-quiz-master/
├── desktop_app.py          # start the application (run this)
│
├── core/                   # Quiz rules and data: no window code
│   ├── quiz_data.py        #   scoring rules, saving results, leaderboard, sounds
│   ├── quiz_questions.py   #   topics and the 40 questions
│   ├── quiz_custom.py      #   teacher questions
│   ├── certificate.py      #   certificate text and downloadable page
│   └── quiz_theme.py       #   colours (charcoal, lime, purple, teal) and constants
│
├── desktop/                # Tkinter screens
│   ├── app.py              #   main window and screen switching
│   ├── screens_home.py     #   welcome, topic and name screens
│   ├── screens_quiz.py     #   quiz, result, review and performance screens
│   ├── screens_leaderboard.py
│   ├── screens_certificate.py #   certificate preview and download
│   ├── screens_teacher.py  #   teacher mode screens
│   ├── widgets.py          #   buttons, cards and labels
│   └── quiz_art.py         #   question pictures drawn on a canvas
│
├── tests/                  # automatic tests for the quiz rules
├── data/                   # quiz_results.json and teacher_questions.json (created automatically)
├── images/                 # optional PNG pictures (the app draws its own pictures)
├── requirements.txt        # no extra packages needed
└── README.md
```

## 4. Setup (Windows, VS Code)
1. Install Python 3.13 from python.org (the project was built and tested with Python 3.13.7). Tkinter is installed together with Python, so no extra packages are needed (`requirements.txt` is empty on purpose).
2. Get the project from GitHub:
   ```
   git clone https://github.com/chay-1/ict-quiz-master.git
   ```
   Then open the `ict-quiz-master` folder in VS Code (**File → Open Folder**).
3. Open **Terminal → New Terminal** in VS Code. To check that Tkinter works, run `python -m tkinter`. A small test window should open.

## 5. How to run
In the VS Code terminal, from the project folder:
```
python desktop_app.py
```
The ICT Quiz Master window opens.

## 6. How to use
1. On the welcome screen, press **START QUIZ**, choose a topic and press **CONTINUE**. Enter your name, read the rules and press **START QUIZ**.
2. Choose an answer (click it or press A–D) and press **CHECK ANSWER**. Read the explanation and press **CONTINUE**.
3. If you are stuck, use the **50/50** lifeline once. Answer before the 20-second timer ends.
4. After question 10, see your score, then open **REVIEW ANSWERS**, **VIEW PERFORMANCE** or the **LEADERBOARD**.
5. On the result screen press **VIEW & DOWNLOAD** to see your certificate and save it.
6. Use **Teacher mode** to write open-ended questions and let a student answer them.

## 7. How it works (technical overview)
- **One framework only.** The whole project uses Tkinter (as instructed by our teacher). Nothing else needs to be installed.
- **Rules and screens are separate.** Scoring, penalties, streak bonuses, saving and ranking are in `core/`. The `desktop/` folder only draws screens and calls those functions.
- **One class per screen.** `App` in `desktop/app.py` closes the current screen and shows the next one with `swap()`.
- **Timers** use Tkinter's `after()` so the window never freezes. Sounds play in a separate thread so they do not pause the quiz.
- **Storage:** results and teacher questions are saved as JSON files in `data/`. A missing or damaged file is treated as empty instead of crashing.

## 8. Testing
```
python -m unittest discover tests
```
There are 16 tests. They check that every topic has 10 questions with four options and a valid answer, that shuffling keeps the correct answer, the scoring rules (streak bonus, penalty, perfect score 155, score never below 0), the time format, saving and ranking of results, and saving and loading of teacher questions.

## 9. Challenges and solutions
| Challenge | Solution |
|---|---|
| Many screens made the code hard to follow | One class per screen and one `App` class to switch between them |
| Sounds paused the quiz | Played sounds in a separate thread |
| A damaged results file could crash the app | Treated a missing or damaged file as an empty list |
| Scoring rules needed to be easy to test | Kept them in `core/` with no window code |
| Pictures needed to work offline | Drew every picture on a Tkinter canvas |
| Colours were repeated in many files | Moved every colour to `core/quiz_theme.py` so the theme can be changed in one place |

## 10. Limitations and future work
- Results are saved on the computer that runs the app, not in an online database.
- There is no login. Students are identified by the name they type.
- Sound effects are tones on Windows only; other systems use the simple system bell.
- Future work: online database, student login, more questions and automatic tests for the screens.

## 11. Team
Dorji Wangmo, Karma Dema, Pema Wangchuk, Rinchen Dema and Sangay Wangmo. Guided by Phurba D Tamang.

## 12. References
- Python documentation: https://docs.python.org/3/
- Tkinter documentation: https://docs.python.org/3/library/tkinter.html
- Tkinter tutorial (W3Schools): https://www.w3schools.com/python/ref_module_tkinter.asp
- GitHub Docs (repositories, commits, README files): https://docs.github.com

## 13. How the project meets the assignment
The assignment asks for a GUI-based application built with Tkinter where users add items, mark them as completed and group them by priority level. In ICT Quiz Master:

| Requirement | Where in the application |
|---|---|
| Add items | Teacher Mode → **ADD QUESTION** (question, model answer, level) |
| Categorise | Four topics on the topic screen |
| Priority levels | Easy / Medium / Hard (green, amber, red) for each topic and each teacher question |
| Mark as completed | Each answered question is marked on the question numbers; **FINISH QUIZ** completes the quiz and saves the result |
| Delete items | Teacher Mode → **DELETE SELECTED** (or the Delete key) |
| Show progress | Progress bar, question number, score, streak, performance screen and leaderboard |
| Tkinter widgets | Frame, Label, Entry, Text, Listbox, Canvas, Scrollbar, messagebox and a custom FlatButton; layout with pack, grid and place |
