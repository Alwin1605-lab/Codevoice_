"""
Test script for MongoDB User API.
Tests registration, login, and profile management functionality.
"""

import requests
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8001"

# Use timestamp for unique test data
TEST_TIMESTAMP = int(time.time())
TEST_EMAIL = f"test{TEST_TIMESTAMP}@example.com"
TEST_NAME = f"Test User {TEST_TIMESTAMP}"

def test_user_registration():
    """Test user registration."""
    logger.info("Testing user registration...")
    
    url = f"{BASE_URL}/api/users/register"
    data = {
        "name": TEST_NAME,
        "email": TEST_EMAIL,
        "password": "testpassword123"
    }
    
    response = requests.post(url, json=data)
    logger.info(f"Registration response: {response.status_code}")
    
    if response.status_code == 201:
        logger.info("✓ User registration successful")
        return response.json()["user"]
    else:
        logger.error(f"✗ Registration failed: {response.text}")
        return None

def test_user_login():
    """Test user login."""
    logger.info("Testing user login...")
    
    url = f"{BASE_URL}/api/users/login"
    data = {
        "email": TEST_EMAIL,
        "password": "testpassword123"
    }
    
    response = requests.post(url, json=data)
    logger.info(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        logger.info("✓ User login successful")
        return response.json()["user"]
    else:
        logger.error(f"✗ Login failed: {response.text}")
        return None

def test_get_user_profile(user_id):
    """Test getting user profile."""
    logger.info(f"Testing get user profile for ID: {user_id}")
    
    url = f"{BASE_URL}/api/users/{user_id}"
    response = requests.get(url)
    logger.info(f"Get profile response: {response.status_code}")
    
    if response.status_code == 200:
        logger.info("✓ Get user profile successful")
        return response.json()["user"]
    else:
        logger.error(f"✗ Get profile failed: {response.text}")
        return None

def test_update_user_profile(user_id):
    """Test updating user profile."""
    logger.info(f"Testing update user profile for ID: {user_id}")
    
    url = f"{BASE_URL}/api/users/{user_id}"
    data = {
        "disability": "Visual impairment",
        "can_type": False,
        "preferred_input_method": "voice",
        "programming_experience": "intermediate",
        "preferred_languages": ["python", "javascript"],
        "assistive_technologies": {
            "screen_reader": True,
            "voice_control": True,
            "switch_control": False,
            "other": "Dragon NaturallySpeaking"
        }
    }
    
    response = requests.put(url, json=data)
    logger.info(f"Update profile response: {response.status_code}")
    
    if response.status_code == 200:
        logger.info("✓ Update user profile successful")
        return response.json()["user"]
    else:
        logger.error(f"✗ Update profile failed: {response.text}")
        return None

def test_migrated_user_login():
    """Test login with migrated user."""
    logger.info("Testing login with migrated user...")
    
    url = f"{BASE_URL}/api/users/login"
    data = {
        "email": "alwindharsanam.23aid@kongu.edu",
        "password": "alwin123"  # Original password (will be hashed)
    }
    
    response = requests.post(url, json=data)
    logger.info(f"Migrated user login response: {response.status_code}")
    
    if response.status_code == 200:
        logger.info("✓ Migrated user login successful")
        return response.json()["user"]
    else:
        logger.error(f"✗ Migrated user login failed: {response.text}")
        return None

def test_health_check():
    """Test health check endpoint."""
    logger.info("Testing health check...")
    
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    logger.info(f"Health check response: {response.status_code}")
    
    if response.status_code == 200:
        logger.info("✓ Health check successful")
        logger.info(f"Health status: {response.json()}")
    else:
        logger.error(f"✗ Health check failed: {response.text}")

def main():
    """Run all tests."""
    logger.info("Starting MongoDB User API tests...")
    
    # Test health check
    test_health_check()
    
    # Test user registration
    new_user = test_user_registration()
    if not new_user:
        logger.error("Registration failed - skipping dependent tests")
        return
    
    user_id = new_user.get("id")
    logger.info(f"New user ID: {user_id}")
    
    # Test user login
    logged_in_user = test_user_login()
    if not logged_in_user:
        logger.error("Login failed")
    
    # Test get profile
    profile = test_get_user_profile(user_id)
    if not profile:
        logger.error("Get profile failed")
    
    # Test update profile
    updated_profile = test_update_user_profile(user_id)
    if not updated_profile:
        logger.error("Update profile failed")
    else:
        logger.info(f"Updated profile: {json.dumps(updated_profile, indent=2)}")
    
    # Test migrated user login
    migrated_user = test_migrated_user_login()
    if migrated_user:
        logger.info(f"Migrated user: {migrated_user['email']}")
    
    logger.info("All tests completed!")

if __name__ == "__main__":
    main()