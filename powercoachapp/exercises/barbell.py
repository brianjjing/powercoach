import math
import numpy as np
import mediapipe as mp
from powercoachapp.extensions import shared_data

mp_pose = mp.solutions.pose
mplandmarks = mp.solutions.pose.PoseLandmark

def calculate_angle(a, b, c):
#Calculates the angle in degrees between three landmarks (a, b, c) with b as the vertex.

    #Converting to pixel coords, and using numpy for faster calculations:
    ax_pix = a.x * shared_data['frame_width']
    ay_pix = a.y * shared_data['frame_height']
    az_val = a.z
    vec_a_pix = np.array([ax_pix, ay_pix, az_val])
    
    bx_pix = b.x * shared_data['frame_width']
    by_pix = b.y * shared_data['frame_height']
    bz_val = b.z
    vec_b_pix = np.array([bx_pix, by_pix, bz_val])
    
    cx_pix = c.x * shared_data['frame_width']
    cy_pix = c.y * shared_data['frame_height']
    cz_val = c.z
    vec_c_pix = np.array([cx_pix, cy_pix, cz_val])
    
    #Vector must point from B outwards in both of em, so it's a-b and c-b.
    ba_vec = vec_a_pix - vec_b_pix
    bc_vec = vec_c_pix - vec_b_pix

    dot_product = np.dot(ba_vec, bc_vec)
    magnitude_ba = np.linalg.norm(ba_vec) + 1e-8
    magnitude_bc = np.linalg.norm(bc_vec) + 1e-8

    # Cosine of the angle, clamped to [-1, 1] to avoid floating point errors with np.arccos (could be smth like -1.0000001)
    cosine_theta = dot_product / (magnitude_ba * magnitude_bc)
    theta_deg = np.degrees(np.arccos(np.clip(cosine_theta, -1.0, 1.0)))
    return theta_deg

#Coordinates are already normalized!
def conventional_deadlift(poselandmarks, bbox, stage):
    #Check all the constants for every frame first. Make conditions a little lenient, so they aren't triggered all the time:
    
    #1. Hands on bar
    lt_height = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB].y * shared_data['frame_height']
    rt_height = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB].y * shared_data['frame_height']
    #debugging:
    #shared_data['message'] = f"lt: {lt_height:.2f} rt: {rt_height:.2f} bbox: {bbox.origin_y:.2f} - {(bbox.origin_y - bbox.height):.2f}"
    if not (bbox.origin_y < lt_height < (bbox.origin_y+bbox.height)) and (bbox.origin_y < rt_height < (bbox.origin_y+bbox.height)):
        return "HANDS ON THE BARBELL"
    
    #2. Feet shoulder width apart
    # Feet
    ls = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    ls_width = ls.x * shared_data['frame_width']
    rs_width = rs.x * shared_data['frame_width']
    lf_width = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x * shared_data['frame_width']
    rf_width = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x * shared_data['frame_width']
    shoulder_width = abs(ls_width - rs_width)
    foot_width = abs(lf_width - rf_width) + 1e-8 #To avoid 0 division
    #Tolerances, tweak these values:
    low_tol = 0.6
    upper_tol = 1.4
    #Debugging:
    shared_data['message'] = f"SHOULD-FOOT WIDTH RATIO: {shoulder_width/foot_width}"
    if not (low_tol < (shoulder_width/foot_width) < upper_tol):
        return "FEET SHOULD BE SHOULDER WIDTH APART"
    
    #3. Don't round back
    #SHK threshold: 125 degrees
    lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
    rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    shk_angle_left = calculate_angle(ls, lh, lk)
    shk_angle_right = calculate_angle(rs, rh, rk)
    
    shk_angle_threshold = 120 # Degrees, needs tuning.
    if shk_angle_left < shk_angle_threshold or shk_angle_right < shk_angle_threshold:
        return "KEEP BACK STRAIGHT, DO NOT ROUND BACK"
    
    #4. Arms straight
    lw = poselandmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    rw = poselandmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    le = poselandmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    re = poselandmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
    arm_straightness_angle_left = calculate_angle(ls, le, lw)
    arm_straightness_angle_right = calculate_angle(rs, re, rw)
    
    arm_straight_threshold_min = 160 # Degrees, needs tuning. Can be higher like 170-175
    if arm_straightness_angle_left < arm_straight_threshold_min or arm_straightness_angle_right < arm_straight_threshold_min:
        return "KEEP YOUR ARMS STRAIGHT"
    
    #5. Keep neck neutral (probably need 3d coords)
    l_ear = poselandmarks[mp_pose.PoseLandmark.LEFT_EAR]
    neck_angle_left = calculate_angle(l_ear, ls, lh)
    neck_angle_threshold = 150 # Degrees, needs tuning
    if neck_angle_left < neck_angle_threshold:
        return "KEEP YOUR NECK NEUTRAL AND ALIGNED WITH YOUR SPINE"    
    
    #Now for the lifting after the pre-checks:
    if stage == 'concentric':
        lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
        rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
        left_threshold_from_hip = (lh.y - lk.y)/2
        right_threshold_from_hip = (rh.y - rk.y)/2
        bbell_height = (bbox.origin_y + (bbox.origin_y - bbox.height))/2
        
        if ((lh.y - left_threshold_from_hip) <= bbell_height) and ((rh.y - right_threshold_from_hip) <= bbell_height):
            shared_data['deadlift_stage'] = 'eccentric'
            return "DESCEND BAR BACK TO GROUND"
        return "LIFT BAR TO HIP LEVEL, DRIVE FEET INTO THE GROUND"
    else: #Stage is 'eccentric'.
        lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
        la = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        ra = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
        left_threshold_from_ankle = (lk.y - la.y)/3
        right_threshold_from_ankle = (rk.y - ra.y)/3
        bbell_height = (bbox.origin_y + (bbox.origin_y - bbox.height))/2
        
        if ((la.y + left_threshold_from_ankle) <= bbell_height) and ((ra.y + right_threshold_from_ankle) <= bbell_height):
            shared_data['deadlift_stage'] = 'concentric'
            return "LIFT BAR TO HIP LEVEL, DRIVE FEET INTO THE GROUND"
        return "DESCEND BAR BACK TO GROUND"

def squat(poselandmarks, bbox, stage):#Feet HIP width
    #Should work for front and back squat
    
    #Constants:
    
    #Concentric:
        #Goal is to
    #Eccentric:
        #Goal is to
    return "Exercise algorithm in creation"

def rdl(poselandmarks, bbox, stage):
    return "Exercise algorithm in creation"

def hang_clean(poselandmarks, bbox, stage):
    return "Exercise algorithm in creation"

def bench(poselandmarks, bbox, stage):
    return "Exercise algorithm in creation"

def curl(poselandmarks, bbox, stage):
    return "Exercise algorithm in creation"

def overhead_press(poselandmarks, bbox, stage):
    return "Exercise algorithm in creation"

def row(poselandmarks, bbox, stage):
    return "Exercise algorithm in creation"

barbell_exercises = {
    'conventional_deadlift': conventional_deadlift, #Only works for conventional since feet shoulder width apart
    'squat': squat,
    'rdl': rdl,
    'hang_clean': hang_clean,
    'incline_bench': bench,
    'curl': curl,
    'overhead_press': overhead_press,
    'row': row
}