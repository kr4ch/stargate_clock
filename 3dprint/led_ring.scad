// Mounting bracket for LED stripe

$fn=1024;

height = 2;
// Outer diameter 17.3 cm, Width 2 cm
outer_r = 84;
inner_r = 68;

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
