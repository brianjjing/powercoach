//
//  CameraManager.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 4/12/25.
//

import AVFoundation
import Foundation
import SwiftUI

class CameraManager: NSObject, ObservableObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    @Published var session = AVCaptureSession()
    private var currentCameraPosition: AVCaptureDevice.Position = .front
    @EnvironmentObject var webSocketManager: WebSocketManager

    override init() {
        super.init()
        configureSession(for: currentCameraPosition)
    }

    func configureSession(for position: AVCaptureDevice.Position) {
        session.beginConfiguration()
        session.inputs.forEach { session.removeInput($0) }
        //session.outputs.forEach { session.removeOutput($0) }
        
        //Just have this display on the actual screen instead
        //Guard sees if the variable acc has a value or not
        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: position),
              let input = try? AVCaptureDeviceInput(device: device),
              session.canAddInput(input) else {
                print("Failed to create input: couldn't access camera at position \(position)")
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
    
    //Implementing this optional method to deal with frames. Every time a video frame is captured by the output variable, this method will be called, using the frameHandlingQueue, since .
    func captureOutput(_ output: AVCaptureOutput,
                       didOutput sampleBuffer: CMSampleBuffer, //A sample buffer is just a raw video frame
                       from connection: AVCaptureConnection) {
        
        // UNDERSTAND THE IMAGE TYPE CONVERSION:
        // CMSampleBuffer → CVPixelBuffer → CIImage → CGImage → UIImage (understand the data types later)
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        let ciImage = CIImage(cvImageBuffer: pixelBuffer)
        let context = CIContext()
        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else { return }

        let uiImage = UIImage(cgImage: cgImage)

        // Convert to JPEG data
        guard let jpegData = uiImage.jpegData(compressionQuality: 0.7) else { return }

        // Convert to base64 string
        let base64String = jpegData.base64EncodedString()
        webSocketManager.emit(event: "handle_powercoach_frame", with: [base64String])
    }

    
    func flipCamera() {
        let newPosition: AVCaptureDevice.Position = currentCameraPosition == .back ? .front : .back
        configureSession(for: newPosition)
    }
}
