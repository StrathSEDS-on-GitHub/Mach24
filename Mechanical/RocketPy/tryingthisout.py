from rocketpy import Environment, SolidMotor, Rocket, Flight
from rocketpy.plots.compare import CompareFlights
import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tqdm import tqdm

# Initialise MACC LaunchPad
env = Environment(latitude=55.433982, longitude= -5.696031, elevation=0)

#launchday = (2024, 7, 10, 12) #Approximate 
launchday = datetime.date.today() + datetime.timedelta(days=1)

env.set_date( (launchday.year, launchday.month, launchday.day, 9) )

# env.set_atmospheric_model(
#     # type="Forecast", file="GFS"
#     type="custom_atmosphere",
    
#     pressure=None,
#     temperature=300,
#     wind_u=[(0,10), (500,10)], #Positive for East, Negative for West
#     wind_v=[(0,0.1), (100,0.1)], #Positive for North, Negative for South
# )

#env.info()

#Info from OR
length = 1.98
centre_of_mass = 1.14

#From Rules
max_drift = 1500

### Motor Setup ###

Pro54K1440 = SolidMotor(
    thrust_source="./data/Cesaroni_K1440.eng",     #import
    dry_mass=0.7302,
    dry_inertia=(0,0,0),
    nozzle_radius=52 / 2000,                #find
    grain_number=6,
    grain_density=1.129,                    #find
    grain_outer_radius=52 / 2000,           #find
    grain_initial_inner_radius=15 / 1000,   #find
    grain_initial_height=142 / 1000,        #find
    grain_separation=5 / 1000,              #find
    grains_center_of_mass_position=0.3,     #find
    center_of_dry_mass_position=0.3,        #find
    nozzle_position=0,
    burn_time=1.65,
    throat_radius=5 / 1000,
    coordinate_system_orientation="nozzle_to_combustion_chamber"
)

payload_mass = 1.2
vehicle_mass = 5.26

total_mass = vehicle_mass + payload_mass

radius = 8 / 200

Ixx = 0.25 * total_mass * radius**2 + 1/12 * total_mass * length**2
Irr = 0.5 * total_mass * radius**2
main_diameter = 75 / 100
drogue_diameter = 40 / 100

### Vehicle Setup ###

strath_with_payload = Rocket(
    radius=80 / 2000,
    mass=total_mass,
    center_of_mass_without_motor=0,
    inertia= (Ixx,Ixx,Irr),
    power_off_drag="./data/powerOffDragCurve.CSV",
    power_on_drag="./data/powerOnDragCurve.CSV",
    coordinate_system_orientation="tail_to_nose",
)

strath_without_payload = Rocket(
    radius=80 / 2000,
    mass=vehicle_mass,
    center_of_mass_without_motor=0,
    inertia= (Ixx,Ixx,Irr),
    power_off_drag="./data/powerOffDragCurve.CSV",
    power_on_drag="./data/powerOnDragCurve.CSV",
    coordinate_system_orientation="tail_to_nose",
)

strath_with_payload.add_motor(Pro54K1440, position=-(0.71-0.075))

nosecone = strath_with_payload.add_nose(
    length=0.3,
    kind="vonKarman",
    position=centre_of_mass
)

fins = strath_with_payload.add_trapezoidal_fins(
    n=4,
    root_chord=16/ 100,
    tip_chord=6 / 100,
    span=6.3 / 100,
    position=-(0.71-0.16),      #verify
    cant_angle=0
)

buttons = strath_with_payload.set_rail_buttons(
    upper_button_position=0.2,
    lower_button_position=-0.2,
    angular_position=45
)


tail = strath_with_payload.add_tail(
    top_radius=8 / 200,
    bottom_radius=5.5 / 200, #verify
    length=7.5 / 100, #verify
    position=-0.71, #verify
)


drogue = strath_without_payload.add_parachute(
    name="drogue",
    cd_s=0.8 * 3.1415926 * (drogue_diameter/2)**2,
    trigger="apogee",
    
)

main = strath_without_payload.add_parachute(
    name="main",
    cd_s=0.8 * 3.1415926 * (main_diameter/2)**2,
    trigger=500,

)

### CanSat Setup ###

cansat = Rocket(
    radius = 76 / 2000,
    mass = payload_mass,
    inertia = (0.1, 0.1, 0.001),
    power_off_drag = 0.5,
    power_on_drag = 0.5,
    center_of_mass_without_motor = 0
)

cansast_chute = cansat.add_parachute(
    name = "cansat parachute",
    cd_s = 0.8 * 3.1415926 * (0.40/2)**2,
    trigger = "apogee",
    sampling_rate = 105,
    lag = 1.5,
)

number_of_speeds = 6 # add one to desired number
max_speed = 10
speed_increment = number_of_speeds / max_speed

number_of_angles = 5
max_angle = 20
angle_increment = number_of_angles / max_angle

vehicle_impact_matrix = np.zeros((number_of_speeds, number_of_angles))
payload_impact_matrix = np.zeros((number_of_speeds, number_of_angles))

for i in tqdm(range(number_of_speeds)):
    for j in tqdm(range(number_of_angles), leave = False):

        wind = i*speed_increment
        angle = j*angle_increment

        env.set_atmospheric_model(
            # type="Forecast", file="GFS"
            type="custom_atmosphere",
            
            pressure=None,
            temperature=300,
            wind_u= wind, #Positive for East, Negative for West
            #wind_v = [], #Positive for North, Negative for South
        )

        # Simulate ascent with payload

        ascent = Flight(
            rocket=strath_with_payload,
            name="Ascent",
            environment=env,
            rail_length=2,
            inclination=90 - angle,
            heading=270,
            terminate_on_apogee = True,
        )

        # Simulate descent for vehicle without payload

        descent = Flight(
            rocket=strath_without_payload,
            name="Rocket Descent",
            environment=env,
            rail_length=2,
            initial_solution=ascent,
        )

        # Save impact distances from simulation in a matrix - will store in CSV later

        vehicle_impact_distance = (descent.x_impact**2 + descent.y_impact**2)**0.5
        vehicle_impact_matrix[i][j] = vehicle_impact_distance

        payload_flight = Flight(
            rocket = cansat,
            name="Payload Descent",
            environment = env,
            rail_length=2,
            initial_solution = ascent,
        )

        payload_impact_distance = (payload_flight.x_impact**2+payload_flight.y_impact**2)**0.5
        payload_impact_matrix[i][j] = payload_impact_distance

with open('vehicle_impact.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Wind Speed", 0, 5, 10, 15, 20])
    for i in range(len(vehicle_impact_matrix)):
        csvwriter.writerow([i*max_speed/number_of_speeds, vehicle_impact_matrix[i][0], vehicle_impact_matrix[i][1], vehicle_impact_matrix[i][2], vehicle_impact_matrix[i][3], vehicle_impact_matrix[i][4]] )

with open('payload_impact.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Wind Speed", 0, 5, 10, 15, 20])
    for i in range(len(payload_impact_matrix)):
        csvwriter.writerow([i*max_speed/number_of_speeds, payload_impact_matrix[i][0], payload_impact_matrix[i][1], payload_impact_matrix[i][2], payload_impact_matrix[i][3], payload_impact_matrix[i][4]] )


### Tkinter time!!
window_height = 720
window_width = round(window_height * 16/9)

payload_impact_window = tk.Tk()
geom = str(window_width) + "x" + str(window_height)
payload_impact_window.geometry(geom)



#transpose matrix for better display optimisation
payload_impact_matrix_transposed = np.transpose(payload_impact_matrix)

#remember it's transposed for label settings
label_width = round(window_width / (number_of_speeds+1))
label_height = round(window_height / (number_of_angles+1))

payload_labels = np.zeros((len(payload_impact_matrix_transposed)+1, len(payload_impact_matrix_transposed[0])+1), dtype=tk.Label)

#blank cell in top left
payload_labels[0][0] = tk.Label(payload_impact_window, bg = "black", width = label_width, height = label_height, bd=2, relief = "solid")

#wind speeds
for j in range(number_of_speeds):
    textvar = tk.StringVar()
    textvar.set(str(j*speed_increment) + " m/s")
    payload_labels[0][j+1] = tk.Label(payload_impact_window, textvariable = textvar, bg = 'white', fg = 'black', width = label_width, height = label_height, bd=2, relief = "solid")

#launch angles
for i in range(number_of_angles):
    textvar = tk.StringVar()
    textvar.set(str(i*angle_increment) + "°")
    payload_labels[i+1][0] = tk.Label(payload_impact_window, textvariable = textvar, font=("Arial",1), bg = 'white', fg = 'black', width = label_width, height = label_height, bd=2, relief = "solid")


#contents
for i in range(len(payload_impact_matrix_transposed)):
    for j in range(len(payload_impact_matrix_transposed[0])):
        # bg_colour = ""
        if payload_impact_matrix_transposed[i][j] > max_drift:
            bg_colour = "red"
        elif payload_impact_matrix_transposed[i][j] > max_drift/2:
            bg_colour = "yellow"
        else:
            bg_colour = "green"

        textvar = tk.StringVar()
        textvar.set(str(round(payload_impact_matrix_transposed[i][j])))
        payload_labels[i+1][j+1] = tk.Label(payload_impact_window, textvariable = textvar, font = ("Arial", 1), fg = "black", bg = bg_colour, width = label_width, height = label_height, bd=2, relief = "solid")

print(payload_labels)
for i in range(len(payload_impact_matrix_transposed)):
    for j in range(len(payload_impact_matrix_transposed[0])):
        payload_labels[i][j].grid(row = j, column = i, sticky = "")

payload_impact_window.mainloop()
payload_impact_window.update()