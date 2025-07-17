//
//  WebSocketManager.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 7/12/25.
//

import Foundation
import SocketIO

//MOVE ALL THE COMMUNICATION LOGIC HERE!!!!

//The websocketmanager instance is the delegate.
//ObservableObject is the protocol that tells the class to watch out for property changes. @Published signifies which properties are to be updated in the views upon being changed.
class WebSocketManager: ObservableObject {
    static let shared = WebSocketManager() //This is the singleton
    
    var manager: SocketManager!
    var socket: SocketIOClient!
    
    @Published var homeDisplay = "Connecting..."
    @Published var powerCoachMessage = "Connecting..."
    
    init() {
        self.manager = SocketManager(socketURL: URL(string: "http://192.168.1.219:10000")!, config: [.log(true), .compress, .forceWebsockets(true), .path("/socket.io")])
        self.socket = self.manager.defaultSocket
        
        socket.on(clientEvent: .connect) { (data, ack) in
            print("EVENT: SOCKET CONNECTED.")
            DispatchQueue.main.async {
                self.homeDisplay = "Home screen in progress..."
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
        if socket.status == .notConnected || socket.status == .disconnected {
            socket.connect()
        } else {
            print("WEBSOCKET ALREADY CONNECTED. STATUS: \(socket.status)")
        }
        print("WEBSOCKET CONNECTED ...")
        
        print("REMINDER: Turn off firewall and filters when you test from phone to computer when testing. THEN PUT EM BACK ON ONCE YOURE DONE")
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
