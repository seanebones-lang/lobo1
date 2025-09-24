//
//  VoiceInput.swift
//  NextElevenTattooPro
//
//  Created by APOLLO AI on 09/21/2025.
//  Copyright © 2025 NextEleven Studios. All rights reserved.
//

import Foundation
import Speech
import AVFoundation
import UIKit

class VoiceInputManager: ObservableObject {
    @Published var isAuthorized = false
    @Published var isRecording = false
    @Published var recognizedText = ""
    @Published var errorMessage: String?
    
    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let audioEngine = AVAudioEngine()
    
    func setup() {
        print("🌊 APOLLO Voice Input Initializing...")
        
        // Request speech recognition authorization
        requestSpeechRecognitionAuthorization()
        
        // Setup audio session
        setupAudioSession()
        
        print("✅ Voice Input Manager initialized")
    }
    
    private func requestSpeechRecognitionAuthorization() {
        SFSpeechRecognizer.requestAuthorization { [weak self] authStatus in
            DispatchQueue.main.async {
                switch authStatus {
                case .authorized:
                    self?.isAuthorized = true
                    print("✅ Speech recognition authorized")
                case .denied:
                    self?.isAuthorized = false
                    self?.errorMessage = "Speech recognition access denied"
                    print("❌ Speech recognition denied")
                case .restricted:
                    self?.isAuthorized = false
                    self?.errorMessage = "Speech recognition restricted"
                    print("❌ Speech recognition restricted")
                case .notDetermined:
                    self?.isAuthorized = false
                    self?.errorMessage = "Speech recognition not determined"
                    print("❌ Speech recognition not determined")
                @unknown default:
                    self?.isAuthorized = false
                    self?.errorMessage = "Unknown speech recognition status"
                    print("❌ Unknown speech recognition status")
                }
            }
        }
    }
    
    private func setupAudioSession() {
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            print("❌ Failed to setup audio session: \(error)")
            errorMessage = "Failed to setup audio session"
        }
    }
    
    func startRecording(completion: @escaping (String) -> Void) {
        guard isAuthorized else {
            errorMessage = "Speech recognition not authorized"
            return
        }
        
        guard !isRecording else { return }
        
        // Cancel any previous recognition task
        if let recognitionTask = recognitionTask {
            recognitionTask.cancel()
            self.recognitionTask = nil
        }
        
        // Setup audio session
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            errorMessage = "Failed to setup audio session"
            return
        }
        
        // Create recognition request
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else {
            errorMessage = "Unable to create recognition request"
            return
        }
        
        recognitionRequest.shouldReportPartialResults = true
        
        // Check if speech recognizer is available
        guard let speechRecognizer = speechRecognizer, speechRecognizer.isAvailable else {
            errorMessage = "Speech recognizer not available"
            return
        }
        
        // Start recognition task
        recognitionTask = speechRecognizer.recognitionTask(with: recognitionRequest) { [weak self] result, error in
            DispatchQueue.main.async {
                if let result = result {
                    self?.recognizedText = result.bestTranscription.formattedString
                    completion(result.bestTranscription.formattedString)
                }
                
                if let error = error {
                    self?.errorMessage = error.localizedDescription
                    self?.stopRecording()
                }
            }
        }
        
        // Setup audio engine
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            recognitionRequest.append(buffer)
        }
        
        // Start audio engine
        audioEngine.prepare()
        do {
            try audioEngine.start()
            isRecording = true
            print("🎤 Voice recording started")
        } catch {
            errorMessage = "Failed to start audio engine"
            print("❌ Failed to start audio engine: \(error)")
        }
    }
    
    func stopRecording() {
        guard isRecording else { return }
        
        audioEngine.stop()
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        
        recognitionRequest = nil
        recognitionTask = nil
        
        isRecording = false
        print("🎤 Voice recording stopped")
    }
    
    func clearRecognizedText() {
        recognizedText = ""
        errorMessage = nil
    }
    
    // MARK: - Tattoo-specific Voice Commands
    
    func processTattooCommand(_ text: String) -> TattooCommand? {
        let lowercaseText = text.lowercased()
        
        if lowercaseText.contains("book appointment") || lowercaseText.contains("schedule") {
            return .bookAppointment
        } else if lowercaseText.contains("show designs") || lowercaseText.contains("portfolio") {
            return .showDesigns
        } else if lowercaseText.contains("pricing") || lowercaseText.contains("cost") {
            return .showPricing
        } else if lowercaseText.contains("contact") || lowercaseText.contains("call") {
            return .contactShop
        } else if lowercaseText.contains("help") || lowercaseText.contains("assistance") {
            return .help
        } else if lowercaseText.contains("cancel") || lowercaseText.contains("stop") {
            return .cancel
        }
        
        return nil
    }
    
    // MARK: - Voice Input Settings
    
    func getSupportedLanguages() -> [String] {
        return SFSpeechRecognizer.supportedLocales().map { $0.identifier }
    }
    
    func setLanguage(_ locale: String) {
        // This would require recreating the speech recognizer with new locale
        // For now, we'll use the default English locale
    }
    
    // MARK: - Error Handling
    
    func getErrorMessage() -> String? {
        return errorMessage
    }
    
    func clearError() {
        errorMessage = nil
    }
}

// MARK: - Tattoo Command Enum

enum TattooCommand {
    case bookAppointment
    case showDesigns
    case showPricing
    case contactShop
    case help
    case cancel
    
    var description: String {
        switch self {
        case .bookAppointment:
            return "Book an appointment"
        case .showDesigns:
            return "Show tattoo designs"
        case .showPricing:
            return "Show pricing information"
        case .contactShop:
            return "Contact the tattoo shop"
        case .help:
            return "Get help and assistance"
        case .cancel:
            return "Cancel current action"
        }
    }
}

// MARK: - Voice Input Extensions

extension VoiceInputManager {
    
    func startTattooConsultation() {
        startRecording { [weak self] text in
            if let command = self?.processTattooCommand(text) {
                print("🎨 Tattoo command recognized: \(command.description)")
                // Handle the command
                self?.handleTattooCommand(command)
            }
        }
    }
    
    private func handleTattooCommand(_ command: TattooCommand) {
        switch command {
        case .bookAppointment:
            // Navigate to appointment booking
            break
        case .showDesigns:
            // Navigate to portfolio
            break
        case .showPricing:
            // Navigate to pricing
            break
        case .contactShop:
            // Open contact options
            break
        case .help:
            // Show help information
            break
        case .cancel:
            stopRecording()
            break
        }
    }
}
