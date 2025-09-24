//
//  NextElevenTattooProApp.swift
//  NextElevenTattooPro
//
//  Created by APOLLO AI on 09/21/2025.
//  Copyright © 2025 NextEleven Studios. All rights reserved.
//

import SwiftUI
import CoreML
import AVFoundation
import Photos
import Speech
import UserNotifications

@main
struct NextElevenTattooProApp: App {
    @StateObject private var apolloAI = ApolloAIManager()
    @StateObject private var hapticManager = HapticFeedbackManager()
    @StateObject private var voiceManager = VoiceInputManager()
    @StateObject private var cameraManager = CameraIntegrationManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(apolloAI)
                .environmentObject(hapticManager)
                .environmentObject(voiceManager)
                .environmentObject(cameraManager)
                .onAppear {
                    setupApp()
                }
        }
    }
    
    private func setupApp() {
        // Request permissions
        requestPermissions()
        
        // Initialize APOLLO AI
        apolloAI.initialize()
        
        // Setup haptic feedback
        hapticManager.setup()
        
        // Setup voice input
        voiceManager.setup()
        
        // Setup camera
        cameraManager.setup()
        
        print("🌊 APOLLO Mobile App Initialized 🌊")
        print("Bundle ID: com.nexteleven.tattoopro.mobile")
        print("Version: 1.0.0")
        print("AI Model: llama3.2:1b")
        print("Platform: iOS 14.0+")
    }
    
    private func requestPermissions() {
        // Camera permission
        AVCaptureDevice.requestAccess(for: .video) { granted in
            print("Camera permission: \(granted)")
        }
        
        // Microphone permission
        AVAudioSession.sharedInstance().requestRecordPermission { granted in
            print("Microphone permission: \(granted)")
        }
        
        // Photo library permission
        PHPhotoLibrary.requestAuthorization { status in
            print("Photo library permission: \(status)")
        }
        
        // Speech recognition permission
        SFSpeechRecognizer.requestAuthorization { status in
            print("Speech recognition permission: \(status)")
        }
        
        // Notification permission
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { granted, error in
            print("Notification permission: \(granted)")
        }
    }
}
