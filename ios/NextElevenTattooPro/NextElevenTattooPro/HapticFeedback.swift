//
//  HapticFeedback.swift
//  NextElevenTattooPro
//
//  Created by APOLLO AI on 09/21/2025.
//  Copyright © 2025 NextEleven Studios. All rights reserved.
//

import UIKit
import CoreHaptics

class HapticFeedbackManager: ObservableObject {
    @Published var isSupported = false
    @Published var isEnabled = true
    
    private var hapticEngine: CHHapticEngine?
    
    func setup() {
        print("🌊 APOLLO Haptic Feedback Initializing...")
        
        // Check if haptic feedback is supported
        isSupported = CHHapticEngine.capabilitiesForHardware().supportsHaptics
        
        if isSupported {
            do {
                hapticEngine = try CHHapticEngine()
                try hapticEngine?.start()
                print("✅ Haptic Engine initialized successfully")
            } catch {
                print("❌ Failed to initialize haptic engine: \(error)")
                isSupported = false
            }
        } else {
            print("⚠️ Haptic feedback not supported on this device")
        }
    }
    
    // MARK: - Basic Haptic Feedback
    
    func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle) {
        guard isEnabled && isSupported else { return }
        
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.impactOccurred()
    }
    
    func notification(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        guard isEnabled && isSupported else { return }
        
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(type)
    }
    
    func selection() {
        guard isEnabled && isSupported else { return }
        
        let generator = UISelectionFeedbackGenerator()
        generator.selectionChanged()
    }
    
    // MARK: - Custom Haptic Patterns
    
    func apolloStartup() {
        guard isEnabled && isSupported else { return }
        
        let pattern = createApolloStartupPattern()
        playHapticPattern(pattern)
    }
    
    func apolloResponse() {
        guard isEnabled && isSupported else { return }
        
        let pattern = createApolloResponsePattern()
        playHapticPattern(pattern)
    }
    
    func apolloError() {
        guard isEnabled && isSupported else { return }
        
        let pattern = createApolloErrorPattern()
        playHapticPattern(pattern)
    }
    
    func apolloSuccess() {
        guard isEnabled && isSupported else { return }
        
        let pattern = createApolloSuccessPattern()
        playHapticPattern(pattern)
    }
    
    // MARK: - Pattern Creation
    
    private func createApolloStartupPattern() -> CHHapticPattern? {
        let events = [
            CHHapticEvent(eventType: .hapticTransient, parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.8),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.6)
            ], relativeTime: 0),
            CHHapticEvent(eventType: .hapticContinuous, parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.5),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.3)
            ], relativeTime: 0.1, duration: 0.3)
        ]
        
        do {
            return try CHHapticPattern(events: events, parameters: [])
        } catch {
            print("❌ Failed to create startup pattern: \(error)")
            return nil
        }
    }
    
    private func createApolloResponsePattern() -> CHHapticPattern? {
        let events = [
            CHHapticEvent(eventType: .hapticTransient, parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.6),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.4)
            ], relativeTime: 0),
            CHHapticEvent(eventType: .hapticTransient, parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.4),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.2)
            ], relativeTime: 0.1)
        ]
        
        do {
            return try CHHapticPattern(events: events, parameters: [])
        } catch {
            print("❌ Failed to create response pattern: \(error)")
            return nil
        }
    }
    
    private func createApolloErrorPattern() -> CHHapticPattern? {
        let events = [
            CHHapticEvent(eventType: .hapticTransient, parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 1.0),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 1.0)
            ], relativeTime: 0),
            CHHapticEvent(eventType: .hapticTransient, parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.8),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.8)
            ], relativeTime: 0.1),
            CHHapticEvent(eventType: .hapticTransient, parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.6),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.6)
            ], relativeTime: 0.2)
        ]
        
        do {
            return try CHHapticPattern(events: events, parameters: [])
        } catch {
            print("❌ Failed to create error pattern: \(error)")
            return nil
        }
    }
    
    private func createApolloSuccessPattern() -> CHHapticPattern? {
        let events = [
            CHHapticEvent(eventType: .hapticTransient, parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.7),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.5)
            ], relativeTime: 0),
            CHHapticEvent(eventType: .hapticTransient, parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.9),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.7)
            ], relativeTime: 0.2)
        ]
        
        do {
            return try CHHapticPattern(events: events, parameters: [])
        } catch {
            print("❌ Failed to create success pattern: \(error)")
            return nil
        }
    }
    
    // MARK: - Pattern Playback
    
    private func playHapticPattern(_ pattern: CHHapticPattern?) {
        guard let pattern = pattern, let engine = hapticEngine else { return }
        
        do {
            let player = try engine.makePlayer(with: pattern)
            try player.start(atTime: 0)
        } catch {
            print("❌ Failed to play haptic pattern: \(error)")
        }
    }
    
    // MARK: - Settings
    
    func toggleHapticFeedback() {
        isEnabled.toggle()
        UserDefaults.standard.set(isEnabled, forKey: "haptic_feedback_enabled")
    }
    
    func loadSettings() {
        isEnabled = UserDefaults.standard.bool(forKey: "haptic_feedback_enabled")
    }
    
    func saveSettings() {
        UserDefaults.standard.set(isEnabled, forKey: "haptic_feedback_enabled")
    }
}

// MARK: - Haptic Feedback Extensions

extension HapticFeedbackManager {
    
    // Tattoo-specific haptic feedback
    func tattooDesignSelected() {
        impact(.medium)
    }
    
    func appointmentBooked() {
        apolloSuccess()
    }
    
    func cameraCapture() {
        impact(.heavy)
    }
    
    func voiceInputStart() {
        impact(.light)
    }
    
    func voiceInputEnd() {
        impact(.medium)
    }
    
    func aiProcessing() {
        let pattern = createAIProcessingPattern()
        playHapticPattern(pattern)
    }
    
    private func createAIProcessingPattern() -> CHHapticPattern? {
        let events = [
            CHHapticEvent(eventType: .hapticContinuous, parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.3),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.2)
            ], relativeTime: 0, duration: 0.5)
        ]
        
        do {
            return try CHHapticPattern(events: events, parameters: [])
        } catch {
            print("❌ Failed to create AI processing pattern: \(error)")
            return nil
        }
    }
}
