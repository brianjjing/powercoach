//
//  CameraManager.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 7/12/25.
//

import AVFoundation
import Foundation
import SwiftUI

//Pipeline: Camera device --> camera session --> output object --> captureOutput method (delegate method)

class CameraManager: NSObject, ObservableObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    @Published var session = AVCaptureSession()
    private var currentCameraPosition: AVCaptureDevice.Position = .front
    private let webSocketManager: WebSocketManager
    
    private var canEmitFrames = false //Makes for a 1-second delay for starting the emitting
    
    init(webSocketManager: WebSocketManager) {
        self.webSocketManager = webSocketManager
        super.init()
        configureSession(for: currentCameraPosition)
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.canEmitFrames = true
        }
    }

    func configureSession(for position: AVCaptureDevice.Position) {
        session.beginConfiguration()
        session.inputs.forEach { session.removeInput($0) }
        
        //Just have this display on the actual screen instead
        //Guard sees if the variable acc has a value or not
        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: position),
              let input = try? AVCaptureDeviceInput(device: device),
              session.canAddInput(input) else {
                print("ERROR: COULDN'T CREATE INPUT DEVICE. COULDN'T ACCESS CAMERA @ POSITION \(position)")
                session.commitConfiguration()
                return
            }
        session.addInput(input)
        
        let output = AVCaptureVideoDataOutput()
        //setting the CameraManager instance as the delegate for handling the output frames.
        output.setSampleBufferDelegate(self, queue: DispatchQueue(label: "frameHandlingQueue")) //naming the queue (thread) we are handling the frames on, since it is asynchronus and happening in the background
        if session.canAddOutput(output) {
            session.addOutput(output)
        } else {
            print("Failed to add output")
            session.commitConfiguration()
            return
        }
        
        session.commitConfiguration()

        if !session.isRunning {
            DispatchQueue.global(qos: .userInitiated).async {
                self.session.startRunning()
            }
        }

        self.currentCameraPosition = position
    }
    
    private var lastSentTime = Date(timeIntervalSince1970: 0) // store last send time
    private let frameSendInterval: TimeInterval = 2 // seconds between frames (0.5s = 2 FPS)
    
    //Implementing this optional method to deal with frames. Every time a video frame is captured by the output variable, this method will be called, using the frameHandlingQueue
    func captureOutput(_ output: AVCaptureOutput, //output is the OBJECT PRODUCING video frames and sending to delegate
                       didOutput sampleBuffer: CMSampleBuffer, //A sample buffer is just a raw video frame
                       from connection: AVCaptureConnection) {

        guard canEmitFrames else { return }
        
        let now = Date()
        guard now.timeIntervalSince(lastSentTime) >= frameSendInterval else { return }
        lastSentTime = now //Only updated once the code gets past the guard statement (so only once every 0.5 seconds)
                
        // UNDERSTAND THE IMAGE TYPE CONVERSION. MAKE THIS PIPELINE SLOWER:
        // CMSampleBuffer → CVPixelBuffer → CIImage → CGImage → UIImage (understand the data types later)
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        let ciImage = CIImage(cvImageBuffer: pixelBuffer)
        let context = CIContext()
        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else { return }
        let uiImage = UIImage(cgImage: cgImage)
        // Convert to JPEG data
        guard let jpegData = uiImage.jpegData(compressionQuality: 0.1) else { return }
        // NEED TO MAKE THE JPEG GOOD QUALITY TOO!!!!! 0.4 IS JUST FOR SMALLER BASE64 MESSAGE!!!

        // Convert to base64 string
        let base64String = jpegData.base64EncodedString()
        print("SENDING BASE64 STRING - # OF CHARACTERS:", base64String.count)
        webSocketManager.emit(event: "handle_powercoach_frame", with: base64String)
    }
    
    func flipCamera() {
        let newPosition: AVCaptureDevice.Position = currentCameraPosition == .back ? .front : .back
        configureSession(for: newPosition)
    }
}
