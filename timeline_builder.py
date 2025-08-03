from datetime import datetime
import plotly.figure_factory as ff
import pandas as pd

def build_gantt_from_json(timeline_json):
    tasks = []
    for event in timeline_json.get("events", []):
        start_date = event["start_date"]
        year = int(start_date.get("year", "1900"))
        month = int(start_date.get("month", 1))
        start = datetime(year, month, 1)
        # Set an end date 1 month later (or customize as needed)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)

        tasks.append(dict(Task=event["text"]["headline"], Start=start, Finish=end))

    df = pd.DataFrame(tasks)

    fig = ff.create_gantt(
        df,
        index_col='Task',
        show_colorbar=True,
        group_tasks=True,
        title="Timeline as Gantt Chart"
    )
    return fig

def timeline_builder(timeline_json):
    title = timeline_json["title"]["text"]["headline"]
    subtitle = timeline_json["title"]["text"]["text"]
    events = timeline_json["events"]

    def format_date(d):
        try:
            dt = datetime.strptime(f'{d["year"]}-{d["month"]}', "%Y-%m")
            return dt.strftime("%b %Y")
        except:
            return f'{d.get("month", "")}/{d.get("year", "")}'

    html_events = ""
    for event in events:
        date_str = format_date(event["start_date"])
        headline = event["text"]["headline"]
        text = event["text"]["text"]
        
        html_events += f"""
        <div class="event" onclick="this.classList.toggle('active')">
          <div class="date">{date_str}</div>
          <h3 class="headline">{headline}</h3>
          <div class="content">{text}</div>
        </div>
        """

    html_code = f"""
    <style>
      .timeline {{
        max-width: 700px;
        margin: 40px auto;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      }}
      .title {{
        text-align: center;
        margin-bottom: 5px;
        font-size: 2rem;
        font-weight: bold;
      }}
      .subtitle {{
        text-align: center;
        color: #666;
        margin-bottom: 30px;
        font-size: 1.2rem;
      }}
      .event {{
        background: #f9f9f9;
        border-left: 4px solid #4a90e2;
        margin-bottom: 15px;
        padding: 15px 20px;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.3s;
      }}
      .event:hover {{
        background: #e6f0ff;
      }}
      .date {{
        font-size: 0.9rem;
        color: #999;
        margin-bottom: 5px;
      }}
      .headline {{
        margin: 0;
        font-weight: 600;
      }}
      .content {{
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
        margin-top: 10px;
        color: #444;
      }}
      .event.active .content {{
        max-height: 500px;
      }}
    </style>

    <div class="timeline">
      <div class="title">{title}</div>
      <div class="subtitle">{subtitle}</div>
      {html_events}
    </div>
    """
    return html_code
