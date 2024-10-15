Table star_data;

void setup() {
  size(1000,1000,P3D);
  smooth();
  frameRate(100);
  background(0);

  star_data = loadTable("../../scaled_data.csv", "header");

}

void draw() {
  background(0);
  translate(width/2, height/2, -100);

  rotateY(PI * frameCount / 1000);
  rotateX(PI * frameCount / 5000);

  noStroke();
  fill(0,100,100);
  directionalLight(200, 200, 200, -1, 0, 0);
  sphere(20);

  for (int i = 0; i < star_data.getRowCount()/4; i++) {
    plotPoint(star_data.getFloat(i, "ra"), star_data.getFloat(i, "dec"), star_data.getFloat(i, "sy_dist") * 10000);
  }
}

// rotate to match RA and DEC, then translate for distance 
void plotPoint(float ra, float dec, float dist) {
  pushMatrix();
  rotateY(radians(ra));
  rotateZ(radians(dec));
  translate(dist, 0, 0);
  noFill();
  stroke(255);
  sphere(random(1.0,2.0));
  popMatrix();

}