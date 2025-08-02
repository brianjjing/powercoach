//
//  SignUpView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 4/13/25.
//

import Foundation
import SwiftUI

class SignUpViewModel: ObservableObject {
    //Property wrappers @Published:
    @Published var signUpUsername: String = ""
    @Published var signUpPassword: String = ""
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var successMessage: String?
    @AppStorage("isAuthenticated") var isAuthenticated: Bool = false

    func signUp() {
        //Render: https://powercoach-1.onrender.com/auth/signup
        //AWS: http://54.67.86.184:10000/auth/signup --> Upgrade to https
        guard let url = URL(string: "https://powercoach-1.onrender.com/auth/signup") else {
            DispatchQueue.main.async {
                self.errorMessage = "Invalid server URL"
            }
            return
        }

        let signUpData: [String: String] = [
            "signUpUsername": signUpUsername,
            "signUpPassword": signUpPassword
        ]
        
        print("signupdata variables created")
        print(signUpUsername)
        print(signUpPassword)
        
        guard let jsonSignUpData = try? JSONSerialization.data(withJSONObject: signUpData) else {
            DispatchQueue.main.async {
                self.errorMessage = "Failed to encode signup data"
            }
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonSignUpData
        
        print("request created")
        
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
                let signupMessage = json["signup_message"] as? String {
                DispatchQueue.main.async {
                    if signupMessage == "Signup successful" {
                        print("Signup succeeded")
                        self.successMessage = "Signup succeeded!! Log in with your new username and password"
                    } else {
                        self.errorMessage = signupMessage
                        print("Could not sign in")
                    }
                }
            }
        }.resume()
    }
}
