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

                
                Button(action: viewModel.login) {
                    Text("Login")
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .disabled(viewModel.isLoading || viewModel.username.isEmpty || viewModel.password.isEmpty)
                
                //Block is recomputed once errorMessage is updated due to the property wrappers @Published, @StateObject, and the DispatchQueue.main.async{} block
                if let error = viewModel.errorMessage {
                    Text("ERROR: " + String(describing: error))
                        .font(.largeTitle)
                        .bold()
                        .foregroundColor(.red)
                }
                
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
        }
        .navigationBarBackButtonHidden(true)
        .fullScreenCover(isPresented: $viewModel.isAuthenticated) {
            ContentView()
        }
    }
}
