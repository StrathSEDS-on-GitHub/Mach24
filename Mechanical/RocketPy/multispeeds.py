from rocketpy import Environment, SolidMotor, Rocket, Flight
from rocketpy.plots.compare import CompareFlights
import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import random

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
centre_of_mass = 1.21

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

payload_mass = 1.006
vehicle_mass = 5.658

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

number_of_speeds = 11 # add one to desired number
max_speed = 10
speed_increment = max_speed / (number_of_speeds-1)

number_of_angles = 5
max_angle = 20
angle_increment = max_angle/(number_of_angles-1)
print(angle_increment)

vehicle_impact_matrix = np.zeros((number_of_speeds, number_of_angles))
payload_impact_matrix = np.zeros((number_of_speeds, number_of_angles))
ascents = np.zeros((number_of_speeds, number_of_angles), dtype=Flight)
descents = np.zeros((number_of_speeds, number_of_angles), dtype=Flight)
cansats = np.zeros((number_of_speeds, number_of_angles), dtype=Flight)

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

        ascents[i][j] = Flight(
            rocket=strath_with_payload,
            name="Ascent",
            environment=env,
            rail_length=2,
            inclination=90 - angle,
            heading=270,
            terminate_on_apogee = True,
        )

        # Simulate descent for vehicle without payload

        descents[i][j] = Flight(
            rocket=strath_without_payload,
            name="Rocket Descent",
            environment=env,
            rail_length=2,
            initial_solution=ascents[i][j],
        )

        # Save impact distances from simulation in a matrix - will store in CSV later

        vehicle_impact_distance = (descents[i][j].x_impact**2 + descents[i][j].y_impact**2)**0.5
        vehicle_impact_matrix[i][j] = vehicle_impact_distance

        # Do the same for payload descent

        cansats[i][j] = Flight(
            rocket = cansat,
            name="Payload Descent",
            environment = env,
            rail_length=2,
            initial_solution = ascents[i][j],
        )

        payload_impact_distance = (cansats[i][j].x_impact**2+cansats[i][j].y_impact**2)**0.5
        payload_impact_matrix[i][j] = payload_impact_distance

with open('vehicle_impact.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    for i in range(len(vehicle_impact_matrix)):
        csvwriter.writerow([vehicle_impact_matrix[i][0], vehicle_impact_matrix[i][1], vehicle_impact_matrix[i][2], vehicle_impact_matrix[i][3], vehicle_impact_matrix[i][4]] )

with open('payload_impact.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    for i in range(len(payload_impact_matrix)):
        csvwriter.writerow([payload_impact_matrix[i][0], payload_impact_matrix[i][1], payload_impact_matrix[i][2], payload_impact_matrix[i][3], payload_impact_matrix[i][4]] )

payload_impact_matrix = np.array(payload_impact_matrix)
vehicle_impact_matrix = np.array(vehicle_impact_matrix)

def get_color(value, min_value, max_value):
    # Normalize the value to be between 0 and 1
    normalized_value = (value - min_value) / (max_value - min_value)
    # Interpolate color from green to red
    red = int(normalized_value * 255)
    green = int((1 - normalized_value) * 255)
    color = f'#{red:02x}{green:02x}00'
    return color

def get_color_boolean(value):
    return '#00FF00' if value else '#FF0000'  # Green for True, Red for False

def display_2d_array(array, title):
    array = np.transpose(array)  # Transpose the array
    
    rows = len(array)
    cols = len(array[0]) if rows > 0 else 0

    # Find min and max values in the array
    min_value = np.min(array)
    max_value = np.max(array)

    fig, ax = plt.subplots()
    im = ax.imshow(array, cmap='RdYlGn_r', vmin=min_value, vmax=max_value)  # Invert colormap with '_r'

    # Create wind speed tick labels
    speeds = [i * speed_increment for i in range(cols)]
    plt.xticks(np.arange(cols), speeds)

    # Create launch angle tick labels
    angles = [i * angle_increment for i in range(rows)]
    plt.yticks(np.arange(rows), angles)

    # Loop over data dimensions and create text annotations
    for i in range(rows):
        for j in range(cols):
            value = abs(array[i, j])
            color = get_color(value, min_value, max_value)
            if value > max_drift:
                text_color = "white"
            else:
                text_color = "black"
            ax.text(j, i, f'{str(round(array[i, j]))}m', ha='center', va='center', color=text_color)

    ax.set_title(title)
    plt.xlabel('Wind Speed (m/s)')  # Update x-axis label
    plt.ylabel('Launch Angle (°)')  # Update y-axis label
    plt.show()

def display_2d_boolean_array(array, title):
    array = np.transpose(array)  # Transpose the array
    
    rows = len(array)
    cols = len(array[0]) if rows > 0 else 0

    fig, ax = plt.subplots()
    im = ax.imshow(array, cmap='RdYlGn', vmin=0, vmax=1)  # Use 0 and 1 for boolean colormap

    # Create wind speed tick labels
    speeds = [i * speed_increment for i in range(cols)]
    plt.xticks(np.arange(cols), speeds)

    # Create launch angle tick labels
    angles = [i * angle_increment for i in range(rows)]
    plt.yticks(np.arange(rows), angles)

    # Loop over data dimensions and create text annotations
    for i in range(rows):
        for j in range(cols):
            value = array[i, j]
            text_color = "white" if value else "black"
            ax.text(j, i, 'Legal' if value else 'Illegal', ha='center', va='center', color=text_color)
            
    ax.set_title(title)
    plt.xlabel('Wind Speed (m/s)')
    plt.ylabel('Launch Angle (°)')
    plt.show()

# Main function
display_2d_array(payload_impact_matrix, 'Payload Impact')
display_2d_array(vehicle_impact_matrix, 'Vehicle Impact')
# display_2d_array(payload_impact_matrix)


# Initializing the impact_boolean_matrix with the same shape as payload_impact_matrix
impact_boolean_matrix = np.zeros_like(payload_impact_matrix, dtype=bool)

# Populating the impact_boolean_matrix
for i in range(payload_impact_matrix.shape[0]):
    for j in range(payload_impact_matrix.shape[1]):
        if payload_impact_matrix[i, j] < max_drift and vehicle_impact_matrix[i, j] < max_drift:
            impact_boolean_matrix[i, j] = True
        else:
            impact_boolean_matrix[i, j] = False

# Convert to numpy array for better compatibility with display function
impact_boolean_matrix = np.array(impact_boolean_matrix)

# Main function
display_2d_boolean_array(impact_boolean_matrix, 'Is this launch legal?')

plotted_windspeed=random.randint(0,number_of_speeds-1)
plotted_angle=random.randint(0,number_of_angles-1)

print("Plotting data for flight at " + str(plotted_windspeed*speed_increment) + " m/s and " + str(plotted_angle*angle_increment) + " degrees")
descents[plotted_windspeed][plotted_angle].plots.linear_kinematics_data()