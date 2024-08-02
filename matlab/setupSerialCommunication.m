function [ardIn, ardOut] = setupSerialCommunication()
    % Get the system name (hostname)
    [status, systName] = system('hostname');
    systName = strtrim(systName);  % Remove any trailing newline characters or spaces
    
    % Define COM ports based on the hostname
    switch systName
        case 'dhcp-10-29-159-123.dyn.MIT.EDU'
            portIn = '/dev/tty.usbmodem11301';
            portOut = '/dev/tty.usbmodem11301';
        case 'TP3Vstim'
            portIn = 'COM3';
            portOut = 'COM4';
        otherwise
            % For macOS, the port names are usually /dev/tty.usbmodemXXXX
            % Adjust according to your specific setup
            if ismac
                portIn = '/dev/tty.usbmodem11301';
                portOut = '/dev/tty.usbmodem11301';
            else
                error('Unknown system name: %s', systName);
            end
    end

    % Clean up any existing serial objects
    if ~isempty(instrfind)
        fclose(instrfind);
        delete(instrfind);
    end

    % Create and configure serial objects
    ardIn = serial(portIn);
    ardIn.InputBufferSize = 50000;
    ardIn.BaudRate = 9600;
    ardIn.Timeout = 2;
    %can replace with single line? ard = serial(port, 'BaudRate', 9600, 'Timeout', 10);
    % Open the serial communication ports
    fopen(ardIn);
    
    ardOut = nan;
end

% Now you can use `ardIn` and `ardOut` for communication
% For example:
% sensorValue = fscanf(ardIn, '%f');  % Read a value from the Arduino
% fprintf(ardOut, '1');  % Send a command to the Arduino
