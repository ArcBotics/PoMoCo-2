import time



# Move: Tilt None

hexy.LF.setFootY(floor)
hexy.LM.setFootY(floor)
hexy.LB.setFootY(floor)

hexy.RF.setFootY(floor)
hexy.RM.setFootY(floor)
hexy.RB.setFootY(floor)


# set all the hip angle to what they should be while standing
hipDeg = -30
hexy.LF.hip(-hipDeg)
hexy.RM.hip(0)
hexy.LB.hip(hipDeg)
hexy.RF.hip(hipDeg)
hexy.LM.hip(0)
hexy.RB.hip(-hipDeg)
