%main script 

[ardIn, ardOut] = setupSerialCommunication();
% Now you can use `ardIn` and `ardOut` for communication
% For example:
% sensorValue = fscanf(ardIn, '%f');  % Read a value from the Arduino
% fprintf(ardOut, '1');  % Send a command to the Arduin