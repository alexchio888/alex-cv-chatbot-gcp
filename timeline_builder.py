from datetime import datetime
import pandas as pd
import plotly.figure_factory as ff
import calendar

def parse_date(date_dict):
    year = int(date_dict.get("year", 1900))
    month = int(date_dict.get("month", 1))
    day = int(date_dict.get("day", 1))
    return datetime(year, month, day)

def build_gantt_from_json(timeline_json):
    import plotly.graph_objects as go
    tasks_by_tag = {}

    for event in timeline_json.get("events", []):
        tags = event.get("tags", [])
        start_date = parse_date(event.get("start_date", {}))
        end_date = parse_date(event.get("end_date", event.get("start_date", {})))
        task = dict(
            Task=event["text"]["headline"],
            Start=start_date,
            Finish=end_date,
            Description=event["text"].get("text", ""),
            Tags=", ".join(tags)
        )
        for tag in tags or ["Uncategorized"]:
            tasks_by_tag.setdefault(tag, []).append(task)

    if not tasks_by_tag:
        return None

    # All tasks combined
    all_tasks = sum(tasks_by_tag.values(), [])

    # Base figure
    df = pd.DataFrame(all_tasks)
    fig = ff.create_gantt(
        df,
        index_col='Task',
        show_colorbar=False,
        group_tasks=True,
        title="",
        showgrid_x=True,
        showgrid_y=True,
        bar_width=0.2
    )

    # Add dropdown for filtering
    buttons = []
    for tag, task_list in tasks_by_tag.items():
        visible = [t["Task"] in [task["Task"] for task in task_list] for t in all_tasks]
        buttons.append(dict(
            label=tag,
            method="update",
            args=[
                {"visible": visible},
                {"title": f"Gantt Chart - {tag}"}
            ]
        ))

    # Add "All" option
    buttons.insert(0, dict(
        label="All",
        method="update",
        args=[
            {"visible": [True] * len(all_tasks)},
            {"title": "Gantt Chart - All Events"}
        ]
    ))

    fig.update_layout(
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            direction="down",
            showactive=True,
            x=0.1,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )]
    )

    # Limit x-axis to today → end of next month
    today = datetime.today()
    year = today.year
    month = today.month + 1
    if month == 13:
        month = 1
        year += 1
    last_day_next_month = calendar.monthrange(year, month)[1]
    end_of_next_month = datetime(year, month, last_day_next_month)

    fig.update_layout(
        xaxis=dict(
            range=[df['Start'].min(), end_of_next_month],
            title="Date",
            constrain='range'
        )
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
