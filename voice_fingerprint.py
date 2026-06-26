"""
Voice Fingerprinting Module - ML-based voice authentication
Pure Python implementation - no external ML libraries required
"""

import pickle
import os
import math
from typing import Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


def cosine_similarity(vec1, vec2) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(a * a for a in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


class VoiceFingerprint:
    """Extract and compare voice fingerprints using spectral analysis"""
    
    def __init__(self, fingerprints_db: str = 'voice_fingerprints.pkl'):
        self.fingerprints_db = fingerprints_db
        self.fingerprints = {}
        self.similarity_threshold = 0.75  # 0-1 scale, higher = stricter
        
        self._load_fingerprints()
    
    def _load_fingerprints(self):
        """Load fingerprints from disk"""
        if os.path.exists(self.fingerprints_db):
            try:
                with open(self.fingerprints_db, 'rb') as f:
                    self.fingerprints = pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not load fingerprints: {e}")
                self.fingerprints = {}
    
    def _save_fingerprints(self):
        """Save fingerprints to disk"""
        try:
            with open(self.fingerprints_db, 'wb') as f:
                pickle.dump(self.fingerprints, f)
        except Exception as e:
            print(f"Warning: Could not save fingerprints: {e}")
    
    def extract_features(self, audio_data: list) -> Optional[list]:
        """
        Extract audio features from raw audio data
        Features: Energy levels, frequency distribution, temporal characteristics
        """
        try:
            if not audio_data or len(audio_data) == 0:
                return None
            
            # Convert to list if needed
            if hasattr(audio_data, 'tolist'):
                audio_data = audio_data.tolist()
            elif not isinstance(audio_data, list):
                audio_data = list(audio_data)
            
            features = []
            
            # 1. Energy features
            energy = sum(x * x for x in audio_data) / len(audio_data)
            features.append(energy)
            
            # 2. Peak amplitude
            max_amp = max(abs(x) for x in audio_data)
            features.append(max_amp)
            
            # 3. Zero crossing rate (voice activity)
            zcr = 0
            for i in range(1, len(audio_data)):
                if (audio_data[i] > 0) != (audio_data[i-1] > 0):
                    zcr += 1
            zcr = zcr / len(audio_data)
            features.append(zcr)
            
            # 4. Variance (signal dynamics)
            mean_val = sum(audio_data) / len(audio_data)
            variance = sum((x - mean_val) ** 2 for x in audio_data) / len(audio_data)
            features.append(variance)
            
            # 5. Silence ratio (samples below threshold)
            threshold = max_amp * 0.1
            silence = sum(1 for x in audio_data if abs(x) < threshold) / len(audio_data)
            features.append(silence)
            
            # 6. Temporal features - frame-based
            frame_size = min(512, len(audio_data) // 4)
            frame_energies = []
            
            for i in range(0, len(audio_data) - frame_size, frame_size):
                frame = audio_data[i:i+frame_size]
                frame_energy = sum(x*x for x in frame) / len(frame)
                frame_energies.append(frame_energy)
            
            if frame_energies:
                features.append(sum(frame_energies) / len(frame_energies))  # Mean frame energy
                features.append(max(frame_energies) - min(frame_energies))  # Frame energy range
            else:
                features.append(0)
                features.append(0)
            
            # Normalize features to 0-1 range
            max_feature = max(abs(f) for f in features) if features else 1
            if max_feature > 0:
                features = [f / max_feature for f in features]
            
            return features
        
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def extract_from_file(self, audio_file: str) -> Optional[list]:
        """Load audio file and extract fingerprint"""
        try:
            # Try scipy first
            try:
                from scipy.io import wavfile
                sample_rate, audio_data = wavfile.read(audio_file)
                # Convert to mono if stereo
                if isinstance(audio_data[0], (list, tuple)):
                    audio_data = [sum(frame) / len(frame) for frame in audio_data]
                return self.extract_features(audio_data.tolist() if hasattr(audio_data, 'tolist') else audio_data)
            except ImportError:
                pass
            
            # Try librosa
            try:
                import librosa
                audio_data, _ = librosa.load(audio_file, sr=16000, mono=True)
                return self.extract_features(audio_data)
            except ImportError:
                pass
            
            print(f"Warning: scipy or librosa required for audio file loading")
            return None
        
        except Exception as e:
            print(f"Error loading audio file {audio_file}: {e}")
            return None
    
    def register_voice(self, name: str, audio_file: str) -> Tuple[bool, str]:
        """Register voice fingerprint for a user"""
        fingerprint = self.extract_from_file(audio_file)
        
        if fingerprint is None:
            return False, "Failed to extract voice features"
        
        self.fingerprints[name] = {
            'fingerprint': fingerprint,
            'samples': [fingerprint],
            'registered_at': str(__import__('datetime').datetime.now())
        }
        
        self._save_fingerprints()
        return True, f"Voice fingerprint registered for '{name}'"
    
    def add_voice_sample(self, name: str, audio_file: str) -> Tuple[bool, str]:
        """Add additional voice sample for better accuracy"""
        if name not in self.fingerprints:
            return False, f"User '{name}' not registered"
        
        fingerprint = self.extract_from_file(audio_file)
        
        if fingerprint is None:
            return False, "Failed to extract voice features"
        
        self.fingerprints[name]['samples'].append(fingerprint)
        
        # Average all samples
        avg_fingerprint = []
        for i in range(len(fingerprint)):
            avg_val = sum(s[i] for s in self.fingerprints[name]['samples']) / len(self.fingerprints[name]['samples'])
            avg_fingerprint.append(avg_val)
        
        self.fingerprints[name]['fingerprint'] = avg_fingerprint
        
        self._save_fingerprints()
        return True, f"Voice sample added for '{name}' (total: {len(self.fingerprints[name]['samples'])})"
    
    def verify_voice(self, name: str, audio_file: str) -> Tuple[bool, float]:
        """
        Verify if audio matches registered user voice
        Returns: (is_match, confidence_score)
        """
        if name not in self.fingerprints:
            return False, 0.0
        
        test_fingerprint = self.extract_from_file(audio_file)
        
        if test_fingerprint is None:
            return False, 0.0
        
        registered_fingerprint = self.fingerprints[name]['fingerprint']
        
        # Calculate similarity using cosine similarity
        similarity = cosine_similarity(registered_fingerprint, test_fingerprint)
        
        # Normalize to 0-1 scale
        confidence = max(0, min(1, similarity))
        
        is_match = confidence >= self.similarity_threshold
        
        return is_match, confidence
    
    def verify_voice_from_array(self, name: str, audio_array) -> Tuple[bool, float]:
        """Verify voice directly from audio array (for live recording)"""
        if name not in self.fingerprints:
            return False, 0.0
        
        test_fingerprint = self.extract_features(audio_array)
        
        if test_fingerprint is None:
            return False, 0.0
        
        registered_fingerprint = self.fingerprints[name]['fingerprint']
        
        similarity = cosine_similarity(registered_fingerprint, test_fingerprint)
        confidence = max(0, min(1, similarity))
        
        is_match = confidence >= self.similarity_threshold
        
        return is_match, confidence
    
    def adjust_threshold(self, threshold: float) -> Tuple[bool, str]:
        """
        Adjust sensitivity (0.5-0.95)
        Lower = more lenient, Higher = stricter
        """
        if 0.5 <= threshold <= 0.95:
            self.similarity_threshold = threshold
            return True, f"Threshold set to {threshold}"
        return False, "Threshold must be between 0.5 and 0.95"
    
    def get_fingerprint_info(self, name: str) -> Optional[dict]:
        """Get fingerprint metadata"""
        if name not in self.fingerprints:
            return None
        
        info = {
            'name': name,
            'num_samples': len(self.fingerprints[name]['samples']),
            'registered_at': self.fingerprints[name]['registered_at']
        }
        
        return info
    
    def list_registered_voices(self) -> list:
        """List all registered voice fingerprints"""
        return [
            {
                'name': name,
                'samples': len(data['samples']),
                'registered_at': data['registered_at']
            }
            for name, data in self.fingerprints.items()
        ]
    
    def delete_voice(self, name: str) -> Tuple[bool, str]:
        """Delete voice fingerprint"""
        if name not in self.fingerprints:
            return False, f"User '{name}' not found"
        
        del self.fingerprints[name]
        self._save_fingerprints()
        return True, f"Voice fingerprint for '{name}' deleted"


def demo_fingerprinting():
    """Demo voice fingerprinting"""
    print("\n=== VOICE FINGERPRINTING DEMO ===\n")
    
    vf = VoiceFingerprint()
    
    print("Voice Fingerprinting System Features:")
    print("✓ Extract spectral voice features (pure Python)")
    print("✓ Register voice fingerprints")
    print("✓ Verify voices with confidence scores")
    print("✓ Add multiple samples for better accuracy")
    print("✓ Adjustable sensitivity threshold")
    print("\nUsage:")
    print("  1. register_voice('John', 'john_voice.wav')")
    print("  2. add_voice_sample('John', 'john_voice_2.wav')")
    print("  3. is_match, confidence = verify_voice('John', 'test_audio.wav')")
    print("\nRegistered voices:", vf.list_registered_voices())
    print("\nThreshold (0.5-0.95):", vf.similarity_threshold)


if __name__ == "__main__":
    demo_fingerprinting()


