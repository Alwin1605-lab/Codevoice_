import asyncio
import aiohttp
import json

async def test_profile_update():
    # First register a test user
    async with aiohttp.ClientSession() as session:
        # Register user
        register_data = {
            "email": "fulltest2@example.com",
            "password": "testpass123",
            "name": "Full Test User 2"
        }
        
        print("=== REGISTERING USER ===")
        async with session.post("http://localhost:8001/api/users/register", json=register_data) as response:
            if response.status in [200, 201]:  # Accept both status codes
                result = await response.json()
                print(f"Registration successful: {result}")
                user_id = result.get("user", {}).get("id")
                if not user_id:
                    print("No user ID returned from registration")
                    return
            else:
                text = await response.text()
                print(f"Registration failed: {response.status} - {text}")
                return
        
        # Headers (no token needed for MongoDB version)
        headers = {"Content-Type": "application/json"}
        
        # Complete profile update with ALL possible fields
        profile_data = {
            "full_name": "Complete Profile Test User",
            "disability": "Visual impairment and mobility limitations",
            "can_type": True,
            "programming_experience": "expert",
            "preferred_languages": ["python", "javascript", "react", "nodejs", "fastapi", "mongodb"],
            "github_username": "complete_test_user_github",
            "assistive_technologies": {
                "screen_reader": True,
                "voice_control": True,
                "switch_control": False,
                "other": "Custom keyboard shortcuts, voice commands, and screen magnifier"
            },
            "additional_needs": "Screen reader compatibility, high contrast themes, voice feedback for all actions",
            "preferred_input_method": "voice_and_keyboard",
            "typing_speed": "fast"
        }
        
        print("\n=== UPDATING PROFILE ===")
        print(f"Sending data: {json.dumps(profile_data, indent=2)}")
        
        async with session.put(f"http://localhost:8001/api/users/{user_id}", json=profile_data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                print(f"Profile update successful: {json.dumps(result, indent=2)}")
            else:
                text = await response.text()
                print(f"Profile update failed: {response.status} - {text}")
        
        # Get profile to verify
        print("\n=== GETTING UPDATED PROFILE ===")
        async with session.get(f"http://localhost:8001/api/users/{user_id}", headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                print(f"Retrieved profile: {json.dumps(result, indent=2)}")
            else:
                text = await response.text()
                print(f"Profile retrieval failed: {response.status} - {text}")

if __name__ == "__main__":
    asyncio.run(test_profile_update())