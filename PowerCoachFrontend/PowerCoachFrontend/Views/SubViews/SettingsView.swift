//
//  SettingsView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/2/25.
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var loginViewModel: LoginViewModel
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var tabIcons: TabIcons
    @Environment(\.colorScheme) var colorScheme //Rerenders the variable and its views when the environment object changes, since it depends on it.
    // Changes button text color based on light or dark mode:
    var buttonTextColor: Color {
        colorScheme == .light ? .black : .white
    }
    
    //Visibility of pop-up sheets:
    @State private var showingLogoutPopup = false
    @State private var showingDeleteAccountPopup = false
    
    var body: some View {
        VStack {
            List {
                Section(header: Text("Security and privacy").font(.title3).bold().foregroundStyle(.primary)) {
                    NavigationLink(destination: InProgressView()) {
                        Text("Change password")
                            .font(.title3)
                            .foregroundColor(.primary)
                            .listRowBackground(Color.clear) // Makes the row background transparent
                    }
                }

                Section(header: Text("App appearance").font(.title3).bold().foregroundStyle(.primary)) {
                    NavigationLink(destination: InProgressView()) {
                        Text("Light Mode / Dark Mode")
                            .font(.title3)
                            .foregroundColor(.primary)
                            .listRowBackground(Color.clear) // Makes the row background transparent
                    }
                }

                Section(header: Text("Audio").font(.title3).bold().foregroundStyle(.primary)) {
                    NavigationLink(destination: InProgressView()) {
                        Text("Coach Voice")
                            .font(.title3)
                            .foregroundColor(.primary)
                            .listRowBackground(Color.clear) // Makes the row background transparent
                    }
                    NavigationLink(destination: InProgressView()) {
                        Text("Coach Volume")
                            .font(.title3)
                            .foregroundColor(.primary)
                            .listRowBackground(Color.clear) // Makes the row background transparent
                    }
                }

                Section(header: Text("Information").font(.title3).bold().foregroundStyle(.primary)) {
                    NavigationLink(destination: InProgressView()) {
                        Text("Support")
                            .font(.title3)
                            .foregroundColor(.primary)
                            .listRowBackground(Color.clear) // Makes the row background transparent
                    }
                    NavigationLink(destination: InProgressView()) {
                        Text("Privacy Policy")
                            .font(.title3)
                            .foregroundColor(.primary)
                            .listRowBackground(Color.clear) // Makes the row background transparent
                    }
                    NavigationLink(destination: InProgressView()) {
                        Text("Terms of Service")
                            .font(.title3)
                            .foregroundColor(.primary)
                            .listRowBackground(Color.clear) // Makes the row background transparent
                    }
                }
                
                Section(header: Text("Account actions").font(.title3).bold().foregroundStyle(.primary)) {
                    Button(action: {showingLogoutPopup.toggle()}) {
                        Text("Log out")
                            .font(.title3)
                            .foregroundColor(.primary) // Explicit red color
                            .listRowBackground(Color.clear) // Makes the row background transparent
                    }
                    Button(action: {showingDeleteAccountPopup.toggle()}) {
                        Text("Delete account")
                            .font(.title3)
                            .foregroundColor(.primary)
                            .listRowBackground(Color.clear) // Makes the row background transparent
                    }
                }
            }
            .listStyle(.plain) // Use .plain to remove the default list dividers and style
        }
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text("Settings")
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .font(.subheadline)
                    .foregroundStyle(.primary)
                    .foregroundColor(.black)
            }
        }
        .sheet(isPresented: $showingLogoutPopup) {
            LogOutPopUpView(showingPopup: $showingLogoutPopup)
                .environmentObject(webSocketManager)
        }
        .sheet(isPresented: $showingDeleteAccountPopup) {
            DeleteAccountPopUpView(showingPopup: $showingDeleteAccountPopup)
                .environmentObject(webSocketManager)
        }
    }
}

struct LogOutPopUpView: View {
    @AppStorage("isAuthenticated") var isAuthenticated: Bool = false
    @EnvironmentObject var loginViewModel: LoginViewModel
    @EnvironmentObject var webSocketManager: WebSocketManager
    @Environment(\.dismiss) var dismiss
    
    @Binding var showingPopup: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Are you sure you'd like to log out?")
                .font(.title)
            Button("Log out") {
                // This action programmatically dismisses the sheet.
                loginViewModel.logout()
                DispatchQueue.main.async {
                    webSocketManager.socket.disconnect()
                }
                showingPopup = false
            }
            .padding()
            .bold()
            .background(Color.red)
            .foregroundColor(.white)
            .cornerRadius(10)
            
            Button("Cancel") {
                // This action programmatically dismisses the sheet.
                dismiss()
            }
            .foregroundColor(.primary)
            
        }
        .padding()
    }
}

struct DeleteAccountPopUpView: View {
    @AppStorage("isAuthenticated") var isAuthenticated: Bool = false
    @EnvironmentObject var webSocketManager: WebSocketManager
    @Environment(\.dismiss) var dismiss
    
    @Binding var showingPopup: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Account deletion services coming in later updates!")
                .font(.title)
            
//            Text("Are you sure you want to delete your account? This action cannot be undone.")
//                .font(.title)
//            Button("Delete account") {
//                // This action programmatically dismisses the sheet.
//                deleteAccount() //Then go to another popup!!!
//                showingPopup = false
//            }
//            .padding()
//            .bold()
//            .background(Color.red)
//            .foregroundColor(.white)
//            .cornerRadius(10)
//            Button("Cancel") {
//                // This action programmatically dismisses the sheet.
//                dismiss()
//            }
//            .foregroundColor(.primary)
            
            Button("OK") {
                // This action programmatically dismisses the sheet.
                dismiss()
            }
            .foregroundColor(.primary)
            .bold()
            
        }
        .padding()
    }
    
    func deleteAccount() {
        //Render: https://powercoach-1.onrender.com/auth/logout
        //AWS: http://54.67.86.184:10000/auth/logout
        
        //Handle deleting account logic - should go to another popup
    }
}

#Preview {
    ProfileView()
        .environmentObject(WebSocketManager.shared)
}
