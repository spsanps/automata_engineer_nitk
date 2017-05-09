from zoom_in import Sensor
from Misc import *

sensor = Sensor()
sensor.max_rate = 50
sensor.set_calibration_data((0, 0), (500, 500))
sensor.initialise_stream()
sensor.video_stream.read()
sensor.auto_set_calibration_data()

# Finding start end positions---------------------------------------------------------------------------------------
start = map_to_cell(sensor.find_initial_position())
print 'Robot Found...'
end = map_to_cell(sensor.find_red_cell())

x,y = end

if x < 3.5: x = 0
else: x = 7
if y < 3.5: y = 0
else: y = 7

end = (x, y)

print start, end
