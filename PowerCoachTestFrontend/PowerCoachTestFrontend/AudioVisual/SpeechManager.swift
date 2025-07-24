//
//  SpeechManager.swift
//  PowerCoachTestFrontend
//
//  Created by Brian Jing on 7/24/25.
//

import AVFoundation

@MainActor
class SpeechSynthesizerManager: NSObject, AVSpeechSynthesizerDelegate { // No need for ObservableObject here unless you want to publish its own state
    static let shared = SpeechSynthesizerManager()
    private let synthesizer = AVSpeechSynthesizer()
    
    //Initializing it here, not in PowerCoachView, so that it can be used in other screens too
    private override init() {
        super.init()
        synthesizer.delegate = self //Delegate receives messages abt the synthesizer's lifecycle
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default, options: [.duckOthers])
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("Failed to set audio session category: \(error.localizedDescription)")
        }
    }

    func speak(_ text: String, language: String = "en-US", rate: Float = AVSpeechUtteranceDefaultSpeechRate, pitch: Float = 1.0, volume: Float = 1.0) {
        // Stop any previous speech to avoid overlapping

        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: language)
        utterance.rate = rate
        utterance.pitchMultiplier = pitch
        utterance.volume = volume
        
        if synthesizer.isSpeaking {
            synthesizer.stopSpeaking(at: .immediate)
        }
        synthesizer.speak(utterance)
    }
}
