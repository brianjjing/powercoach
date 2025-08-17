//
//  LoginViewModel.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 4/19/25.
//

import SwiftUI

class LoginViewModel: ObservableObject {
    @Published var username = ""
    @Published var password = ""
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    @AppStorage("isAuthenticated") var isAuthenticated: Bool = false
    @AppStorage("profileMessage") var profileMessage: String = "User not found"
    @AppStorage("authToken") var authToken: String? {
        didSet {
            // This code runs whenever authToken is changed
            // If the token becomes nil, we set isAuthenticated to false.
            if authToken != nil {
                self.isAuthenticated = true
            } else {
                self.isAuthenticated = false
            }
        }
    }
    
    func login() {
        //Render: https://powercoach-1.onrender.com/auth/login
        //AWS: http://54.67.86.184:10000/auth/login --> upgrade to aws
        guard let appUrl = URL(string: "https://powercoach-1.onrender.com/auth/login") else {
            self.errorMessage = "Invalid server URL"
            return
        }
        
        let loginData: [String: String] = [
            "username": username,
            "password": password
        ]
        
        guard let jsonLoginData = try? JSONSerialization.data(withJSONObject: loginData) else {
            self.errorMessage = "Failed to encode credentials"
            return
        }
        
        var request = URLRequest(url: appUrl)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonLoginData
        
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
               let loginMessage = json["login_message"] as? String,
               let authToken = json["token"] as? String {
                    DispatchQueue.main.async {
                        if loginMessage == "Login successful" {
                            self.isAuthenticated = true
                            self.profileMessage = self.username
                            self.errorMessage = nil
                            //self.authToken = authToken
                            //print("Authentication successful. Token saved: \(String(describing: self.authToken))")
                        } else {
                            self.errorMessage = loginMessage
                        }
                    }
                }
        }.resume()
    }
    
    func logout() {
        //Render: https://powercoach-1.onrender.com/auth/logout
        //AWS: http://54.67.86.184:10000/auth/logout
        guard let url = URL(string:"https://powercoach-1.onrender.com/auth/logout") else { return }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"

        URLSession.shared.dataTask(with: request) { _, _, _ in
            DispatchQueue.main.async {
                self.isAuthenticated = false
                self.authToken = nil
            }
        }.resume()
    }
}
