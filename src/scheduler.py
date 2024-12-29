import schedule
import time
from datetime import datetime, time as dtime
import logging

logger = logging.getLogger(__name__)

class MonitoringSchedule:
    def __init__(self):
        self.active_hours = {
            'start': dtime(0, 0),  # Default: midnight
            'end': dtime(23, 59)   # Default: 11:59 PM
        }
        self.sensitivity_levels = {
            'day': 3000,    # Higher threshold during day
            'night': 2000   # Lower threshold at night
        }
        
    def is_monitoring_time(self) -> bool:
        """Check if current time is within monitoring hours."""
        current_time = datetime.now().time()
        if self.active_hours['start'] <= self.active_hours['end']:
            return self.active_hours['start'] <= current_time <= self.active_hours['end']
        else:  # Handle overnight monitoring (e.g., 22:00 - 06:00)
            return current_time >= self.active_hours['start'] or current_time <= self.active_hours['end']
            
    def get_current_sensitivity(self) -> int:
        """Get motion sensitivity based on time of day."""
        current_hour = datetime.now().hour
        if 6 <= current_hour < 20:  # Daytime: 6 AM - 8 PM
            return self.sensitivity_levels['day']
        return self.sensitivity_levels['night']
        
    def set_monitoring_hours(self, start_time: dtime, end_time: dtime):
        """Set monitoring start and end times."""
        self.active_hours['start'] = start_time
        self.active_hours['end'] = end_time
        logger.info(f"Monitoring hours set to {start_time} - {end_time}")
        
    def set_sensitivity(self, day_level: int, night_level: int):
        """Set motion detection sensitivity levels."""
        self.sensitivity_levels['day'] = day_level
        self.sensitivity_levels['night'] = night_level
        logger.info(f"Sensitivity levels set to: Day={day_level}, Night={night_level}")
