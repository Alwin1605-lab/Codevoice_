"""
Data migration script to transfer user data from JSON files to MongoDB.
Runs once to migrate existing user data, then can be removed.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Import models
from models.user_models import User, AssistiveTechnologies

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_users_to_mongodb():
    """Migrate users from JSON file to MongoDB."""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    database = client["voice_controlled_ide"]
    
    # Initialize Beanie
    await init_beanie(database=database, document_models=[User])
    
    logger.info("Connected to MongoDB for migration")
    
    # Read existing JSON data
    json_file_path = os.path.join("data", "users.json")
    
    if not os.path.exists(json_file_path):
        logger.info("No users.json file found - nothing to migrate")
        return
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users_data = data.get('users', [])
    logger.info(f"Found {len(users_data)} users to migrate")
    
    migrated_count = 0
    skipped_count = 0
    
    for user_data in users_data:
        try:
            # Check if user already exists in MongoDB
            existing_user = await User.find_one(User.email == user_data['email'])
            if existing_user:
                logger.info(f"User {user_data['email']} already exists - skipping")
                skipped_count += 1
                continue
            
            # Convert assistive technologies
            assistive_tech_data = user_data.get('assistiveTechnologies', {})
            assistive_tech = AssistiveTechnologies(
                screen_reader=assistive_tech_data.get('screenReader', False),
                voice_control=assistive_tech_data.get('voiceControl', False),
                switch_control=assistive_tech_data.get('switchControl', False),
                other=assistive_tech_data.get('other', '')
            )
            
            # Create User object
            user = User(
                username=user_data['name'].lower().replace(' ', '_'),
                email=user_data['email'],
                password_hash=user_data['password'],  # Already hashed
                full_name=user_data['name'],
                is_active=True,
                email_verified=False,
                preferred_language="en",
                
                # Accessibility fields from JSON
                disability=user_data.get('disability', ''),
                can_type=user_data.get('canType', True),
                preferred_input_method=user_data.get('preferredInputMethod', ''),
                typing_speed=user_data.get('typingSpeed', ''),
                additional_needs=user_data.get('additionalNeeds', ''),
                programming_experience=user_data.get('programmingExperience', ''),
                preferred_languages=user_data.get('preferredLanguages', []),
                assistive_technologies=assistive_tech,
                
                # Set timestamps
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save to MongoDB
            await user.insert()
            logger.info(f"Migrated user: {user.email}")
            migrated_count += 1
            
        except Exception as e:
            logger.error(f"Failed to migrate user {user_data.get('email', 'unknown')}: {e}")
    
    logger.info(f"Migration completed: {migrated_count} users migrated, {skipped_count} skipped")
    
    # Close MongoDB connection
    client.close()

async def verify_migration():
    """Verify that migration was successful."""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    database = client["voice_controlled_ide"]
    
    # Initialize Beanie
    await init_beanie(database=database, document_models=[User])
    
    # Count users in MongoDB
    user_count = await User.count()
    logger.info(f"Total users in MongoDB: {user_count}")
    
    # List all users
    users = await User.find_all().to_list()
    for user in users:
        logger.info(f"User: {user.email} (ID: {user.id})")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    # Run migration
    asyncio.run(migrate_users_to_mongodb())
    
    # Verify migration
    print("\nVerifying migration...")
    asyncio.run(verify_migration())
    
    print("\nMigration complete!")
    print("You can now delete the data/users.json file if migration was successful.")