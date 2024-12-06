from machine import Pin, PWM, ADC

# Constants for servo control
MIN_PULSE = 1000  # Minimum pulse width in microseconds
MAX_PULSE = 9000  # Maximum pulse width in microseconds
DEAD_ZONE = 3000  # Joystick neutral zone threshold
SMOOTH_STEP = 1  # Maximum change per update for smooth movement

# Servo initialization
x_axis_servo = PWM(Pin(10))  # Horizontal movement
y_axis_servo = PWM(Pin(11))  # Vertical movement
gripper_servo = PWM(Pin(12))  # Gripper control
z_axis_servo = PWM(Pin(13))  # Z-axis movement

# Set servo frequency
x_axis_servo.freq(50)
y_axis_servo.freq(50)
gripper_servo.freq(50)
z_axis_servo.freq(50)

# Joystick and buttons
h_joystick = ADC(Pin(27))  # Horizontal joystick
v_joystick = ADC(Pin(26))  # Vertical joystick
toggle_button = Pin(1, Pin.IN, Pin.PULL_UP)  # Toggle button for Z-axis mode
gripper_button = Pin(16, Pin.IN, Pin.PULL_UP)  # Gripper toggle button

# Initial servo positions
x_pos = 5000
y_pos = 5000
z_pos = 5000
gripper_pos = MIN_PULSE  # Gripper starts closed
is_gripper_open = False  # Gripper state
z_axis_mode = False  # Z-axis mode toggle state (False: forward/backward, True: up/down)

# Previous button states for debouncing
prev_toggle_button_state = 1
prev_gripper_button_state = 1

# Helper function: map joystick values to servo pulse width
def map_value(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Helper function: smooth servo movement
def smooth_update(current, target, step):
    if abs(target - current) > step:
        return current + step if target > current else current - step
    return target

# Main control loop
while True:
    # Handle Z-axis mode toggle button
    toggle_button_state = toggle_button.value()
    if toggle_button_state == 0 and prev_toggle_button_state == 1:  # Button pressed
        z_axis_mode = not z_axis_mode  # Toggle mode
    prev_toggle_button_state = toggle_button_state

    # Handle gripper toggle button
    gripper_button_state = gripper_button.value()
    if gripper_button_state == 0 and prev_gripper_button_state == 1:  # Button pressed
        if is_gripper_open:
            gripper_pos = MIN_PULSE  # Close the gripper
        else:
            gripper_pos = MAX_PULSE  # Open the gripper
        is_gripper_open = not is_gripper_open  # Toggle gripper state
        gripper_servo.duty_u16(gripper_pos)  # Apply the gripper position
        print("Gripper State:", "Open" if is_gripper_open else "Closed")
    prev_gripper_button_state = gripper_button_state

    # Read joystick values
    h_val = h_joystick.read_u16()
    v_val = v_joystick.read_u16()

    # Detect joystick movement (outside the dead zone)
    h_target = x_pos
    v_target = y_pos if not z_axis_mode else z_pos

    if abs(h_val - 32768) > DEAD_ZONE:
        h_target = map_value(h_val, 0, 65535, MIN_PULSE, MAX_PULSE)

    if abs(v_val - 32768) > DEAD_ZONE:
        v_target = map_value(v_val, 0, 65535, MIN_PULSE, MAX_PULSE)

    # Smoothly update servo positions
    x_pos = smooth_update(x_pos, h_target, SMOOTH_STEP)
    if z_axis_mode:
        z_pos = smooth_update(z_pos, v_target, SMOOTH_STEP)
    else:
        y_pos = smooth_update(y_pos, v_target, SMOOTH_STEP)

    # Apply servo positions
    x_axis_servo.duty_u16(x_pos)
    y_axis_servo.duty_u16(y_pos)
    z_axis_servo.duty_u16(z_pos)

    # Gripper position is already handled immediately above

