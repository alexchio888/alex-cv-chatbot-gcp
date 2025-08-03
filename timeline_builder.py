# timeline_builder.py

def get_timeline_css():
    return """
    <style>
      .timeline {
        position: relative;
        max-width: 600px;
        margin: 20px auto;
      }
      .timeline::after {
        content: '';
        position: absolute;
        width: 4px;
        background-color: #4a90e2;
        top: 0;
        bottom: 0;
        left: 20px;
        margin-left: -2px;
      }
      .container {
        padding: 10px 40px;
        position: relative;
        background-color: inherit;
        width: 100%;
      }
      .container::before {
        content: '';
        position: absolute;
        width: 16px;
        height: 16px;
        right: auto;
        background-color: white;
        border: 4px solid #4a90e2;
        top: 15px;
        left: 12px;
        border-radius: 50%;
        z-index: 1;
      }
      .content {
        padding: 10px 20px;
        background-color: #f0f8ff;
        position: relative;
        border-radius: 6px;
      }
      .date {
        font-weight: bold;
        margin-bottom: 5px;
        color: #4a90e2;
      }
    </style>
    """

def build_timeline_html(data):
    timeline_html = '<div class="timeline">'
    for item in data:
        timeline_html += f'''
        <div class="container">
          <div class="content">
            <div class="date">{item["date"]}</div>
            {item["event"]}
          </div>
        </div>
        '''
    timeline_html += '</div>'
    return timeline_html
