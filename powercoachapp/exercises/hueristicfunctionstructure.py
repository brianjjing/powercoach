import time

timern = time.time()
print(timern)

currentcond=1
notinstartposition=True

while notinstartposition:
    cond1 = time.time()<=(timern+2)
    cond2 = time.time()<=(timern+2)
    cond3 = time.time()<=(timern+2)
    cond4 = time.time()<=(timern+2)

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
        print("Condition 4 met, start position reached!")
        notinstartposition = False
    else:
        # If a condition fails, revert to the appropriate state
        if not cond1:
            print("Condition 1 failed, resetting to Condition 1")
            currentcond = 1
        elif not cond2:
            print("Condition 2 failed, resetting to Condition 2")
            currentcond = 2
        elif not cond3:
            print("Condition 3 failed, resetting to Condition 3")
            currentcond = 3
        elif not cond4:
            print("Condition 4 failed, resetting to Condition 4")
            currentcond = 4

    # Small delay to avoid excessive CPU usage
    #time.sleep(0.1) --> Only activate if needed, and make the delay shorter
    
    


#Slower version due to all the redundant manual checks making the time complexity O(n^4) (first algorithm, just keep for the logic of it):
"""
cond1 = time.time()<=(timern+2)
cond2 = time.time()<=(timern+2)
cond3 = time.time()<=(timern+2)
cond4 = time.time()<=(timern+2)
notinstartposition = True
#Brute force method: if statements for every condition, with conditions within each condition that cancel it if one of the previous conditions are not met anymore.
while notinstartposition:
    print('Do cond1')
    while cond1 and notinstartposition:
        print('cond1 met, now do cond2')
        cond1 = time.time()<=(timern+2) #Must reassign throughout 
        while cond1 and cond2 and notinstartposition:
            print('cond2 met, now do cond3') 
            cond2 = time.time()<=(timern+2)
            while cond1 and cond2 and cond3 and notinstartposition:
                print('cond3 met, now do cond4')
                cond3 = time.time()<=(timern+2)
                while cond1 and cond2 and cond3 and cond4:
                    print('cond4 met, in start position')
                    cond4 = time.time()<=(timern+2)
                    notinstartposition = False
"""