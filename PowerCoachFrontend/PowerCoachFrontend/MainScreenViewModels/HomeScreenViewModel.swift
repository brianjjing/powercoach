//
//  HomeScreenDisplay.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/3/25.
//

import SwiftUI

class WorkoutsViewModel: ObservableObject {
    @Published var todaysWorkouts: [Workout] = []
    @Published var otherWorkouts: [Workout] = []
    @Published var errorMessage: String?
    
    @Published var isLoading = false
    @Published var homeDisplayMessage: String = "You don't have a workout plan set yet!"
    
    func displayCurrentWorkout() {
        //self.resetState()
        self.isLoading = true
        
        //Adding url w/ timezone:
        let timezoneIdentifier = TimeZone.current.identifier
        print("Detected timezone: \(timezoneIdentifier)")
        
        //Render: https://powercoach-1.onrender.com/workout/getworkout
        //AWS: http://54.67.86.184:10000/workout/getworkout --> upgrade to aws
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
                    self.homeDisplayMessage = "\(decodedData.home_display_message)"
                    self.todaysWorkouts = decodedData.todays_workouts
                    self.otherWorkouts = decodedData.other_workouts
                } catch {
                    self.errorMessage = "Failed to decode JSON: \(error.localizedDescription)"
                    print(String(describing: self.errorMessage))
                }
            }
        }.resume()
    }
    
    private func resetState() {
        self.homeDisplayMessage = ""
        self.todaysWorkouts = []
        self.otherWorkouts = []
        self.errorMessage = nil
    }
}
