//
//  ProfileView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/28/25.
//


import SwiftUI

struct ProfileView: View {
    @AppStorage("isAuthenticated") var isAuthenticated: Bool = false
    @EnvironmentObject var webSocketManager: WebSocketManager

    var body: some View {
        VStack {
            Text("\(webSocketManager.useridString)")

            Button(action: logout) {
                Text("Logout")
                    .foregroundColor(.red)
                    .padding()
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
