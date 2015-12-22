import time

# Move: Thriller Dance

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

# arms up and to left side
hexy.RF.knee(-60)
hexy.LF.knee(-60)
hexy.RF.ankle(-80)
hexy.LF.ankle(-80)
hexy.RF.hip(80)
hexy.LF.hip(0)
hexy.neck.set(40)

# quick pause
time.sleep(0.5)

# dip body
hexy.LM.setFootY(floor-8)
hexy.LB.setFootY(floor-28)
hexy.RM.setFootY(floor-8)
hexy.RB.setFootY(floor-28)

# arms down and centre
hexy.RF.knee(0)
hexy.LF.knee(0)
hexy.RF.ankle(-60)
hexy.LF.ankle(-60)
hexy.RF.hip(40)
hexy.LF.hip(-40)
hexy.neck.set(0)

# quicker pause
time.sleep(0.2)

# raise body
hexy.LM.setFootY(floor)
hexy.LB.setFootY(floor-20)
hexy.RM.setFootY(floor)
hexy.RB.setFootY(floor-20)

# arms up and to right side
hexy.RF.knee(-60)
hexy.LF.knee(-60)
hexy.RF.ankle(-80)
hexy.LF.ankle(-80)
hexy.RF.hip(0)
hexy.LF.hip(-80)
hexy.neck.set(-40)

# quick pause
time.sleep(0.5)

# dip body
hexy.LM.setFootY(floor-8)
hexy.LB.setFootY(floor-28)
hexy.RM.setFootY(floor-8)
hexy.RB.setFootY(floor-28)

# arms down and centre
hexy.RF.knee(0)
hexy.LF.knee(0)
hexy.RF.ankle(-60)
hexy.LF.ankle(-60)
hexy.RF.hip(40)
hexy.LF.hip(-40)
hexy.neck.set(0)

# quicker pause
time.sleep(0.2)

# raise body
hexy.LM.setFootY(floor)
hexy.LB.setFootY(floor-20)
hexy.RM.setFootY(floor)
hexy.RB.setFootY(floor-20)

# arms up and to right side
hexy.RF.knee(-60)
hexy.LF.knee(-60)
hexy.RF.ankle(-80)
hexy.LF.ankle(-80)
hexy.RF.hip(0)
hexy.LF.hip(-80)
hexy.neck.set(-40)

# quick pause
time.sleep(0.5)

# dip body
hexy.LM.setFootY(floor-8)
hexy.LB.setFootY(floor-28)
hexy.RM.setFootY(floor-8)
hexy.RB.setFootY(floor-28)

# arms down and centre
hexy.RF.knee(0)
hexy.LF.knee(0)
hexy.RF.ankle(-60)
hexy.LF.ankle(-60)
hexy.RF.hip(40)
hexy.LF.hip(-40)
hexy.neck.set(0)

# quicker pause
time.sleep(0.2)

# raise body
hexy.LM.setFootY(floor)
hexy.LB.setFootY(floor-20)
hexy.RM.setFootY(floor)
hexy.RB.setFootY(floor-20)

# arms up and to left side
hexy.RF.knee(-60)
hexy.LF.knee(-60)
hexy.RF.ankle(-80)
hexy.LF.ankle(-80)
hexy.RF.hip(80)
hexy.LF.hip(0)
hexy.neck.set(40)

# quick pause
time.sleep(0.5)

# dip body
hexy.LM.setFootY(floor-8)
hexy.LB.setFootY(floor-28)
hexy.RM.setFootY(floor-8)
hexy.RB.setFootY(floor-28)

# arms down and centre
hexy.RF.knee(0)
hexy.LF.knee(0)
hexy.RF.ankle(-60)
hexy.LF.ankle(-60)
hexy.RF.hip(40)
hexy.LF.hip(-40)
hexy.neck.set(0)

# quicker pause
time.sleep(0.2)

# raise body
hexy.LM.setFootY(floor)
hexy.LB.setFootY(floor-20)
hexy.RM.setFootY(floor)
hexy.RB.setFootY(floor-20)

# arms up and to left side
hexy.RF.knee(-60)
hexy.LF.knee(-60)
hexy.RF.ankle(-80)
hexy.LF.ankle(-80)
hexy.RF.hip(80)
hexy.LF.hip(0)
hexy.neck.set(40)

# quick pause
time.sleep(0.5)

# dip body
hexy.LM.setFootY(floor-8)
hexy.LB.setFootY(floor-28)
hexy.RM.setFootY(floor-8)
hexy.RB.setFootY(floor-28)

# arms down and centre
hexy.RF.knee(0)
hexy.LF.knee(0)
hexy.RF.ankle(-60)
hexy.LF.ankle(-60)
hexy.RF.hip(40)
hexy.LF.hip(-40)
hexy.neck.set(0)

# quicker pause
time.sleep(0.5)

# plant front legs
hexy.LF.replantFoot(-40,stepTime=0.3)
hexy.RF.replantFoot(40,stepTime=0.3)
time.sleep(0.4)
hexy.LF.setFootY(floor+60)
hexy.RF.setFootY(floor+60)

