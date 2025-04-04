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
    @Published var powerCoachMessage = "Loading ..."
    @Published var userid = "Unknown user ID"
    
    init() {
        self.manager = SocketManager(socketURL: URL(string: "https://powercoach-1.onrender.com")!, config: [.log(true), .compress, .forceWebsockets(true)])
        self.socket = self.manager.defaultSocket
        
        socket.on(clientEvent: .connect) { (data, ack) in
            print("Socket connected")
            self.displayString = "POWERCOACH"
        }
        
        socket.on(clientEvent: .disconnect) { (data, ack) in
            print("Socket disconnected")
        }
        
        socket.onAny { (event) in
            print("Received event: \(String(describing: event.event)), with items: \(String(describing: event.items))")
        }
        
        socket.on("powercoach_message") { (data, ack) in
            print("POWERCOACH MESSAGE IS RECEIVED")
            print(data)
            print(type(of: data))
            if let powerCoachString = data[0] as? String,
               let powerCoachData = powerCoachString.data(using: .utf8) {
                DispatchQueue.main.async {
                    self.powerCoachMessage = String(decoding: powerCoachData, as: UTF8.self)
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
    
    func emit(event: String, with items: NSArray = []) {
        print("Emitting event: \(event)")
        
        switch self.socket.status {
        case .connected:
            self.socket.emit(event, items)
            print("Emitted event: \(event), with items: \(items)")
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


//RAW WEBSOCKET IMPLEMENTATION:

//    var webSocketTask: URLSessionWebSocketTask?
//    //UrlSession manages network tasks (api calls, websocket tasks, etc)
//    var urlSession: URLSession!
//    //Current Engine.IO
//    let webSocketURL = "ws://127.0.0.1:5000/socket.io/?EIO=4&transport=websocket"
//
//    //@Published changes the variable within a CLASS (can be across multiple views)
//    var isConnected = false
//    @Published var displayString = "Connecting..."
//    @Published var powerCoachMessage = "Loading ..."
//    @Published var userid = "Unknown user ID"
//
//    //Private so it cannot be initialized outside the class. Here it is only initialized once in the class in the first line, making it a singleton.
//    //Override since it overrides the NSObject initializer
////    private override init() {
////        super.init() //Initializing parent class (NSObject) so that self can be initialized
////        let configuration = URLSessionConfiguration.default
////        urlSession = URLSession(configuration: configuration, delegate: self, delegateQueue: OperationQueue())
////    }
//
//    func connect() {
//        print("Connecting ...")
//        guard let url = URL(string: webSocketURL) else {
//            print("Invalid URL.")
//            return
//        }
//        print("url object created")
//
//        let request = URLRequest(url: url)
//        print("url request created")
//
//        webSocketTask = urlSession.webSocketTask(with: request)
//        print("webSocketTask initialized")
//        //I just need to determine where resume() is ...
//        webSocketTask?.resume()
//        print("webSocketTask started - HTTP request sent")
//        //^^^ Once this is done, didOpenWithProtocol delegate method automatically is invoked
//    }
//
//    func disconnect() {
//        webSocketTask?.cancel(with: .goingAway, reason: nil)
//        isConnected = false
//    }
//
//    func send(message: String) {
//        //CONTINUOUSLY SEND MESSAGES!!!
//        let wsMessage = URLSessionWebSocketTask.Message.string(message)
//        webSocketTask?.send(wsMessage, completionHandler: { error in
//            if let error = error {
//                print("WebSocket sending error: \(error)")
//                return //Only do this for infinite loops
//            }
//        })
//    }
//
//    func listen() {
//        //[weak self] prevents a strong reference cycle between the WebSocketManager instance (delegate) and the closure.
//        webSocketTask?.receive { [weak self] result in
//            switch result {
//            case .success(let message):
//                switch message {
//                case .string(let text):
//                    print("Received JSON string: \(text)")
//
//                    let packetType = text.prefix(1)
//                    let payloadString = String(text.dropFirst())
//
//                    switch packetType {
//                    case "2":
//                        print("Received a ping")
//                        if payloadString == "" {
//                            self?.send(message: "3")
//                            print("Sent a pong")
//                        }
//                        else {
//                            if let data = payloadString.data(using: .utf8) {
//                                print("Data: \(data)")
////                                do {
////                                    let decodedConnection = try JSONDecoder().decode(Connection.self, from: data)
////                                    print("Decoded Connection: \(decodedConnection)")
////
////                                    //Dispatches this background task asynchronously to the main thread
////                                    DispatchQueue.main.async {
////                                        self?.displayString = "POWERCOACH"
////                                        self?.userid = decodedConnection.sid
////                                    }
////                                } catch {
////                                    print("Failed to decode JSON: \(error)")
////                                }
//                            }
//                            //print(String(describing: payloadString))
//                            print("CODE WILL BE WRITTEN TO TAKE IN 2 DATA")
//                        }
//
//                    case "0":
//                        if let data = payloadString.data(using: .utf8) {
//                            do {
//                                let decodedConnection = try JSONDecoder().decode(Connection.self, from: data)
//                                print("Decoded Connection: \(decodedConnection)")
//
//                                //Dispatches this background task asynchronously to the main thread
//                                DispatchQueue.main.async {
//                                    self?.displayString = "POWERCOACH"
//                                    self?.userid = decodedConnection.sid
//                                }
//                            } catch {
//                                print("Failed to decode JSON: \(error)")
//                            }
//                        }
//                    default:
//                        print("Unknown packet type: \(packetType)")
//                    }
//                default:
//                    print("Unknown data type, data not sent as a JSON string")
//                }
//            case .failure(let error):
//                print("WebSocket receiving error: \(error)")
//                return //should return only if the receiving error is an infinite loop (Socket is not connected) or goes on too long
//            }
//            // Recursively, continuously listen
//            self?.listen()
//        }
//    }
//}
//
//extension WebSocketManager: URLSessionWebSocketDelegate {
//    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
//        print("WebSocket connected")
//        isConnected = true
//        print("isConnected set to true")
//        //Ping???
//        listen()
//        print("Message listening started")
//    }
//
//    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
//        print("WebSocket disconnected, for reason: \(String(describing: reason))")
//        isConnected = false
//    }
