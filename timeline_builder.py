from datetime import datetime
import pandas as pd
import plotly.figure_factory as ff
import calendar
import plotly.graph_objects as go

def parse_date(date_dict):
    year = int(date_dict.get("year", 1900))
    month = int(date_dict.get("month", 1))
    day = int(date_dict.get("day", 1))
    return datetime(year, month, day)

def build_gantt_from_json(timeline_json):
    events_by_tag = {}
    all_events = []

    # Parse and group events
    for event in timeline_json.get("events", []):
        tags = event.get("tags", []) or ["Uncategorized"]
        start = parse_date(event.get("start_date", {}))
        end = parse_date(event.get("end_date", event.get("start_date", {})))
        headline = event["text"]["headline"]
        description = event["text"].get("text", "")
        for tag in tags:
            events_by_tag.setdefault(tag, []).append(dict(
                task=headline,
                start=start,
                end=end,
                description=description,
                tag=tag
            ))
        all_events.append(dict(
            task=headline,
            start=start,
            end=end,
            description=description,
            tag=", ".join(tags)
        ))

    fig = go.Figure()
    buttons = []

    # Utility: add traces for a group of events
    def add_event_traces(events, visible):
        for i, e in enumerate(events):
            fig.add_trace(go.Bar(
                x=[(e["end"] - e["start"]).days],
                y=[e["task"]],
                base=e["start"],
                orientation='h',
                text=e["description"],
                hovertemplate=f"{e['task']}<br>{e['start'].date()} to {e['end'].date()}<br>{e['description']}",
                marker_color='steelblue',
                visible=visible
            ))

    # Add all event traces (first tag: visible, others: hidden)
    tag_names = sorted(events_by_tag.keys())
    for i, tag in enumerate(["All"] + tag_names):
        if tag == "All":
            add_event_traces(all_events, True)
        else:
            add_event_traces(events_by_tag[tag], False)

    # Create visibility masks and buttons
    traces_per_tag = { "All": len(all_events) }
    for tag in tag_names:
        traces_per_tag[tag] = len(events_by_tag[tag])

    start_idx = 0
    for i, tag in enumerate(["All"] + tag_names):
        total = sum(traces_per_tag.values())
        visible = [False] * total
        count = traces_per_tag[tag]
        visible[start_idx:start_idx + count] = [True] * count

        y_labels = [e["task"] for e in all_events] if tag == "All" else [e["task"] for e in events_by_tag[tag]]

        buttons.append(dict(
            label=tag,
            method="update",
            args=[
                {"visible": visible},
                {"yaxis": {"categoryorder": "array", "categoryarray": y_labels[::-1]}}
            ]
        ))
        start_idx += count

    # Layout
    today = datetime.today()
    year = today.year
    month = today.month + 1
    if month == 13:
        month = 1
        year += 1
    last_day = calendar.monthrange(year, month)[1]
    end_of_next_month = datetime(year, month, last_day)

    fig.update_layout(
        title="Professional Timeline",
        barmode='stack',
        xaxis=dict(
            title="Date",
            range=[min(e["start"] for e in all_events), end_of_next_month],
            constrain='range',
            showgrid=True
        ),
        yaxis=dict(
            title="",
            categoryorder="array",
            categoryarray=[e["task"] for e in all_events][::-1]
        ),
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            direction="down",
            showactive=True,
            x=0,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )],
        height=600
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
