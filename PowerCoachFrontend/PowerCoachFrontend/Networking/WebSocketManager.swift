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
    
    @Published var homeDisplay = "Connecting..."
    @Published var workoutPlanDisplay = "Connecting..."
    @Published var forumDisplay = "Connecting..."
    @Published var powerCoachMessage = "Connecting..."
    @Published var useridString = "User ID not found"
    
    init() {
        self.manager = SocketManager(socketURL: URL(string: "https://powercoach-1.onrender.com")!, config: [.log(true), .compress, .forceWebsockets(true), .path("/socket.io")])
        self.socket = self.manager.defaultSocket
        
        socket.on(clientEvent: .connect) { (data, ack) in
            print("EVENT: SOCKET CONNECTED.")
            if let sidDict = data[1] as? [String: Any],
                let sidString = sidDict["sid"] as? String,
                    let sidData = sidString.data(using: .utf8) {
                        DispatchQueue.main.async {
                            self.useridString = "Hi, User \(String(decoding: sidData, as: UTF8.self))!"
                        }
            }
            DispatchQueue.main.async {
                self.homeDisplay = "Home screen in progress..."
                self.workoutPlanDisplay = "Workout plan screen in progress..."
                self.forumDisplay = "Forum screen in progress..."
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
        
//        socket.on("powercoach_connection") { (data, ack) in
//            if let powerCoachString = data[0] as? String,
//               let powerCoachData = powerCoachString.data(using: .utf8) {
//                DispatchQueue.main.async {
//                    self.powerCoachActive = true
//                    self.powerCoachMessage = String(decoding: powerCoachData, as: UTF8.self)
//                }
//            }
//        }
//        socket.on("powercoach_disconnection") { (data, ack) in
//            if let powerCoachString = data[0] as? String,
//               let powerCoachData = powerCoachString.data(using: .utf8) {
//                DispatchQueue.main.async {
//                    self.powerCoachMessage = String(decoding: powerCoachData, as: UTF8.self)
//                    self.powerCoachActive = false
//                }
//            }
//        }
    }
    
    func emit(event: String, with items: String) {
        print("EMITTING EVENT: \(event)")
        
        switch self.socket.status {
        case .connected:
            self.socket.emit(event, items)
            print("EMITTED EVENT: \(event), WITH ITEMS: \(items)")
            break
        case .connecting:
            print("WEBSOCKET STILL CONNECTING, WILL EMIT EVENT \(event) ONCE IT CONNECTS ... \n")
            self.socket.once(clientEvent: .connect) { (object, ack) in
                self.socket.emit(event, items)
                print("EMITTED EVENT: \(event), WITH ITEMS: \(items)")
            }
            break
        case .notConnected:
            print("ERROR WITH EMITTING EVENT \(event): WEBSOCKET NOT CONNECTED\n")
            break
        case .disconnected:
            print("ERROR WITH EMITTING EVENT \(event): WEBSOCKET DISCONNECTED\n")
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
            print("EMITTED EVENT: \(event)")
            break
        case .connecting:
            print("WEBSOCKET STILL CONNECTING, WILL EMIT EVENT \(event) ONCE IT CONNECTS ... \n")
            self.socket.once(clientEvent: .connect) { (object, ack) in
                self.socket.emit(event)
                print("EMITTED EVENT: \(event)")
            }
            break
        case .notConnected:
            print("ERROR WITH EMITTING EVENT \(event): WEBSOCKET NOT CONNECTED\n")
            break
        case .disconnected:
            print("ERROR WITH EMITTING EVENT \(event): WEBSOCKET DISCONNECTED\n")
            break
        default:
            break
        }
    }
    
//    func handlePowerCoachMessage(data: String) {
//        print("PowerCoachMessage is being handled")
//        print("Received message: \(data)")
//        
//        // Parse the JSON string to extract the message
//        if let jsonData = data.data(using: .utf8),
//           let decodedMessage = try? JSONDecoder().decode(PowerCoachMessage.self, from: jsonData) {
//            // Update the powerCoachMessage property with the decoded message
//            DispatchQueue.main.async {
//                self.powerCoachMessage = decodedMessage.json_data
//                print(decodedMessage.json_data)
//            }
//        }
//    }

}
