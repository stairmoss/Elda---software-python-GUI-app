# Defines the capabilities available to the AI

SYSTEM_FUNCTIONS = [
    {
        "name": "open_youtube",
        "description": "Opens the YouTube app on the patient's device to play music or videos.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "call_caregiver",
        "description": "Initiates a video or voice call to the assigned caregiver.",
        "parameters": {
            "type": "object",
            "properties": {
                "urgency": {
                    "type": "string",
                    "enum": ["low", "high"],
                    "description": "Urgency level of the call."
                }
            },
            "required": ["urgency"]
        }
    },
    {
        "name": "adjust_volume",
        "description": "Changes the device volume.",
        "parameters": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "integer",
                    "description": "Volume level from 0 to 100."
                }
            },
            "required": ["level"]
        }
    }
]

def get_function_schemas():
    return SYSTEM_FUNCTIONS
