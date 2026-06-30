import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Tuple, Optional
from voice_fingerprint import VoiceFingerprint
import numpy as np


class AuthenticationSystem:
    """Multi-level authentication system for personal assistant"""
    
    def __init__(self, users_db_path: str = 'users.json', default_user: str = 'Anbu'):
        if users_db_path is None:
            users_db_path = ROOT_DIR / 'users.json'
        else:
            users_db_path = Path(users_db_path) if Path(users_db_path).is_absolute() else ROOT_DIR / users_db_path

        self.users_db_path = str(Path(users_db_path).resolve())
        self.default_user = default_user
        self.current_user = None
        self.is_authenticated = False
        self.voice_fp = VoiceFingerprint()  # ML-based voice fingerprinting
        self._load_users_db()
    
    def _load_users_db(self):
        """Load users database from JSON file"""
        if not os.path.exists(self.users_db_path):
            self._create_default_db()
        
        with open(self.users_db_path, 'r') as f:
            self.users_db = json.load(f)
    
    def _create_default_db(self):
        """Create default users database with Anbu user"""
        default_db = {
            'Anbu': {
                'is_default': True,
                'voice_id': None,
                'passcode': None,
                'created_at': datetime.now().isoformat(),
                'access_level': 'default'
            }
        }
        
        with open(self.users_db_path, 'w') as f:
            json.dump(default_db, f, indent=4)
        
        self.users_db = default_db
    
    def _hash_passcode(self, passcode: str) -> str:
        """Hash passcode with SHA-256"""
        return hashlib.sha256(passcode.encode()).hexdigest()
    
    def register_user(self, name: str, voice_file: str, passcode: str) -> Tuple[bool, str]:
        """Register new user with voice fingerprint and passcode"""
        if name.lower() == self.default_user.lower():
            return False, "Cannot register with default user name"
        
        if name in self.users_db:
            return False, f"User '{name}' already exists"
        
        # Register voice fingerprint
        success, fp_msg = self.voice_fp.register_voice(name, voice_file)
        if not success:
            return False, f"Voice registration failed: {fp_msg}"
        
        hashed_passcode = self._hash_passcode(passcode)
        
        self.users_db[name] = {
            'is_default': False,
            'voice_id': name,  # Reference to fingerprint in voice_fp
            'passcode': hashed_passcode,
            'created_at': datetime.now().isoformat(),
            'access_level': 'custom',
            'voice_samples': 1
        }
        
        self._save_users_db()
        return True, f"User '{name}' registered with voice fingerprint and passcode"
    
    def authenticate_default_user(self, voice_param: Optional[str] = None) -> Tuple[bool, str]:
        """
        Authenticate as default user (Anbu)
        - Checks voice parameter
        - If voice fails, enters full authentication
        """
        if voice_param:
            if self._verify_voice(self.default_user, voice_param):
                self.current_user = self.default_user
                self.is_authenticated = True
                return True, f"Welcome {self.default_user}! Voice verified."
        
        # Fall back to verification mode
        return self._enter_verification_mode(self.default_user)
    
    def authenticate_custom_user(self, name: str, voice_param: Optional[str] = None, 
                                 passcode: Optional[str] = None) -> Tuple[bool, str]:
        """
        Authenticate custom user
        - Checks authorization in directory
        - Requires voice + passcode verification
        """
        if name not in self.users_db:
            return False, f"User '{name}' not found. Please register first."
        
        user = self.users_db[name]
        
        if user['is_default']:
            return False, "Use authenticate_default_user() for default user"
        
        # Verify voice
        if not voice_param or not self._verify_voice(name, voice_param):
            return False, "Voice verification failed"
        
        # Verify passcode
        if not passcode or not self._verify_passcode(name, passcode):
            return False, "Passcode verification failed"
        
        self.current_user = name
        self.is_authenticated = True
        return True, f"Welcome {name}! Full authentication successful."
    
    def _verify_voice(self, name: str, voice_sample: str) -> bool:
        """
        Verify voice using ML fingerprinting
        voice_sample can be file path or audio array
        """
        user = self.users_db.get(name)
        if not user:
            return False
        
        try:
            # If voice_sample is a file path
            if isinstance(voice_sample, str) and os.path.exists(voice_sample):
                is_match, confidence = self.voice_fp.verify_voice(name, voice_sample)
                print(f"[Voice Verification] {name}: Confidence {confidence:.2%}")
                return is_match
            
            # If voice_sample is audio array (numpy)
            elif isinstance(voice_sample, np.ndarray):
                is_match, confidence = self.voice_fp.verify_voice_from_array(name, voice_sample)
                print(f"[Voice Verification] {name}: Confidence {confidence:.2%}")
                return is_match
            
            else:
                print("[Voice Verification] Invalid voice sample format")
                return False
        
        except Exception as e:
            print(f"[Voice Verification] Error: {e}")
            return False
    
    def _verify_passcode(self, name: str, passcode: str) -> bool:
        """Verify passcode"""
        user = self.users_db.get(name)
        if not user or not user['passcode']:
            return False
        
        hashed_input = self._hash_passcode(passcode)
        return user['passcode'] == hashed_input
    
    def _enter_verification_mode(self, name: str) -> Tuple[bool, str]:
        """Full verification process when voice fails"""
        user = self.users_db.get(name)
        
        if not user:
            return False, "User not found"
        
        if user['is_default']:
            # Default user can proceed with voice setup
            print("[Authentication Mode] Setting up voice for default user...")
            return True, "Default user voice setup required. Please train voice sample."
        
        # Custom user needs passcode
        return False, "Full authentication required. Passcode needed."
    
    def add_voice_training(self, name: str, voice_file: str) -> Tuple[bool, str]:
        """Add voice sample for improved accuracy (multiple samples = better matching)"""
        if name not in self.users_db:
            return False, f"User '{name}' not found"
        
        success, msg = self.voice_fp.add_voice_sample(name, voice_file)
        if success:
            self.users_db[name]['voice_samples'] = self.users_db[name].get('voice_samples', 1) + 1
            self._save_users_db()
        
        return success, msg
    
    def set_voice_sensitivity(self, sensitivity: float) -> Tuple[bool, str]:
        """
        Adjust voice verification sensitivity
        0.5 = lenient, 0.95 = strict (default: 0.75)
        """
        success, msg = self.voice_fp.adjust_threshold(sensitivity)
        return success, msg
    
    def get_voice_info(self, name: str) -> Optional[dict]:
        """Get voice fingerprint information"""
        return self.voice_fp.get_fingerprint_info(name)
    
    def list_voice_profiles(self) -> list:
        """List all registered voice profiles"""
        return self.voice_fp.list_registered_voices()
    
        """Change user passcode"""
        if name not in self.users_db:
            return False, f"User '{name}' not found"
        
        if not self._verify_passcode(name, old_passcode):
            return False, "Old passcode is incorrect"
        
        hashed_new = self._hash_passcode(new_passcode)
        self.users_db[name]['passcode'] = hashed_new
        self._save_users_db()
        
        return True, "Passcode changed successfully"
    
    def get_user_info(self, name: str) -> Optional[Dict]:
        """Get user information"""
        if name not in self.users_db:
            return None
        
        user = self.users_db[name].copy()
        user.pop('passcode', None)  # Don't expose passcode
        return user
    
    def list_all_users(self) -> list:
        """List all registered users"""
        return [
            {
                'name': name,
                'is_default': info['is_default'],
                'access_level': info['access_level'],
                'created_at': info['created_at']
            }
            for name, info in self.users_db.items()
        ]
    
    def logout(self) -> Tuple[bool, str]:
        """Logout current user"""
        if not self.is_authenticated:
            return False, "No user logged in"
        
        user_name = self.current_user
        self.current_user = None
        self.is_authenticated = False
        return True, f"User '{user_name}' logged out successfully"
    
    def _save_users_db(self):
        """Save users database to JSON file"""
        with open(self.users_db_path, 'w') as f:
            json.dump(self.users_db, f, indent=4)
    
    def get_access_level(self) -> Optional[str]:
        """Get current user access level"""
        if not self.is_authenticated or not self.current_user:
            return None
        
        return self.users_db[self.current_user]['access_level']


def demo_authentication():
    """Demo authentication flows"""
    auth = AuthenticationSystem()
    
    print("\n=== AUTHENTICATION SYSTEM DEMO ===\n")
    
    # Demo 1: Default user authentication
    print("1. Default User (Anbu) - Voice verification:")
    success, msg = auth.authenticate_default_user(voice_param="anbu_voice_sample")
    print(f"   Result: {msg}\n")
    
    # Demo 2: Register custom user
    print("2. Register Custom User (Sarah):")
    success, msg = auth.register_user("Sarah", "sarah_voice_sample", "secure123")
    print(f"   Result: {msg}\n")
    
    # Demo 3: Authenticate custom user
    print("3. Authenticate Custom User (Sarah):")
    success, msg = auth.authenticate_custom_user("Sarah", "sarah_voice_sample", "secure123")
    print(f"   Result: {msg}\n")
    
    # Demo 4: List users
    print("4. All Registered Users:")
    for user in auth.list_all_users():
        print(f"   - {user}\n")
    
    # Demo 5: Logout
    print("5. Logout:")
    success, msg = auth.logout()
    print(f"   Result: {msg}\n")


if __name__ == "__main__":
    demo_authentication()
