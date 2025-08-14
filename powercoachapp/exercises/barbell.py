import numpy as np
import mediapipe as mp
from powercoachapp.extensions import shared_data

mp_pose = mp.solutions.pose
mplandmarks = mp.solutions.pose.PoseLandmark

#HELPER FUNCTIONS:
def calculate_angle(a, b, c):
#Calculates the angle in degrees between three landmarks (a, b, c) with b as the vertex.

    #Converting to pixel coords, and using numpy for faster calculations:
    vec_a_pix = np.array([a.x, a.y, a.z])
    vec_b_pix = np.array([b.x, b.y, b.z])
    vec_c_pix = np.array([c.x, c.y, c.z])
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

def elbow_flare(left_shoulder, right_shoulder, left_elbow, right_elbow):
    left_elbow_angle = calculate_angle(right_shoulder, left_shoulder, left_elbow)
    right_elbow_angle = calculate_angle(left_shoulder, right_shoulder, right_elbow)
    elbow_flare_angle_min = 100
    elbow_flare_angle_max = 170
    
    if not ((elbow_flare_angle_min < left_elbow_angle < elbow_flare_angle_max) and (elbow_flare_angle_min < right_elbow_angle < elbow_flare_angle_max)):
        if (left_elbow_angle < elbow_flare_angle_min) or (right_elbow_angle < elbow_flare_angle_min):
            return "ELBOWS ARE TOO TUCKED INWARDS"
        else:
            return "ELBOWS ARE TOO FLARED OUTWARDS"
    return None

def hands_on_bar(bbox, left_thumb, right_thumb):
    lt_height = left_thumb.y * shared_data['frame_height']
    rt_height = right_thumb.y * shared_data['frame_height']
    #debugging:
    #shared_data['message'] = f"lt: {lt_height:.2f} rt: {rt_height:.2f} bbox: {bbox.origin_y:.2f} - {(bbox.origin_y - bbox.height):.2f}"
    if not ((bbox.origin_y < lt_height < (bbox.origin_y+bbox.height)) and (bbox.origin_y < rt_height < (bbox.origin_y+bbox.height))):
        return "HANDS ON THE BARBELL"
    #MIGHT NEED TO MAKE A WIDER RANGE, SINCE BARBELL DETECTION BBOX WILL BE VERY THIN.
    return None

def feet_shoulder_width_apart(left_shoulder, right_shoulder, left_ankle, right_ankle, ratio_tolerance):
    ls = left_shoulder
    rs = right_shoulder
    lf = left_ankle
    rf = right_ankle
    ls_width = ls.x * shared_data['frame_width']
    rs_width = rs.x * shared_data['frame_width']
    lf_width = lf.x * shared_data['frame_width']
    rf_width = rf.x * shared_data['frame_width']
    shoulder_width = abs(ls_width - rs_width)
    foot_width = abs(lf_width - rf_width) + 1e-8 #To avoid 0 division
    #Tolerances, tweak these values:
    low_tol = 1 - ratio_tolerance
    upper_tol = 1 + ratio_tolerance
    #Debugging:
    shared_data['message'] = f"SHOULD-FOOT WIDTH RATIO: {shoulder_width/foot_width}"
    if not (low_tol < (shoulder_width/foot_width) < upper_tol):
        return "FEET SHOULD BE SHOULDER WIDTH APART"
    return None

def dont_round_back(left_shoulder, right_shoulder, left_hip, right_hip, left_knee, right_knee, shk_min_angle_threshold):
    #SHK threshold: 125 degrees
    ls = left_shoulder
    rs = right_shoulder
    lh = left_hip
    rh = right_hip
    lk = left_knee
    rk = right_knee
    shk_angle_left = calculate_angle(ls, lh, lk)
    shk_angle_right = calculate_angle(rs, rh, rk)
    
    #shk_angle_threshold needs tuning.
    if (shk_angle_left < shk_min_angle_threshold) or (shk_angle_right < shk_min_angle_threshold):
        return "KEEP BACK STRAIGHT, DO NOT ROUND BACK"
    return None

def bend_down_lower(left_shoulder, right_shoulder, left_hip, right_hip, left_knee, right_knee, shk_max_angle_threshold):
    ls = left_shoulder
    rs = right_shoulder
    lh = left_hip
    rh = right_hip
    lk = left_knee
    rk = right_knee
    shk_angle_left = calculate_angle(ls, lh, lk)
    shk_angle_right = calculate_angle(rs, rh, rk)
    
    #shk_angle_threshold needs tuning.
    if (shk_angle_left > shk_max_angle_threshold) or (shk_angle_right > shk_max_angle_threshold):
        return "BEND DOWN LOWER, KEEPING BACK FLAT"
    return None

def arms_straight(left_shoulder, right_shoulder, left_elbow, right_elbow, left_wrist, right_wrist):
    ls = left_shoulder
    rs = right_shoulder
    le = left_elbow
    re = right_elbow
    lw = left_wrist
    rw = right_wrist
    arm_straightness_angle_left = calculate_angle(ls, le, lw)
    arm_straightness_angle_right = calculate_angle(rs, re, rw)
    
    arm_straight_threshold_min = 160 # Degrees, needs tuning. Can be higher like 170-175
    if (arm_straightness_angle_left < arm_straight_threshold_min) or (arm_straightness_angle_right < arm_straight_threshold_min):
        return "KEEP YOUR ARMS STRAIGHT"
    return None

def arm_lockout(left_shoulder, right_shoulder, left_elbow, right_elbow, left_wrist, right_wrist):
    ls = left_shoulder
    rs = right_shoulder
    le = left_elbow
    re = right_elbow
    lw = left_wrist
    rw = right_wrist
    arm_straightness_angle_left = calculate_angle(ls, le, lw)
    arm_straightness_angle_right = calculate_angle(rs, re, rw)
    
    arm_straight_threshold_min = 160 # Degrees, needs tuning. Can be higher like 170-175
    if (arm_straightness_angle_left >= arm_straight_threshold_min) or (arm_straightness_angle_right >= arm_straight_threshold_min):
        return "DESCEND BAR BACK TO CHEST"
    return None

def arm_fully_stretched(left_shoulder, right_shoulder, left_elbow, right_elbow, left_wrist, right_wrist):
    ls = left_shoulder
    rs = right_shoulder
    le = left_elbow
    re = right_elbow
    lw = left_wrist
    rw = right_wrist
    arm_straightness_angle_left = calculate_angle(ls, le, lw)
    arm_straightness_angle_right = calculate_angle(rs, re, rw)
    
    arm_straight_threshold_min = 160 # Degrees, needs tuning. Can be higher like 170-175
    if (arm_straightness_angle_left >= arm_straight_threshold_min) or (arm_straightness_angle_right >= arm_straight_threshold_min):
        return "CURL BARBELL UPWARDS"
    return None

def arm_fully_curled(left_shoulder, right_shoulder, left_elbow, right_elbow, left_wrist, right_wrist):
    ls = left_shoulder
    rs = right_shoulder
    le = left_elbow
    re = right_elbow
    lw = left_wrist
    rw = right_wrist
    arm_curlness_angle_left = calculate_angle(ls, le, lw)
    arm_curlness_angle_right = calculate_angle(rs, re, rw)
    
    arm_curl_threshold_max = 45 # Degrees, needs tuning. Can be higher like 170-175
    if (arm_curlness_angle_left <= arm_curl_threshold_max) or (arm_curlness_angle_right <= arm_curl_threshold_max):
        return "LOWER BAR UNTIL ARMS FULLY STRETCHED"
    return None

def wrist_straight(left_elbow, right_elbow, left_wrist, right_wrist, left_index, right_index):
    le = left_elbow
    re = right_elbow
    lw = left_wrist
    rw = right_wrist
    li = left_index
    ri = right_index
    wrist_straightness_angle_left = calculate_angle(li, lw, le)
    wrist_straightness_angle_right = calculate_angle(ri, rw, re)
    
    wrist_straight_threshold_min = 120 #Needs tweaking
    if (wrist_straightness_angle_left <= wrist_straight_threshold_min) or (wrist_straightness_angle_right <= wrist_straight_threshold_min):
        return "STRAIGHTEN YOUR WRISTS"
    return None

def elbows_not_too_forward(left_elbow, right_elbow, left_shoulder, right_shoulder, left_hip, right_hip, esh_threshold_max):
    le = left_elbow
    re = right_elbow
    ls = left_shoulder
    rs = right_shoulder
    lh = left_hip
    rh = right_hip
    esh_angle_left = calculate_angle(le, ls, lh)
    esh_angle_right = calculate_angle(re, rs, rh)
    
    if (esh_angle_left > esh_threshold_max) or (esh_angle_right > esh_threshold_max):
        return "DO NOT PUSH ELBOWS TOO FAR FORWARD"
    return None

def no_knee_cave(left_knee, right_knee, left_ankle, right_ankle):
    lk = left_knee
    rk = right_knee
    lf = left_ankle
    rf = right_ankle
    lk_width = lk.x * shared_data['frame_width']
    rk_width = rk.x * shared_data['frame_width']
    lf_width = lf.x * shared_data['frame_width']
    rf_width = rf.x * shared_data['frame_width']
    
    if (rk_width-lk_width)/(rf_width-lf_width) < 0.9:
        return "DO NOT CAVE KNEES INWARD"
    return None

def keep_neck_straight(left_ear, left_shoulder, left_hip, neck_angle_threshold):
    le = left_ear
    ls = left_shoulder
    lh = left_hip
    neck_angle_left = calculate_angle(le, ls, lh)
    if neck_angle_left < neck_angle_threshold: # Degrees, needs tuning
        return "KEEP YOUR NECK NEUTRAL AND ALIGNED WITH YOUR SPINE"
    return None

def get_under_bar_for_squat(bbox, left_shoulder, right_shoulder, left_thumb, right_thumb, left_mouth, right_mouth):
    ls_height = left_shoulder.y * shared_data['frame_height']
    rs_height = right_shoulder.y * shared_data['frame_height']
    lt_height = left_thumb.y * shared_data['frame_height']
    rt_height = right_thumb.y * shared_data['frame_height']
    lm_height = left_mouth.y * shared_data['frame_height']
    rm_height = right_mouth.y * shared_data['frame_height']
    bbell_height = bbox.origin_y + bbox.height/2
    #MIGHT NEED TO MAKE A WIDER RANGE, SINCE BARBELL DETECTION BBOX WILL BE VERY THIN.
    
    if not ((bbox.origin_y < lt_height < (bbox.origin_y+bbox.height)) and (bbox.origin_y < rt_height < (bbox.origin_y+bbox.height)) and (lm_height < bbell_height < ls_height) and (rm_height < bbell_height < rs_height)):
        return "PUT THE BAR ON YOUR TRAPS AND GRAB IT WITH BOTH HANDS"
    return None

def leg_lockout(left_hip, right_hip, left_knee, right_knee, left_ankle, right_ankle, lift):
    lh = left_hip
    rh = right_hip
    lk = left_knee
    rk = right_knee
    lf = left_ankle
    rf = right_ankle
    leg_straightness_angle_left = calculate_angle(lh, lk, lf)
    leg_straightness_angle_right = calculate_angle(rh, rk, rf)
    
    leg_straight_threshold_min = 160 # Degrees, needs tuning. Can be higher like 170-175
    if lift == 'deadlift':
        if (leg_straightness_angle_left >= leg_straight_threshold_min) and (leg_straightness_angle_right >= leg_straight_threshold_min):
            return "DESCEND BAR BACK TO GROUND"
    elif lift == 'squat':
        if (leg_straightness_angle_left >= leg_straight_threshold_min) and (leg_straightness_angle_right >= leg_straight_threshold_min):
            return "DESCEND, PUSH YOUR HIPS DOWN AND KNEES OUT"
    if lift == 'rdl':
        if (leg_straightness_angle_left >= leg_straight_threshold_min) and (leg_straightness_angle_right >= leg_straight_threshold_min):
            return "DESCEND BAR BELOW KNEES, PUSH YOUR HIPS BACK"
    return None

#Addon function to leg_lockout to check for deadlift finished???
def bar_at_hip_height(bbox, left_hip, right_hip, left_knee, right_knee, lift):
    lh_height = left_hip.y * shared_data['frame_height']
    rh_height = right_hip.y * shared_data['frame_height']
    lk_height = left_knee.y * shared_data['frame_height']
    rk_height = right_knee.y * shared_data['frame_height']
    left_concentric_to_eccentric_y_position = lh_height + (lk_height - lh_height)/2
    right_concentric_to_eccentric_y_position = rh_height + (rk_height - rh_height)/2
    bbell_y_position = bbox.origin_y + bbox.height/2
    
    if lift == 'deadlift':
        #If bbell_y_position goes below the threshold point y position (it needs to have a smaller value, since position is negative as it goes up)
        if (bbell_y_position <= left_concentric_to_eccentric_y_position) and (bbell_y_position <= right_concentric_to_eccentric_y_position):
            return "DESCEND BAR BACK TO GROUND"
    elif lift == 'row':
        if (bbell_y_position <= left_concentric_to_eccentric_y_position) and (bbell_y_position <= right_concentric_to_eccentric_y_position):
            return "LOWER BAR BELOW KNEES WITH BACK STRAIGHT"
    return None

def bar_below_knees(bbox, left_knee, right_knee, lift):
    lk_height = left_knee.y * shared_data['frame_height']
    rk_height = right_knee.y * shared_data['frame_height']
    bbell_y_position = bbox.origin_y + bbox.height/2
    
    #If bbell_y_position goes above the threshold point y position (it needs to have a bigger value, since position is negative as it goes up)
    if lift == 'rdl':
        if (bbell_y_position > lk_height) and (bbell_y_position > rk_height):
            return "LIFT BAR TO HIP LEVEL, DRIVE FEET INTO THE GROUND"
    elif lift == 'row':
        if (bbell_y_position > lk_height) and (bbell_y_position > rk_height):
            return "PULL BAR TOWARDS BELLY BUTTON WHILE BENT OVER"
    return None

#EXERCISES HERE:
def conventional_deadlift(poselandmarks, bbox, stage):
    #Check all the constants for every frame first. Make conditions a little lenient, so they aren't triggered all the time:
    
    #1. Hands on bar
    lt = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB]
    rt = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
    hands_on_bar_message = hands_on_bar(bbox, lt, rt)
    if hands_on_bar_message:
        return hands_on_bar_message
    #MIGHT NEED TO MAKE A WIDER RANGE, SINCE BARBELL DETECTION BBOX WILL BE VERY THIN.
    
    #2. Feet shoulder width apart
    ls = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
    feet_shoulder_width_message = feet_shoulder_width_apart(ls, rs, lf, rf, 0.4)
    if feet_shoulder_width_message:
        return feet_shoulder_width_message
    
    #3. Don't round back
    #SHK threshold: 125 degrees
    lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
    rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    dont_round_back_message = dont_round_back(ls, rs, lh, rh, lk, rk, 125)
    if dont_round_back_message:
        return dont_round_back_message
    
    #4. Arms straight
    le = poselandmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    re = poselandmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
    lw = poselandmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    rw = poselandmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    arms_straight_message = arms_straight(ls, rs, le, re, lw, rw)
    if arms_straight_message:
        return arms_straight_message
    
    #5. Keep neck neutral
    l_ear = poselandmarks[mp_pose.PoseLandmark.LEFT_EAR]
    keep_neck_straight_message = keep_neck_straight(l_ear, ls, lh, 150)
    if keep_neck_straight_message:
        return keep_neck_straight_message
    
    #Now for the lifting after the pre-checks:
    if stage == 'concentric':
        #Concentric goal: Get to leg lockout
        leg_lockout_message = leg_lockout(lh, rh, lk, rk, lf, rf, 'deadlift')
        if leg_lockout_message:
            shared_data['lift_stage'] = 'eccentric'
            return leg_lockout_message
        #If this check is bad: Add a second check (function you already defined) for bar at hip level
        return "LIFT BAR TO HIP LEVEL, DRIVE FEET INTO THE GROUND"
    else: #Stage is 'eccentric'.
        lk_height = lk.y * shared_data['frame_height']
        rk_height = rk.y * shared_data['frame_height']
        lf_height = lf.y * shared_data['frame_height']
        rf_height = rf.y * shared_data['frame_height']
        left_threshold_from_ankle = lk_height + 2*(lf_height - lk_height)/3
        right_threshold_from_ankle = rk_height + 2*(rf_height - rk_height)/3
        bbell_y_position = bbox.origin_y + bbox.height/2
        
        #If bbell_y_position goes above the threshold point y position (it needs to have a bigger value, since position is negative as it goes up)
        if (bbell_y_position >= left_threshold_from_ankle) and (bbell_y_position >= right_threshold_from_ankle):
            shared_data['lift_stage'] = 'concentric'
            return "LIFT BAR TO HIP LEVEL, DRIVE FEET INTO THE GROUND"
        return "DESCEND BAR BACK TO GROUND"

def rdl(poselandmarks, bbox, stage):
    #Constants:
    
    #1. Hands on bar
    lt = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB]
    rt = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
    hands_on_bar_message = hands_on_bar(bbox, lt, rt)
    if hands_on_bar_message:
        return hands_on_bar_message
    #MIGHT NEED TO MAKE A WIDER RANGE, SINCE BARBELL DETECTION BBOX WILL BE VERY THIN.
    
    #2. Feet shoulder width apart
    ls = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
    feet_shoulder_width_message = feet_shoulder_width_apart(ls, rs, lf, rf, 0.4)
    if feet_shoulder_width_message:
        return feet_shoulder_width_message
    
    #3. Don't round back
    #SHK threshold: 125 degrees
    lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
    rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    dont_round_back_message = dont_round_back(ls, rs, lh, rh, lk, rk)
    if dont_round_back_message:
        return dont_round_back_message
    
    #4. Arms straight
    le = poselandmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    re = poselandmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
    lw = poselandmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    rw = poselandmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    arms_straight_message = arms_straight(ls, rs, le, re, lw, rw)
    if arms_straight_message:
        return arms_straight_message
    
    #5. Keep neck neutral
    l_ear = poselandmarks[mp_pose.PoseLandmark.LEFT_EAR]
    keep_neck_straight_message = keep_neck_straight(l_ear, ls, lh, 150)
    if keep_neck_straight_message:
        return keep_neck_straight_message
    
    #Concentric goal: Straight legs
    if stage == 'concentric':
        leg_lockout_message = leg_lockout(lh, rh, lk, rk, lf, rf, 'rdl')
        if leg_lockout_message:
            shared_data['lift_stage'] = 'eccentric'
            return leg_lockout_message
        return "LIFT BAR TO HIP LEVEL, DRIVE FEET INTO THE GROUND"
    #Eccentric goal: Bar right below knees
    else:
        lk_height = lk.y * shared_data['frame_height']
        rk_height = rk.y * shared_data['frame_height']
        bbell_y_position = bbox.origin_y + bbox.height/2
        
        #If bbell_y_position goes above the threshold point y position (it needs to have a bigger value, since position is negative as it goes up)
        if (bbell_y_position > lk_height) and (bbell_y_position > rk_height):
            shared_data['lift_stage'] = 'concentric'
            return "LIFT BAR TO HIP LEVEL, DRIVE FEET INTO THE GROUND"
        return "DESCEND BAR BELOW KNEES, PUSH YOUR HIPS BACK"

def deep_squat(poselandmarks, bbox, stage):#Feet HIP width
    #HKF under 60 degrees - Should work for front and back squat
    
    #Constants:
    #1. Feet shoulder width apart (make this VERY lenient)
    ls = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
    feet_shoulder_width_message = feet_shoulder_width_apart(ls, rs, lf, rf, 0.55)
    if feet_shoulder_width_message:
        return feet_shoulder_width_message
    #2. Get under the bar
    lt = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB]
    rt = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
    lm = poselandmarks[mp_pose.PoseLandmark.MOUTH_LEFT]
    rm = poselandmarks[mp_pose.PoseLandmark.MOUTH_RIGHT]
    get_under_bar_message = get_under_bar_for_squat(bbox, ls, rs, lt, rt, lm, rm)
    if get_under_bar_message:
        return get_under_bar_message
    #3. Do not round back
    lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
    rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    dont_round_back_message = dont_round_back(ls, rs, lh, rh, lk, rk, 125)
    if dont_round_back_message:
        return dont_round_back_message
    #4. No knee cave
    no_knee_cave_message = no_knee_cave(lk, rk, lf, rf)
    if no_knee_cave_message:
        return no_knee_cave_message
    #5. Neck straight
    l_ear = poselandmarks[mp_pose.PoseLandmark.LEFT_EAR]
    keep_neck_straight_message = keep_neck_straight(l_ear, ls, lh, 150)
    if keep_neck_straight_message:
        return keep_neck_straight_message
    #Can't really see butt wink or unevenness for now
        
    if stage == 'concentric':
        #Concentric:
        #Goal is to get legs straight
        leg_lockout_message = leg_lockout(lh, rh, lk, rk, lf, rf, 'squat')
        if leg_lockout_message:
            shared_data['lift_stage'] = 'eccentric'
            return leg_lockout_message
        return "SQUAT, DRIVE YOUR HIPS UP AND PUSH THROUGH FEET"
    else:
        #Eccentric:
            #Goal is to get knees over toes and HKF to under 60 degrees.
            #z val of knees should be SMALLER than Z val of toes
        lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
        rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
        lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
        
        left_hkf_angle = calculate_angle(lh, lk, lf)
        right_hkf_angle = calculate_angle(rh, rk, rf)
        
        if (lk.z < lf.z) and (rk.z < rf.z) and (left_hkf_angle <= 60) and (right_hkf_angle <= 60):
            shared_data['lift_stage'] = 'concentric'
            return "SQUAT, DRIVE YOUR HIPS UP AND PUSH THROUGH FEET"
        return "DESCEND, PUSH YOUR HIPS DOWN AND KNEES OUT"
        

def parallel_squat(poselandmarks, bbox, stage):#Feet HIP width
    #HKF to 80 degrees - Should work for front and back squat
    
    #Constants:
    #1. Feet shoulder width apart (make this VERY lenient)
    ls = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
    feet_shoulder_width_message = feet_shoulder_width_apart(ls, rs, lf, rf, 0.55)
    if feet_shoulder_width_message:
        return feet_shoulder_width_message
    #2. Get under the bar
    lt = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB]
    rt = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
    lm = poselandmarks[mp_pose.PoseLandmark.MOUTH_LEFT]
    rm = poselandmarks[mp_pose.PoseLandmark.MOUTH_RIGHT]
    get_under_bar_message = get_under_bar_for_squat(bbox, ls, rs, lt, rt, lm, rm)
    if get_under_bar_message:
        return get_under_bar_message
    #3. Do not round back
    lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
    rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    dont_round_back_message = dont_round_back(ls, rs, lh, rh, lk, rk, 125)
    if dont_round_back_message:
        return dont_round_back_message
    #4. No knee cave
    no_knee_cave_message = no_knee_cave(lk, rk, lf, rf)
    if no_knee_cave_message:
        return no_knee_cave_message
    #5. Neck straight
    l_ear = poselandmarks[mp_pose.PoseLandmark.LEFT_EAR]
    keep_neck_straight_message = keep_neck_straight(l_ear, ls, lh, 150)
    if keep_neck_straight_message:
        return keep_neck_straight_message
    #Can't really see butt wink or unevenness for now
        
    if stage == 'concentric':
        #Concentric:
        #Goal is to get legs straight
        leg_lockout_message = leg_lockout(lh, rh, lk, rk, lf, rf, 'squat')
        if leg_lockout_message:
            shared_data['lift_stage'] = 'eccentric'
            return leg_lockout_message
        return "SQUAT, DRIVE YOUR HIPS UP AND PUSH THROUGH FEET"
    else:
        #Eccentric:
            #Goal is to get knees over toes and HKF to under 80 degrees.
            #z val of knees should be SMALLER than Z val of toes
        lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
        rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
        lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
        
        left_hkf_angle = calculate_angle(lh, lk, lf)
        right_hkf_angle = calculate_angle(rh, rk, rf)
        
        if (lk.z < lf.z) and (rk.z < rf.z) and (left_hkf_angle <= 80) and (right_hkf_angle <= 80):
            shared_data['lift_stage'] = 'concentric'
            return "SQUAT, DRIVE YOUR HIPS UP AND PUSH THROUGH FEET"
        return "DESCEND, PUSH YOUR HIPS DOWN AND KNEES OUT"

def quarter_squat(poselandmarks, bbox, stage):#Feet HIP width
    #HKF to 135 degrees - Should work for front and back squat
    
    #Constants:
    #1. Feet shoulder width apart (make this VERY lenient)
    ls = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
    feet_shoulder_width_message = feet_shoulder_width_apart(ls, rs, lf, rf, 0.55)
    if feet_shoulder_width_message:
        return feet_shoulder_width_message
    #2. Get under the bar
    lt = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB]
    rt = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
    lm = poselandmarks[mp_pose.PoseLandmark.MOUTH_LEFT]
    rm = poselandmarks[mp_pose.PoseLandmark.MOUTH_RIGHT]
    get_under_bar_message = get_under_bar_for_squat(bbox, ls, rs, lt, rt, lm, rm)
    if get_under_bar_message:
        return get_under_bar_message
    #3. Do not round back
    lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
    rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    dont_round_back_message = dont_round_back(ls, rs, lh, rh, lk, rk, 125)
    if dont_round_back_message:
        return dont_round_back_message
    #4. No knee cave
    no_knee_cave_message = no_knee_cave(lk, rk, lf, rf)
    if no_knee_cave_message:
        return no_knee_cave_message
    #5. Neck straight
    l_ear = poselandmarks[mp_pose.PoseLandmark.LEFT_EAR]
    keep_neck_straight_message = keep_neck_straight(l_ear, ls, lh, 150)
    if keep_neck_straight_message:
        return keep_neck_straight_message
    #Can't really see butt wink or unevenness for now
        
    if stage == 'concentric':
        #Concentric:
        #Goal is to get legs straight
        leg_lockout_message = leg_lockout(lh, rh, lk, rk, lf, rf, 'squat')
        if leg_lockout_message:
            shared_data['lift_stage'] = 'eccentric'
            return leg_lockout_message
        return "SQUAT, DRIVE YOUR HIPS UP AND PUSH THROUGH FEET"
    else:
        #Eccentric:
            #Goal is to get knees over toes and HKF to under 80 degrees.
            #z val of knees should be SMALLER than Z val of toes
        lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
        rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
        lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
        
        left_hkf_angle = calculate_angle(lh, lk, lf)
        right_hkf_angle = calculate_angle(rh, rk, rf)
        
        if (lk.z < lf.z) and (rk.z < rf.z) and (left_hkf_angle <= 135) and (right_hkf_angle <= 135):
            shared_data['lift_stage'] = 'concentric'
            return "SQUAT, DRIVE YOUR HIPS UP AND PUSH THROUGH FEET"
        return "DESCEND, PUSH YOUR HIPS DOWN AND KNEES OUT"

def standing_overhead_press(poselandmarks, bbox, stage):
    #Can be seated or standing
    #Constants:
    #1. Hands on bar
    lt = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB]
    rt = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
    hands_on_bar_message = hands_on_bar(bbox, lt, rt)
    if hands_on_bar_message:
        return hands_on_bar_message
    #MIGHT NEED TO MAKE A WIDER RANGE, SINCE BARBELL DETECTION BBOX WILL BE VERY THIN.
    
    #2. Feet shoulder width apart
    ls = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
    feet_shoulder_width_message = feet_shoulder_width_apart(ls, rs, lf, rf, 0.4)
    if feet_shoulder_width_message:
        return feet_shoulder_width_message
    
    #3. Don't round back
    lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
    rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    dont_round_back_message = dont_round_back(ls, rs, lh, rh, lk, rk, 160)
    if dont_round_back_message:
        return dont_round_back_message
    
    #4. Neck straight
    l_ear = poselandmarks[mp_pose.PoseLandmark.LEFT_EAR]
    keep_neck_straight_message = keep_neck_straight(l_ear, ls, lh, 160)
    if keep_neck_straight_message:
        return keep_neck_straight_message
    
    #5. x and z angles should be between 100 and 170 degrees (of both shoulders + the elbow.)
    le = poselandmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    re = poselandmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
    elbow_flare_message = elbow_flare(ls, rs, le, re)
    if elbow_flare_message:
        return elbow_flare_message
    
    #Concentric goal: Arms straight
    if stage == 'concentric':
        lw = poselandmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        rw = poselandmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        arm_lockout_message = arm_lockout(ls, rs, le, re, lw, rw)
        if arm_lockout_message:
            shared_data['lift_stage'] = 'eccentric'
            return arm_lockout_message
        return "PRESS THE BAR ABOVE YOUR HEAD UNTIL ARMS ARE STRAIGHT"
    else:
        lm_height = poselandmarks[mp_pose.PoseLandmark.MOUTH_LEFT].y * shared_data['frame_height']
        rm_height = poselandmarks[mp_pose.PoseLandmark.MOUTH_RIGHT].y * shared_data['frame_height']
        bbell_height = bbox.origin_y + bbox.height/2
        
        if (lm_height < bbell_height) and (rm_height < bbell_height):
            shared_data['lift_stage'] = 'concentric'
            return "PRESS THE BAR ABOVE YOUR HEAD UNTIL ARMS ARE STRAIGHT"
        return "DESCEND BAR BACK TO CHEST"

def barbell_row(poselandmarks, bbox, stage):
    #Constants:
    #1. Hands on bar
    lt = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB]
    rt = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
    hands_on_bar_message = hands_on_bar(bbox, lt, rt)
    if hands_on_bar_message:
        return hands_on_bar_message
    #MIGHT NEED TO MAKE A WIDER RANGE, SINCE BARBELL DETECTION BBOX WILL BE VERY THIN.
    
    #2. Feet shoulder width apart
    ls = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
    feet_shoulder_width_message = feet_shoulder_width_apart(ls, rs, lf, rf, 0.5)
    if feet_shoulder_width_message:
        return feet_shoulder_width_message
    
    #3. Don't round back (LENIENT SHK threshold)
    #SHK threshold: 90 degrees, can't go below
    lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
    rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    dont_round_back_message = dont_round_back(ls, rs, lh, rh, lk, rk, 90) #Tweak the 90 degrees here, maybe even lower?
    if dont_round_back_message:
        return dont_round_back_message
    
    #4. Keep neck neutral
    l_ear = poselandmarks[mp_pose.PoseLandmark.LEFT_EAR]
    keep_neck_straight_message = keep_neck_straight(l_ear, ls, lh, 150)
    if keep_neck_straight_message:
        return keep_neck_straight_message
    
    #5. Don't be too straight (make a LOW SHK threshold)
    bend_down_lower_message = bend_down_lower(ls, rs, lh, rh, lk, rk, 135)
    if bend_down_lower_message:
        bend_down_lower_message
    
    #Concentric goal: Bar at hip level
    if stage == 'concentric':
        lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
        rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
        bar_at_hip_height_message = bar_at_hip_height(lh, rh, lk, rk, 'row')
        if bar_at_hip_height_message:
            shared_data['lift_stage'] = 'eccentric'
            return bar_at_hip_height_message
        return "PULL BAR TOWARDS BELLY BUTTON WHILE BENT OVER"
    #Eccentric goal: Bar below knees
    else:
        lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
        bar_below_knees_message = bar_below_knees(bbox, lk, rk, 'row')
        if bar_below_knees_message:
            shared_data['lift_stage'] = 'concentric'
            return bar_below_knees_message
        return "LOWER BAR BELOW KNEES WITH BACK STRAIGHT"

def barbell_bicep_curls(poselandmarks, bbox, stage):
    #Constants:
    #1. Hands on bar
    lt = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB]
    rt = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
    hands_on_bar_message = hands_on_bar(bbox, lt, rt)
    if hands_on_bar_message:
        return hands_on_bar_message
    
    #2. Feet shoulder width apart
    ls = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
    feet_shoulder_width_message = feet_shoulder_width_apart(ls, rs, lf, rf, 0.4)
    if feet_shoulder_width_message:
        return feet_shoulder_width_message
    
    #3. Keep back straight
    lh = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
    rh = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    lk = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    rk = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    dont_round_back_message = dont_round_back(ls, rs, lh, rh, lk, rk, 155)
    if dont_round_back_message:
        return dont_round_back_message
    
    #4. Don't sway elbows, keep them at similar Z as torso
    le = poselandmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    re = poselandmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
    elbows_not_too_forward_message = elbows_not_too_forward(le, re, ls, rs, lh, rh, 55)
    if elbows_not_too_forward_message:
        return elbows_not_too_forward_message
    
    #5. Wrist straight
    lw = poselandmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    rw = poselandmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    li = poselandmarks[mp_pose.PoseLandmark.LEFT_INDEX]
    ri = poselandmarks[mp_pose.PoseLandmark.RIGHT_INDEX]
    wrist_straight_message = wrist_straight(le, re, lw, rw, li, ri)
    if wrist_straight_message:
        return wrist_straight_message
    
    #Concentric goal: Arms at a 120 degree angle
    if stage == 'concentric':
        arm_fully_curled_message = arm_fully_curled(ls, rs, le, re, lw, rw)
        if arm_fully_curled_message:
            shared_data['lift_stage'] = 'eccentric'
            return arm_fully_curled_message
        return "CURL BARBELL UPWARDS"
    #Eccentric goal: Arms stretched straight
    else:
        arm_fully_stretched_message = arm_fully_stretched(ls, rs, le, re, lw, rw)
        if arm_fully_stretched_message:
            shared_data['lift_stage'] = 'concentric'
            return arm_fully_stretched_message
        return "LOWER BAR UNTIL ARMS FULLY STRETCHED"

#TO-DO:
#Should I even do weightlifting exercises, when they happen so fast??? (Maybe just post-lift feedback for those)
def hang_clean(poselandmarks, bbox, stage):
    #Constants:
    #Concentric goal:
    #Eccentric goal:
    return "Exercise algorithm in creation"

def power_clean(poselandmarks, bbox, stage):
    #Constants:
    #Concentric goal:
    #Eccentric goal:
    return "Exercise algorithm in creation"

def clean_and_jerk(poselandmarks, bbox, stage):
    #Constants:
    #Concentric goal:
    #Eccentric goal:
    return "Exercise algorithm in creation"

def snatch(poselandmarks, bbox, stage):
    #Constants:
    #Concentric goal:
    #Eccentric goal:
    return "Exercise algorithm in creation"

def seated_overhead_press_or_incline_bench(poselandmarks, bbox, stage):
    #Constants:
    #Concentric goal:
    #Eccentric goal:
    return "Exercise algorithm in creation"

def bench(poselandmarks, bbox, stage):
    #Constants:
    #Concentric goal:
    #Eccentric goal:
    return "Exercise algorithm in creation"

def skullcrushers(poselandmarks, bbox, stage):
    #Constants:
    #Concentric goal:
    #Eccentric goal:
    return "Exercise algorithm in creation"

#After writing the first ten algorithms^^^, train the dataset to perfection.
#Then frontend. Then testtesttest

barbell_exercises = {
    'Conventional Deadlifts': conventional_deadlift, #Only works for conventional since feet shoulder width apart
    'RDLs': rdl,
    'Deep Squats': deep_squat,
    '90-Degree Squats': parallel_squat,
    'Quarter Squats': quarter_squat,
    'Barbell Overhead Presses': standing_overhead_press,
    'Barbell Bicep Curls': barbell_bicep_curls,
    'Barbell Rows': barbell_rows
}