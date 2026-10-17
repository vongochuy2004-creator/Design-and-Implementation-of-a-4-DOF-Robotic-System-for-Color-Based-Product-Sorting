
import math

def forward_kinematics(theta1, theta2, theta3, base_sl):
    # Convert angles to radians
    L1 = 130
    L2 = 140
    L3 = 140

    t1 = math.radians(theta1)
    t2 = math.radians(theta2)
    t3 = math.radians(theta3)

    # Precompute cosines and sines
    C1 = math.cos(t1)
    S1 = math.sin(t1)
    C2 = math.cos(t2)
    S2 = math.sin(t2)
    C23 = math.cos(t2 + t3)
    S23 = math.sin(t2 + t3)

    #Compute each element
    x = (C1 * (L2 * S2 + L3 * C23) + (60*C1)) 
    y = (S1 * (L2 * S2 + L3 * C23)+ (60*S1)) - base_sl
    z = (L1 + L2 * C2 - L3 * S23 - 30)

    # x = round((C1 * (L2 * C2 + L3 * C23)) + (30*C1))
    # y = round(S1 * (L2 * C2 + L3 * C23) + (30*S1))
    # z = round((L1 + L2 * S2 + L3 * S23) - 10) 

    return x, y, z

def inverse_kinematics(px, py_b, pz, base):
    
    L1 = 130
    L2 = 140
    L3 = 140
    pzw = pz +30
    py = py_b + base
    ##theta1
    q1 = math.atan2(py, px)
    the1 = round(math.degrees(q1))
    C1 = math.cos(q1)
  
    ##theta3 
    u = (px - 60*C1) / C1
    v = L1 - pzw
    
    s3 = -((u*u + v*v - L2*L2 - L3*L3) / (2*L2*L3))
    c3 = math.sqrt(1 - s3*s3)
    q3 = math.atan2(s3, c3)
    the3 = round(math.degrees(q3))
    ##theta2
    c2 = ((u*L3*c3 - v*(L2 - L3*s3)) / (L3*L3*c3*c3 + (L2 - L3*s3)*(L2 - L3*s3)))
    s2 = ((v + c2*(L2 - L3*s3)) / (L3*c3))
    q2 = math.atan2(s2, c2)
    the2 = round(math.degrees(q2))
    ##return
    return the1, the2, the3, base
