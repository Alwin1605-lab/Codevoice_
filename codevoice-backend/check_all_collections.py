import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models.user_models import User
from models.project_models import Project, ProjectFile, CodeSession, VoiceCommand
from models.collaboration_models import CollaborationSession, CollaborationEvent, CollaborationInvite
from models.analytics_models import UsageAnalytics, TranscriptionAnalytics, LearningProgress, Notification, APIRateLimit, AudioFile, ProjectBackup

async def check_all_collections():
    """Check all collections in the database for data."""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    database = client.voice_controlled_ide
    
    # Initialize Beanie with all models
    await init_beanie(
        database=database,
        document_models=[
            User,
            Project, CodeSession, VoiceCommand,
            CollaborationSession, CollaborationEvent, CollaborationInvite,
            UsageAnalytics, TranscriptionAnalytics, LearningProgress, 
            Notification, APIRateLimit, AudioFile, ProjectBackup
        ]
    )
    
    print("=== CHECKING ALL COLLECTIONS ===\n")
    
    # Check each collection
    collections_to_check = [
        ("Users", User),
        ("Projects", Project),
        ("Code Sessions", CodeSession),
        ("Voice Commands", VoiceCommand),
        ("Collaboration Sessions", CollaborationSession),
        ("Collaboration Events", CollaborationEvent),
        ("Collaboration Invites", CollaborationInvite),
        ("Usage Analytics", UsageAnalytics),
        ("Transcription Analytics", TranscriptionAnalytics),
        ("Learning Progress", LearningProgress),
        ("Notifications", Notification),
        ("API Rate Limits", APIRateLimit),
        ("Audio Files", AudioFile),
        ("Project Backups", ProjectBackup),
    ]
    
    for collection_name, model_class in collections_to_check:
        try:
            count = await model_class.count()
            print(f"📊 {collection_name}: {count} documents")
            
            if count > 0:
                # Show first few documents
                docs = await model_class.find().limit(3).to_list()
                for i, doc in enumerate(docs, 1):
                    print(f"   Sample {i}: {doc.dict()}")
                print()
        except Exception as e:
            print(f"❌ Error checking {collection_name}: {e}")
    
    # Check raw database collections
    print("\n=== RAW DATABASE COLLECTIONS ===")
    collection_names = await database.list_collection_names()
    for name in collection_names:
        collection = database[name]
        count = await collection.count_documents({})
        print(f"📁 {name}: {count} documents")

if __name__ == "__main__":
    asyncio.run(check_all_collections())