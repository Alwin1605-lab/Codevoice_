import asyncio
import aiohttp
import json

async def test_new_database_apis():
    """Test the new database-backed APIs to ensure they save data."""
    
    async with aiohttp.ClientSession() as session:
        print("=== TESTING NEW DATABASE APIs ===\n")
        
        # Test 1: Create a Project
        print("1. Testing Project Creation...")
        project_data = {
            "name": "Test Voice Controlled App",
            "description": "A test project created via new database API",
            "natural_language_prompt": "Create a voice-controlled application with React frontend",
            "framework": "react",
            "features": ["voice-control", "responsive-design", "accessibility"],
            "is_public": True
        }
        
        try:
            async with session.post("http://localhost:8001/api/projects/create", json=project_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Project created: {result}")
                    project_id = result.get("project", {}).get("id")
                else:
                    text = await response.text()
                    print(f"❌ Project creation failed: {response.status} - {text}")
                    project_id = None
        except Exception as e:
            print(f"❌ Project creation error: {e}")
            project_id = None
        
        # Test 2: List Projects
        print("\n2. Testing Project Listing...")
        try:
            async with session.get("http://localhost:8001/api/projects/list") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Projects listed: {len(result.get('projects', []))} projects found")
                    for proj in result.get('projects', [])[:3]:  # Show first 3
                        print(f"   - {proj.get('name')} (ID: {proj.get('id')})")
                else:
                    text = await response.text()
                    print(f"❌ Project listing failed: {response.status} - {text}")
        except Exception as e:
            print(f"❌ Project listing error: {e}")
        
        # Test 3: Create Collaboration Session
        print("\n3. Testing Collaboration Session Creation...")
        session_data = {
            "name": "Test Collaboration Session",
            "description": "Testing the new database collaboration API",
            "project_id": project_id,
            "creator_id": "test_user_123",
            "max_participants": 5,
            "is_public": True
        }
        
        try:
            async with session.post("http://localhost:8001/api/collaboration/sessions", json=session_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Collaboration session created: {result}")
                    session_id = result.get("session", {}).get("id")
                else:
                    text = await response.text()
                    print(f"❌ Collaboration session creation failed: {response.status} - {text}")
                    session_id = None
        except Exception as e:
            print(f"❌ Collaboration session creation error: {e}")
            session_id = None
        
        # Test 4: List Collaboration Sessions
        print("\n4. Testing Collaboration Session Listing...")
        try:
            async with session.get("http://localhost:8001/api/collaboration/sessions") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Collaboration sessions listed: {len(result.get('sessions', []))} sessions found")
                    for sess in result.get('sessions', [])[:3]:  # Show first 3
                        print(f"   - {sess.get('name')} (ID: {sess.get('id')})")
                else:
                    text = await response.text()
                    print(f"❌ Collaboration session listing failed: {response.status} - {text}")
        except Exception as e:
            print(f"❌ Collaboration session listing error: {e}")
        
        # Test 5: Save Voice Command
        print("\n5. Testing Voice Command Saving...")
        command_data = {
            "user_id": "test_user_123",
            "command_text": "Create a new React component called UserProfile",
            "command_type": "code_generation",
            "language": "en",
            "confidence_score": 0.95,
            "execution_successful": True,
            "response_text": "React component created successfully",
            "execution_time_ms": 1500
        }
        
        try:
            async with session.post("http://localhost:8001/api/voice-commands/commands", json=command_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Voice command saved: {result}")
                else:
                    text = await response.text()
                    print(f"❌ Voice command saving failed: {response.status} - {text}")
        except Exception as e:
            print(f"❌ Voice command saving error: {e}")
        
        # Test 6: Save Usage Analytics
        print("\n6. Testing Usage Analytics Saving...")
        analytics_data = {
            "user_id": "test_user_123",
            "feature_used": "project_creation",
            "session_duration_seconds": 300,
            "actions_performed": 5,
            "errors_encountered": 0,
            "success_rate": 100.0,
            "additional_data": {"browser": "Chrome", "os": "Windows"}
        }
        
        try:
            async with session.post("http://localhost:8001/api/voice-commands/usage-analytics", json=analytics_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Usage analytics saved: {result}")
                else:
                    text = await response.text()
                    print(f"❌ Usage analytics saving failed: {response.status} - {text}")
        except Exception as e:
            print(f"❌ Usage analytics saving error: {e}")
        
        print("\n=== NEW DATABASE API TESTING COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_new_database_apis())