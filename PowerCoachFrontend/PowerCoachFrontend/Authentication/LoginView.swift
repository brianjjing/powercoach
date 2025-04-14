//
//  LoginView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 4/13/25.
//

//Default page. Can go to signup if you dojn't have an acct.

import SwiftUI

struct LoginView: View {
    @State private var username: String = ""
    @State private var password: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @AppStorage("isAuthenticated") var isAuthenticated: Bool = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Login")
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
                
                Button(action: login) {
                    Text("Login")
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .disabled(isLoading || username.isEmpty || password.isEmpty)
                
                Spacer()
                Spacer()
                
                Text("Don't have an account?")
                    .font(.body)
                NavigationLink(destination: SignUpView()) {
                    Text("Sign up")
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
            }
            .padding()
            .fullScreenCover(isPresented: $isAuthenticated) {
                ContentView()
            }
        }
    }
    
    func login() {
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
        
        //Sends over the POST request above, then deals with the returned variables.
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
                let loginMessage = json["login_message"] as? String {
                DispatchQueue.main.async {
                    if loginMessage == "Login successful" {
                        isAuthenticated = true
                        //GET THE TOKEN TOO!!!!!
                    } else {
                        errorMessage = loginMessage
                    }
                }
            }
        }.resume()
    }
}
