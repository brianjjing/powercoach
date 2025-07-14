import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.components.containers.bounding_box import BoundingBox
from powercoachapplocal.extensions import shared_data

mp_pose = mp.solutions.pose
mplandmarks = mp.solutions.pose.PoseLandmark

#screenwidth = 3024
#screenheight = 1964
#Will use the normalized coords instead, but go to screen width and screen height if you deem that better

#Coordinates are already normalized!
def start_test(poselandmarks, bbox, stage):
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
        shared_data['message'] = f"SHOULDER TO FOOT WIDTH RATIO: {shoulder_width/foot_width}"
        
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
        shared_data['message'] = f"lt: {lt_height:.2f} rt: {rt_height:.2f} bbox: {(bbox.origin_y - bbox.height):.2f} - {bbox.origin_y:.2f}"
        
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


#Change this whole structure to match what's above:
def start(poselandmarks, bbox: BoundingBox):
    #Criteria:
    currentcond=1
    notinstartposition=True

    while notinstartposition:
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
        
        #Z COORD IS ALREADY NORMALIZED!!!
        generalbodythreshold = 0.15 #Only do specific thresholds for things that are way diffs
        cond1 = (abs(poselandmarks.landmark[mplandmarks.LEFT_HEEL.value].x - poselandmarks.landmark[mplandmarks.LEFT_SHOULDER.value].x)<=generalbodythreshold) and (abs(poselandmarks.landmark[mplandmarks.RIGHT_HEEL.value].x - poselandmarks.landmark[mplandmarks.RIGHT_SHOULDER.value].x)<=generalbodythreshold)                                                                                                                                   
        cond2 = 1==1 #Figure out how to get the z value of the bounding box
        cond3 = ((bbox.origin_y<poselandmarks.landmark[mplandmarks.LEFT_INDEX.value].y<(bbox.origin_y+bbox.height)) and (bbox.origin_y<poselandmarks.landmark[mplandmarks.RIGHT_INDEX.value].y<(bbox.origin_y+bbox.height)))
        cond4 = 1==1 #Figure out how to get angles, and how this would theoretically work
        cond5 = 1==1 #Figure out a better way to test for posterior pelvic tilt
        #left arm straight:
        cond6 = (abs(poselandmarks.landmark[mplandmarks.LEFT_ELBOW.value].x - poselandmarks.landmark[mplandmarks.LEFT_SHOULDER.value].x)<=generalbodythreshold) and (abs(poselandmarks.landmark[mplandmarks.LEFT_WRIST.value].x - poselandmarks.landmark[mplandmarks.LEFT_SHOULDER.value].x)<=generalbodythreshold) and (abs(poselandmarks.landmark[mplandmarks.RIGHT_ELBOW.value].x - poselandmarks.landmark[mplandmarks.RIGHT_SHOULDER.value].x)<=generalbodythreshold) and (abs(poselandmarks.landmark[mplandmarks.RIGHT_WRIST.value].x - poselandmarks.landmark[mplandmarks.RIGHT_SHOULDER.value].x)<=generalbodythreshold)
        generalfacethreshold = 0.1 #Probably need to tweak this further
        eyemidpointxval = poselandmarks.landmark[mplandmarks.RIGHT_EYE.value].x + (poselandmarks.landmark[mplandmarks.LEFT_EYE.value].x-poselandmarks.landmark[mplandmarks.RIGHT_EYE.value].x)/2
        shouldersmidpointxval = poselandmarks.landmark[mplandmarks.RIGHT_SHOULDER.value].x + (poselandmarks.landmark[mplandmarks.LEFT_SHOULDER.value].x - poselandmarks.landmark[mplandmarks.RIGHT_SHOULDER.value].x)/2
        cond7 = ((abs(poselandmarks.landmark[mplandmarks.NOSE.value].x - eyemidpointxval))<=generalfacethreshold) and (abs(poselandmarks.landmark[mplandmarks.NOSE.value].z-(poselandmarks.landmark[mplandmarks.RIGHT_EYE.value].z+poselandmarks.landmark[mplandmarks.LEFT_EYE.value].z)/2)<=generalfacethreshold) and (abs(poselandmarks.landmark[mplandmarks.NOSE.value].x-shouldersmidpointxval)<=generalbodythreshold)
        
        
#['LEFT_ANKLE', 'LEFT_EAR', 'LEFT_ELBOW', 'LEFT_EYE', 'LEFT_EYE_INNER', 'LEFT_EYE_OUTER', 'LEFT_FOOT_INDEX', 'LEFT_HEEL', 'LEFT_HIP',
#'LEFT_INDEX', 'LEFT_KNEE', 'LEFT_PINKY', 'LEFT_SHOULDER', 'LEFT_THUMB', 'LEFT_WRIST', 'MOUTH_LEFT', 'MOUTH_RIGHT', 'NOSE', 
#'RIGHT_ANKLE', 'RIGHT_EAR', 'RIGHT_ELBOW', 'RIGHT_EYE', 'RIGHT_EYE_INNER', 'RIGHT_EYE_OUTER', 'RIGHT_FOOT_INDEX', 'RIGHT_HEEL', 
#'RIGHT_HIP', 'RIGHT_INDEX', 'RIGHT_KNEE', 'RIGHT_PINKY', 'RIGHT_SHOULDER', 'RIGHT_THUMB', 'RIGHT_WRIST']

        if currentcond == 1 and cond1:
            print("Condition 1 met, moving to Condition 2")
            currentcond = 2
        elif currentcond == 2 and cond1 and cond2:
            print("Condition 2 met, moving to Condition 3")
            currentcond = 3
        elif currentcond == 3 and cond1 and cond2 and cond3:
            print("Condition 3 met, moving to Condition 4")
            currentcond = 4
        elif currentcond == 4 and cond1 and cond2 and cond3 and cond4:
            print("Condition 4 met, moving to Condition 5")
            currentcond = 5
        elif currentcond == 5 and cond1 and cond2 and cond3 and cond4 and cond5:
            print("Condition 5 met, moving to Condition 6")
            currentcond = 6
        elif currentcond == 6 and cond1 and cond2 and cond3 and cond4 and cond5 and cond6:
            print("Condition 6 met, moving to Condition 7")
            currentcond = 7
        elif currentcond == 7 and cond1 and cond2 and cond3 and cond4 and cond5 and cond6 and cond7:
            return ("Condition 7 met, moving to start")
            notinstartposition = False
            #MAKE IT KEEP GOING UNTIL THE LIFT IS STARTED. FOR NOW, YOU ARE JUST GOING UNTIL IT IS IN THE POSITION.
        else:
            # If a condition fails, revert to the appropriate state
            if not cond1:
                return ("Feet shoulder width apart!")
                currentcond = 1
            elif not cond2:
                return ("Condition 2 failed, resetting to Condition 2")
                currentcond = 2
            elif not cond3:
                return ("Hands on the barbell!")
                currentcond = 3
            elif not cond4:
                return ("Condition 4 failed, resetting to Condition 4")
                currentcond = 4
            elif not cond5:
                return ("Condition 5 failed, resetting to Condition 5")
                currentcond = 5
            else:
                return ("Condition 6 failed, resetting to Condition 6")
                currentcond = 6

def lift(poselandmarks):
    #Problem: Could be a squat forward instead of a deadlift.
    #Knees too far forward, hips too high up, etc.
    #Problem: Rounded back
    #Need anti shrug and optimal lat engagement!
    return 'Lift valid'
def lockout(poselandmarks):
    #Straight arms (z vals)
    #Straight torso (z vals)
    #Straight legs (z vals)
    #Hands on barbell (y vals)
    return 'Locked out'
def negative(poselandmarks):
    return 'Negative valid'