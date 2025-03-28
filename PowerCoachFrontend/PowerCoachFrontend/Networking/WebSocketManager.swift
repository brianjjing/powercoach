//
//  WebSocketManager.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/18/25.
//

import Foundation

//MOVE ALL THE COMMUNICATION LOGIC HERE!!!!

//The websocketmanager instance is the delegate.
//ObservableObject is the protocol that tells the class to watch out for property changes. @Published signifies which properties are to be updated in the views upon being changed.
class WebSocketManager: NSObject, ObservableObject {
    static let shared = WebSocketManager()
    
    var webSocketTask: URLSessionWebSocketTask?
    //UrlSession manages network tasks (api calls, websocket tasks, etc)
    var urlSession: URLSession!
    //Current Engine.IO
    let webSocketURL = "ws://127.0.0.1:5000/socket.io/?EIO=4&transport=websocket"
    
    //@Published changes the variable within a CLASS (can be across multiple views)
    var isConnected = false
    @Published var displayString = "Connecting..."
    @Published var powerCoachMessage = "Loading ..."
    @Published var userid = "Unknown user ID"
    
    //Private so it cannot be initialized outside the class. Here it is only initialized once in the class in the first line, making it a singleton.
    //Override since it overrides the NSObject initializer
    private override init() {
        super.init() //Initializing parent class (NSObject) so that self can be initialized
        let configuration = URLSessionConfiguration.default
        urlSession = URLSession(configuration: configuration, delegate: self, delegateQueue: OperationQueue())
    }
    
    func connect() {
        print("Connecting ...")
        guard let url = URL(string: webSocketURL) else {
            print("Invalid URL.")
            return
        }
        print("url object created")
        
        let request = URLRequest(url: url)
        print("url request created")
        
        webSocketTask = urlSession.webSocketTask(with: request)
        print("webSocketTask initialized")
        //I just need to determine where resume() is ...
        webSocketTask?.resume()
        print("webSocketTask started - HTTP request sent")
        //^^^ Once this is done, didOpenWithProtocol delegate method automatically is invoked
    }
    
    func disconnect() {
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        isConnected = false
    }
    
    func send(message: String) {
        //CONTINUOUSLY SEND MESSAGES!!!
        let wsMessage = URLSessionWebSocketTask.Message.string(message)
        webSocketTask?.send(wsMessage, completionHandler: { error in
            if let error = error {
                print("WebSocket sending error: \(error)")
            }
        })
    }
    
    func listen() {
        //[weak self] prevents a strong reference cycle between the WebSocketManager instance (delegate) and the closure.
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    print("Received JSON string: \(text)")
                    
                    let packetType = text.prefix(1)
                    let payloadString = String(text.dropFirst())
                    
                    switch packetType {
                    case "2":
                        print("Received a ping")
                        if payloadString == "" {
                            self?.send(message: "3")
                            print("Sent a pong")
                        }
                        else {
                            print("CODE WILL BE WRITTEN TO TAKE IN 2 DATA")
                        }
                        
                    case "0":
                        if let data = payloadString.data(using: .utf8) {
                            do {
                                let decodedConnection = try JSONDecoder().decode(Connection.self, from: data)
                                print("Decoded Connection: \(decodedConnection)")

                                //Dispatches this background task asynchronously to the main thread
                                DispatchQueue.main.async {
                                    self?.displayString = "POWERCOACH"
                                    self?.userid = decodedConnection.sid
                                }
                            } catch {
                                print("Failed to decode JSON: \(error)")
                            }
                        }
                    default:
                        print("Unknown packet type: \(packetType)")
                    }
                default:
                    print("Unknown data type, data not sent as a JSON string")
                }
            case .failure(let error):
                print("WebSocket receiving error: \(error)")
                return //should return only if the receiving error is an infinite loop (Socket is not connected) or goes on too long
            }
            // Recursively, continuously listen
            self?.listen()
        }
    }
}

extension WebSocketManager: URLSessionWebSocketDelegate {
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
        print("WebSocket connected")
        isConnected = true
        print("isConnected set to true")
        //Ping???
        listen()
        print("Message listening started")
    }
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        print("WebSocket disconnected, for reason: \(String(describing: reason))")
        isConnected = false
    }
}
