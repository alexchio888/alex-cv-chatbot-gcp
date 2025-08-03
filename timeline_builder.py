from datetime import datetime
import plotly.figure_factory as ff
import pandas as pd

def build_gantt_from_json(json_data):
    # Parse events into a DataFrame suitable for Plotly Gantt
    tasks = []
    for event in json_data.get("events", []):
        start_year = event["start_date"].get("year", "2000")
        start_month = event["start_date"].get("month", "01")
        # Compose start date string
        start_date = f"{start_year}-{start_month.zfill(2)}-01"
        
        # For simplicity, we assume each event lasts one month; 
        # you can adjust this logic if you have end_date or durations
        # Here we just add 1 month for end date (roughly)
        end_year = start_year
        end_month = str(int(start_month) + 1) if int(start_month) < 12 else "12"
        if int(start_month) == 12:
            end_year = str(int(start_year) + 1)
            end_month = "01"
        end_date = f"{end_year}-{end_month.zfill(2)}-01"
        
        tasks.append(dict(
            Task=event["text"]["headline"],
            Start=start_date,
            Finish=end_date,
            Description=event["text"]["text"]
        ))
    
    df = pd.DataFrame(tasks)
    
    fig = ff.create_gantt(
        df,
        index_col='Task',
        show_colorbar=True,
        group_tasks=True,
        title=json_data["title"]["text"]["headline"],
        bar_width=0.3,
        showgrid_x=True,
        showgrid_y=True,
        hover_data=['Description']
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
