
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    tasks = []
    project_name = ""
    error = ""

    if request.method == "POST":

        project_name = request.form.get("project_name", "").strip()
        milestone_text = request.form.get("milestones", "").strip()

        if not project_name:
            error = "Please enter a project name."

        elif not milestone_text:
            error = "Please enter at least one milestone."

        else:
            lines = milestone_text.splitlines()

            for line_number, line in enumerate(lines, start=1):

                if not line.strip():
                    continue

                parts = [part.strip() for part in line.split("|")]

                if len(parts) != 3:
                    error = f"Line {line_number}: Use Task | Start Date | End Date."
                    break

                task_name, start_date, end_date = parts

                try:
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                    end = datetime.strptime(end_date, "%Y-%m-%d")

                    if end < start:
                        error = f"Line {line_number}: End date cannot be before start date."
                        break

                    duration = (end - start).days + 1

                    tasks.append({
                        "name": task_name,
                        "start": start_date,
                        "end": end_date,
                        "duration": duration
                    })

                except ValueError:
                    error = f"Line {line_number}: Please use YYYY-MM-DD dates."
                    break

            if not tasks and not error:
                error = "Please enter at least one valid task."

            if error:
                tasks = []

    return render_template(
        "index.html",
        tasks=tasks,
        project_name=project_name,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
