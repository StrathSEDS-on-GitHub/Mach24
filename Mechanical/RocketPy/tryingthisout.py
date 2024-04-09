from rocketpy import Environment, SolidMotor, Rocket, Flight
import datetime

# Initialise MACC LaunchPad
env = Environment(latitude=55.433982, longitude= -5.696031, elevation=0)

launchday = datetime.date.today() + datetime.timedelta(days=1)

env.set_date( (launchday.year, launchday.month, launchday.day, 9) )

env.set_atmospheric_model(type="Forecast", file="GFS")

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
dry_mass = 5.978
radius = 8 / 200
Ixx = 0.25 * dry_mass * radius**2 + 1/12 * dry_mass * length**2
Irr = 0.5 * dry_mass * radius**2
main_diameter = 66 / 100
drogue_diameter = 38.1 / 100


Pro54K1440 = SolidMotor(
    thrust_source="./data/Cesaroni_K1440.eng",     #import
    dry_mass=0.7302,
    dry_inertia=(Ixx,Ixx,Irr),                    #find
    nozzle_radius=15 / 1000,                 #find
    grain_number=6,
    grain_density=1.129,     #find
    grain_outer_radius=54 / 2000,            #find
    grain_initial_inner_radius=15 / 1000,    #find
    grain_initial_height=142 / 1000,        #find
    grain_separation=5 / 1000,              #find
    grains_center_of_mass_position=0.3,       #find
    center_of_dry_mass_position=0.3,          #find
    nozzle_position=0,
    burn_time=1.65,
    throat_radius=5 / 1000,
    coordinate_system_orientation="nozzle_to_combustion_chamber"
)

strath = Rocket(
    radius=80 / 2000,
    mass=5.978,
    inertia= (0,0,0),
    power_off_drag="./data/powerOffDragCurve.CSV",
    power_on_drag="./data/powerOnDragCurve.CSV",
    center_of_mass_without_motor=0,
    coordinate_system_orientation="tail_to_nose",
)

strath.add_motor(Pro54K1440, position=-(0.71-0.075))

nosecone = strath.add_nose(
    length=0.3,
    kind="vonKarman",
    position=centre_of_mass
)

fins = strath.add_trapezoidal_fins(
    n=4,
    root_chord=16/ 100,
    tip_chord=6 / 100,
    span=6.3 / 100,
    position=-(0.71-0.16),      #verify
    cant_angle=0
)

buttons = strath.set_rail_buttons(
    upper_button_position=0.2,
    lower_button_position=-0.2,
    angular_position=45
)

drogue = strath.add_parachute(
    name="drogue",
    cd_s=0.8 * 3.1415926 * drogue_diameter,
    trigger="apogee",
    
)

main = strath.add_parachute(
    name="main",
    cd_s=0.8 * 3.1415926 * main_diameter,
    trigger=300,

)

tail = strath.add_tail(
    top_radius=8 / 200,
    bottom_radius=5.5 / 200, #verify
    length=7.5 / 100, #verify
    position=-0.71 #verify
)

#rocket.all_info()

print("\n Rocket Drawing:\n ____________")
strath.draw()


#print("Setting Up Test Flight")
test_flight = Flight(
    rocket=strath,
    environment=env,
    rail_length=2,
    inclination=90,
    heading=0,
)
#print("Test Flight Info")
test_flight.plots.trajectory_3d()
test_flight.export_kml(
    file_name="trajectory.kml",
    extrude=True,
    altitude_mode="relative_to_ground",
)