import nidaqmx
import time

def send_digital_trigger(card_id='Dev1', port_line='port0/line1', microscope='2P3', pulse_duration=0.001):
    """Sends a digital trigger pulse (high then low) to the specified DAQ channel.
    
    Args:
        card_id (str): The ID of the DAQ device (e.g., 'Dev1').
        port_line (str): The port and line to which the signal is sent (e.g., 'port0/line1').
        microscope (str): Name of the microscope for channel naming.
        pulse_duration (float): The duration (in seconds) for which the pulse stays high.
    """
    try:
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan(f'{card_id}/{port_line}', 
                                       name_to_assign_to_lines=f'trigger_{microscope}')
            
            task.write(True)
            time.sleep(pulse_duration)
            task.write(False)
            
        print(f"Digital trigger sent to {card_id}/{port_line} for {pulse_duration} seconds.")
    
    except Exception as e:
        print(f"Error sending digital trigger: {e}")

def send_analog_trigger(card_id='Dev1', channel='ao0', microscope='2P3', pulse_duration=0.001):
    """Sends an analog trigger pulse (5V then 0V) to the specified DAQ channel.
    
    Args:
        card_id (str): The ID of the DAQ device (e.g., 'Dev1').
        channel (str): The analog output channel (e.g., 'ao0').
        microscope (str): Name of the microscope for channel naming.
        pulse_duration (float): The duration (in seconds) for which the pulse stays high.
    """
    try:
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(f'{card_id}/{channel}', 
                                               name_to_assign_to_channel=f'AnI1_{microscope}')
            
            task.write(0.0)
            task.write(5.0)
            time.sleep(pulse_duration)
            task.write(0.0)
            
        print(f"Analog trigger sent to {card_id}/{channel} for {pulse_duration} seconds.")
    
    except Exception as e:
        print(f"Error sending analog trigger: {e}")

def send_analog_pulse(card_id='Dev1', channel='ao0', microscope='2P3', 
                     trigger_duration=0.500, pulse_duration=0.001, num_pulses=50):
    """Sends an initial analog trigger followed by a series of pulses.
    
    Args:
        card_id (str): The ID of the DAQ device (e.g., 'Dev1').
        channel (str): The analog output channel (e.g., 'ao0').
        microscope (str): Name of the microscope for channel naming.
        trigger_duration (float): Duration of initial trigger pulse.
        pulse_duration (float): Duration of each subsequent pulse.
        num_pulses (int): Number of pulses to send after initial trigger.
    """
    try:
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(f'{card_id}/{channel}', 
                                               name_to_assign_to_channel=f'AnI1_{microscope}')
            
            # Initial trigger
            task.write(0.0)
            task.write(5.0)
            time.sleep(trigger_duration)
            task.write(0.0)
            print(f"Analog trigger sent to {card_id}/{channel} for {trigger_duration} seconds.")
            
            # Pulse sequence
            for i in range(num_pulses):
                task.write(5.0)
                time.sleep(pulse_duration)
                task.write(0.0)
                time.sleep(pulse_duration)
    
    except Exception as e:
        print(f"Error sending analog trigger: {e}")

