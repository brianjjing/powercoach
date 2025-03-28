//
//  PowerCoachFrontend.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/18/25.
//

/*
See the LICENSE.txt file for this sample’s licensing information.

Abstract:
The top-level definition of the Landmarks app.
*/

import SwiftUI

@main
struct PowerCoachFrontend: App {
    @StateObject private var webSocketManager = WebSocketManager.shared
        
    init() {
        webSocketManager.connect()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(webSocketManager)
        }
    }
}
