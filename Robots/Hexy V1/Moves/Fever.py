import time

# Move: Night Fever Dance

# Get the front legs into space @ front
hexy.LF.replantFoot(-40,stepTime=0.3)
time.sleep(0.4)
hexy.RF.replantFoot(40,stepTime=0.3)
time.sleep(0.4)

# move the mid-legs forwards to support body
hexy.LM.replantFoot(-40,stepTime=0.3)
time.sleep(0.4)
hexy.RM.replantFoot(40,stepTime=0.3)
time.sleep(0.4)

# lean back a bit
hexy.RB.setFootY(floor-20)
hexy.LB.setFootY(floor-20)
hexy.LF.setFootY(floor+60)

time.sleep(0.5)

# wave right arm about (up and right)
hexy.RF.knee(-60)
hexy.RF.ankle(0)
hexy.RF.hip(0)
hexy.neck.set(-40)
# dip body
hexy.LF.setFootY(floor+62)
hexy.LM.setFootY(floor-8)
hexy.LB.setFootY(floor-28)
hexy.RM.setFootY(floor-8)
hexy.RB.setFootY(floor-28)

# wait a bit
time.sleep(0.4)

# right arm down
hexy.RF.knee(50)
hexy.RF.ankle(-50)
hexy.RF.hip(70)
hexy.neck.set(30)
# raise body
hexy.LF.setFootY(floor+70)
hexy.LM.setFootY(floor)
hexy.LB.setFootY(floor-20)
hexy.RM.setFootY(floor)
hexy.RB.setFootY(floor-20)
# wait a bit
time.sleep(0.4)

# wave right arm about (up and right)
hexy.RF.knee(-60)
hexy.RF.ankle(0)
hexy.RF.hip(0)
hexy.neck.set(-40)
# dip body
hexy.LF.setFootY(floor+62)
hexy.LM.setFootY(floor-8)
hexy.LB.setFootY(floor-28)
hexy.RM.setFootY(floor-8)
hexy.RB.setFootY(floor-28)

# wait a bit
time.sleep(0.4)

# right arm down
hexy.RF.knee(50)
hexy.RF.ankle(-50)
hexy.RF.hip(70)
hexy.neck.set(30)
# raise body
hexy.LF.setFootY(floor+70)
hexy.LM.setFootY(floor)
hexy.LB.setFootY(floor-20)
hexy.RM.setFootY(floor)
hexy.RB.setFootY(floor-20)
# wait a bit
time.sleep(0.4)

# wave right arm about (up and right)
hexy.RF.knee(-60)
hexy.RF.ankle(0)
hexy.RF.hip(0)
hexy.neck.set(-40)
# dip body
hexy.LF.setFootY(floor+62)
hexy.LM.setFootY(floor-8)
hexy.LB.setFootY(floor-28)
hexy.RM.setFootY(floor-8)
hexy.RB.setFootY(floor-28)

# wait a bit
time.sleep(0.4)

# right arm down
hexy.RF.knee(50)
hexy.RF.ankle(-50)
hexy.RF.hip(70)
hexy.neck.set(30)
# raise body
hexy.LF.setFootY(floor+70)
hexy.LM.setFootY(floor)
hexy.LB.setFootY(floor-20)
hexy.RM.setFootY(floor)
hexy.RB.setFootY(floor-20)
# wait a bit
time.sleep(0.4)

# wave right arm about (up and right)
hexy.RF.knee(-60)
hexy.RF.ankle(0)
hexy.RF.hip(0)
hexy.neck.set(-40)
# dip body
hexy.LF.setFootY(floor+62)
hexy.LM.setFootY(floor-8)
hexy.LB.setFootY(floor-28)
hexy.RM.setFootY(floor-8)
hexy.RB.setFootY(floor-28)

# wait a bit
time.sleep(0.4)

# right arm down
hexy.RF.knee(50)
hexy.RF.ankle(-50)
hexy.RF.hip(70)
hexy.neck.set(30)
# raise body
hexy.LF.setFootY(floor+70)
hexy.LM.setFootY(floor)
hexy.LB.setFootY(floor-20)
hexy.RM.setFootY(floor)
hexy.RB.setFootY(floor-20)
# wait a bit
time.sleep(0.4)

# TODO: jiggle hips (requires some new inverse kinematics)
