//
//  SignUpView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 4/19/25.
//

import SwiftUI

struct SignUpView: View {
    @StateObject var viewModel = SignUpViewModel()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Sign Up")
                    .font(.largeTitle)
                    .bold()
                
                TextField("Username", text: $viewModel.signUpUsername)
                SecureField("Password", text: $viewModel.signUpPassword)
                
                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }
                
                NavigationLink(destination: LoginView()) {
                    Text("Log In")
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
            }
            .padding()
            .fullScreenCover(isPresented: $viewModel.isAuthenticated) {
                ContentView()
            }
        }
    }
}
