import screen_brightness_control as sbc
from AppOpener import open as open_app
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math

class SystemTools:
    @staticmethod
    def set_volume(level: int):
        """Sets the system volume to the specified percentage (0-100)."""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            # Volume range is usually -65.25 to 0.0 dB
            # We need to map 0-100 to this scalar
            # pycaw allows setting scalar volume directly (0.0 to 1.0)
            scalar = max(0.0, min(1.0, level / 100.0))
            volume.SetMasterVolumeLevelScalar(scalar, None)
            return f"Volume set to {level}%"
        except Exception as e:
            return f"Error setting volume: {e}"

    @staticmethod
    def set_brightness(level: int):
        """Sets the screen brightness to the specified percentage (0-100)."""
        try:
            sbc.set_brightness(level)
            return f"Brightness set to {level}%"
        except Exception as e:
            return f"Error setting brightness: {e}"

    @staticmethod
    def open_application(app_name: str):
        """Opens the specified application by name."""
        try:
            # clean up name
            app_name = app_name.lower().replace("open ", "").strip()
            open_app(app_name, match_closest=True)
            return f"Opening {app_name}"
        except Exception as e:
            return f"Error opening application: {e}"

# Tool Definitions for FunctionGemma
TOOLS_SCHEMA = [
    {
        "name": "set_volume",
        "description": "Adjust the computer's speaker volume.",
        "parameters": {
            "type": "object",
            "properties": {
                "level": {"type": "integer", "description": "Target volume level (0-100)"}
            },
            "required": ["level"]
        }
    },
    {
        "name": "set_brightness",
        "description": "Adjust the computer's screen brightness.",
        "parameters": {
            "type": "object",
            "properties": {
                "level": {"type": "integer", "description": "Target brightness level (0-100)"}
            },
            "required": ["level"]
        }
    },
    {
        "name": "open_application",
        "description": "Open a software application on the computer.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "Name of the application (e.g., 'notepad', 'chrome')"}
            },
            "required": ["app_name"]
        }
    }
]
