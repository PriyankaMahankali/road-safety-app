import requests
import pyttsx3
import speech_recognition as sr
from geopy.geocoders import Nominatim
from googletrans import Translator

# Initialize components
geolocator = Nominatim(user_agent="road_safety_app")
translator = Translator()
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def get_location():
    """Get current location (sample location provided)."""
    try:
        location = geolocator.geocode("Hyderabad, India")  # Replace with specific location
        if location is None:
            speak("Location not found. Please check the location name.")
            return (0.0, 0.0)  # Default location
        return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Error in get_location: {e}")
        return (0.0, 0.0)

def get_emergency_alerts(location):
    """Fetch emergency alerts based on location."""
    api_key = "bb1ce043b69feb621db3b0b0f3593d49"  # OpenWeatherMap API Key
    lat, lon = location
    try:
        response = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={api_key}&exclude=minutely,hourly,daily&units=metric")
        data = response.json()
        
        if "alerts" in data:
            alerts = data["alerts"]
            alert_messages = []
            for alert in alerts:
                event = alert["event"]
                description = alert["description"]
                start = alert["start"]
                end = alert["end"]
                alert_messages.append(f"{event}: {description} (Valid from {start} to {end})")
            return alert_messages
        else:
            return []  # No alerts
    except Exception as e:
        print(f"Error in get_emergency_alerts: {e}")
        return []

def get_real_time_traffic_updates(location):
    """Fetch real-time traffic updates using the TomTom Traffic API."""
    api_key = "ZeWGFVS8goVsNGUVL0MDPCMuwc9ls8ew"
    lat, lon = location
    try:
        response = requests.get(
            f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={api_key}"
        )
        data = response.json()
        if "flowSegmentData" in data:
            current_speed = data["flowSegmentData"]["currentSpeed"]
            free_flow_speed = data["flowSegmentData"]["freeFlowSpeed"]
            travel_time = data["flowSegmentData"]["currentTravelTime"]
            update = (
                f"Traffic update: Current speed is {current_speed} km/h, "
                f"free-flow speed is {free_flow_speed} km/h, and estimated travel time is {travel_time / 60:.2f} minutes."
            )
        else:
            update = "No traffic data available at your location."
    except Exception as e:
        print(f"Error in get_real_time_traffic_updates: {e}")
        update = "Failed to retrieve traffic information."
    
    return update

def check_and_trigger_emergency_alerts():
    """Check for emergencies and trigger alerts if found."""
    location = get_location()
    emergency_alerts = get_emergency_alerts(location)
    if emergency_alerts:
        for alert in emergency_alerts:
            emergency_alert(alert)

def emergency_alert(alert_message):
    """Read out emergency alerts."""
    speak(f"Emergency alert: {alert_message}")

# Example integration into voice assistant
def voice_assistant():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening for commands...")
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio)
            speak(f"You said: {command}")
            
            if "traffic" in command.lower():
                location = get_location()
                update = get_real_time_traffic_updates(location)
                speak(update)
            
            elif "weather" in command.lower():
                forecast = get_weather_forecast()
                speak(forecast)

            elif "emergency alerts" in command.lower():
                check_and_trigger_emergency_alerts()
            
            else:
                speak("Sorry, I can't handle that command yet.")
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand the command.")
        except Exception as e:
            print(f"Error in voice_assistant: {e}")

# Call this in the main program loop
if __name__ == "__main__":
    voice_assistant()  # Activates the voice assistant
    check_and_trigger_emergency_alerts()  # Regularly check for emergency alerts
