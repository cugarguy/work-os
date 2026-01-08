#!/usr/bin/env python3
"""
Demo script for conversational capture functionality.

This demonstrates the real-time conversational capture workflow:
1. Entity detection in conversation
2. Clarification questions
3. Update proposals
4. Confirmed update application
5. Conversation summary generation
"""

import tempfile
from pathlib import Path
from notes_processor import NotesProcessor


def demo_conversational_capture():
    """Demonstrate conversational capture workflow."""
    
    print("=" * 70)
    print("Conversational Capture Demo")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        processor = NotesProcessor(base_dir)
        
        # Simulate a conversation
        conversation_history = []
        
        # Turn 1: User shares information about a meeting
        print("\n--- Turn 1: User shares meeting information ---")
        note1 = "Had a great discussion with [[John]] about [[API Design Patterns]]"
        print(f"User: {note1}")
        
        response1 = processor.process_conversational(note1)
        print(f"\nEntities detected: {len(response1.entities_detected)}")
        for entity in response1.entities_detected:
            print(f"  - {entity.type}: {entity.value} (confidence: {entity.confidence:.2f})")
        
        if response1.clarification_questions:
            print(f"\nClarification questions:")
            for q in response1.clarification_questions:
                print(f"  - {q}")
        
        if response1.proposed_updates:
            print(f"\nProposed updates: {len(response1.proposed_updates)}")
            for update in response1.proposed_updates:
                print(f"  - {update['action']}: {update.get('title') or update.get('name')}")
            
            # Apply updates
            result1 = processor.apply_conversational_updates(
                response1.proposed_updates, 
                confirmed=True
            )
            conversation_history.append({
                'turn': 1,
                'note': note1,
                'applied_updates': result1['updates']
            })
            print(f"\nUpdates applied: {result1['message']}")
        
        # Turn 2: User shares more context with previous entities
        print("\n\n--- Turn 2: User provides more context ---")
        note2 = "[[John]] suggested we look at [[Microservices Architecture]] too"
        print(f"User: {note2}")
        
        # Use context from previous turn
        context = {
            'previous_entities': response1.entities_detected
        }
        response2 = processor.process_conversational(note2, context=context)
        
        print(f"\nEntities detected: {len(response2.entities_detected)}")
        for entity in response2.entities_detected:
            print(f"  - {entity.type}: {entity.value} (confidence: {entity.confidence:.2f})")
        
        if response2.proposed_updates:
            print(f"\nProposed updates: {len(response2.proposed_updates)}")
            for update in response2.proposed_updates:
                print(f"  - {update['action']}: {update.get('title') or update.get('name')}")
            
            # Apply updates
            result2 = processor.apply_conversational_updates(
                response2.proposed_updates,
                confirmed=True
            )
            conversation_history.append({
                'turn': 2,
                'note': note2,
                'applied_updates': result2['updates']
            })
            print(f"\nUpdates applied: {result2['message']}")
        
        # Turn 3: Ambiguous note requiring clarification
        print("\n\n--- Turn 3: Ambiguous note ---")
        note3 = "API stuff"
        print(f"User: {note3}")
        
        response3 = processor.process_conversational(note3)
        
        if response3.clarification_questions:
            print(f"\nClarification needed:")
            for q in response3.clarification_questions:
                print(f"  - {q}")
            print("\n(User would provide clarifications here)")
        
        # Generate conversation summary
        print("\n\n--- Conversation Summary ---")
        summary = processor.generate_conversation_summary(conversation_history)
        print(summary)
        
        print("\n" + "=" * 70)
        print("Demo complete!")
        print("=" * 70)


if __name__ == '__main__':
    demo_conversational_capture()
