//
//  ProfileView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/28/25.
//

import SwiftUI

struct ProfileView: View {
    @AppStorage("profileMessage") var profileMessage: String = "User not found"
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var tabIcons: TabIcons
    @Environment(\.colorScheme) var colorScheme //Rerenders the variable and its views when the environment object changes, since it depends on it.
    // Changes button text color based on light or dark mode:
    var buttonTextColor: Color {
        colorScheme == .light ? .black : .white
    }

    var body: some View {
        VStack {
            CircleCoach()
            
            Text("\(profileMessage)")
                .font(.title)
                .fontWeight(.black)
                .foregroundColor(.primary)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            
            NavigationLink(destination: InProgressView()) {
                Text("Edit Profile")
                    .padding()
                    .font(.title3)
                    .bold()
                    .background(Color(.systemGray6))
                    .foregroundStyle(buttonTextColor)
                    .cornerRadius(12)
            }
            
            Text("Personal stats arriving in later updates ...")
                .font(.title)
                .fontWeight(.black)
                .foregroundColor(Color.red)
                .foregroundColor(.black)
                .multilineTextAlignment(.center)
        }
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                NavigationLink(destination: SettingsView()) {
                    Image(systemName: "gearshape")
                        .font(.system(size: UIScreen.main.bounds.width/20))
                        .foregroundColor(.primary)
                }
            }
        }
    }
}

#Preview {
    ProfileView()
        .environmentObject(WebSocketManager.shared)
        .environmentObject(TabIcons.sharedTab)
}
