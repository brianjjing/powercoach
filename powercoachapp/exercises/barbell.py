import mediapipe as mp
from powercoachapp.extensions import shared_data

mp_pose = mp.solutions.pose
mplandmarks = mp.solutions.pose.PoseLandmark

#Coordinates are already normalized!
def deadlift(poselandmarks, bbox, stage):
    #3 SIMPLE TESTS: FEET SHOULDER WIDTH APART, HANDS ON BAR, BAR SHOULD GO FROM FEET --> HIPS --> FEET
    if stage == 1:
    #Initial message: 
        shared_data['message'] = "FEET SHOULDER WIDTH APART"
    
    #1. Feet shoulder width apart:
        # Shoulders
        ls = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        rs = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        # Feet
        lf = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        rf = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
        #Widths:
        shoulder_width = abs(ls.x - rs.x)
        foot_width     = abs(lf.x - rf.x) + 1e-8 #To avoid 0 division
        #Tolerances, tweak these values:
        low_tol = 0.6
        upper_tol = 1.4
        #Debugging:
        shared_data['message'] = f"SHOULD-FOOT WIDTH RATIO: {shoulder_width/foot_width}"
        
        if low_tol < (shoulder_width/foot_width) < upper_tol:
            shared_data['deadlift_stage'] = 2
            shared_data['message'] = "HANDS ON BAR"
    elif stage == 2:
        #If hands are same y and z val as the bar, then go to the lifting stage:
        #Thumbs:
        lt = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB]
        rt = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
        #Thumb heights:
        lt_height = lt.y * shared_data['frame_width']
        rt_height = rt.y * shared_data['frame_height']
        #debugging:
        shared_data['message'] = f"lt: {lt_height:.2f} rt: {rt_height:.2f} bbox: {bbox.origin_y:.2f} - {(bbox.origin_y - bbox.height):.2f}"
        
        if ((bbox.origin_y - bbox.height) < lt_height < bbox.origin_y) and ((bbox.origin_y - bbox.height) < rt_height < bbox.origin_y):
            shared_data['deadlift_stage'] = 3
            shared_data['message'] = "LIFT BAR ALL THE WAY UP"
    #LIFTING STAGE, 3 IS THE BASELINE NOW. ALSO MAKE FORM CORRECTIONS ALONG THE WAY, BUT FOR NOW JUST HANDLE THE UP/DOWN.
    elif stage == 3:
        #Lifting stage, get to lockout
        shared_data['message'] = "LIFT BAR ALL THE WAY UP"
        
    elif stage == 4:
        #Final stage, descent after lockout
        shared_data['message'] = "GO BACK DOWN"
        #Make it go back to stage 3 once you're back down, alternating between the two.
    else:
        shared_data['message'] = f"STAGE IS {shared_data['deadlift_stage']}"

#Steps to implement:
#1. Feet shoulder width apart (compare x values)
    #What to do: Find a way to get condition to be met as long as it is, but when it isn't      
    #Find a way for it to both show this on screen, and say it vocally
#2. Get BEHIND AND IN MIDDLE OF barbell:
    #Hips behind shins which are close to and behind barbell (compare z values)
    #Top and bottom of body are in middlish of the barbell x value
#3. Hand on barbell: fingers on similar y value??? (you have to detect the barbell too)
#4. Person is squatted down: (Knees bent - Hip-knee-ankle angle small), (Leaned over - Knee-hip-chest angle small) --> So, head is in front of hips (meaning head z vals will be positive)
#5. Posterior pelvic tilt: chest similar z value to shoulders
#6. Arms are straight: shoulder, elbow, wrist in SIMILAR x and z values on both arms:
    #if poselandmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x==poselandmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value].x==poselandmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value].x:
#7. Looking straight ahead: use angle between nose and eye level (midpoint of eyes) to see if looking straight ahead
    #similar x level for nose and eyes (no head tilt)
    #z coords of eyes and nose are equalish (no looking too up or down)
    #nose and neck (middle of shoulders) similar x value