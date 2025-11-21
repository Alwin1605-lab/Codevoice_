#!/usr/bin/env python3
"""
Debug script to test profile data storage and retrieval.
Run this to verify what's actually being saved to MongoDB.
"""

import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.user_models import User, AssistiveTechnologies
from datetime import datetime

async def debug_profile_data():
    """Debug profile data storage and retrieval."""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    
    # Initialize beanie with User model
    await init_beanie(database=client.voice_controlled_ide, document_models=[User])
    
    print("=== CURRENT USERS IN DATABASE ===")
    users = await User.find_all().to_list()
    
    for user in users:
        print(f"\n--- User: {user.email} ---")
        print(f"Full Name: {user.full_name}")
        print(f"Disability: {user.disability}")
        print(f"Can Type: {user.can_type}")
        print(f"Programming Experience: {user.programming_experience}")
        print(f"Preferred Languages: {user.preferred_languages}")
        print(f"GitHub Username: {user.github_username}")
        print(f"Assistive Technologies: {user.assistive_technologies}")
        print(f"Voice Settings: {user.voice_settings}")
        print(f"Additional Needs: {user.additional_needs}")
        print(f"Preferred Input Method: {user.preferred_input_method}")
        print(f"Typing Speed: {user.typing_speed}")
        print("=" * 50)
    
    # Test updating a user with comprehensive data
    if users:
        test_user = users[0]
        print(f"\n=== TESTING COMPREHENSIVE UPDATE FOR {test_user.email} ===")
        
        # Update with all possible data
        test_user.full_name = "Complete Test Profile"
        test_user.disability = "Comprehensive disability info"
        test_user.can_type = True
        test_user.preferred_input_method = "voice_and_keyboard"
        test_user.typing_speed = "medium"
        test_user.additional_needs = "Screen reader and voice support"
        test_user.programming_experience = "expert"
        test_user.preferred_languages = ["python", "javascript", "react", "fastapi"]
        test_user.github_username = "comprehensive_test_user"
        test_user.assistive_technologies = AssistiveTechnologies(
            screen_reader=True,
            voice_control=True,
            switch_control=False,
            other="Custom keyboard shortcuts and voice commands"
        )
        test_user.updated_at = datetime.utcnow()
        
        # Save the updated user
        await test_user.save()
        
        print("User updated successfully!")
        
        # Retrieve and display the updated user
        updated_user = await User.get(test_user.id)
        print(f"\n--- UPDATED USER DATA ---")
        print(f"Full Name: {updated_user.full_name}")
        print(f"Disability: {updated_user.disability}")
        print(f"Can Type: {updated_user.can_type}")
        print(f"Programming Experience: {updated_user.programming_experience}")
        print(f"Preferred Languages: {updated_user.preferred_languages}")
        print(f"GitHub Username: {updated_user.github_username}")
        print(f"Assistive Technologies: {updated_user.assistive_technologies}")
        print(f"Additional Needs: {updated_user.additional_needs}")
        print(f"Preferred Input Method: {updated_user.preferred_input_method}")
        print(f"Typing Speed: {updated_user.typing_speed}")
        print(f"Updated At: {updated_user.updated_at}")
    
    # Close the connection
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_profile_data())