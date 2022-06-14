import colorsys
import datetime as date_time
import logging
import os.path
import subprocess
import threading
import time
from subprocess import PIPE, Popen, check_output

import ST7735
import requests
from PIL import Image, ImageDraw, ImageFont
from bme280 import BME280
from enviroplus import gas
from fonts.ttf import RobotoMedium as UserFont
from pms5003 import PMS5003, ReadTimeoutError

import variables as variable_file
from db_connect import db_create_connection
from db_input import db_send_to_local_db
from log_write_to_text_file import log_write_to_text_file

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559

    ltr559 = LTR559()
except ImportError:
    import ltr559
from enviroplus.noise import Noise

# go to writeable dir
os.chdir('/pi-enviro')

# log_write_to_text_file('msg')
log_write_to_text_file('Program Started')

# test for database & create one if not exist
my_file = os.path.isfile("data.db")
if my_file == False:
    import db_setup

    db_setup.create_tables()
    db_setup.add_data()
    print("Created db")

# db connect
database = r"data.db"
db_file = database
conn = db_create_connection(db_file)


def update_check():
    result = subprocess.run(['sudo', 'sh', './git_update.sh'], capture_output=True)
    print('update_check: {0} {1}'.format(result.stdout, result.stderr))
    log_write_to_text_file('update_check: {0} {1}'.format(result.stdout, result.stderr))


def dashboard_start():
    def process():
        result = subprocess.run(['sudo', 'systemctl', 'restart', 'pi-enviro.dashboard.service'], capture_output=True)
        print('dashboard starting: {0} {1}'.format(result.stdout, result.stderr))
        log_write_to_text_file('dashboard starting: {0} {1}'.format(result.stdout, result.stderr))

    t = threading.Thread(target=process, args=())
    t.start()


print("""luftdaten_combined.py - This combines the functionality of luftdaten.py and combined.py
================================================================================================
Luftdaten INFO
Reads temperature, pressure, humidity,
PM2.5, and PM10 from Enviro plus and sends data to Luftdaten,
the citizen science air quality project.
Note: you'll need to register with Luftdaten at:
https://meine.luftdaten.info/ and enter your Raspberry Pi
serial number that's displayed on the Enviro plus LCD along
with the other details before the data appears on the
Luftdaten map.
Press Ctrl+C to exit!
========================================================================
Combined INFO:
Displays readings from all of Enviro plus' sensors
Press Ctrl+C to exit!
""")

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info(""" """)
bus = SMBus(1)

# Create BME280 instance
bme280 = BME280(i2c_dev=bus)

# Create PMS5003 instance
pms5003 = PMS5003()

noise = Noise()

# Create a values dict to store the data
variables = ["temperature",
             "pressure",
             "humidity",
             "light",
             "oxidised",
             "reduced",
             "nh3",
             "pm1",
             "pm25",
             "pm10"]  # "decibels"]
units = ["C",
         "hPa",
         "%",
         "Lux",
         "kO",
         "kO",
         "kO",
         "ug/m3",
         "ug/m3",
         "ug/m3"]  # "db"]

# Define your own warning limits
# The limits definition follows the order of the variables array
# Example limits explanation for temperature:
# [4,18,28,35] means
# [-273.15 .. 4] -> Dangerously Low
# (4 .. 18]      -> Low
# (18 .. 28]     -> Normal
# (28 .. 35]     -> High
# (35 .. MAX]    -> Dangerously High
# DISCLAIMER: The limits provided here are just examples and come
# with NO WARRANTY. The authors of this example code claim
# NO RESPONSIBILITY if reliance on the following values or this
# code in general leads to ANY DAMAGES or DEATH.
limits = [[4, 18, 25, 35],
          [250, 650, 1013.25, 1015],
          [20, 30, 60, 70],
          [-1, -1, 30000, 100000],
          [-1, -1, 40, 50],
          [-1, -1, 450, 550],
          [-1, -1, 200, 300],
          [-1, -1, 50, 100],
          [-1, -1, 50, 100],
          [-1, -1, 50, 100]]  # , [-1, -1, 50, 100]]

# RGB palette for values on the combined screen
palette = [(0, 0, 255),  # Dangerously Low
           (0, 255, 255),  # Low
           (0, 255, 0),  # Normal
           (255, 255, 0),  # High
           (255, 0, 0)]  # Dangerously High
values_lcd = {}


# Read values from BME280 and PMS5003 and return as dict
def read_values(comp_temp, mod_press, raw_humid, raw_pm25, raw_pm10):
    values = {}
    values["temperature"] = "{:.2f}".format(comp_temp)
    values["pressure"] = "{:.2f}".format(mod_press)
    values["humidity"] = "{:.2f}".format(raw_humid)
    values["P2"] = str(raw_pm25)
    values["P1"] = str(raw_pm10)
    return values


# Get CPU temperature to use for compensation
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'],
                    stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])


# Get Raspberry Pi serial number to use as ID
def get_serial_number():
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line[0:6] == 'Serial':
                return line.split(":")[1].strip()


# Check for Wi-Fi connection
def check_wifi():
    if check_output(['hostname', '-I']):
        return True
    else:
        return False


# Create ST7735 LCD display class
st7735 = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display
st7735.begin()

WIDTH = st7735.width
HEIGHT = st7735.height

# Set up canvas and font
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font_size_small = 10
font_size_large = 20
font = ImageFont.truetype(UserFont, font_size_large)
smallfont = ImageFont.truetype(UserFont, font_size_small)
x_offset = 2
y_offset = 2
message = ""

# The position of the top bar
top_pos = 25


# Saves the data to be used in the graphs later and prints to the log


def save_data(idx, data):
    variable = variables[idx]
    # Maintain length of list
    values_lcd[variable] = values_lcd[variable][1:] + [data]
    unit = units[idx]
    message = "{}: {:.1f} {}".format(variable[:4], data, unit)
    logging.info(message)


# Displays data and text on the 0.96" LCD
def display_text(variable, data, unit):
    # Maintain length of list
    values_lcd[variable] = values_lcd[variable][1:] + [data]
    # Scale the values for the variable between 0 and 1
    vmin = min(values_lcd[variable])
    vmax = max(values_lcd[variable])
    colours = [(v - vmin + 1) / (vmax - vmin + 1)
               for v in values_lcd[variable]]
    # Format the variable name and value
    message = "{}: {:.1f} {}".format(variable[:4], data, unit)
    logging.info(message)
    draw.rectangle((0, 0, WIDTH, HEIGHT), (255, 255, 255))
    for i in range(len(colours)):
        # Convert the values to colours from red to blue
        colour = (1.0 - colours[i]) * 0.6
        r, g, b = [int(x * 255.0)
                   for x in colorsys.hsv_to_rgb(colour, 1.0, 1.0)]
        # Draw a 1-pixel wide rectangle of colour
        draw.rectangle((i, top_pos, i + 1, HEIGHT), (r, g, b))
        # Draw a line graph in black
        line_y = HEIGHT - \
                 (top_pos + (colours[i] * (HEIGHT - top_pos))) + top_pos
        draw.rectangle((i, line_y, i + 1, line_y + 1), (0, 0, 0))
    # Write the text at the top in black
    draw.text((0, 0), message, font=font, fill=(0, 0, 0))
    st7735.display(img)


# Displays all the text on the 0.96" LCD
def display_everything():
    draw.rectangle((0, 0, WIDTH, HEIGHT), (0, 0, 0))
    column_count = 2
    row_count = (len(variables) / column_count)
    for i in range(len(variables)):
        variable = variables[i]
        data_value = values_lcd[variable][-1]
        unit = units[i]
        x = x_offset + ((WIDTH // column_count) * (i // row_count))
        y = y_offset + ((HEIGHT / row_count) * (i % row_count))
        message = "{}: {:.1f} {}".format(variable[:4], data_value, unit)
        lim = limits[i]
        rgb = palette[0]
        for j in range(len(lim)):
            if data_value > lim[j]:
                rgb = palette[j + 1]
        draw.text((x, y), message, font=smallfont, fill=rgb)
    st7735.display(img)


def send_to_luftdaten(values, id):
    pm_values = dict(i for i in values.items() if i[0].startswith("P"))
    temp_values = dict(i for i in values.items() if not i[0].startswith("P"))

    pm_values_json = [{"value_type": key, "value": val}
                      for key, val in pm_values.items()]
    temp_values_json = [{"value_type": key, "value": val}
                        for key, val in temp_values.items()]

    resp_1 = requests.post(
        "https://api.luftdaten.info/v1/push-sensor-data/",
        json={
            "software_version": "enviro-plus 0.0.1",
            "sensordatavalues": pm_values_json
        },
        headers={
            "X-PIN": "1",
            "X-Sensor": id,
            "Content-Type": "application/json",
            "cache-control": "no-cache"
        }
    )

    resp_2 = requests.post(
        "https://api.luftdaten.info/v1/push-sensor-data/",
        json={
            "software_version": "enviro-plus 0.0.1",
            "sensordatavalues": temp_values_json
        },
        headers={
            "X-PIN": "11",
            "X-Sensor": id,
            "Content-Type": "application/json",
            "cache-control": "no-cache"
        }
    )

    if resp_1.ok and resp_2.ok:
        return True
    else:
        return False


# add to db via thread, otherwise screws up time
def send_to_db(datetime, temperature, pressure, humidity, light, oxidised, reduced, nh3, pm1, pm25, pm10, decibels):
    t = threading.Thread(target=db_send_to_local_db, args=(
        datetime, temperature, pressure, humidity, light, oxidised, reduced, nh3, pm1, pm25, pm10, decibels))
    t.start()


def run():
    print('running run')
    log_write_to_text_file('running run')
    # Compensation factor for temperature
    comp_factor = 1

    # Raspberry Pi ID to send to Luftdaten
    id = "raspi-" + get_serial_number()

    # Added for state
    delay = 0.5  # Debounce the proximity tap
    mode = 10  # The starting mode
    last_page = 0
    light = 1

    for v in variables:
        values_lcd[v] = [1] * WIDTH

    # Text settings
    font_size = 16
    font = ImageFont.truetype(UserFont, font_size)
    cpu_temps = [get_cpu_temperature()] * 5

    # Display Raspberry Pi serial and Wi-Fi status
    print("Raspberry Pi serial: {}".format(get_serial_number()))
    print("Wi-Fi: {}\n".format("connected" if check_wifi() else "disconnected"))

    time_since_update = 0
    update_time = time.time()
    cpu_temps_len = float(len(cpu_temps))

    # Main loop to read data, display, and send to Luftdaten
    log_write_to_text_file('Starting While Loop')
    while True:
        try:
            # add sleep for every i seconds
            time.sleep(3)

            curtime = time.time()
            time_since_update = curtime - update_time

            # Calculate these things once, not twice
            cpu_temp = get_cpu_temperature()
            # Smooth out with some averaging to decrease jitter
            cpu_temps = cpu_temps[1:] + [cpu_temp]
            avg_cpu_temp = sum(cpu_temps) / cpu_temps_len
            raw_temp = bme280.get_temperature()
            comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / comp_factor)

            raw_press = bme280.get_pressure()
            raw_humid = bme280.get_humidity()
            try:
                pm_values = pms5003.read()
                raw_pm25 = pm_values.pm_ug_per_m3(2.5)
                raw_pm10 = pm_values.pm_ug_per_m3(10)
            except ReadTimeoutError:
                pms5003.reset()
                pm_values = pms5003.read()
                raw_pm25 = pm_values.pm_ug_per_m3(2.5)
                raw_pm10 = pm_values.pm_ug_per_m3(10)

            if time_since_update > 145:
                values = read_values(comp_temp, raw_press * 100,
                                     raw_humid, raw_pm25, raw_pm10)
                #########################################################################################
                # restart dashboard for new data
                #########################################################################################
                if variable_file.dashboard == True:
                    dashboard_start()

                #########################################################################################
                # send data to Luftdaten
                #########################################################################################
                if variable_file.Luftdaten == True:
                    resp = send_to_luftdaten(values, id)
                    print("Response: {}\n".format("ok" if resp else "failed"))

                update_time = curtime

                #########################################################################################
                # send data to db
                #########################################################################################
                # vars
                datetime = date_time.datetime.now().isoformat()
                temperature = comp_temp
                pressure = raw_press
                humidity = raw_humid
                light = ltr559.get_lux()
                data = gas.read_all()
                oxidised = data.oxidising / 1000
                reduced = data.reducing / 1000
                nh3 = data.nh3 / 1000
                pm1 = float(pm_values.pm_ug_per_m3(1.0))
                pm25 = raw_pm25
                pm10 = raw_pm10
                decibels = ' '

                # send to db
                send_to_db(datetime, temperature, pressure, humidity, light, oxidised, reduced, nh3, pm1, pm25, pm10,
                           decibels)
                light = 1

            # Now comes the combined.py functionality:
            # If the proximity crosses the threshold, toggle the mode
            proximity = ltr559.get_proximity()
            if proximity > 1500 and curtime - last_page > delay:
                mode = (mode + 1) % 11
                last_page = curtime
            # One mode for each variable
            if mode == 0:
                # variable = "temperature"
                unit = "C"
                display_text(variables[mode], comp_temp, unit)

            if mode == 1:
                # variable = "pressure"
                unit = "hPa"
                display_text(variables[mode], raw_press, unit)

            if mode == 2:
                # variable = "humidity"
                unit = "%"
                display_text(variables[mode], raw_humid, unit)

            if mode == 3:
                # variable = "light"
                unit = "Lux"
                if proximity < 10:
                    data = ltr559.get_lux()
                else:
                    data = 1
                display_text(variables[mode], data, unit)

            if mode == 4:
                # variable = "oxidised"
                unit = "kO"
                data = gas.read_all()
                data = data.oxidising / 1000
                display_text(variables[mode], data, unit)

            if mode == 5:
                # variable = "reduced"
                unit = "kO"
                data = gas.read_all()
                data = data.reducing / 1000
                display_text(variables[mode], data, unit)

            if mode == 6:
                # variable = "nh3"
                unit = "kO"
                data = gas.read_all()
                data = data.nh3 / 1000
                display_text(variables[mode], data, unit)

            if mode == 7:
                # variable = "pm1"
                unit = "ug/m3"
                data = float(pm_values.pm_ug_per_m3(1.0))
                display_text(variables[mode], data, unit)

            if mode == 8:
                # variable = "pm25"
                unit = "ug/m3"
                display_text(variables[mode], float(raw_pm25), unit)

            if mode == 9:
                # variable = "pm10"
                unit = "ug/m3"
                display_text(variables[mode], float(raw_pm10), unit)

            if mode == 10:
                # Everything on one screen
                save_data(0, comp_temp)
                save_data(1, raw_press)
                display_everything()
                save_data(2, raw_humid)
                if proximity < 10:
                    raw_data = ltr559.get_lux()
                else:
                    raw_data = 1
                save_data(3, raw_data)
                display_everything()
                gas_data = gas.read_all()
                save_data(4, gas_data.oxidising / 1000)
                save_data(5, gas_data.reducing / 1000)
                save_data(6, gas_data.nh3 / 1000)
                display_everything()
                pms_data = None
                save_data(7, float(pm_values.pm_ug_per_m3(1.0)))
                save_data(8, float(raw_pm25))
                save_data(9, float(raw_pm10))
                display_everything()

            if mode == 11:
                variable = "reduced"
                unit = "kO"
                data = gas.read_all()
                data = data.reducing / 1000
                display_text(variables[mode], data, unit)

                """
                amps = noise.get_amplitudes_at_frequency_ranges([
                    (100, 200),
                    (500, 600),
                    (1000, 1200)
                ])
                amps = [n * 32 for n in amps]
                unit = "db"
                data = amps
                display_text(variables[mode], data, unit)


                # test                
                disp = ST7735.ST7735(
                    port=0,
                    cs=ST7735.BG_SPI_CS_FRONT,
                    dc=9,
                    backlight=0,
                    rotation=90)
                    
                    or
                    
                    img = Image.new('RGB', (disp.width, disp.height), color=(0, 0, 0))
                    draw = ImageDraw.Draw(img)

            if mode == 12:
                data = ''
                amps = noise.get_amplitudes_at_frequency_ranges([
                    (10, 10000)
                ])
                # amps = [n * 32 for n in amps]
                img2 = img.copy()
                draw.rectangle((0, 0, disp.width, disp.height), (0, 0, 0))
                img.paste(img2, (1, 0))
                draw.line((0, 0, 0, amps[0]), fill=(0, 0, 255))
                disp.display(img)
                print(amps)
            """
        except Exception as e:
            print(e)
            log_write_to_text_file('{0}'.format(e))


if __name__ == '__main__':
    if variable_file.update == True:
        update_check()
    run()
