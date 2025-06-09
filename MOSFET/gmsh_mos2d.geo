device_width =     1000.0e-7;
gate_width =       500.0e-7;
diffusion_width =  0.4;

air_thickness =          1e-7;
gate_oxide_thickness =   5e-7;
control_gate_thickness = 100e-7;
device_thickness =       1000e-7;
diffusion_thickness =    100e-7;

epsilon = 5e-7;
reduction = 10;
super_epsilon = 2.5e-7;
super_reduction = 10;


y_diffusion_spacing =    1e-6;
x_diffusion_spacing =  1e-5;

x_bulk_left =    0.0;
x_bulk_right =   x_bulk_left + device_width;
x_center =       0.5 * (x_bulk_left + x_bulk_right);
x_gate_left =    x_center - 0.5 * (gate_width);
x_gate_right =   x_center + 0.5 * (gate_width);
x_device_left =  x_bulk_left - air_thickness;
x_device_right = x_bulk_right + air_thickness;

y_bulk_top =       0.0;
y_gate_oxide_top = y_bulk_top - gate_oxide_thickness;
y_gate_top = y_gate_oxide_top - control_gate_thickness;
y_bulk_bottom =    y_bulk_top + device_thickness;

//// Bulk
Point(1) = {x_bulk_left, y_bulk_top, 0, x_diffusion_spacing};
Point(15) = {x_gate_left-epsilon, y_bulk_top, 0, x_diffusion_spacing};
Point(2) = {x_gate_left, y_bulk_top, 0, x_diffusion_spacing/reduction};
Point(3) = {x_gate_right, y_bulk_top, 0, x_diffusion_spacing/reduction};
Point(16) = {x_gate_right+epsilon, y_bulk_top, 0, x_diffusion_spacing};
Point(4) = {x_bulk_right, y_bulk_top, 0, x_diffusion_spacing};
Point(5) = {x_bulk_right, y_bulk_bottom, 0, x_diffusion_spacing};
Point(6) = {x_bulk_left, y_bulk_bottom,0, x_diffusion_spacing};

// Gate Oxide
Point(11) = {x_gate_left, y_gate_oxide_top, 0, x_diffusion_spacing/super_reduction};
Point(12) = {x_gate_right, y_gate_oxide_top, 0, x_diffusion_spacing/super_reduction};

// Control Gate
Point(13) = {x_gate_left, y_gate_top, 0, x_diffusion_spacing};
Point(14) = {x_gate_right, y_gate_top, 0, x_diffusion_spacing};


// bulk
Line(1) = {1, 15};
Line(30) = {15, 2};
Line(2) = {2, 3};
Line(32) = {3, 16};
Line(3) = {16, 4};
Line(4) = {4, 5};
Line(5) = {5, 6};
Line(6) = {6, 1};
Line Loop(7) = {1, 30, 2, 32, 3, 4, 5, 6};
Plane Surface(8) = {7};

// gate oxide
Line(9) = {2, 11};
Line(10) = {11, 12};
Line(11) = {12, 3};
Line Loop(12) = {9, 10, 11, -2};
Plane Surface(13) = {12};

// control gate
Line(14) = {11,13};
Line(15) = {13,14};
Line(16) = {14,12};
Line Loop(17) = {14,15,16,-10};
Plane Surface(18) = {17};

// mesh from body contact to oxide interface
Field[1] = Attractor;
Field[1].EdgesList = {1,2,3};

Field[2] = Threshold;
Field[2].IField = 1;
Field[2].LcMin = x_diffusion_spacing/10;
Field[2].LcMax = x_diffusion_spacing/2;
Field[2].DistMin = 1.5 * diffusion_thickness;
Field[2].DistMax = 5 * diffusion_thickness;

// Interface at bulk and oxide
Field[3] = Box;
Field[3].VIn = x_diffusion_spacing/200;          // Small elements in this region
Field[3].VOut = x_diffusion_spacing;         // Larger elements outside
Field[3].XMin = x_gate_left-(5*epsilon);
Field[3].XMax = x_gate_right+(5*epsilon);
Field[3].YMin = y_bulk_top-super_epsilon;
Field[3].YMax = y_bulk_top+super_epsilon;

// Interface at nitride top and gate oxide bottom
Field[4] = Box;
Field[4].VIn = x_diffusion_spacing/200;          // Small elements in this region
Field[4].VOut = x_diffusion_spacing;         // Larger elements outside
Field[4].XMin = x_gate_left;
Field[4].XMax = x_gate_right;
Field[4].YMin = y_gate_oxide_top-(super_epsilon);
Field[4].YMax = y_gate_oxide_top+super_epsilon;

// left diffusion vertical
Field[5] = Box;
Field[5].VIn = x_diffusion_spacing/50;          // Small elements in this region
Field[5].VOut = x_diffusion_spacing;         // Larger elements outside
Field[5].XMin = x_gate_left-(2*epsilon);
Field[5].XMax = x_gate_left+(2*epsilon);
Field[5].YMin = 0.0;
Field[5].YMax = diffusion_thickness;

// left diffusion horizontal
Field[6] = Box;
Field[6].VIn = x_diffusion_spacing/50;          // Small elements in this region
Field[6].VOut = x_diffusion_spacing;         // Larger elements outside
Field[6].XMin = 0.0;
Field[6].XMax = x_gate_left;
Field[6].YMin = diffusion_thickness-(2*epsilon);
Field[6].YMax = diffusion_thickness+(2*epsilon);

// right diffusion vertical
Field[7] = Box;
Field[7].VIn = x_diffusion_spacing/50;          // Small elements in this region
Field[7].VOut = x_diffusion_spacing;         // Larger elements outside
Field[7].XMin = x_gate_right-(2*epsilon);
Field[7].XMax = x_gate_right+(2*epsilon);
Field[7].YMin = 0.0;
Field[7].YMax = diffusion_thickness;

// right diffusion horizontal
Field[8] = Box;
Field[8].VIn = x_diffusion_spacing/50;          // Small elements in this region
Field[8].VOut = x_diffusion_spacing;         // Larger elements outside
Field[8].XMin = x_gate_right;
Field[8].XMax = device_width;
Field[8].YMin = diffusion_thickness-(2*epsilon);
Field[8].YMax = diffusion_thickness+(2*epsilon);


// Use minimum of all the fields as the background field
Field[11] = Min;
Field[11].FieldsList = {2, 3, 4, 5, 6, 7, 8};
Background Field = 11;


// Don't extend the elements sizes from the boundary inside the domain
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.Algorithm=5; /*Delaunay*/
//Mesh.RandomFactor=1e-5; /*perturbation*/
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.CharacteristicLengthFromCurvature = 0;
Mesh.CharacteristicLengthExtendFromBoundary = 0;

Physical Line("gate_oxide_interface") = {10};
Physical Line("bulk_oxide_interface") = {2};

Physical Line("gate_contact") = {15};
Physical Line("source_contact") = {1};
Physical Line("drain_contact") = {3};
Physical Line("body_contact") = {5};

Physical Surface("bulk") = {8};
Physical Surface("oxide") = {13};
Physical Surface("gate") = {18};

