# Smart Security Camera

A Python-based smart security camera system that uses computer vision for motion detection and sends email notifications with captured images.

## Features

- Real-time motion detection using OpenCV
- Email notifications with captured images
- Automatic image cleanup
- Multi-threaded design for better performance
- Configurable sensitivity and email settings

## Requirements

- Python 3.8+
- Webcam
- Gmail account for notifications

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

3. Create a `.env` file with your email settings:
```env
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECEIVER=receiver-email@gmail.com
```

## Usage

Run the main script:
```bash
python main.py
```

- Press 'q' to quit the application
- Motion detection will automatically start when the program runs
- Email notifications will be sent when motion is detected

## Configuration

You can adjust the following parameters in `config.py`:
- Motion detection sensitivity
- Minimum object size
- Email notification settings
- Image cleanup settings

## Security Note

- Never commit your email credentials to version control
- Use environment variables or a `.env` file for sensitive data
- Generate an App Password for Gmail instead of using your account password

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Michael Williams - [GitHub Profile](https://github.com/mwill20)
