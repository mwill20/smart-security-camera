# Smart Security Camera

A Python-based smart security camera system with advanced features including face detection, web interface, and configurable monitoring schedules.

## Features

- Real-time motion detection using OpenCV
- Face detection using Haar Cascades
- Web interface for live monitoring and configuration
- Configurable monitoring schedules (day/night settings)
- Enhanced notifications:
  - Email notifications with timestamped images
  - SMS notifications via Twilio (optional)
  - Multiple images per detection event
- Motion tracking with direction detection
- Multi-threaded design for optimal performance
- Automatic image cleanup

## Requirements

- Python 3.8+
- Webcam
- Gmail account for email notifications
- Twilio account for SMS notifications (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mwill20/smart-security-camera.git
cd smart-security-camera
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your settings:
```env
# Email Settings
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECEIVER=receiver-email@gmail.com

# Twilio Settings (Optional)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_FROM=your-twilio-number
TWILIO_PHONE_TO=your-phone-number
```

## Usage

1. Run the main script:
```bash
python main.py
```

2. Access the web interface:
- Open http://localhost:5000 in your browser
- View live camera feed
- Configure monitoring hours
- Adjust motion sensitivity for day/night

3. Features:
- Motion detection starts automatically after 1 minute of inactivity
- Face detection highlights detected faces in blue rectangles
- Motion tracking shows movement direction
- Status display shows current monitoring state
- Timestamp overlay on video feed

## Configuration

### Web Interface Settings
- Monitoring Hours: Set active monitoring periods
- Motion Sensitivity: Adjust separately for day and night
- Face Detection: Toggle on/off
- SMS Notifications: Enable/disable (requires Twilio)

### Advanced Configuration (`config.py`)
- Frame dimensions and FPS
- Motion detection parameters
- Face detection settings
- Web interface host/port
- Notification settings
- Image cleanup parameters

## Security Notes

- Never commit sensitive credentials to version control
- Use environment variables or `.env` file for credentials
- Generate an App Password for Gmail instead of using account password
- Web interface runs on localhost by default for security

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Michael Williams - [GitHub Profile](https://github.com/mwill20)

## Recent Updates

### Version 2.0 (December 2023)
- Added face detection capability
- Implemented web interface for remote monitoring
- Added configurable monitoring schedules
- Enhanced notifications with SMS support
- Improved motion tracking with direction detection
- Added timestamp overlay to video feed
