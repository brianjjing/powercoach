//
//  WorkoutViewModel.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/3/25.
//

import SwiftUI; import Foundation

class WorkoutsViewModel: ObservableObject {
    //Workout getting:
    @Published var todaysWorkouts: [Workout] = []
    @Published var otherWorkouts: [Workout] = []
    
    //Workout creation:
    @Published var createdWorkout: CreatedWorkout = CreatedWorkout(
        name: "My Workout",
        numExercises: 1,
        sets: [0],
        reps: [0],
        startDateTime: Date(), //Gives the whole datetime
        everyBlankDays: 7
    )
    
    //Messages:
    @Published var isLoading = false
    @Published var homeDisplayMessage: String = "You don't have a workout plan set yet!"
    @Published var errorMessage: String? = nil
    @Published var workoutCreatorViewErrorMessage: String? = nil
    
    func displayCurrentWorkout() {
        self.resetState()
        self.isLoading = true
        
        //Adding url w/ timezone:
        let timezoneIdentifier = TimeZone.current.identifier
        print("Detected timezone: \(timezoneIdentifier)")
        
        //Render: https://powercoach-1.onrender.com/workouts/getworkouts
        //AWS: http://54.67.86.184:10000/workouts/getworkouts --> upgrade to aws
        let appUrlString = "https://powercoach-1.onrender.com/workouts/getworkouts"
        
        guard var urlComponents = URLComponents(string: appUrlString) else { //Building URL w/ URLComponents. It's the right format, as straight up making a string URL with string formatting has formatting issues due to encoding.
            self.errorMessage = "Invalid server URL"
            self.isLoading = false
            return
        }
        
        let timezoneQueryItem = URLQueryItem(name: "timezone", value: timezoneIdentifier)
        
        urlComponents.queryItems = [timezoneQueryItem]

        guard let finalUrl = urlComponents.url else {
            self.errorMessage = "Failed to construct URL with timezone"
            self.isLoading = false
            return
        }
        print("Final URL: \(finalUrl)")
        
        var request = URLRequest(url: finalUrl)
        request.httpMethod = "GET"
        
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in //weak self makes self an optional.
            DispatchQueue.main.async {
                guard let self = self else { return }
                self.isLoading = false
            
                
                if let error = error {
                    self.errorMessage = "Request failed: \(error.localizedDescription)"
                    print(String(describing: self.errorMessage))
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    self.errorMessage = "Invalid server response."
                    print(String(describing: self.errorMessage))
                    return
                }
                
                // Handle success case (status code 200)
                guard httpResponse.statusCode == 200 else {
                    print("HTTP Request Failed with status code: \(httpResponse.statusCode)")
                    print("Request URL: \(String(describing: httpResponse.url))")
                    print("Response Headers: \(httpResponse.allHeaderFields)")
                    self.errorMessage = "Unknown error. Please reload and try again."
                    print(String(describing: self.errorMessage))
                    return
                }
                
                guard let data = data else {
                    self.errorMessage = "Data not received from server. Please reload and try again."
                    print(String(describing: self.errorMessage))
                    return
                }
                
                do {
                    let decodedData = try JSONDecoder().decode(WorkoutResponse.self, from: data)
                    self.homeDisplayMessage = "\(decodedData.homeDisplayMessage)"
                    self.todaysWorkouts = decodedData.todaysWorkouts
                    self.otherWorkouts = decodedData.otherWorkouts
                } catch {
                    self.errorMessage = "Failed to decode JSON: \(error.localizedDescription)"
                    print(String(describing: self.errorMessage))
                }
            }
        }.resume()
    }
    
    func addExercise() {
        if self.createdWorkout.numExercises > 15 {
            workoutCreatorViewErrorMessage = "Can't have more than 15 exercises in a workout!"
            //Make a function to gray out the foreach.
        }
        else {
            workoutCreatorViewErrorMessage = nil
            self.createdWorkout.numExercises += 1
            self.createdWorkout.exercises.append("Select available exercise")
            self.createdWorkout.sets.append(0)
            self.createdWorkout.reps.append(0)
        }
    }
    
    func deleteExercise() {
        self.createdWorkout.numExercises -= 1
        //Add deletionindex logic.
    }
    
    func createWorkout() {
        //Set startDate to Date() and every_blank_days
        self.isLoading = true
        
        
        //Render: https://powercoach-1.onrender.com/workouts/createworkout
        //AWS: http://54.67.86.184:10000/workouts/createworkout --> upgrade to aws
        guard let appUrl = URL(string: "https://powercoach-1.onrender.com/workouts/createworkout") else {
            self.errorMessage = "Invalid server URL"
            return
        }
        
        let createdWorkoutData: [String: Any] = [
            "name": createdWorkout.name,
            "num_exercises": createdWorkout.numExercises,
            "exercises": createdWorkout.exercises,
            "sets": createdWorkout.sets,
            "reps": createdWorkout.reps,
            "start_datetime": Date(),
            "every_blank_days": 7
        ]
        
        struct CreatedWorkout: Codable {
            var name: String
            var numExercises: Int
            var exercises: [String] = ["Select exercise"]
            var sets: [Int]
            var reps: [Int]
            var startDateTime: Date
            var everyBlankDays: Int
            let availableExercises = ["conventional_deadlift", "rdl", "deep_squat", "quarter_squat", "standing_overhead_press", "barbell_bicep_curls", "barbell_rows"]
        }


        guard let jsonCreatedWorkoutData = try? JSONSerialization.data(withJSONObject: createdWorkoutData) else {
            self.errorMessage = "Failed to encode credentials"
            return
        }

        var request = URLRequest(url: appUrl)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonCreatedWorkoutData
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    self.errorMessage = "Request failed: \(error.localizedDescription)"
                }
                return
            }
            
            guard let data = data else {
                DispatchQueue.main.async {
                    self.errorMessage = "No data received from server"
                }
                return
            }
            
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let workoutCreationMessage = json["workout_creation_message"] as? String {
                DispatchQueue.main.async {
                    if workoutCreationMessage == "Workout creation successful" {
                        self.errorMessage = "Workout creation successful!"
                    } else {
                        self.errorMessage = workoutCreationMessage
                    }
                }
            }
        }.resume()
        
        self.resetState()
    }
    
    private func resetState() {
        self.homeDisplayMessage = ""
        self.todaysWorkouts = []
        self.otherWorkouts = []
        self.createdWorkout = CreatedWorkout(
            name: "My Workout",
            numExercises: 1,
            sets: [0],
            reps: [0],
            startDateTime: Date(), //Make it today
            everyBlankDays: 7
        )
        self.errorMessage = nil
        self.workoutCreatorViewErrorMessage = nil
    }
}
