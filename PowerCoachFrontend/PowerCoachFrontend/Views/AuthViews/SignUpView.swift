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
                
                //$ is used for two-way binding - reading in the typed input and displaying it back.
                TextField("Username", text: $viewModel.signUpUsername)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
                SecureField("Password", text: $viewModel.signUpPassword)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)
                
                Button(action: viewModel.signUp) {
                    Text("Create account")
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .disabled(viewModel.isLoading || viewModel.signUpUsername.isEmpty || viewModel.signUpPassword.isEmpty)
                
                //Block is recomputed once errorMessage is updated due to the property wrappers @Published, @StateObject
                if let error = viewModel.errorMessage {
                    Text("ERROR: " + String(describing: error))
                        .font(.title)
                        .bold()
                        .foregroundColor(.red)
                }
                
                if let success = viewModel.successMessage {
                    Text(String(describing: success))
                        .font(.title)
                        .bold()
                        .foregroundColor(.red)
                }
                
                Spacer()
                
                Text("Already have an account?")
                    .font(.title3)
                    .foregroundStyle(.primary)
                NavigationLink(destination: LoginView()) {
                    Text("Log In")
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
            }
            .padding()
        }
        .navigationBarBackButtonHidden(true)
        .fullScreenCover(isPresented: $viewModel.isAuthenticated) {
            ContentView()
        }
    }
}
