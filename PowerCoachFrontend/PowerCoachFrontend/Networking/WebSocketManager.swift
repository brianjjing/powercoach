//
//  WebSocketManager.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/18/25.
//

import Foundation
import SocketIO

//MOVE ALL THE COMMUNICATION LOGIC HERE!!!!

//The websocketmanager instance is the delegate.
//ObservableObject is the protocol that tells the class to watch out for property changes. @Published signifies which properties are to be updated in the views upon being changed.
class WebSocketManager: ObservableObject {
    static let shared = WebSocketManager()
    
    var manager: SocketManager!
    var socket: SocketIOClient!
    
    @Published var displayString = "Connecting..."
    @Published var powerCoachMessage = "PowerCoach connecting..."
    @Published var powerCoachActive = false
    @Published var useridString = "User ID not found"
    
    init() {
        self.manager = SocketManager(socketURL: URL(string: "https://powercoach-1.onrender.com")!, config: [.log(true), .compress, .forceWebsockets(true), .path("/socket.io")])
        self.socket = self.manager.defaultSocket
        
        socket.on(clientEvent: .connect) { (data, ack) in
            print("Socket connected")
//            print(data)
//            print(type(of: data))
            if let sidDict = data[1] as? [String: Any],
                let sidString = sidDict["sid"] as? String,
                    let sidData = sidString.data(using: .utf8) {
                        DispatchQueue.main.async {
                            self.useridString = "User \(String(decoding: sidData, as: UTF8.self)) logged in"
                        }
            }
            self.displayString = "POWERCOACH"
        }
        
        socket.on(clientEvent: .disconnect) { (data, ack) in
            print("Socket disconnected")
//            print(data)
//            print(type(of: data))
        }
        
        socket.onAny { (event) in
            print("Received event: \(String(describing: event.event)), with items: \(String(describing: event.items))")
        }
        
        socket.on("powercoach_connection") { (data, ack) in
            if let powerCoachString = data[0] as? String,
               let powerCoachData = powerCoachString.data(using: .utf8) {
                DispatchQueue.main.async {
                    self.powerCoachActive = true
                    self.powerCoachMessage = String(decoding: powerCoachData, as: UTF8.self)
                }
            }
        }
        
        socket.on("powercoach_message") { (data, ack) in
            print("POWERCOACH MESSAGE IS RECEIVED")
//            print(data)
//            print(type(of: data))
            if let powerCoachString = data[0] as? String,
               let powerCoachData = powerCoachString.data(using: .utf8) {
                DispatchQueue.main.async {
                    self.powerCoachMessage = String(decoding: powerCoachData, as: UTF8.self)
                }
            }
        }
        
        socket.on("powercoach_disconnection") { (data, ack) in
            if let powerCoachString = data[0] as? String,
               let powerCoachData = powerCoachString.data(using: .utf8) {
                DispatchQueue.main.async {
                    self.powerCoachMessage = String(decoding: powerCoachData, as: UTF8.self)
                    self.powerCoachActive = false
                }
            }
        }
        
        socket.on("test_response") { (data, ack) in
            print("test_response received")
            print(data)
//            print(data)
//            print("Received powercoach_message")
//            self.handlePowerCoachMessage(data: data)
        }
        
//        socket.connect(timeoutAfter: 0) {
//            print(" --------- ---- %d", self.socket.status)
//        }
        
        socket.connect()
        
    }
    
    func emit(event: String, with items: [String]) {
        print("Emitting event: \(event)")
        
        switch self.socket.status {
        case .connected:
            self.socket.emit(event, items)
            print("Emitted event: \(event), with json String: \(items)")
            break
        case .connecting:
            print(" \n\n ------- Connecting ----- \n\n", event)
            self.socket.once(clientEvent: .connect) { (object, ack) in
                self.socket.emit(event, items)
                print(" \n\n ------- ConnectOnce ----- \n\n", event)
            }
            break
        case .notConnected:
            print(" \n\n ------- Not Connected ----- \n\n", event)
            break
        case .disconnected:
            print(" \n\n ------- Disconnected ----- \n\n", event)
            break
        default:
            break
        }
    }
    
    func emit(event: String) {
        print("Emitting event: \(event)")
        
        switch self.socket.status {
        case .connected:
            self.socket.emit(event)
            print("Emitted event: \(event)")
            break
        case .connecting:
            print(" \n\n ------- Connecting ----- \n\n", event)
            self.socket.once(clientEvent: .connect) { (object, ack) in
                self.socket.emit(event)
                print(" \n\n ------- ConnectOnce ----- \n\nEmitting event: \(event)")
            }
            break
        case .notConnected:
            print(" \n\n ------- Not Connected ----- \n\n", event)
            break
        case .disconnected:
            print(" \n\n ------- Disconnected ----- \n\n", event)
            break
        default:
            break
        }
    }
    
    func handlePowerCoachMessage(data: [Any]) {
        // Data will be an array where the first element is the event name
        // and the second element is the actual message (as a string in this case)
        print("PowerCoachMessage is being handled")
        if let jsonString = data[1] as? String {
            print("Received message: \(jsonString)")
            
            // Parse the JSON string to extract the message
            if let jsonData = jsonString.data(using: .utf8),
               let decodedMessage = try? JSONDecoder().decode(PowerCoachMessage.self, from: jsonData) {
                // Update the powerCoachMessage property with the decoded message
                DispatchQueue.main.async {
                    self.powerCoachMessage = decodedMessage.json_data
                    print(decodedMessage.json_data)
                }
            }
        }
    }

}
