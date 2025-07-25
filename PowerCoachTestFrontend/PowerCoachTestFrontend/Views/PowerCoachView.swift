//
//  PowerCoachView.swift
//  PowerCoachTestFrontend
//
//  Created by Brian Jing on 7/12/25.
//

import SwiftUI
import AVFoundation

struct PowerCoachView: View {
    @Environment(\.dismiss) var dismiss //@Environment() gives access to system-defined values. In this case it's the keypath to the .dismiss function.
    @EnvironmentObject var webSocketManager: WebSocketManager //Environment object makes it so that it uses the singleton, which is defined below the #Preview at the bottom of the file
    @StateObject private var cameraManager: CameraManager //StateObject is tied to the updates of the view
    
    init(webSocketManager: WebSocketManager) {
        //This _cameraManager variable accesses the backing storage (the wrapper of type StateObject<CameraManager>, whereas cameraManager is the get-only wrapped value, the instance of CameraManager). We are just initializing that here, and it is invisibly created.
        _cameraManager = StateObject(wrappedValue: CameraManager(webSocketManager: webSocketManager))
    }
    
    var body: some View {
        
        ZStack {
            CameraView(session: cameraManager.session)
                .edgesIgnoringSafeArea(.all)
            
            VStack {
                Text(webSocketManager.powerCoachMessage)
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.black)
                    .padding()
                    .background(Color.white)
                    .cornerRadius(12)
                    .multilineTextAlignment(.center)
                
                Spacer()
                
                HStack {
                    Spacer()

                    Button(action: {
                        cameraManager.flipCamera()
                    }) {
                        Image(systemName: "arrow.triangle.2.circlepath.camera")
                            .font(.title2)
                            .foregroundColor(.black)
                            .padding()
                            .background(Color.white)
                            .clipShape(Circle())
                            .shadow(radius: 6)
                    }
                    .padding(.bottom, UIScreen.main.bounds.height/25)
                    .padding(.trailing, UIScreen.main.bounds.width/20)
                }
            }
            .padding()
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                        Button(action: {
                            dismiss()
                        }) {
                            Image(systemName: "x.circle.fill")
                                .font(.system(size: UIScreen.main.bounds.width/15))
                                .foregroundColor(.white)
                        }
                }
                ToolbarItem(placement: .principal) {
                    Text("POWERCOACH")
                        .font(.title)
                        .fontWeight(.black)
                        .foregroundColor(Color.red)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .foregroundColor(.black)
                }
            }
        }
//        .navigationTitle("POWERCOACH")
//        .navigationBarTitleDisplayMode(.inline)
        .navigationBarBackButtonHidden(true)
        .onAppear {
            webSocketManager.emit(event: "start_powercoach")
        }
        .onDisappear {
            webSocketManager.emit(event: "stop_powercoach")
        }
        .onChange(of: webSocketManager.powerCoachMessage, initial: false) { oldMessage, newMessage in // iOS 17+ syntax
            // Ensure you don't speak initial "Connecting..." or empty messages
            if !newMessage.isEmpty && newMessage != "Connecting..." && newMessage != "Message loading..." {
                SpeechSynthesizerManager.shared.speak(newMessage)
            }
        }
    }
}

//This is where it is initialized. #Preview is just a tag that makes a preview available on the right.
#Preview {
    PowerCoachView(webSocketManager: WebSocketManager.shared)
        .environmentObject(WebSocketManager.shared)
}
