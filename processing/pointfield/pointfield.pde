float x,y,z,rot; //<>//
float change = 1;
int COUNT = 500;
int DIMENSION = 1000;
float[][] list3d = new float[COUNT][3];


void setup() {
  size(1000,1000,P3D);
  smooth();
  frameRate(30);
  background(0);

  for (int i=0; i < COUNT; i++) {
    for(int j=0; j < 3; j++) {
      list3d[i][j] = random(-DIMENSION, DIMENSION);
    }
  }
    
  //for (int i=0; i < COUNT-1; i++) {
  //  drawPoint(list3d[i]);
  //  i = i+1;
  //}
}

void draw() {

  //rotateX(PI / 6);
  //rotateY(PI / 6);
  
  background(0);
  translate(width/2, height/2, -200);

  
  //float[][] list3d = new float[COUNT][3];
  //for (int i=0; i < COUNT; i++) {
  //  for(int j=0; j < 3; j++) {
  //    list3d[i][j] = random(600);
  //  }
  //}
  rotateY(PI * frameCount / 1000);
  rotateX(PI * frameCount / 5000);
  
  noStroke();
  fill(0,100,100);
  directionalLight(200, 200, 200, -1, 0, 0);
  sphere(66);

  for (int i=0; i < COUNT-1; i++) { //<>//
    drawPoint(list3d[i]);
    i = i+1;
  }
}

void drawPoint(float[] list) {
  pushMatrix();
  translate(list[0], list[1], list[2]);
  noFill();
  stroke(255);
  sphere(random(1.0,2.0));
  popMatrix();
}
