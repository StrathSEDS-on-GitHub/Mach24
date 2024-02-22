clear
format("long")
%% Import Metric Flight Data
flight_data = readmatrix("Flight Data.csv");
% import forces in Newtons [N]
flight_data(:,8:11) = flight_data(:,8:11)*4.448222; %lb2N
% import distances in meters [m]
flight_data(:,11:12) = flight_data(:,11:12)*0.0254; %in2m
flight_data(:,23:24) = flight_data(:,23:24)*0.3048; %ft2m
% import acceleration data in meters per square seconds [m/s^2]
flight_data(:,15:17) = flight_data(:,15:17)*0.3048; %[ft/s^2]2[m/s^2]
% import velocity data in m/s
flight_data(:,18:20) = flight_data(:,18:20)*0.3048; %ft/s2m/s
%% Import High V Drag Data
imported_drag_data = readmatrix("Mach vs CD FR.csv");
decimal_place = 6;
x = linspace(0,1.1,10^(decimal_place-1)*(11)+1);
interp_drag_data = zeros(length(x),size(imported_drag_data,2));
interp_drag_data(:,1) = x;
interp_drag_data(:,2) = interp1(imported_drag_data(:,1),imported_drag_data(:,2),x);
interp_drag_data(:,3) = interp1(imported_drag_data(:,1),imported_drag_data(:,3),x);
interp_drag_data(:,4) = interp1(imported_drag_data(:,1),imported_drag_data(:,4),x);
%% Determine where to stop
[minM, I] = min(flight_data(2:end,4));
time_to_apogee = flight_data(I,1);
%% Find lowest summed drag coefficient
rocket_drag_5_5 = sum(interp1(interp_drag_data(:,1), interp_drag_data(:,2), flight_data(1:I,4)));
rocket_drag_6 = sum(interp1(interp_drag_data(:,1), interp_drag_data(:,3), flight_data(1:I,4)));
rocket_drag_6_5 = sum(interp1(interp_drag_data(:,1), interp_drag_data(:,4), flight_data(1:I,4)));
%%