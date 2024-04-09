from rocketpy import Environment, SolidMotor, Rocket, Flight
from rocketpy.plots.compare import CompareFlights
import datetime

# Initialise MACC LaunchPad
env = Environment(latitude=55.433982, longitude= -5.696031, elevation=0)

launchday = datetime.date.today() + datetime.timedelta(days=1)

env.set_date( (launchday.year, launchday.month, launchday.day, 9) )

env.set_atmospheric_model(
    type="Forecast", file="GFS"
    
    
    # pressure=None,
    # temperature=300,
    # wind_u=[(0,5), (1000,10)], #Positive for East, Negative for West
    # wind_v=[(0,-2), (500,3), (1600,2)], #Positive for North, Negative for South
)

#env.info()

K1440ThurstCurve = [
   0.015, 893.963,
   0.026, 1563.355,
   0.030, 1671.321,
   0.035, 1718.827,
   0.047, 1667.003,
   0.063, 1628.135,
   0.100, 1671.321,
   0.200, 1701.552,
   0.300, 1705.871,
   0.400, 1710.189,
   0.500, 1705.871,
   0.600, 1701.552,
   0.700, 1684.277,
   0.800, 1658.366,
   0.900, 1619.498,
   1.000, 1597.904,
   1.100, 1546.080,
   1.221, 1498.575,
   1.300, 1144.445,
   1.337, 1062.39,
   1.400, 1058.072,
   1.447, 1053.753,
   1.500, 716.898,
   1.543, 578.700,
   1.600, 306.625,
   1.644, 125.241,
   1.700, 0.0]

#Info from OR
length = 1.73
centre_of_mass = 1.02




Pro54K1440 = SolidMotor(
    thrust_source="./data/Cesaroni_K1440.eng",     #import
    dry_mass=0.7302,
    dry_inertia=(0,0,0),
    nozzle_radius=15 / 1000,                #find
    grain_number=6,
    grain_density=1.129,                    #find
    grain_outer_radius=54 / 2000,           #find
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

payload_mass = 1
dry_mass = 5.978

vehicle_mass = dry_mass - payload_mass

radius = 8 / 200
Ixx = 0.25 * dry_mass * radius**2 + 1/12 * dry_mass * length**2
Irr = 0.5 * dry_mass * radius**2
main_diameter = 66 / 100
drogue_diameter = 38.1 / 100

strath_with_payload = Rocket(
    radius=80 / 2000,
    mass=vehicle_mass + payload_mass,
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
    trigger=300,

)

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
    cd_s = 0.8 * 3.1415926 * (0.15/2)**2,
    trigger = "apogee",
    sampling_rate = 105,
    lag = 1.5,
)

stage_one = Flight(
    rocket=strath_with_payload,
    environment=env,
    rail_length=2,
    inclination=90,
    heading=0,
    terminate_on_apogee = True,
)

stage_two = Flight(
    rocket=strath_without_payload,
    environment=env,
    rail_length=2,
    initial_solution=stage_one,
)

payload_flight = Flight(
    rocket = cansat,
    environment = env,
    rail_length=2,
    initial_solution = stage_one,
)
#print("Test Flight Info")
# test_flight.plots.trajectory_3d()
# test_flight.export_kml(
#     file_name="trajectory.kml",
#     extrude=True,
#     altitude_mode="relative_to_ground",
# )

comparison = CompareFlights(
    [stage_one, stage_two, payload_flight]
)

#comparison.trajectories_3d(legend=True)

stage_one.export_kml(
    file_name="ascent.kml",
    extrude=True,
    altitude_mode="relative_to_ground"
)
stage_two.export_kml(
    file_name="descent.kml",
    extrude=True,
    altitude_mode="relative_to_ground"
)
payload_flight.export_kml(
    file_name="payload.kml",
    extrude=True,
    altitude_mode="relative_to_ground"
)