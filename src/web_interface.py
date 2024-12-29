from flask import Flask, render_template, Response, jsonify, request
import cv2
import threading
import logging
from datetime import datetime, time
import os

logger = logging.getLogger(__name__)

class WebInterface:
    def __init__(self, camera, scheduler):
        # Get the directory containing web_interface.py
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
        self.app = Flask(__name__, template_folder=template_dir)
        self.camera = camera
        self.scheduler = scheduler
        
        # Register routes
        self.app.route('/')(self.index)
        self.app.route('/video_feed')(self.video_feed)
        self.app.route('/api/settings', methods=['GET', 'POST'])(self.settings)
        
    def index(self):
        """Render main page."""
        return render_template('index.html')
        
    def gen_frames(self):
        """Generate camera frames."""
        while True:
            success, frame = self.camera.read_frame()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                       
    def video_feed(self):
        """Video streaming route."""
        return Response(self.gen_frames(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
                       
    def settings(self):
        """Handle settings API."""
        if request.method == 'GET':
            return jsonify({
                'monitoring_hours': {
                    'start': self.scheduler.active_hours['start'].strftime('%H:%M'),
                    'end': self.scheduler.active_hours['end'].strftime('%H:%M')
                },
                'sensitivity': self.scheduler.sensitivity_levels
            })
            
        data = request.json
        if 'monitoring_hours' in data:
            start = datetime.strptime(data['monitoring_hours']['start'], '%H:%M').time()
            end = datetime.strptime(data['monitoring_hours']['end'], '%H:%M').time()
            self.scheduler.set_monitoring_hours(start, end)
            
        if 'sensitivity' in data:
            self.scheduler.set_sensitivity(
                data['sensitivity']['day'],
                data['sensitivity']['night']
            )
            
        return jsonify({'status': 'success'})
        
    def run(self, host='0.0.0.0', port=5000):
        """Run the web interface."""
        # Create templates directory if it doesn't exist
        os.makedirs('templates', exist_ok=True)
        
        # Create index.html template
        with open('templates/index.html', 'w') as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Security Camera Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .video-container {
            margin-bottom: 20px;
        }
        .settings {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 200px;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
        }
        .status.monitoring {
            background-color: #d4edda;
            color: #155724;
        }
        .status.waiting {
            background-color: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Security Camera Monitor</h1>
        
        <div class="video-container">
            <img src="{{ url_for('video_feed') }}" width="100%">
        </div>
        
        <div class="settings">
            <h2>Settings</h2>
            <div class="form-group">
                <label>Monitoring Hours</label>
                <input type="time" id="startTime"> to <input type="time" id="endTime">
            </div>
            
            <div class="form-group">
                <label>Motion Sensitivity</label>
                <div>
                    <label>Day: <input type="number" id="daySensitivity" min="1000" max="5000"></label>
                    <label>Night: <input type="number" id="nightSensitivity" min="1000" max="5000"></label>
                </div>
            </div>
            
            <button onclick="saveSettings()">Save Settings</button>
        </div>
    </div>

    <script>
        // Load current settings
        fetch('/api/settings')
            .then(response => response.json())
            .then(data => {
                document.getElementById('startTime').value = data.monitoring_hours.start;
                document.getElementById('endTime').value = data.monitoring_hours.end;
                document.getElementById('daySensitivity').value = data.sensitivity.day;
                document.getElementById('nightSensitivity').value = data.sensitivity.night;
            });

        function saveSettings() {
            const settings = {
                monitoring_hours: {
                    start: document.getElementById('startTime').value,
                    end: document.getElementById('endTime').value
                },
                sensitivity: {
                    day: parseInt(document.getElementById('daySensitivity').value),
                    night: parseInt(document.getElementById('nightSensitivity').value)
                }
            };

            fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Settings saved successfully!');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to save settings');
            });
        }
    </script>
</body>
</html>
            """)
            
        # Run Flask app in a separate thread
        thread = threading.Thread(target=self.app.run, kwargs={
            'host': host,
            'port': port,
            'debug': False,
            'use_reloader': False
        })
        thread.daemon = True
        thread.start()
        logger.info(f"Web interface running at http://{host}:{port}")
