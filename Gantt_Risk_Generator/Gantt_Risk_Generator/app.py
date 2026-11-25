
from flask import Flask, render_template, request
from datetime import datetime
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)


def assess_risk(probability, impact):

    scores = {"Low": 1, "Medium": 2, "High": 3}
    score = scores[probability] * scores[impact]

    if score >= 6:
        level = "High"
        mitigation = "Prepare an alternative plan and monitor this risk closely."
    elif score >= 3:
        level = "Medium"
        mitigation = "Monitor the risk and prepare preventive measures."
    else:
        level = "Low"
        mitigation = "Continue regular monitoring."

    return score, level, mitigation


def parse_tasks(project_name, milestone_text):

    tasks = []

    if not project_name:
        return [], "Please enter a project name."

    if not milestone_text:
        return [], "Please enter at least one milestone."

    for line_number, line in enumerate(milestone_text.splitlines(), start=1):

        if not line.strip():
            continue

        parts = [part.strip() for part in line.split("|")]

        if len(parts) != 3:
            return [], f"Line {line_number}: Use Task | Start Date | End Date."

        task_name, start_date, end_date = parts

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            if end < start:
                return [], f"Line {line_number}: End date cannot be before start date."

            duration = (end - start).days + 1

            tasks.append({
                "name": task_name,
                "start": start_date,
                "end": end_date,
                "duration": duration
            })

        except ValueError:
            return [], f"Line {line_number}: Please use YYYY-MM-DD dates."

    if not tasks:
        return [], "Please enter at least one valid task."

    return tasks, ""


def create_gantt_chart(tasks, project_name):

    if not tasks:
        return None

    fig = px.timeline(
        tasks,
        x_start="start",
        x_end="end",
        y="name",
        title=f"Project Timeline: {project_name}",
        labels={
            "name": "Project Tasks",
            "start": "Start Date",
            "end": "End Date"
        },
        color="name"
    )

    fig.update_yaxes(autorange="reversed")

    fig.update_layout(
        template="plotly_white",
        height=450,
        showlegend=False
    )

    return pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn"
    )


@app.route("/", methods=["GET", "POST"])
def home():

    tasks = []
    risks = []
    project_name = ""
    error = ""
    gantt_chart = None

    if request.method == "POST":

        form_type = request.form.get("form_type", "project")

        print("FORM TYPE RECEIVED:", form_type)
        print("FORM DATA RECEIVED:", request.form.to_dict())

        project_name = request.form.get("project_name", "").strip()
        milestone_text = request.form.get("milestones", "").strip()

        # PROCESS PROJECT MILESTONES

        if form_type == "project":

            tasks, error = parse_tasks(project_name, milestone_text)

            if tasks and not error:
                gantt_chart = create_gantt_chart(tasks, project_name)

        # PROCESS RISK ASSESSMENT

        elif form_type == "risk":

            tasks, error = parse_tasks(project_name, milestone_text)

            if not error:

                risk_text = request.form.get("risks", "").strip()

                if not risk_text:
                    error = "Please enter at least one project risk."

                else:

                    for line_number, line in enumerate(risk_text.splitlines(), start=1):

                        if not line.strip():
                            continue

                        parts = [part.strip() for part in line.split("|")]

                        if len(parts) != 3:
                            error = (
                                f"Risk line {line_number}: "
                                "Use Risk Description | Probability | Impact."
                            )
                            break

                        description, probability, impact = parts

                        if probability not in ["Low", "Medium", "High"]:
                            error = f"Risk line {line_number}: Invalid probability."
                            break

                        if impact not in ["Low", "Medium", "High"]:
                            error = f"Risk line {line_number}: Invalid impact."
                            break

                        score, level, mitigation = assess_risk(
                            probability, impact
                        )

                        risks.append({
                            "description": description,
                            "probability": probability,
                            "impact": impact,
                            "score": score,
                            "level": level,
                            "mitigation": mitigation
                        })

                    if not risks and not error:
                        error = "Please enter at least one valid risk."

                    if error:
                        risks = []

            if tasks and not error:
                gantt_chart = create_gantt_chart(tasks, project_name)

    return render_template(
        "index.html",
        tasks=tasks,
        project_name=project_name,
        error=error,
        gantt_chart=gantt_chart,
        risks=risks
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
