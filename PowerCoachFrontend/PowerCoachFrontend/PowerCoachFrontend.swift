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
import SocketIO

@main
struct PowerCoachFrontend: App {
    @AppStorage("isAuthenticated") var isAuthenticated: Bool = false
    @StateObject var webSocketManager = WebSocketManager.shared
    @StateObject var tabIcons = TabIcons.sharedTab
    @StateObject private var workoutsViewModel = WorkoutsViewModel()
    @Environment(\.scenePhase) private var scenePhase

    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    var body: some Scene {
        WindowGroup {
            if isAuthenticated == true {
                ContentView()
                    .environmentObject(webSocketManager)
                    .environmentObject(tabIcons)
                    .environmentObject(workoutsViewModel)
            }
            else {
                LoginView()
            }
        }
        .onChange(of: scenePhase, initial: false) { oldPhase, newPhase in
            switch newPhase {
            case .active:
                print("Scene Phase is .active. Websocket will connect in websocketmanager init()")
            case .inactive:
                print("App ScenePhase: Inactive.")
                // App is temporarily interrupted (phone call, control center).
                // Usually, you don't disconnect here unless battery drain is critical for brief pauses.
                // The socket might drop if inactive for too long anyway.
            case .background:
                print("App ScenePhase: Background. Disconnecting WebSocket.")
                // This is the primary place to disconnect when the app goes to background.
                // This saves battery and server resources.
                webSocketManager.emit(event: "disconnect") // Example: tell server app went background
                webSocketManager.socket?.disconnect()
            @unknown default:
                print("App ScenePhase: Unknown new phase.")
            }
        }
    }
}

class AppDelegate: NSObject, UIApplicationDelegate {
    //If you want to begin with portrait mode, set this to portrait
    static var orientation: UIInterfaceOrientationMask = .portrait
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil)
        -> Bool {
        return true
    }
    func application(_ application: UIApplication, supportedInterfaceOrientationsFor window: UIWindow?) -> UIInterfaceOrientationMask {
        return Self.orientation //Self referrs to the current type
    }
}
