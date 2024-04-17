clear
%% Input variables of rocket dimensions in mm

%diameter at base of nosecone
nose_base_diameter = 131;

%total length of nosecone
nose_length = 350;

%nose shape parameter, find out more online if you are curious
shape_parameter = 0;

%mm increment for points on x-axis
increment = 1;

%x-axis value to start from
step_value = 0;

%% Calculating setup variables

%R/sqrt*pi
nose_base_radius = nose_base_diameter/2;
R_div_sqrt_pi = nose_base_radius/sqrt(pi);

%number of x-axis points
number_x = nose_length/increment;

%% Calculating y-axis values for x-axis points

%for loop to find each axis value for points
%+1 becuase MATLAB, fuck you.
for i=1:number_x +1
    %find values for x-axis
    M(i,1) = step_value;

    %values for z-axis will be zero
    M(i,3) = 0;

    %find variable theta to simplify equation typing
    theta = acos(1-(2*M(i,1)/nose_length));
    
    %find values for y-axis
    M(i,2) = R_div_sqrt_pi * sqrt(theta - ((sin(2*theta))/2)+shape_parameter*(sin(theta)^3));

    %Update counter for next iteration
    step_value = step_value + increment;
end

%% Export as .txt

writematrix(M,'vk_nose_data')
disp("check your folder for a 'nosy' surprise")