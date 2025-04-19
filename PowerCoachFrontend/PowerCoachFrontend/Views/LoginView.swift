//
//  LoginView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 4/19/25.
//

import SwiftUI

struct LoginView: View {
    @StateObject var viewModel = LoginViewModel()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Login")
                    .font(.largeTitle)
                    .bold()
                
                TextField("Username", text: $viewModel.username)
                SecureField("Password", text: $viewModel.password)
                
                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }
                
                Button(action: viewModel.login) {
                    Text("Login")
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .disabled(viewModel.isLoading || viewModel.username.isEmpty || viewModel.password.isEmpty)
                
                Spacer()
                
                NavigationLink(destination: SignUpView()) {
                    Text("Sign up")
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
