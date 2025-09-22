//
//  ContentView.swift
//  NextElevenTattooPro
//
//  Created by APOLLO AI on 09/21/2025.
//  Copyright © 2025 NextEleven Studios. All rights reserved.
//

import SwiftUI
import CoreML

struct ContentView: View {
    @EnvironmentObject var apolloAI: ApolloAIManager
    @EnvironmentObject var hapticManager: HapticFeedbackManager
    @EnvironmentObject var voiceManager: VoiceInputManager
    @EnvironmentObject var cameraManager: CameraIntegrationManager
    
    @State private var selectedTab = 0
    @State private var isAIActive = false
    @State private var showingCamera = false
    @State private var showingVoiceInput = false
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Main Chat Interface
            ChatInterfaceView()
                .tabItem {
                    Image(systemName: "message.fill")
                    Text("APOLLO Chat")
                }
                .tag(0)
            
            // Camera Integration
            CameraView()
                .tabItem {
                    Image(systemName: "camera.fill")
                    Text("Camera")
                }
                .tag(1)
            
            // Voice Input
            VoiceInputView()
                .tabItem {
                    Image(systemName: "mic.fill")
                    Text("Voice")
                }
                .tag(2)
            
            // Settings
            SettingsView()
                .tabItem {
                    Image(systemName: "gear.fill")
                    Text("Settings")
                }
                .tag(3)
        }
        .accentColor(.blue)
        .onAppear {
            setupAPOLLO()
        }
    }
    
    private func setupAPOLLO() {
        print("🌊 APOLLO Mobile Interface Loading 🌊")
        print("AI Status: \(apolloAI.isInitialized ? "Active" : "Initializing")")
        print("Device Capabilities: \(apolloAI.deviceCapabilities)")
    }
}

struct ChatInterfaceView: View {
    @EnvironmentObject var apolloAI: ApolloAIManager
    @EnvironmentObject var hapticManager: HapticFeedbackManager
    
    @State private var messageText = ""
    @State private var messages: [ChatMessage] = []
    @State private var isTyping = false
    
    var body: some View {
        NavigationView {
            VStack {
                // APOLLO Status Header
                HStack {
                    Image(systemName: "brain.head.profile")
                        .foregroundColor(.blue)
                    Text("APOLLO AI")
                        .font(.headline)
                        .fontWeight(.bold)
                    Spacer()
                    StatusIndicator(isActive: apolloAI.isInitialized)
                }
                .padding()
                .background(Color(.systemGray6))
                
                // Messages List
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 12) {
                        ForEach(messages) { message in
                            MessageBubble(message: message)
                        }
                        
                        if isTyping {
                            TypingIndicator()
                        }
                    }
                    .padding()
                }
                
                // Input Area
                HStack {
                    TextField("Ask APOLLO anything...", text: $messageText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .onSubmit {
                            sendMessage()
                        }
                    
                    Button(action: sendMessage) {
                        Image(systemName: "paperplane.fill")
                            .foregroundColor(.white)
                            .padding(8)
                            .background(Color.blue)
                            .clipShape(Circle())
                    }
                    .disabled(messageText.isEmpty || isTyping)
                }
                .padding()
            }
            .navigationTitle("APOLLO Chat")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    private func sendMessage() {
        guard !messageText.isEmpty else { return }
        
        let userMessage = ChatMessage(
            id: UUID(),
            content: messageText,
            isUser: true,
            timestamp: Date()
        )
        
        messages.append(userMessage)
        messageText = ""
        isTyping = true
        
        // Haptic feedback
        hapticManager.impact(.light)
        
        // Process with APOLLO AI
        apolloAI.processMessage(userMessage.content) { response in
            DispatchQueue.main.async {
                let apolloMessage = ChatMessage(
                    id: UUID(),
                    content: response,
                    isUser: false,
                    timestamp: Date()
                )
                
                messages.append(apolloMessage)
                isTyping = false
                
                // Haptic feedback for response
                hapticManager.impact(.medium)
            }
        }
    }
}

struct CameraView: View {
    @EnvironmentObject var cameraManager: CameraIntegrationManager
    @EnvironmentObject var apolloAI: ApolloAIManager
    
    var body: some View {
        NavigationView {
            VStack {
                if cameraManager.isAuthorized {
                    CameraPreviewView()
                        .environmentObject(cameraManager)
                } else {
                    CameraPermissionView()
                }
            }
            .navigationTitle("Camera")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

struct VoiceInputView: View {
    @EnvironmentObject var voiceManager: VoiceInputManager
    @EnvironmentObject var apolloAI: ApolloAIManager
    
    @State private var isRecording = false
    @State private var recognizedText = ""
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Voice Input Status
                VStack {
                    Image(systemName: isRecording ? "mic.fill" : "mic.slash.fill")
                        .font(.system(size: 60))
                        .foregroundColor(isRecording ? .red : .gray)
                    
                    Text(isRecording ? "Listening..." : "Tap to speak")
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
                
                // Recognized Text
                if !recognizedText.isEmpty {
                    VStack(alignment: .leading) {
                        Text("Recognized:")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(recognizedText)
                            .padding()
                            .background(Color(.systemGray6))
                            .cornerRadius(8)
                    }
                }
                
                // Record Button
                Button(action: toggleRecording) {
                    Text(isRecording ? "Stop Recording" : "Start Recording")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .background(isRecording ? Color.red : Color.blue)
                        .cornerRadius(25)
                }
                .disabled(!voiceManager.isAuthorized)
                
                Spacer()
            }
            .padding()
            .navigationTitle("Voice Input")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    private func toggleRecording() {
        if isRecording {
            voiceManager.stopRecording()
            isRecording = false
        } else {
            voiceManager.startRecording { text in
                recognizedText = text
                // Process with APOLLO AI
                apolloAI.processMessage(text) { response in
                    // Handle response
                }
            }
            isRecording = true
        }
    }
}

struct SettingsView: View {
    @EnvironmentObject var apolloAI: ApolloAIManager
    
    var body: some View {
        NavigationView {
            List {
                Section("APOLLO AI") {
                    HStack {
                        Text("Status")
                        Spacer()
                        Text(apolloAI.isInitialized ? "Active" : "Inactive")
                            .foregroundColor(apolloAI.isInitialized ? .green : .red)
                    }
                    
                    HStack {
                        Text("Model")
                        Spacer()
                        Text("llama3.2:1b")
                            .foregroundColor(.secondary)
                    }
                    
                    HStack {
                        Text("Version")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.secondary)
                    }
                }
                
                Section("Device Capabilities") {
                    ForEach(apolloAI.deviceCapabilities, id: \.name) { capability in
                        HStack {
                            Text(capability.name)
                            Spacer()
                            Image(systemName: capability.available ? "checkmark.circle.fill" : "xmark.circle.fill")
                                .foregroundColor(capability.available ? .green : .red)
                        }
                    }
                }
                
                Section("About") {
                    HStack {
                        Text("Bundle ID")
                        Spacer()
                        Text("com.nexteleven.tattoopro.mobile")
                            .foregroundColor(.secondary)
                            .font(.caption)
                    }
                    
                    HStack {
                        Text("Build")
                        Spacer()
                        Text("1")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

// Supporting Views
struct StatusIndicator: View {
    let isActive: Bool
    
    var body: some View {
        Circle()
            .fill(isActive ? Color.green : Color.red)
            .frame(width: 12, height: 12)
    }
}

struct MessageBubble: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.isUser {
                Spacer()
                Text(message.content)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(16)
            } else {
                Text(message.content)
                    .padding()
                    .background(Color(.systemGray5))
                    .cornerRadius(16)
                Spacer()
            }
        }
    }
}

struct TypingIndicator: View {
    @State private var animationOffset: CGFloat = 0
    
    var body: some View {
        HStack {
            HStack(spacing: 4) {
                ForEach(0..<3) { index in
                    Circle()
                        .fill(Color.gray)
                        .frame(width: 8, height: 8)
                        .offset(y: animationOffset)
                        .animation(
                            Animation.easeInOut(duration: 0.6)
                                .repeatForever()
                                .delay(Double(index) * 0.2),
                            value: animationOffset
                        )
                }
            }
            .padding()
            .background(Color(.systemGray5))
            .cornerRadius(16)
            Spacer()
        }
        .onAppear {
            animationOffset = -5
        }
    }
}

struct CameraPreviewView: View {
    @EnvironmentObject var cameraManager: CameraIntegrationManager
    
    var body: some View {
        VStack {
            Text("Camera Preview")
                .font(.headline)
            Text("Camera integration ready")
                .foregroundColor(.secondary)
        }
    }
}

struct CameraPermissionView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "camera.fill")
                .font(.system(size: 60))
                .foregroundColor(.gray)
            
            Text("Camera Permission Required")
                .font(.headline)
            
            Text("Please enable camera access in Settings to use this feature.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
            
            Button("Open Settings") {
                if let settingsUrl = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(settingsUrl)
                }
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}

// Data Models
struct ChatMessage: Identifiable {
    let id: UUID
    let content: String
    let isUser: Bool
    let timestamp: Date
}

struct DeviceCapability {
    let name: String
    let available: Bool
}

#Preview {
    ContentView()
        .environmentObject(ApolloAIManager())
        .environmentObject(HapticFeedbackManager())
        .environmentObject(VoiceInputManager())
        .environmentObject(CameraIntegrationManager())
}
