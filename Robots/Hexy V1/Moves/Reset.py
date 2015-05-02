import time
 
deg = -30

# pickup and put all the feet centered and on the floor.


hexy.LF.setFootY(0)
hexy.RM.setFootY(0)
hexy.LB.setFootY(0)

time.sleep(0.4)

hexy.LF.replantFoot(-deg,stepTime=0.3)
hexy.RM.replantFoot(0,stepTime=0.3)
hexy.LB.replantFoot(deg,stepTime=0.3)

time.sleep(0.5)

hexy.RF.setFootY(0)
hexy.LM.setFootY(0)
hexy.RB.setFootY(0)

time.sleep(0.4)

hexy.RF.replantFoot(deg,stepTime=0.3)
hexy.LM.replantFoot(0,stepTime=0.3)
hexy.RB.replantFoot(-deg,stepTime=0.3)

time.sleep(0.5)

# set all the hip angle to what they should be while standing
move("Tilt None")