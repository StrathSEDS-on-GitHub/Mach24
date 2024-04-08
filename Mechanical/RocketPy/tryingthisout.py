from rocketpy import Environment, SolidMotor, Rocket, Flight
import datetime

# Initialise MACC LaunchPad
env = Environment(latitude=55.433316, longitude= -5.699037, elevation=0)

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



Pro54K1440 = SolidMotor(
    thrust_source=1440,  #"../data/Cesaroni_K1440.eng",     #import
    dry_mass=0.7302,
    dry_inertia=(0,0,0),                    #find
    nozzle_radius=0 / 1000,                 #find
    grain_number=6,
    grain_density=1.129,     #find
    grain_outer_radius=33 / 1000,            #find
    grain_initial_inner_radius=15 / 1000,    #find
    grain_initial_height=120 / 1000,        #find
    grain_separation=5 / 1000,              #find
    grains_center_of_mass_position=0.3,       #find
    center_of_dry_mass_position=0.3,          #find
    nozzle_position=0,
    burn_time=1.65,
    throat_radius=0 / 1000,                 #find
    coordinate_system_orientation="nozzle_to_combustion_chamber"
)

rocket = Rocket(
    radius=80 / 1000,
    mass=5.978,
    inertia= (0,0,0),                       #find
    power_off_drag="../data/powerOffDragCurve.CSV",
    power_on_drag="../data/powerOnDragCurve.CSV",
    center_of_mass_without_motor=0,
    coordinate_system_orientation="tail_to_nose",
)

nosecone = rocket.add_nose(
    length=0.3,
    kind="vonKarman",
    position=1.02              #verify
)

fins = rocket.add_trapezoidal_fins(
    n=4,
    root_chord=16/ 100,
    tip_chord=6 / 100,
    span=6.3 / 100,
    position=-0.48,      #verify
    cant_angle=0
)

rocket.all_info()