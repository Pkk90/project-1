import kivy 
kivy.require('2.0.0')
import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from kivy import Config
Config.set('graphics', 'multisamples', '0')

import datetime
import ephem
import requests

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.animation import Animation
from hijri_converter import convert

# Dictionary to map Hijri month numbers to their names
hijri_month_names = {
    1: "Muharram",
    2: "Safar",
    3: "Rabi' al-Awwal",
    4: "Rabi' al-Thani",
    5: "Jumada al-Ula",
    6: "Jumada al-Thani",
    7: "Rajab",
    8: "Sha'ban",
    9: "Ramadan",
    10: "Shawwal",
    11: "Dhu al-Qi'dah",
    12: "Dhu al-Hijjah"
}

class DateTimeApp(App):
    def build(self):
        # Create the main layout
        layout = BoxLayout(orientation='vertical', padding=20)

        # Create labels to display the data
        location_label = Label(markup=True, font_size='28sp', color=(1, 0.843, 0, 1))  # Orange color
        datetime_label = Label(markup=True, font_size='30sp', color=(1, 1, 1, 1))  # White color
        prayer_times_label1 = Label(markup=True, font_size='27sp', color=(1, 0, 1, 1))  # Magenta color
        
        sunrise_label = Label(markup=True, font_size='27sp', color=(1, 0, 0, 1))  # Red color
        sunset_label = Label(markup=True, font_size='27sp', color=(0, 1, 0, 1))  # Green color
        moonrise_label = Label(markup=True, font_size='27sp', color=(0, 0, 1, 1))  # Blue color
        moonset_label = Label(markup=True, font_size='27sp', color=(1, 0, 1, 1))  # Magenta color
        illumination_label = Label(markup=True, font_size='27sp')
        
        def get_hijri_date_now():
        # Get the current Gregorian date as a datetime object
            current_gregorian_date = datetime.datetime.now()

            # Extract year, month, and day from the datetime object
            year = current_gregorian_date.year
            month = current_gregorian_date.month
            day = current_gregorian_date.day

            # Convert the current Gregorian date to Hijri date
            current_hijri_date = convert.Gregorian(year, month, day).to_hijri()
            
            return current_hijri_date
        
        

        current_hijri_date = get_hijri_date_now()
        hijri_month = current_hijri_date.month
        hijri_year = current_hijri_date.year
        hijri_day = current_hijri_date.day

        hijri_month_name = hijri_month_names.get(hijri_month, "Unknown")
        hijri_date_label = Label(text=f"[color=008080][size=32 sp]Hijri Date: [/color][color=800080]{hijri_year:04d} - {hijri_month:02d}  ({hijri_month_name}) - {hijri_day:02d}[/color][/size]", markup=True)

        

        layout.add_widget(location_label)
        layout.add_widget(datetime_label)
        layout.add_widget(hijri_date_label)
        layout.add_widget(prayer_times_label1)
        layout.add_widget(sunrise_label)
        layout.add_widget(sunset_label)
        layout.add_widget(moonrise_label)
        layout.add_widget(moonset_label)
        layout.add_widget(illumination_label)
        

        # Calculate and update the static values for sunrise, sunset, moonrise, and moonset
        observer = ephem.Observer()
        observer.lat = '35.6763'  # Latitude of Tunis
        observer.lon = '10.0951'  # Longitude of Tunis
        observer.elev = 10  # Elevation of the observer

        sun = ephem.Sun()
        moon = ephem.Moon()

        sunrise = observer.previous_rising(sun).datetime() + datetime.timedelta(hours=1)
        sunset = observer.next_setting(sun).datetime() + datetime.timedelta(hours=1)
        moonrise = observer.previous_rising(moon).datetime() + datetime.timedelta(hours=1)
        moonset = observer.next_setting(moon).datetime() + datetime.timedelta(hours=1)
        illumination = round(moon.phase / 100.0, 3) * 100

        sunrise = sunrise.strftime("%H:%M:%S")
        sunset = sunset.strftime("%H:%M:%S")
        moonrise = moonrise.strftime("%H:%M:%S")
        moonset = moonset.strftime("%H:%M:%S")

        prayer_times_label1.text = "[b]Prayer Times[/b]\nLoading..."
        

        # Fetch and update the prayer times from the API
        prayer_times = self.get_prayer_times("Kairouan", "Tunisia", datetime.datetime.now().strftime("%d-%m-%Y"))
        if prayer_times:
            # Filter out unnecessary prayers
            prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
            prayer_times_str1 = ""
            for prayer in prayers:
                time = prayer_times[prayer]
                prayer_times_str1 += f"[color=00ffff]{prayer.capitalize()}: {time}[/color]   "
            prayer_times_label1.text = f" [size=25 sp] {prayer_times_str1} [/size]"

        location_label.text = f'[color=ffd700]Location: Kairouan[/color]'
        datetime_label.text = f'[color=008080][size=30 sp]Current Date and Time[/size][/color]: Initializing...'
        sunrise_label.text = f'[color=008080]Sunrise[/color]: [color=ffd700] {sunrise} [/color]'
        sunset_label.text = f'[color=008080]Sunset[/color]: [color=ff4500] {sunset} [/color]'
        moonrise_label.text = f'[color=008080]Moonrise[/color]: [color=00cc66] {moonrise} [/color]'
        moonset_label.text = f'[color=008080]Moonset[/color]: [color=ff9933] {moonset} [/color]'
        illumination_label.text = f'[color=008080]Moon Phase (%) [/color]: [color=9932cc] {illumination} [/color]'

        # Schedule the update of the datetime label every second
        Clock.schedule_interval(lambda dt: self.update_datetime(datetime_label), 1)

        # Apply smooth animation effect to the datetime label
        anim = Animation(color=(1, 1, 1, 1), duration=1) + Animation(color=(1, 1, 1, 0.5), duration=1)
        anim.repeat = True
        anim.start(datetime_label)

        return layout

    def update_datetime(self, datetime_label):
        current_time = datetime.datetime.now()
        date_time = current_time.strftime("[color=336699] %A %Y-%m-%d [/color] [color=336699] [size=37 sp] %H:%M:%S [/color][/size]")
        datetime_label.text = f'[color=ffffff][size=30 sp]Date & Time[/size][/color]: {date_time}'

    def get_prayer_times(self, city, country, date):
        url = f"http://api.aladhan.com/v1/timingsByCity/{date}"
        params = {
            "city": city,
            "country": country,
            "method": 3  # Adjust the calculation method as needed
        }

        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code == 200:
            timings = data["data"]["timings"]
            return timings
        else:
            print("Error:", data["status"])
            return None

if __name__ == '__main__':
    DateTimeApp().run()



