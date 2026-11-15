# 🎓 ICT Quiz Master

An interactive ICT quiz game built in Python. It has **two web applications (Streamlit and Gradio)** and an offline **Tkinter desktop version**. All three versions use the same question bank and scoring rules.

## 1. Problem and solution
**Problem:** Students need regular practice with ICT concepts and quick feedback, but many online quiz tools need internet and are not based on the ICT topics studied in class.

**Solution:** ICT Quiz Master lets a student choose an ICT topic, answer 10 questions with a live timer, get instant feedback with explanations, earn streak bonuses, join a leaderboard and download a PDF certificate. Teachers can add and delete their own questions.

## 2. Features
- Four topics (Computer Fundamentals, Networking, Database, Cybersecurity) with 40 questions, shuffled every attempt
- Animated question pictures stored locally (no internet needed)
- Sound effects for correct, wrong and completed quiz, with a sound on/off switch
- Live elapsed timer
- Scoring: 10 points per correct answer, streak bonuses, penalty below the pass mark (6/10), score never below 0
- Leaderboard sorted by score, streak or speed
- Teacher mode: add and delete questions, choose difficulty
- Landscape PDF Certificate of Completion with a red border, gold line and Bhutanese *Druk* key-pattern corners

## 3. Project structure
```text
ict-quiz-master/
├── streamlit_app.py        # Streamlit web app   (run this)
├── gradio_app.py           # Gradio web app      (run this)
├── desktop_app.py          # Tkinter desktop app (run this)
│
├── core/                   # Shared logic: no user-interface code
│   ├── quiz_core.py        #   quiz flow: start, check answer, finish
│   ├── quiz_data.py        #   scoring rules, saving results, leaderboard
│   ├── quiz_questions.py   #   topics and the 40 questions
│   ├── quiz_custom.py      #   teacher questions
│   └── quiz_theme.py       #   colours and constants
│
├── web/
│   └── web_game_assets.py  # question pictures, sounds and PDF certificate
│
├── desktop/                # Tkinter version only
│   ├── app.py              #   main window
│   ├── screens_*.py        #   home, quiz, leaderboard and teacher screens
│   ├── widgets.py          #   buttons, cards and labels
│   └── quiz_art.py         #   drawings
│
├── images/                 # 40 animated SVG question pictures
├── sounds/                 # correct.wav, wrong.wav, celebration.wav
├── assets/                 # Druk key corner and round emblem for the certificate
├── tests/                  # automatic tests for the shared logic
├── data/                   # quiz_results.json and teacher_questions.json (created automatically)
├── requirements.txt
└── README.md
```

## 4. Setup (VS Code)
1. Install Python 3.13 (the project was built and tested with Python 3.13.7).
2. Get the project from GitHub. Either clone it:
   ```
   git clone https://github.com/chay-1/ict-quiz-master.git
   ``` 
   Then open the `ict-quiz-master` folder in VS Code (File → Open Folder).

3. In VS Code, open **Terminal → New Terminal** and create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install the packages:
   ```
   pip install -r requirements.txt
   ```

## 5. How to run
| Version | Command | Opens at |
|---|---|---|
| Streamlit | `streamlit run streamlit_app.py` | http://localhost:8501 |
| Gradio | `python gradio_app.py` | http://127.0.0.1:7860 |
| Tkinter | `python desktop_app.py` | desktop window |

Run each command from the project folder (the folder that contains `streamlit_app.py`) with the virtual environment active. Use a separate terminal for each app if you run two together.

## 6. How to use
1. Enter your name (at least 2 characters), choose a topic and press **Start quiz**.
2. Choose an answer and press **Check answer**. Read the explanation and press **Next**.
3. After question 10, see your score and download the certificate.
4. Open **Leaderboard** to compare scores, and **Teacher mode** to manage questions.

Sounds play automatically after each answer and at the end of the quiz. Turn them off with the **Sound effects** checkbox.

## 7. How it works (technical overview)
- **One set of rules.** Scoring, streaks, penalties and ranking are in `core/`. The three interfaces only show screens and call these functions, so they always give the same score.
- **Streamlit** re-runs the script after every click, so the quiz is kept in `st.session_state`. A fragment refreshes the timer every second.
- **Gradio** connects buttons to functions with `.click` events and keeps the quiz in `gr.State`.
- **Certificate:** ReportLab draws a landscape A4 PDF. One key-pattern corner picture is mirrored into the four corners and a round emblem sits above the title. Colours are set at the top of `certificate_pdf()` in `web/web_game_assets.py`. To add school logos, save them as `assets/logo_left.png` and `assets/logo_right.png`; they appear automatically beside the emblem.
- **Storage:** results and teacher questions are saved as JSON in `data/`. A missing or damaged file is treated as empty instead of crashing.

## 8. Testing
```
python -m unittest discover tests
```
The tests check that every topic has 10 questions, the scoring (perfect score 155, all wrong 0), saving and ranking of results, and that the certificate is a valid PDF.

## 9. Challenges and solutions
| Challenge | Solution |
|---|---|
| Streamlit forgets variables on every click | Stored the quiz in `st.session_state` |
| Gradio buttons change many parts of the page | Returned values for each output component in order |
| Three versions must score the same | Moved the rules to the shared `core/` folder |
| Too much empty space around the question picture | Matched the picture box to the 16:9 shape of the drawings |
| Code was hard to find | Organised files into `core/`, `web/` and `desktop/` folders |

## 10. Limitations and future work
- Results are saved on the computer that runs the app, not in an online database.
- There is no login. Students are identified by the name they type.
- Future work: online database, student login, more automatic tests.

## 11. Team
Dorji Wangmo, Karma Dema, Pema Wangchuk, Rinchen Dema and Sangay Wangmo. Guided by Phurba D Tamang.

## 12. References
- Streamlit documentation: https://docs.streamlit.io/
- Gradio documentation: https://www.gradio.app/docs/
- Python documentation: https://docs.python.org/3/
- ReportLab documentation: https://docs.reportlab.com/
- GitHub documentation: https://docs.github.com/