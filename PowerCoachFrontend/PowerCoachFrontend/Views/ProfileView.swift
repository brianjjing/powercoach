//
//  ProfileView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/28/25.
//


import SwiftUI

struct ProfileView: View {
    @AppStorage("isAuthenticated") var isAuthenticated: Bool = false
    @AppStorage("profileMessage") var profileMessage: String = "User not found"
    @EnvironmentObject var webSocketManager: WebSocketManager

    var body: some View {
        VStack {
            
            Button(action: logout) {
                Text("Logout")
                    .padding()
                    .font(.title)
                    .bold()
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(12)
            }
        }
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text("\(profileMessage)")
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .foregroundColor(.black)
            }
            ToolbarItem(placement: .topBarTrailing) {
                //Make this a button later
                Image(systemName: "gearshape")
                    .font(.system(size: UIScreen.main.bounds.width/20))
                    .foregroundColor(.white)
            }
        }
    }

    func logout() {
        guard let url = URL(string: "https://powercoach-1.onrender.com/auth/logout") else { return }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"

        URLSession.shared.dataTask(with: request) { _, _, _ in
            DispatchQueue.main.async {
                isAuthenticated = false
                webSocketManager.socket.disconnect()
            }
        }.resume()
    }
}

#Preview {
    ProfileView()
        .environmentObject(WebSocketManager.shared)
}
