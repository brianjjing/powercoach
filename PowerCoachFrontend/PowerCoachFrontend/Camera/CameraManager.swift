//
//  CameraManager.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 4/12/25.
//

import AVFoundation
import Foundation

class CameraManager: ObservableObject {
    @Published var session = AVCaptureSession()
    private var currentCameraPosition: AVCaptureDevice.Position = .back

    init() {
        configureSession(for: currentCameraPosition)
    }

    func configureSession(for position: AVCaptureDevice.Position) {
        session.beginConfiguration()
        session.inputs.forEach { session.removeInput($0) }

        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: position),
              let input = try? AVCaptureDeviceInput(device: device),
              session.canAddInput(input) else {
            print("Failed to access camera at position \(position)")
            session.commitConfiguration()
            return
        }

        session.addInput(input)
        session.commitConfiguration()

        if !session.isRunning {
            DispatchQueue.global(qos: .userInitiated).async {
                self.session.startRunning()
            }
        }

        self.currentCameraPosition = position
    }

    func flipCamera() {
        let newPosition: AVCaptureDevice.Position = currentCameraPosition == .back ? .front : .back
        configureSession(for: newPosition)
    }
}
