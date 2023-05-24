// Mounting bracket for LED stripe

$fn=1024;

height = 8;
// Diameter 15.4 to 15.5 cm
outer_r = 78;
inner_r = 77;

translate([0,0,0]) {
    difference() {
        // Outer cylinder
        cylinder(height,outer_r,outer_r);

        // Inner cylinder 
        translate([0,0,-5]) {
            cylinder(height+10,inner_r,inner_r);
        }
    }
}

echo(version=version());
