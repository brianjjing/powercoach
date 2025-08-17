//
//  LoginView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 4/19/25.
//

import SwiftUI

struct LoginView: View {
    @EnvironmentObject var loginViewModel: LoginViewModel
    
    var body: some View {
        NavigationView {
            VStack() {
                Text("Login")
                    .font(.largeTitle)
                    .bold()
                
                TextField("Username", text: $loginViewModel.username)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
                
                SecureField("Password", text: $loginViewModel.password)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)
                
                Button(action: loginViewModel.login) {
                    Text("Login")
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .disabled(loginViewModel.isLoading || loginViewModel.username.isEmpty || loginViewModel.password.isEmpty)
                
                //Block is recomputed once errorMessage is updated due to the property wrappers @Published, @StateObject, and the DispatchQueue.main.async{} block
                if let error = loginViewModel.errorMessage {
                    Text("ERROR: " + String(describing: error))
                        .font(.title3)
                        .bold()
                        .foregroundColor(.red)
                        .multilineTextAlignment(.leading)
                }
                
                Spacer()
                
                Text("Don't have an account?")
                    .font(.title3)
                    .foregroundStyle(.primary)
                
                NavigationLink(destination: SignUpView()) {
                    Text("Sign up")
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
            }
            .padding()
        }
        .navigationBarBackButtonHidden(true)
        .fullScreenCover(isPresented: $loginViewModel.isAuthenticated) {
            ContentView()
        }
    }
}
