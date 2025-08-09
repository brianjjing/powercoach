//
//  HomeScreenDisplay.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/3/25.
//

import SwiftUI

class HomeScreenViewModel: ObservableObject {
    @Published var current_workout: String?
    @Published var workout_name: String?
    @Published var num_exercises: Int?
    @Published var workout_exercises: [String]?
    @Published var workout_sets: [Int]?
    @Published var workout_reps: [Int]?
    @Published var workout_weights: [Int]?
    @Published var errorMessage: String?
    
    @Published var isLoading = false
    @Published var homeDisplayMessage: String = "You don't have a workout plan set yet!"
    
    func displayCurrentWorkout() {
        //self.resetState()
        self.isLoading = true
        
        //Render: https://powercoach-1.onrender.com/workout/getworkout
        //AWS: http://54.67.86.184:10000/workout/getworkout --> upgrade to aws
        let appUrlString = "https://powercoach-1.onrender.com/workout/getworkout"
        
        guard let appUrl = URL(string: appUrlString) else {
            self.errorMessage = "Invalid server URL"
            self.isLoading = false
            return
        }
        
        var request = URLRequest(url: appUrl)
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
                
                if httpResponse.statusCode == 404 {
                    print("ERROR CODE 404:")
                    self.homeDisplayMessage = "You don't have a workout plan set yet!"
                    print(String(describing: self.homeDisplayMessage))
                    return
                }
                
                // Handle success case (status code 200)
                guard httpResponse.statusCode == 200 else {
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
                    self.homeDisplayMessage = "Today's workout: \(decodedData.name)"
                    self.current_workout = decodedData.name
                    self.workout_name = decodedData.name
                    self.workout_exercises = decodedData.exercises
                    self.workout_sets = decodedData.sets
                    self.workout_sets = decodedData.reps
                    self.workout_weights = decodedData.weights
                    self.errorMessage = nil
                    
                    print(String(describing: self.current_workout))
                    
                } catch {
                    self.errorMessage = "Failed to decode JSON: \(error.localizedDescription)"
                    print(String(describing: self.errorMessage))
                }
            }
        }.resume()
    }
    
    private func resetState() {
        self.current_workout = nil
        self.workout_name = nil
        self.workout_exercises = nil
        self.workout_sets = nil
        self.workout_reps = nil
        self.workout_weights = nil
        self.homeDisplayMessage = ""
        self.errorMessage = nil
    }
}
