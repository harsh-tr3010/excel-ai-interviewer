**AI Excel Mock Interviewer**

An AI-powered Excel interview platform with FastAPI backend and Gradio frontend, featuring webcam recording, TTS instructions, and automated question evaluation.

**Features**

20-question Excel mock interview with automated evaluation.

Text-to-Speech (TTS) instructions for candidates.

Webcam recording for candidate monitoring.

Auto-timer with submission upon timeout.

Detailed summary and result storage in CSV.

Duplicate email check for unique attempts.

Backend API routes for frontend integration.

**Installation & Setup**
1. Clone the Repository
git clone <your-repo-url>
cd excel-ai-interviewer

2. Create Python Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

3. Install Dependencies
pip install -r requirements.txt


**Dependencies Used:**

**Library	Purpose**
**fastapi**	Backend API server to handle requests and responses.
**uvicorn**	ASGI server to run FastAPI locally.
**gradio**	Frontend interface for interactive interview and webcam integration.
**pandas**	Handle question CSVs, results CSVs, and data manipulation.
**Pillow** (PIL)	Handle and resize interviewer avatar images.
**gtts**	Convert text instructions/questions to speech (TTS).
**shutil**	Handle file saving/moving for recordings.
**glob**	Delete temporary TTS files automatically.
**os & time**	Manage file paths, directories, and timestamps.

4. Prepare Data

Place your interview questions in data/excel_questions.csv.

Format:

Question,ExpectedAnswer
"What is SUM function in Excel?","=SUM(A1:A10)"
"How to freeze panes?","View -> Freeze Panes"

5. Run the App
Option 1: Gradio GUI
python -m app.gui


Opens a local web app at http://127.0.0.1:7860.

Auto TTS instructions and webcam recording included.

Option 2: FastAPI API
uvicorn app.routes:app --reload


**API endpoints:**

POST /start → Start test, return first question & TTS.

GET /question → Fetch next question.

POST /answer → Submit answer for evaluation.

POST /submit → Submit test, save CSV & webcam recording.

**How It Works**

Candidate enters name and email.

Instructions TTS plays automatically.

Webcam recording starts immediately on start.

Candidate answers questions sequentially.

Answers evaluated via ExcelEvaluator.

Timer automatically submits after 5 minutes or when candidate submits.

Results saved per candidate and appended to master CSV (results/all_results.csv).

Webcam recording is saved under results/recordings.

**Notes**

Ensure webcam access is allowed in browser for recording.

Duplicate email attempts are blocked automatically.

TTS files and recordings are auto-managed to avoid clutter.

Default max questions: 20, passing score: 15 correct answers.
