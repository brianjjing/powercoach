//
//  WebSocketManager.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/18/25.
//

import AVFoundation
import Foundation
import SocketIO
import SwiftUI

//MOVE ALL THE COMMUNICATION LOGIC HERE!!!!

//The websocketmanager instance is the delegate.
//ObservableObject is the protocol that tells the class to watch out for property changes. @Published signifies which properties are to be updated in the views upon being changed.
class WebSocketManager: ObservableObject {
    static let shared = WebSocketManager()
    
    var manager: SocketManager!
    var socket: SocketIOClient!
    
    @Published var workoutPlanDisplay = "Connecting..."
    @Published var forumDisplay = "Connecting..."
    @Published var powerCoachMessage = "Connecting..."
    
    @Published var currentWorkout: String?
    
    init() {
        //RENDER API URL: https://powercoach-1.onrender.com
        //AWS IP: https://powercoachapp.com
        self.manager = SocketManager(socketURL: URL(string: "https://powercoachapp.com")!, config: [.log(true), .compress, .forceWebsockets(true), .path("/socket.io")])
        self.socket = self.manager.defaultSocket
        
        socket.on(clientEvent: .connect) { (data, ack) in
            print("EVENT: SOCKET CONNECTED.")
            DispatchQueue.main.async {
                self.workoutPlanDisplay = "Select a workout below or press the plus button to create a new one!"
                self.forumDisplay = "POWERCOACH forums coming soon..."
                self.powerCoachMessage = "Message loading..."
            }
        }
        
        socket.on(clientEvent: .disconnect) { (data, ack) in
            print("EVENT: SOCKET DISCONNECTED.")
        }
        
        socket.onAny { (event) in
            print("CLIENT RECEIVED EVENT: \(String(describing: event.event)), WITH ITEMS: \(String(describing: event.items))")
        }
        
        socket.on("powercoach_message") { (data, ack) in
            print("CLIENT RECEIVED EVENT: POWERCOACH MESSAGE")
//            print(data)
//            print(type(of: data))
            if let powerCoachString = data[0] as? String,
               let powerCoachData = powerCoachString.data(using: .utf8) {
                DispatchQueue.main.async {
                    self.powerCoachMessage = String(decoding: powerCoachData, as: UTF8.self)
                }
            }
        }
        
        socket.on("test_response") { (data, ack) in
            print("CLIENT RECEIVED EVENT: TEST RESPONSE")
            print(data)
        }
        
        print("WEBSOCKET CONNECTING ...")
        socket.connect()
        print("WEBSOCKET CONNECTED ...")
    }
    
    enum SocketPayload {
        case text(String)
        case binary(Data)
    }
    
    func emit(event: String, with items: Data) {
        print("EMITTING EVENT: \(event)")
        
        switch self.socket.status {
        case .connected:
            self.socket.emit(event, items)
            print("EMITTED EVENT: \(event), WITH ITEMS: \(items)")
        case .connecting:
            print("WEBSOCKET STILL CONNECTING, WILL EMIT EVENT \(event) ONCE IT CONNECTS ... \n")
            self.socket.once(clientEvent: .connect) { (object, ack) in
                self.socket.emit(event, items)
                print("EMITTED EVENT: \(event), WITH ITEMS: \(items)")
            }
        case .notConnected:
            print("ERROR WITH EMITTING EVENT \(event): WEBSOCKET NOT CONNECTED\n")
            socket.once(clientEvent: .connect) { data, ack in
                self.socket.emit(event, items)
            }
            socket.connect()
        case .disconnected:
            print("ERROR WITH EMITTING EVENT \(event): WEBSOCKET DISCONNECTED\n")
            socket.once(clientEvent: .connect) { data, ack in
                self.socket.emit(event, items)
            }
            socket.connect()
        default:
            break
        }
    }
    
    func emit(event: String, with items: String) {
        print("EMITTING EVENT: \(event)")
        
        switch self.socket.status {
        case .connected:
            self.socket.emit(event, items)
            print("EMITTED EVENT: \(event), WITH ITEMS: \(items)")
        case .connecting:
            print("WEBSOCKET STILL CONNECTING, WILL EMIT EVENT \(event) ONCE IT CONNECTS ... \n")
            self.socket.once(clientEvent: .connect) { (object, ack) in
                self.socket.emit(event, items)
                print("EMITTED EVENT: \(event), WITH ITEMS: \(items)")
            }
        case .notConnected:
            print("ERROR WITH EMITTING EVENT \(event): WEBSOCKET NOT CONNECTED\n")
            socket.once(clientEvent: .connect) { data, ack in
                self.socket.emit(event, items)
            }
            socket.connect()
        case .disconnected:
            print("ERROR WITH EMITTING EVENT \(event): WEBSOCKET DISCONNECTED\n")
            socket.once(clientEvent: .connect) { data, ack in
                self.socket.emit(event, items)
            }
            socket.connect()
        default:
            break
        }
    }
    
    func emit(event: String) {
        print("Emitting event: \(event)")
        
        switch self.socket.status {
        case .connected:
            self.socket.emit(event)
            print("EMITTED EVENT: \(event)")
        case .connecting:
            print("WEBSOCKET STILL CONNECTING, WILL EMIT EVENT \(event) ONCE IT CONNECTS ... \n")
            self.socket.once(clientEvent: .connect) { (object, ack) in
                self.socket.emit(event)
                print("EMITTED EVENT: \(event)")
            }
        case .notConnected:
            print("ERROR WITH EMITTING EVENT \(event): WEBSOCKET NOT CONNECTED\n")
            socket.once(clientEvent: .connect) { data, ack in
                self.socket.emit(event)
            }
            socket.connect()
        case .disconnected:
            print("ERROR WITH EMITTING EVENT \(event): WEBSOCKET DISCONNECTED\n")
            socket.once(clientEvent: .connect) { data, ack in
                self.socket.emit(event)
            }
            socket.connect()
        default:
            break
        }
    }
}
