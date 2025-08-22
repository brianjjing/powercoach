//
//  WorkoutViewModel.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/3/25.
//

import SwiftUI; import Foundation

class WorkoutsViewModel: ObservableObject {
    //Workout getting:
    @Published var workouts: [Workout] = []
    @AppStorage("authToken") var authToken: String?
    
    //Workout creation:
    // FIX: createdWorkout is now a struct that contains an array of `Exercise` structs.
    @Published var createdWorkout: CreatedWorkout = CreatedWorkout(
        name: "My Workout",
        exercises: [Exercise(id: UUID())],
        everyBlankDays: 7
    )
    
    //Messages:
    @Published var isLoading = false
    @Published var homeDisplayMessage: String = "You don't have a workout plan set yet!"
    @Published var getWorkoutErrorMessage: String? = nil
    @Published var addExerciseErrorMessage: String? = nil
    @Published var createWorkoutErrorMessage: String? = nil
    @Published var deleteWorkoutErrorMessage: String? = nil
    
    func getWorkouts() {
        self.getWorkoutErrorMessage = nil
        self.isLoading = true
        
        guard let token = authToken else {
            self.getWorkoutErrorMessage = "User is not authenticated."
            self.isLoading = false
            return
        }
        
        //Adding url w/ timezone:
        let timezoneIdentifier = TimeZone.current.identifier
        print("Detected timezone: \(timezoneIdentifier)")
        
        //Render: https://powercoach-1.onrender.com/workouts/getworkouts
        //AWS: http://54.67.86.184:10000/workouts/getworkouts --> upgrade to aws
        let appUrlString = "https://powercoach-1.onrender.com/workouts/getworkouts"
        
        guard var urlComponents = URLComponents(string: appUrlString) else { //Building URL w/ URLComponents. It's the right format, as straight up making a string URL with string formatting has formatting issues due to encoding.
            self.getWorkoutErrorMessage = "Invalid server URL"
            self.isLoading = false
            return
        }
        
        let timezoneQueryItem = URLQueryItem(name: "timezone", value: timezoneIdentifier)
        
        urlComponents.queryItems = [timezoneQueryItem]

        guard let finalUrl = urlComponents.url else {
            self.getWorkoutErrorMessage = "Failed to construct URL with timezone"
            self.isLoading = false
            return
        }
        
        print("Final URL: \(finalUrl)")
        
        var request = URLRequest(url: finalUrl)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in //weak self makes self an optional.
            DispatchQueue.main.async {
                guard let self = self else { return }
                self.isLoading = false
            
                
                if let error = error {
                    self.getWorkoutErrorMessage = "Request failed: \(error.localizedDescription)"
                    print(String(describing: self.getWorkoutErrorMessage))
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    self.getWorkoutErrorMessage = "Invalid server response."
                    print(String(describing: self.getWorkoutErrorMessage))
                    return
                }
                
                // Handle success case (status code 200)
                guard httpResponse.statusCode == 200 else {
                    print("HTTP Request Failed with status code: \(httpResponse.statusCode)")
                    print("Request URL: \(String(describing: httpResponse.url))")
                    print("Response Headers: \(httpResponse.allHeaderFields)")
                    self.getWorkoutErrorMessage = "Unknown error. Please reload and try again."
                    print(String(describing: self.getWorkoutErrorMessage))
                    return
                }
                
                guard let data = data else {
                    self.getWorkoutErrorMessage = "Data not received from server. Please reload and try again."
                    print(String(describing: self.getWorkoutErrorMessage))
                    return
                }
                
                do {
                    let decoder = JSONDecoder()
                    decoder.keyDecodingStrategy = .convertFromSnakeCase
                    let decodedData = try decoder.decode(WorkoutResponse.self, from: data)
                    
                    //Display message is name of the first one that is today.
                    self.homeDisplayMessage = "\(decodedData.homeDisplayMessage)"
                    print(self.homeDisplayMessage)
                    self.workouts = decodedData.workouts
                    print(self.workouts)
                } catch {
                    self.getWorkoutErrorMessage = "Failed to decode JSON: \(error.localizedDescription)"
                    print(String(describing: self.getWorkoutErrorMessage))
                }
            }
        }.resume()
    }
    
    func addExercise() {
        DispatchQueue.main.async {
            if self.createdWorkout.exercises.count >= 15 {
                self.addExerciseErrorMessage = "Can't have more than 15 exercises in a workout!"
            }
            else {
                self.addExerciseErrorMessage = nil
                self.createdWorkout.exercises.append(Exercise(id: UUID()))
            }
        }
    }
    
    // FIX: The delete function now takes an `Exercise` object, not an index.
    // It finds the correct exercise to remove based on its unique `id`.
    func deleteExercise(exercise: Exercise) {
        DispatchQueue.main.async {
            if let index = self.createdWorkout.exercises.firstIndex(where: { $0.id == exercise.id }) {
                self.createdWorkout.exercises.remove(at: index)
                self.addExerciseErrorMessage = nil
                print("Successfully deleted exercise with ID: \(exercise.id)")
                print("New count: \(self.createdWorkout.exercises.count)")
            } else {
                self.addExerciseErrorMessage = "Exercise not found for deletion."
                print("Error: Exercise with ID \(exercise.id) not found.")
            }
        }
    }
    
    func addExerciseToExisting(workout: Workout) {
        DispatchQueue.main.async {
            ...
        }
    }
    
    func deleteExerciseFromExisting(workout: Workout) {
        DispatchQueue.main.async {
            ...
        }
    }
    
    func editWorkout(workout: Workout) {
        //Convert the exercise ids to strings!
    }
    
    func createWorkout() {
        self.createWorkoutErrorMessage = nil
        self.isLoading = true
        
        guard let token = authToken else {
            DispatchQueue.main.async {
                self.createWorkoutErrorMessage = "User is not authenticated."
                self.isLoading = false
            }
            return
        }
        
        guard let appUrl = URL(string: "https://powercoach-1.onrender.com/workouts/createworkout") else {
            self.createWorkoutErrorMessage = "Invalid server URL"
            return
        }
        
        let createdWorkoutData: [String: Any] = [
            "name": createdWorkout.name,
            // Map the new `Exercise` objects to the old array format for the backend
            "exercise_uuids": createdWorkout.exercises.map { String(describing: $0.id) },
            "exercise_names": createdWorkout.exercises.map { $0.name }, //$0 is the implicit argument name, refers to the sole argument in the closure.
            "sets": createdWorkout.exercises.map { $0.sets },
            "reps": createdWorkout.exercises.map { $0.reps },
            "every_blank_days": 7
        ]
        
        print(createdWorkoutData)
        
        guard let jsonCreatedWorkoutData = try? JSONSerialization.data(withJSONObject: createdWorkoutData) else {
            self.createWorkoutErrorMessage = "Failed to encode created workout"
            return
        }

        var request = URLRequest(url: appUrl)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization") // Add this line
        request.httpBody = jsonCreatedWorkoutData
        
        print("request created")
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    self.createWorkoutErrorMessage = "Request failed: \(error.localizedDescription)"
                    print(self.createWorkoutErrorMessage)
                }
                return
            }
            
            guard let data = data else {
                DispatchQueue.main.async {
                    self.createWorkoutErrorMessage = "No data received from server"
                    print(self.createWorkoutErrorMessage)
                }
                return
            }
            
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                if let workoutCreationMessage = json["workout_creation_message"] as? String {
                    DispatchQueue.main.async {
                        if workoutCreationMessage == "Workout creation successful" {
                            self.createWorkoutErrorMessage = "Workout creation successful!"
                            print(self.createWorkoutErrorMessage)
                            self.resetCreation()
                        } else {
                            self.createWorkoutErrorMessage = workoutCreationMessage
                            print(self.createWorkoutErrorMessage)
                        }
                    }
                }
                else if let workoutCreationMessage = json["authorization_error_message"] as? String {
                    DispatchQueue.main.async {
                        self.createWorkoutErrorMessage = workoutCreationMessage
                        print(self.createWorkoutErrorMessage)
                    }
                }
            }
                
        }.resume()
    }
    
    func deleteWorkout(workoutToDelete: Workout) {
        self.deleteWorkoutErrorMessage = nil
        
        guard let token = authToken else {
            DispatchQueue.main.async {
                self.createWorkoutErrorMessage = "User is not authenticated."
                self.isLoading = false
            }
            return
        }
        
        guard let url = URL(string: "https://powercoach-1.onrender.com/workouts/deleteworkout") else {
            deleteWorkoutErrorMessage = "Invalid URL"
            return
        }
        
        let deletedWorkoutData: [String: Int?] = [
            "workout_id": workoutToDelete.workoutId
        ]
        
        print(deletedWorkoutData)
        
        guard let jsonDeletedWorkoutData = try? JSONSerialization.data(withJSONObject: deletedWorkoutData) else {
            self.deleteWorkoutErrorMessage = "Failed to encode deleted workout"
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization") // Add this line
        request.httpBody = jsonDeletedWorkoutData
        
        print("request created")
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    self.deleteWorkoutErrorMessage = "Request failed: \(error.localizedDescription)"
                    print(self.deleteWorkoutErrorMessage)
                }
                return
            }
            
            guard let data = data else {
                DispatchQueue.main.async {
                    self.deleteWorkoutErrorMessage = "No data received from server"
                    print(self.deleteWorkoutErrorMessage)
                }
                return
            }
            
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                if let workoutDeletionMessage = json["workout_deletion_message"] as? String {
                    DispatchQueue.main.async {
                        if workoutDeletionMessage == "Workout deletion successful" {
                            self.deleteWorkoutErrorMessage = "Workout deletion successful!"
                            print(self.deleteWorkoutErrorMessage)
                            
                            // Find the index of the workout to delete and remove it from the array
                            if let index = self.workouts.firstIndex(where: { $0.workoutId == workoutToDelete.workoutId }) {
                                self.workouts.remove(at: index)
                                print("Successfully removed workout with ID \(workoutToDelete.workoutId) from local array.")
                            }
                        } else {
                            self.deleteWorkoutErrorMessage = workoutDeletionMessage
                            print(self.deleteWorkoutErrorMessage)
                        }
                    }
                }
                else if let workoutCreationMessage = json["authorization_error_message"] as? String {
                    DispatchQueue.main.async {
                        self.deleteWorkoutErrorMessage = workoutCreationMessage
                        print(self.deleteWorkoutErrorMessage)
                    }
                }
            }
                
        }.resume()
    }
    
    func resetCreation() {
        self.createdWorkout = CreatedWorkout(
            name: "My Workout",
            everyBlankDays: 7
        )
    }
    
    //Resets absolutely everything
    private func resetState() {
        self.homeDisplayMessage = ""
        self.workouts = []
        // FIX: Resetting to the new data model
        self.createdWorkout = CreatedWorkout(
            name: "My Workout",
            everyBlankDays: 7
        )
        self.getWorkoutErrorMessage = nil
        self.addExerciseErrorMessage = nil
        self.createWorkoutErrorMessage = nil
        self.deleteWorkoutErrorMessage = nil
    }
}
