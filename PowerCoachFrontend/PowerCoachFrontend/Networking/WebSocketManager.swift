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
    @Published var isConnected = false
    @Published var detectionString = "String loading..."
    
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
    
    //How to continuously call?
    private func listen() {
        //CONTINUOUSLY LISTEN!!!
        
        //[weak self] prevents a strong reference cycle between the WebSocketManager instance (delegate) and the closure.
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    print("Received JSON string: \(text)")
                    
                    // Decode the JSON string into the ImageFeed model
                    if let data = text.data(using: .utf8) {
                        do {
                            let decoded = try JSONDecoder().decode(ImageFeed.self, from: data)
                            print("Decoded Detection: \(decoded)")

                            DispatchQueue.main.async {
                                self?.detectionString = decoded.jsonData
                            }
                        } catch {
                            print("Failed to decode JSON: \(error)")
                        }
                    }
                default:
                    print("Unknown data type, data not sent as a JSON string")
                }
            case .failure(let error):
                print("WebSocket receiving error: \(error)")
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

//            .onChange(of: detectionString, initial: true) {
//                //Task allows for the asynchronous 'try await getDetection' line to be passed synchronously, which is needed for this closure parameter.
//                Task {
//                    detectionString = "NEW detection"
//                    print("NEW detection")
//                    do {
//                        detectionString = "Getting detection ..."
//                        detection = try await getDetection()
//                        detectionString = "Response decoded"
//                        detectionString = "Detection gotten"
//                        detectionString = "Detection converted to string"
//                        detectionString = String(describing: detection)
//                        print(iteration)
//                        iteration = iteration + 1
//                    } catch GHError.invalidURL {
//                        detectionString = "Invalid URL"
//                        print("Invalid URL")
//                    } catch GHError.invalidResponse {
//                        detectionString = "Invalid response"
//                        print("Invalid response")
//                    } catch GHError.invalidData {
//                        detectionString = "Invalid data, line 42"
//                        print("Invalid data, line 42")
//                    } catch {
//                        detectionString = "Unspecified error"
//                        print("Unspecified error")
//                    }
//                }
//            }

//    func getDetection() async throws -> ImageFeed {
//
//        //Converts to URL object:
//        guard let url = URL(string: endpoint) else { throw GHError.invalidURL }
//        detectionString = "Changed to a URL object"
//
//        detectionString = "Getting data and response"
////        let session = URLSession(
////            configuration: .default,
////            delegate: self,
////            delegateQueue: .main)
////
////        let webSocket = session.webSocketTask(with: url)
//        let (data, response) = try await URLSession.shared.data(from: url)
//        detectionString = "Got data and response"
//        print("Data:", data)
//        print("Response:", response)
//
//        detectionString = "Changing response to HTTPURLRESPONSE"
//        guard let response = response as? HTTPURLResponse, response.statusCode == 200 else {
//            detectionString = "Invalid response"
//            throw GHError.invalidResponse
//        }
//        detectionString = "Response changed to HTTPURLRESPONSE"
//
//        detectionString = "Decoding response ..."
//        do {
//            let decoder = JSONDecoder()
//            decoder.keyDecodingStrategy = .convertFromSnakeCase
//            return try decoder.decode(ImageFeed.self, from: data)
//        } catch {
//            detectionString = "Invalid data, line 94"
//            print("Invalid data, line 94")
//            throw GHError.invalidData
//        }
//    }
