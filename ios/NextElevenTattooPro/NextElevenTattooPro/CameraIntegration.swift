//
//  CameraIntegration.swift
//  NextElevenTattooPro
//
//  Created by APOLLO AI on 09/21/2025.
//  Copyright © 2025 NextEleven Studios. All rights reserved.
//

import Foundation
import AVFoundation
import UIKit
import Photos
import Vision

class CameraIntegrationManager: ObservableObject {
    @Published var isAuthorized = false
    @Published var isCameraAvailable = false
    @Published var capturedImage: UIImage?
    @Published var errorMessage: String?
    
    private let captureSession = AVCaptureSession()
    private var videoDeviceInput: AVCaptureDeviceInput?
    private var photoOutput = AVCapturePhotoOutput()
    private var videoPreviewLayer: AVCaptureVideoPreviewLayer?
    
    func setup() {
        print("🌊 APOLLO Camera Integration Initializing...")
        
        // Request camera permission
        requestCameraPermission()
        
        // Setup capture session
        setupCaptureSession()
        
        print("✅ Camera Integration Manager initialized")
    }
    
    private func requestCameraPermission() {
        AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
            DispatchQueue.main.async {
                self?.isAuthorized = granted
                if granted {
                    print("✅ Camera access authorized")
                } else {
                    print("❌ Camera access denied")
                    self?.errorMessage = "Camera access is required for tattoo consultations"
                }
            }
        }
    }
    
    private func setupCaptureSession() {
        guard isAuthorized else { return }
        
        captureSession.beginConfiguration()
        
        // Set session preset
        if captureSession.canSetSessionPreset(.photo) {
            captureSession.sessionPreset = .photo
        }
        
        // Add video input
        guard let videoDevice = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let videoDeviceInput = try? AVCaptureDeviceInput(device: videoDevice),
              captureSession.canAddInput(videoDeviceInput) else {
            errorMessage = "Unable to setup camera input"
            captureSession.commitConfiguration()
            return
        }
        
        self.videoDeviceInput = videoDeviceInput
        captureSession.addInput(videoDeviceInput)
        
        // Add photo output
        if captureSession.canAddOutput(photoOutput) {
            captureSession.addOutput(photoOutput)
            photoOutput.isHighResolutionCaptureEnabled = true
        }
        
        captureSession.commitConfiguration()
        isCameraAvailable = true
    }
    
    func startPreview() -> AVCaptureVideoPreviewLayer? {
        guard isAuthorized && isCameraAvailable else { return nil }
        
        if videoPreviewLayer == nil {
            videoPreviewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
            videoPreviewLayer?.videoGravity = .resizeAspectFill
        }
        
        DispatchQueue.global(qos: .userInitiated).async {
            self.captureSession.startRunning()
        }
        
        return videoPreviewLayer
    }
    
    func stopPreview() {
        DispatchQueue.global(qos: .userInitiated).async {
            self.captureSession.stopRunning()
        }
    }
    
    func capturePhoto() {
        guard isAuthorized && isCameraAvailable else {
            errorMessage = "Camera not available"
            return
        }
        
        let settings = AVCapturePhotoSettings()
        settings.isHighResolutionPhotoEnabled = true
        
        if photoOutput.availablePhotoCodecTypes.contains(.hevc) {
            settings.format = [AVVideoCodecKey: AVVideoCodecType.hevc]
        }
        
        photoOutput.capturePhoto(with: settings, delegate: PhotoCaptureDelegate { [weak self] image in
            DispatchQueue.main.async {
                self?.capturedImage = image
                self?.processTattooImage(image)
            }
        })
    }
    
    private func processTattooImage(_ image: UIImage) {
        print("🎨 Processing tattoo image with APOLLO AI...")
        
        // Use Vision framework for image analysis
        guard let cgImage = image.cgImage else { return }
        
        let request = VNClassifyImageRequest { [weak self] request, error in
            if let error = error {
                print("❌ Image classification error: \(error)")
                return
            }
            
            guard let observations = request.results as? [VNClassificationObservation] else { return }
            
            // Process classification results
            self?.processImageClassification(observations)
        }
        
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        do {
            try handler.perform([request])
        } catch {
            print("❌ Failed to perform image classification: \(error)")
        }
    }
    
    private func processImageClassification(_ observations: [VNClassificationObservation]) {
        let topObservations = observations.prefix(5)
        
        for observation in topObservations {
            print("🔍 Classification: \(observation.identifier) - \(observation.confidence)")
        }
        
        // Check if image contains tattoo-related content
        let tattooKeywords = ["tattoo", "ink", "body art", "design", "pattern"]
        let hasTattooContent = topObservations.contains { observation in
            tattooKeywords.contains { keyword in
                observation.identifier.lowercased().contains(keyword)
            }
        }
        
        if hasTattooContent {
            print("✅ Tattoo-related content detected")
            // Process with APOLLO AI for tattoo analysis
        } else {
            print("ℹ️ No tattoo-related content detected")
        }
    }
    
    func saveImageToPhotoLibrary() {
        guard let image = capturedImage else { return }
        
        PHPhotoLibrary.requestAuthorization { [weak self] status in
            DispatchQueue.main.async {
                switch status {
                case .authorized, .limited:
                    UIImageWriteToSavedPhotosAlbum(image, self, #selector(self?.image(_:didFinishSavingWithError:contextInfo:)), nil)
                case .denied, .restricted:
                    self?.errorMessage = "Photo library access denied"
                case .notDetermined:
                    self?.errorMessage = "Photo library access not determined"
                @unknown default:
                    self?.errorMessage = "Unknown photo library status"
                }
            }
        }
    }
    
    @objc private func image(_ image: UIImage, didFinishSavingWithError error: Error?, contextInfo: UnsafeRawPointer) {
        if let error = error {
            errorMessage = "Failed to save image: \(error.localizedDescription)"
        } else {
            print("✅ Image saved to photo library")
        }
    }
    
    func clearCapturedImage() {
        capturedImage = nil
        errorMessage = nil
    }
    
    // MARK: - Tattoo-specific Camera Features
    
    func enableTattooMode() {
        // Configure camera for tattoo photography
        guard let device = videoDeviceInput?.device else { return }
        
        do {
            try device.lockForConfiguration()
            
            // Set focus mode for close-up shots
            if device.isFocusModeSupported(.continuousAutoFocus) {
                device.focusMode = .continuousAutoFocus
            }
            
            // Set exposure mode
            if device.isExposureModeSupported(.continuousAutoExposure) {
                device.exposureMode = .continuousAutoExposure
            }
            
            // Set white balance
            if device.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance) {
                device.whiteBalanceMode = .continuousAutoWhiteBalance
            }
            
            device.unlockForConfiguration()
        } catch {
            print("❌ Failed to configure camera for tattoo mode: \(error)")
        }
    }
    
    func enableFlash() {
        guard let device = videoDeviceInput?.device else { return }
        
        do {
            try device.lockForConfiguration()
            if device.hasFlash {
                device.flashMode = .auto
            }
            device.unlockForConfiguration()
        } catch {
            print("❌ Failed to enable flash: \(error)")
        }
    }
    
    func disableFlash() {
        guard let device = videoDeviceInput?.device else { return }
        
        do {
            try device.lockForConfiguration()
            if device.hasFlash {
                device.flashMode = .off
            }
            device.unlockForConfiguration()
        } catch {
            print("❌ Failed to disable flash: \(error)")
        }
    }
    
    // MARK: - Error Handling
    
    func getErrorMessage() -> String? {
        return errorMessage
    }
    
    func clearError() {
        errorMessage = nil
    }
}

// MARK: - Photo Capture Delegate

class PhotoCaptureDelegate: NSObject, AVCapturePhotoCaptureDelegate {
    private let completion: (UIImage) -> Void
    
    init(completion: @escaping (UIImage) -> Void) {
        self.completion = completion
    }
    
    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        if let error = error {
            print("❌ Photo capture error: \(error)")
            return
        }
        
        guard let imageData = photo.fileDataRepresentation(),
              let image = UIImage(data: imageData) else {
            print("❌ Failed to create image from photo data")
            return
        }
        
        completion(image)
    }
}

// MARK: - Camera Integration Extensions

extension CameraIntegrationManager {
    
    func switchCamera() {
        guard let currentInput = videoDeviceInput else { return }
        
        let preferredPosition: AVCaptureDevice.Position = currentInput.device.position == .back ? .front : .back
        
        guard let videoDevice = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: preferredPosition),
              let videoDeviceInput = try? AVCaptureDeviceInput(device: videoDevice) else {
            return
        }
        
        captureSession.beginConfiguration()
        captureSession.removeInput(currentInput)
        
        if captureSession.canAddInput(videoDeviceInput) {
            captureSession.addInput(videoDeviceInput)
            self.videoDeviceInput = videoDeviceInput
        } else {
            captureSession.addInput(currentInput)
        }
        
        captureSession.commitConfiguration()
    }
    
    func getCameraPosition() -> AVCaptureDevice.Position {
        return videoDeviceInput?.device.position ?? .back
    }
    
    func isFlashAvailable() -> Bool {
        return videoDeviceInput?.device.hasFlash ?? false
    }
    
    func isTorchAvailable() -> Bool {
        return videoDeviceInput?.device.hasTorch ?? false
    }
}
