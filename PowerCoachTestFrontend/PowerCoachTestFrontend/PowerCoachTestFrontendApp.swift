//
//  PowerCoachFrontend.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 7/12/25.
//

/*
See the LICENSE.txt file for this sample’s licensing information.

Abstract:
The top-level definition of the Landmarks app.
*/

import SwiftUI
import SocketIO

@main
struct PowerCoachFrontend: App {
    @StateObject var webSocketManager = WebSocketManager.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(webSocketManager)
        }
    }
}
