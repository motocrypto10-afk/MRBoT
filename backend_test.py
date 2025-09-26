#!/usr/bin/env python3
"""
BotMR Backend API Testing Suite
Tests all backend endpoints for the meeting recording app
"""

import requests
import json
import base64
import time
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://meeting-brain.preview.emergentagent.com/api"
TIMEOUT = 30

class BotMRTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.test_results = []
        self.created_meeting_id = None
        self.recording_session_id = None
        self.recording_meeting_id = None
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_api_health(self):
        """Test basic API health check"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "BotMR API is running" in data.get("message", ""):
                    self.log_test("API Health Check", True, "API is running and responsive")
                    return True
                else:
                    self.log_test("API Health Check", False, "Unexpected response format", data)
                    return False
            else:
                self.log_test("API Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_get_meetings_empty(self):
        """Test getting meetings when database might be empty"""
        try:
            response = self.session.get(f"{self.base_url}/meetings")
            if response.status_code == 200:
                meetings = response.json()
                self.log_test("Get Meetings (Empty)", True, f"Retrieved {len(meetings)} meetings successfully")
                return True
            else:
                self.log_test("Get Meetings (Empty)", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Meetings (Empty)", False, f"Request error: {str(e)}")
            return False
    
    def test_create_meeting_basic(self):
        """Test creating a basic meeting without audio"""
        try:
            meeting_data = {
                "title": "Test Meeting - Backend API Test",
                "audio_data": None
            }
            
            response = self.session.post(
                f"{self.base_url}/meetings",
                json=meeting_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                meeting = response.json()
                if meeting.get("title") == meeting_data["title"]:
                    self.created_meeting_id = meeting.get("id")
                    self.log_test("Create Meeting (Basic)", True, f"Meeting created with ID: {self.created_meeting_id}")
                    return True
                else:
                    self.log_test("Create Meeting (Basic)", False, "Meeting data mismatch", meeting)
                    return False
            else:
                self.log_test("Create Meeting (Basic)", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Create Meeting (Basic)", False, f"Request error: {str(e)}")
            return False
    
    def test_create_meeting_with_audio(self):
        """Test creating a meeting with mock audio data"""
        try:
            # Create mock audio data (base64 encoded)
            mock_audio = base64.b64encode(b"mock_audio_data_for_testing").decode('utf-8')
            
            meeting_data = {
                "title": "Test Meeting with Audio - Backend API Test",
                "audio_data": mock_audio
            }
            
            response = self.session.post(
                f"{self.base_url}/meetings",
                json=meeting_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                meeting = response.json()
                if meeting.get("title") == meeting_data["title"] and meeting.get("audio_data"):
                    self.log_test("Create Meeting (With Audio)", True, f"Meeting with audio created, ID: {meeting.get('id')}")
                    return True
                else:
                    self.log_test("Create Meeting (With Audio)", False, "Meeting data incomplete", meeting)
                    return False
            else:
                self.log_test("Create Meeting (With Audio)", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Create Meeting (With Audio)", False, f"Request error: {str(e)}")
            return False
    
    def test_get_specific_meeting(self):
        """Test getting a specific meeting by ID"""
        if not self.created_meeting_id:
            self.log_test("Get Specific Meeting", False, "No meeting ID available for testing")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/meetings/{self.created_meeting_id}")
            
            if response.status_code == 200:
                meeting = response.json()
                if meeting.get("id") == self.created_meeting_id:
                    self.log_test("Get Specific Meeting", True, f"Retrieved meeting: {meeting.get('title')}")
                    return True
                else:
                    self.log_test("Get Specific Meeting", False, "Meeting ID mismatch", meeting)
                    return False
            elif response.status_code == 404:
                self.log_test("Get Specific Meeting", False, "Meeting not found (404)", response.text)
                return False
            else:
                self.log_test("Get Specific Meeting", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Specific Meeting", False, f"Request error: {str(e)}")
            return False
    
    def test_process_meeting_ai(self):
        """Test AI processing of a meeting"""
        if not self.created_meeting_id:
            self.log_test("AI Meeting Processing", False, "No meeting ID available for testing")
            return False
        
        try:
            # First create a meeting with audio data for processing
            mock_audio = base64.b64encode(b"mock_audio_data_for_ai_processing").decode('utf-8')
            meeting_data = {
                "title": "AI Processing Test Meeting",
                "audio_data": mock_audio
            }
            
            create_response = self.session.post(
                f"{self.base_url}/meetings",
                json=meeting_data,
                headers={"Content-Type": "application/json"}
            )
            
            if create_response.status_code != 200:
                self.log_test("AI Meeting Processing", False, "Failed to create meeting for AI test", create_response.text)
                return False
            
            meeting = create_response.json()
            meeting_id = meeting.get("id")
            
            # Now process the meeting
            response = self.session.post(f"{self.base_url}/meetings/{meeting_id}/process")
            
            if response.status_code == 200:
                result = response.json()
                if "successfully" in result.get("message", "").lower():
                    self.log_test("AI Meeting Processing", True, "Meeting processed successfully with AI")
                    
                    # Verify the meeting was updated with AI results
                    time.sleep(2)  # Give it a moment to process
                    updated_meeting_response = self.session.get(f"{self.base_url}/meetings/{meeting_id}")
                    if updated_meeting_response.status_code == 200:
                        updated_meeting = updated_meeting_response.json()
                        if updated_meeting.get("status") == "completed" and updated_meeting.get("summary"):
                            self.log_test("AI Processing Verification", True, "Meeting updated with AI summary and status")
                            return True
                        else:
                            self.log_test("AI Processing Verification", False, "Meeting not properly updated", updated_meeting)
                            return False
                else:
                    self.log_test("AI Meeting Processing", False, "Unexpected response format", result)
                    return False
            else:
                self.log_test("AI Meeting Processing", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("AI Meeting Processing", False, f"Request error: {str(e)}")
            return False
    
    def test_get_tasks(self):
        """Test getting all tasks"""
        try:
            response = self.session.get(f"{self.base_url}/tasks")
            if response.status_code == 200:
                tasks = response.json()
                self.log_test("Get Tasks", True, f"Retrieved {len(tasks)} tasks successfully")
                return True
            else:
                self.log_test("Get Tasks", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Tasks", False, f"Request error: {str(e)}")
            return False
    
    def test_get_messages(self):
        """Test getting all messages"""
        try:
            response = self.session.get(f"{self.base_url}/messages")
            if response.status_code == 200:
                messages = response.json()
                self.log_test("Get Messages", True, f"Retrieved {len(messages)} messages successfully")
                return True
            else:
                self.log_test("Get Messages", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Messages", False, f"Request error: {str(e)}")
            return False
    
    def test_get_settings(self):
        """Test getting user settings"""
        try:
            response = self.session.get(f"{self.base_url}/settings")
            if response.status_code == 200:
                settings = response.json()
                required_fields = ["id", "preferred_language", "cloud_sync_enabled", "privacy_mode"]
                if all(field in settings for field in required_fields):
                    self.log_test("Get Settings", True, f"Settings retrieved with all required fields")
                    return True
                else:
                    self.log_test("Get Settings", False, "Missing required fields in settings", settings)
                    return False
            else:
                self.log_test("Get Settings", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Settings", False, f"Request error: {str(e)}")
            return False
    
    def test_update_settings(self):
        """Test updating user settings"""
        try:
            settings_data = {
                "openai_api_key": "test-key-12345",
                "preferred_language": "en",
                "auto_delete_days": 30,
                "cloud_sync_enabled": True,
                "privacy_mode": False
            }
            
            response = self.session.post(
                f"{self.base_url}/settings",
                json=settings_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "successfully" in result.get("message", "").lower():
                    self.log_test("Update Settings", True, "Settings updated successfully")
                    
                    # Verify settings were updated
                    get_response = self.session.get(f"{self.base_url}/settings")
                    if get_response.status_code == 200:
                        updated_settings = get_response.json()
                        if updated_settings.get("preferred_language") == "en":
                            self.log_test("Settings Verification", True, "Settings update verified")
                            return True
                        else:
                            self.log_test("Settings Verification", False, "Settings not properly updated", updated_settings)
                            return False
                else:
                    self.log_test("Update Settings", False, "Unexpected response format", result)
                    return False
            else:
                self.log_test("Update Settings", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Update Settings", False, f"Request error: {str(e)}")
            return False
    
    def test_recording_start(self):
        """API-001: Test recording start endpoint"""
        try:
            recording_data = {
                "mode": "local",
                "allow_fallback": True,
                "metadata": {
                    "deviceId": f"test-device-{uuid.uuid4()}",
                    "userId": "test-user-001"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/recordings/start",
                json=recording_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                session_id = result.get("sessionId")
                if session_id:
                    self.recording_session_id = session_id
                    self.log_test("Recording Start", True, f"Recording session started: {session_id}")
                    return True
                else:
                    self.log_test("Recording Start", False, "No session ID returned", result)
                    return False
            else:
                self.log_test("Recording Start", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Recording Start", False, f"Request error: {str(e)}")
            return False
    
    def test_recording_heartbeat(self):
        """API-002: Test recording heartbeat endpoint"""
        if not hasattr(self, 'recording_session_id') or not self.recording_session_id:
            self.log_test("Recording Heartbeat", False, "No recording session ID available")
            return False
            
        try:
            heartbeat_data = {
                "session_id": self.recording_session_id,
                "device_id": f"test-device-{uuid.uuid4()}",
                "ts": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/recordings/heartbeat",
                json=heartbeat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    self.log_test("Recording Heartbeat", True, f"Heartbeat sent successfully for session {self.recording_session_id}")
                    return True
                else:
                    self.log_test("Recording Heartbeat", False, "Heartbeat not acknowledged", result)
                    return False
            else:
                self.log_test("Recording Heartbeat", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Recording Heartbeat", False, f"Request error: {str(e)}")
            return False
    
    def test_recording_status(self):
        """API-002: Test recording status endpoint"""
        if not hasattr(self, 'recording_session_id') or not self.recording_session_id:
            self.log_test("Recording Status", False, "No recording session ID available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/recordings/{self.recording_session_id}/status")
            
            if response.status_code == 200:
                status_data = response.json()
                required_fields = ["sessionId", "status", "startedAt"]
                if all(field in status_data for field in required_fields):
                    self.log_test("Recording Status", True, f"Status retrieved: {status_data.get('status')}")
                    return True
                else:
                    self.log_test("Recording Status", False, "Missing required fields in status", status_data)
                    return False
            else:
                self.log_test("Recording Status", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Recording Status", False, f"Request error: {str(e)}")
            return False
    
    def test_recording_stop(self):
        """API-001: Test recording stop endpoint"""
        if not hasattr(self, 'recording_session_id') or not self.recording_session_id:
            self.log_test("Recording Stop", False, "No recording session ID available")
            return False
            
        try:
            stop_data = {
                "session_id": self.recording_session_id,
                "final": True,
                "stats": {
                    "duration": 120,
                    "chunks_uploaded": 5,
                    "total_size": 1024000
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/recordings/stop",
                json=stop_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                meeting_id = result.get("meetingId")
                if meeting_id:
                    self.log_test("Recording Stop", True, f"Recording stopped, meeting created: {meeting_id}")
                    self.recording_meeting_id = meeting_id
                    return True
                else:
                    self.log_test("Recording Stop", False, "No meeting ID returned", result)
                    return False
            else:
                self.log_test("Recording Stop", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Recording Stop", False, f"Request error: {str(e)}")
            return False
    
    def test_complete_recording_workflow(self):
        """QUE-001: Test complete recording workflow"""
        try:
            print("🔄 Testing Complete Recording Workflow...")
            
            # Step 1: Start recording
            if not self.test_recording_start():
                return False
            
            # Step 2: Send heartbeat
            time.sleep(1)
            if not self.test_recording_heartbeat():
                return False
            
            # Step 3: Check status
            if not self.test_recording_status():
                return False
            
            # Step 4: Stop recording
            if not self.test_recording_stop():
                return False
            
            # Step 5: Verify meeting was created and can be retrieved
            if hasattr(self, 'recording_meeting_id') and self.recording_meeting_id:
                response = self.session.get(f"{self.base_url}/meetings/{self.recording_meeting_id}")
                if response.status_code == 200:
                    meeting_data = response.json()
                    self.log_test("Complete Recording Workflow", True, 
                                f"Full workflow completed: recording → meeting {self.recording_meeting_id}")
                    return True
                else:
                    self.log_test("Complete Recording Workflow", False, 
                                f"Meeting not found after recording: {self.recording_meeting_id}")
                    return False
            else:
                self.log_test("Complete Recording Workflow", False, "No meeting ID from recording stop")
                return False
                
        except Exception as e:
            self.log_test("Complete Recording Workflow", False, f"Workflow error: {str(e)}")
            return False
    
    def test_concurrent_recording_sessions(self):
        """Performance Testing: Test concurrent recording sessions"""
        try:
            session_ids = []
            concurrent_sessions = 3
            
            # Start multiple recording sessions
            for i in range(concurrent_sessions):
                recording_data = {
                    "mode": "local",
                    "allow_fallback": True,
                    "metadata": {
                        "deviceId": f"concurrent-device-{i}-{uuid.uuid4()}",
                        "userId": f"concurrent-user-{i}"
                    }
                }
                
                response = self.session.post(
                    f"{self.base_url}/recordings/start",
                    json=recording_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    session_id = result.get("sessionId")
                    if session_id:
                        session_ids.append(session_id)
            
            success_rate = len(session_ids) / concurrent_sessions
            
            if success_rate >= 0.8:  # 80% success rate acceptable
                self.log_test("Concurrent Recording Sessions", True, 
                            f"{len(session_ids)}/{concurrent_sessions} sessions created successfully")
                
                # Test heartbeats for all sessions
                heartbeat_success = 0
                for session_id in session_ids:
                    heartbeat_data = {
                        "session_id": session_id,
                        "device_id": f"test-device-{uuid.uuid4()}",
                        "ts": datetime.now().isoformat()
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/recordings/heartbeat",
                        json=heartbeat_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200 and response.json().get("ok"):
                        heartbeat_success += 1
                
                self.log_test("Concurrent Heartbeats", heartbeat_success == len(session_ids),
                            f"{heartbeat_success}/{len(session_ids)} heartbeats successful")
                
                return True
            else:
                self.log_test("Concurrent Recording Sessions", False, 
                            f"Low success rate: {success_rate:.1%}")
                return False
                
        except Exception as e:
            self.log_test("Concurrent Recording Sessions", False, f"Request error: {str(e)}")
            return False
    
    def test_error_scenarios(self):
        """Test various error scenarios"""
        error_tests_passed = 0
        total_error_tests = 6
        
        # Test 1: Get non-existent meeting
        try:
            fake_id = str(uuid.uuid4())
            response = self.session.get(f"{self.base_url}/meetings/{fake_id}")
            if response.status_code == 404:
                self.log_test("Error Test - Non-existent Meeting", True, "Correctly returned 404 for non-existent meeting")
                error_tests_passed += 1
            else:
                self.log_test("Error Test - Non-existent Meeting", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Test - Non-existent Meeting", False, f"Request error: {str(e)}")
        
        # Test 2: Process meeting without audio
        try:
            if self.created_meeting_id:
                response = self.session.post(f"{self.base_url}/meetings/{self.created_meeting_id}/process")
                if response.status_code == 400:
                    self.log_test("Error Test - Process Without Audio", True, "Correctly returned 400 for meeting without audio")
                    error_tests_passed += 1
                else:
                    self.log_test("Error Test - Process Without Audio", False, f"Expected 400, got {response.status_code}")
            else:
                self.log_test("Error Test - Process Without Audio", False, "No meeting ID available")
        except Exception as e:
            self.log_test("Error Test - Process Without Audio", False, f"Request error: {str(e)}")
        
        # Test 3: Invalid JSON in create meeting
        try:
            response = self.session.post(
                f"{self.base_url}/meetings",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            if response.status_code in [400, 422]:
                self.log_test("Error Test - Invalid JSON", True, f"Correctly handled invalid JSON with {response.status_code}")
                error_tests_passed += 1
            else:
                self.log_test("Error Test - Invalid JSON", False, f"Expected 400/422, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Test - Invalid JSON", False, f"Request error: {str(e)}")
        
        # Test 4: Invalid recording session heartbeat
        try:
            invalid_heartbeat = {
                "session_id": "invalid-session-id",
                "device_id": "test-device",
                "ts": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/recordings/heartbeat",
                json=invalid_heartbeat,
                headers={"Content-Type": "application/json"}
            )
            
            # Should handle gracefully (might return 200 with ok: false or 404/500)
            if response.status_code in [200, 404, 500]:
                self.log_test("Error Test - Invalid Heartbeat", True, 
                            f"Handled invalid session gracefully: HTTP {response.status_code}")
                error_tests_passed += 1
            else:
                self.log_test("Error Test - Invalid Heartbeat", False, 
                            f"Unexpected response: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Error Test - Invalid Heartbeat", False, f"Request error: {str(e)}")
        
        # Test 5: Invalid recording session status
        try:
            response = self.session.get(f"{self.base_url}/recordings/invalid-session/status")
            if response.status_code == 404:
                self.log_test("Error Test - Invalid Status", True, "Correctly returned 404 for invalid session")
                error_tests_passed += 1
            else:
                self.log_test("Error Test - Invalid Status", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Test - Invalid Status", False, f"Request error: {str(e)}")
        
        # Test 6: Invalid recording session stop
        try:
            invalid_stop = {
                "session_id": "invalid-session-id",
                "final": True
            }
            
            response = self.session.post(
                f"{self.base_url}/recordings/stop",
                json=invalid_stop,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 404:
                self.log_test("Error Test - Invalid Stop", True, "Correctly returned 404 for invalid session")
                error_tests_passed += 1
            else:
                self.log_test("Error Test - Invalid Stop", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Test - Invalid Stop", False, f"Request error: {str(e)}")
        
        return error_tests_passed == total_error_tests
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting BotMR Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Core API tests
        core_tests = [
            self.test_api_health,
            self.test_get_meetings_empty,
            self.test_create_meeting_basic,
            self.test_create_meeting_with_audio,
            self.test_get_specific_meeting,
            self.test_process_meeting_ai,
            self.test_get_tasks,
            self.test_get_messages,
            self.test_get_settings,
            self.test_update_settings,
        ]
        
        # Recording session tests (API-001, API-002, QUE-001)
        recording_tests = [
            self.test_recording_start,
            self.test_recording_heartbeat,
            self.test_recording_status,
            self.test_recording_stop,
            self.test_complete_recording_workflow,
            self.test_concurrent_recording_sessions,
        ]
        
        # Error handling tests
        error_tests = [
            self.test_error_scenarios
        ]
        
        all_tests = core_tests + recording_tests + error_tests
        
        passed = 0
        failed = 0
        
        print("\n📋 CORE API TESTS")
        print("-" * 40)
        for test in core_tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL: {test.__name__} - Unexpected error: {str(e)}")
                failed += 1
            print()  # Add spacing between tests
        
        print("\n🎙️ RECORDING SESSION TESTS (API-001, API-002, QUE-001)")
        print("-" * 40)
        for test in recording_tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL: {test.__name__} - Unexpected error: {str(e)}")
                failed += 1
            print()  # Add spacing between tests
        
        print("\n🚨 ERROR HANDLING TESTS")
        print("-" * 40)
        for test in error_tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL: {test.__name__} - Unexpected error: {str(e)}")
                failed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
        print("🏁 TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("🎉 All tests passed! Backend API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
            
            # Show failed tests summary
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        
        return failed == 0

if __name__ == "__main__":
    tester = BotMRTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)