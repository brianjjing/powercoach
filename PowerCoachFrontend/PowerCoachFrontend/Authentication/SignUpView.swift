//
//  SignUpView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 4/13/25.
//

import SwiftUI

struct SignUpView: View {
    @State private var username: String = ""
    @State private var password: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @State private var isLoggedIn: Bool = false
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Sign Up")
                .font(.largeTitle)
                .bold()
            
            TextField("Username", text: $username)
                .autocapitalization(.none)
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(10)
            
            SecureField("Password", text: $password)
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(10)
            
            if let error = errorMessage {
                Text(error)
                    .foregroundColor(.red)
                    .font(.caption)
            }
            
            Button(action: signUp) {
                Text("Sign Up")
                    .foregroundColor(.white)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.blue)
                    .cornerRadius(10)
            }
            .disabled(isLoading || username.isEmpty || password.isEmpty)
            
            Spacer()
        }
        .padding()
        .fullScreenCover(isPresented: $isLoggedIn) {
            Text("Welcome, \(username)!")
        }
    }
    
    func signUp() {
        guard let appUrl = URL(string: "https://powercoach-1.onrender.com") else {
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
    }
}
