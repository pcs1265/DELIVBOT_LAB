void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.flush();

  pinMode(13, OUTPUT);
  
  pinMode(8, OUTPUT);
  digitalWrite(8, HIGH);
  pinMode(9, OUTPUT);
  digitalWrite(9, HIGH);
  pinMode(10, OUTPUT);
  digitalWrite(10, HIGH);

  pinMode(5, INPUT);
  pinMode(6, INPUT);
  pinMode(7, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:

}

void serialEvent(){
  char command = Serial.read();
  if(command == 's'){
    char status[4] = "000";
    //단락일 때 0 출력 
    status[0] = digitalRead(5) + '0';
    status[1] = digitalRead(6) + '0';
    status[2] = digitalRead(7) + '0';    

    Serial.println(status);
    
  }else if(command >= '1' && command <= '3'){
    int box_num = command - '1';
    digitalWrite(13, LOW);
    delay(1000);
    digitalWrite(13, HIGH);
    Serial.println(box_num);
  }else{
    Serial.println('e');
  }
}