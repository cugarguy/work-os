#!/usr/bin/env python3
"""
Notes Processing Engine for WorkOS

This module provides functionality to process raw notes from multiple input
sources (file-based inbox, interactive sessions, conversational capture, and
meeting notes) and route them to appropriate handlers.
"""

import re
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an extracted entity from notes"""
    type: str  # 'knowledge', 'person', 'time', 'meeting'
    value: str  # The entity text
    context: str  # Surrounding context
    confidence: float  # 0.0 to 1.0
    ambiguous: bool  # Whether this entity needs clarification
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class ProcessedNote:
    """Represents a processed note with extracted entities"""
    original_text: str
    entities: List[Entity]
    note_type: str  # 'knowledge', 'people', 'time', 'meeting', 'mixed'
    requires_clarification: bool
    clarification_questions: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['entities'] = [e.to_dict() for e in self.entities]
        return result


@dataclass
class ProcessingResult:
    """Result of batch notes processing"""
    processed_count: int
    knowledge_created: List[str]
    knowledge_updated: List[str]
    people_created: List[str]
    people_updated: List[str]
    time_entries_created: List[str]
    errors: List[str]
    summary: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class InteractiveSession:
    """Represents an interactive processing session"""
    session_id: str
    notes: List[str]
    current_index: int
    processed_notes: List[ProcessedNote]
    pending_clarifications: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['processed_notes'] = [n.to_dict() for n in self.processed_notes]
        return result


@dataclass
class ConversationResponse:
    """Response from conversational note processing"""
    entities_detected: List[Entity]
    clarification_questions: List[str]
    proposed_updates: List[Dict]
    requires_confirmation: bool
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['entities_detected'] = [e.to_dict() for e in self.entities_detected]
        return result


@dataclass
class MeetingProcessingResult:
    """Result of meeting notes processing"""
    meeting_id: str
    attendees: List[str]
    topics: List[str]
    knowledge_created: List[str]
    knowledge_updated: List[str]
    people_updated: List[str]
    connections_created: List[Dict]
    summary: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)


class NotesProcessor:
    """
    Process raw notes from multiple input sources and route to appropriate handlers.
    
    Supports:
    - Batch processing from inbox file
    - Interactive processing with clarifications
    - Real-time conversational capture
    - Meeting notes integration
    """
    
    # Patterns for entity detection
    WIKILINK_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')
    PERSON_MENTION_PATTERN = re.compile(r'@(\w+)|with (\w+)|discussed with (\w+)', re.IGNORECASE)
    TIME_PATTERN = re.compile(r'(\d+)\s*(hour|hr|minute|min)s?', re.IGNORECASE)
    
    # Keywords for knowledge topics
    KNOWLEDGE_KEYWORDS = [
        'learned', 'discovered', 'found out', 'realized', 'understanding',
        'concept', 'idea', 'approach', 'pattern', 'strategy', 'technique',
        'about', 'regarding', 'related to', 'notes on'
    ]
    
    # Keywords for people mentions
    PEOPLE_KEYWORDS = [
        'met with', 'talked to', 'discussed with', 'collaborated with',
        'worked with', 'meeting with', 'call with', 'sync with'
    ]
    
    def __init__(self, base_dir: Path):
        """
        Initialize the notes processor.
        
        Args:
            base_dir: Base directory containing the WorkOS system
        """
        self.base_dir = Path(base_dir)
        self.notes_inbox = self.base_dir / 'NOTES_INBOX.md'
        
        # Ensure inbox exists
        if not self.notes_inbox.exists():
            self.notes_inbox.write_text("# Notes Inbox\n\n", encoding='utf-8')
    
    def process_batch(self, notes_file: Optional[Path] = None) -> ProcessingResult:
        """
        Process notes from inbox file in batch mode.
        
        Reads all notes from the inbox, extracts entities, creates/updates
        knowledge and people documents, then clears the inbox.
        
        Args:
            notes_file: Optional path to notes file (defaults to NOTES_INBOX.md)
            
        Returns:
            ProcessingResult with summary of all updates
        """
        if notes_file is None:
            notes_file = self.notes_inbox
        
        if not notes_file.exists():
            logger.error(f"Notes file not found: {notes_file}")
            return ProcessingResult(
                processed_count=0,
                knowledge_created=[],
                knowledge_updated=[],
                people_created=[],
                people_updated=[],
                time_entries_created=[],
                errors=[f"Notes file not found: {notes_file}"],
                summary="No notes to process"
            )
        
        try:
            # Read notes
            with open(notes_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into individual notes (by blank lines or headers)
            notes = self._split_notes(content)
            
            # Process each note
            result = ProcessingResult(
                processed_count=len(notes),
                knowledge_created=[],
                knowledge_updated=[],
                people_created=[],
                people_updated=[],
                time_entries_created=[],
                errors=[],
                summary=""
            )
            
            for note_text in notes:
                if not note_text.strip():
                    continue
                
                try:
                    # Extract entities
                    entities = self.extract_entities(note_text)
                    
                    # Route to appropriate handlers
                    # Note: Actual routing to KnowledgeManager, PeopleManager, etc.
                    # will be implemented in the MCP server layer
                    
                    # For now, just track what would be created/updated
                    for entity in entities:
                        if entity.type == 'knowledge':
                            if self._is_new_knowledge(entity.value):
                                result.knowledge_created.append(entity.value)
                            else:
                                result.knowledge_updated.append(entity.value)
                        elif entity.type == 'person':
                            if self._is_new_person(entity.value):
                                result.people_created.append(entity.value)
                            else:
                                result.people_updated.append(entity.value)
                        elif entity.type == 'time':
                            result.time_entries_created.append(f"time_entry_{len(result.time_entries_created)}")
                
                except Exception as e:
                    logger.error(f"Error processing note: {e}")
                    result.errors.append(f"Error processing note: {str(e)}")
            
            # Generate summary
            result.summary = self._generate_batch_summary(result)
            
            # Clear inbox (preserve header)
            self._clear_inbox(notes_file)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return ProcessingResult(
                processed_count=0,
                knowledge_created=[],
                knowledge_updated=[],
                people_created=[],
                people_updated=[],
                time_entries_created=[],
                errors=[f"Batch processing error: {str(e)}"],
                summary="Processing failed"
            )
    
    def process_interactive(self, notes_file: Optional[Path] = None) -> InteractiveSession:
        """
        Start an interactive processing session.
        
        Presents notes one at a time, asks clarifying questions, and
        waits for user confirmation before applying updates.
        
        Args:
            notes_file: Optional path to notes file (defaults to NOTES_INBOX.md)
            
        Returns:
            InteractiveSession object for managing the session
        """
        if notes_file is None:
            notes_file = self.notes_inbox
        
        if not notes_file.exists():
            logger.error(f"Notes file not found: {notes_file}")
            return InteractiveSession(
                session_id=str(uuid.uuid4()),
                notes=[],
                current_index=0,
                processed_notes=[],
                pending_clarifications=[]
            )
        
        try:
            # Read notes
            with open(notes_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into individual notes
            notes = self._split_notes(content)
            
            # Create session
            session = InteractiveSession(
                session_id=str(uuid.uuid4()),
                notes=notes,
                current_index=0,
                processed_notes=[],
                pending_clarifications=[]
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Error starting interactive session: {e}")
            return InteractiveSession(
                session_id=str(uuid.uuid4()),
                notes=[],
                current_index=0,
                processed_notes=[],
                pending_clarifications=[]
            )
    
    def process_next_note(self, session: InteractiveSession) -> Optional[ProcessedNote]:
        """
        Process the next note in an interactive session.
        
        Extracts entities, detects ambiguities, and generates clarification
        questions for the current note.
        
        Args:
            session: The interactive session
            
        Returns:
            ProcessedNote for the current note, or None if session is complete
        """
        if session.current_index >= len(session.notes):
            return None
        
        try:
            # Get current note
            note_text = session.notes[session.current_index]
            
            # Extract entities
            entities = self.extract_entities(note_text)
            
            # Detect ambiguities and missing context
            clarification_questions = self._generate_clarification_questions(entities, note_text)
            
            # Check for missing context
            missing_context_questions = self._detect_missing_context(entities, note_text)
            clarification_questions.extend(missing_context_questions)
            
            # Determine note type
            note_type = self._determine_note_type(entities)
            
            # Create processed note
            processed_note = ProcessedNote(
                original_text=note_text,
                entities=entities,
                note_type=note_type,
                requires_clarification=len(clarification_questions) > 0,
                clarification_questions=clarification_questions
            )
            
            # Add to session
            session.processed_notes.append(processed_note)
            
            # Store pending clarifications if any
            if clarification_questions:
                session.pending_clarifications.append({
                    'note_index': session.current_index,
                    'questions': clarification_questions,
                    'answers': {}
                })
            
            return processed_note
            
        except Exception as e:
            logger.error(f"Error processing note: {e}")
            return None
    
    def incorporate_clarifications(self, session: InteractiveSession, 
                                   note_index: int, 
                                   clarifications: Dict[str, str]) -> ProcessedNote:
        """
        Incorporate user clarifications into a processed note.
        
        Updates the entities and proposed updates based on user-provided
        clarifications.
        
        Args:
            session: The interactive session
            note_index: Index of the note being clarified
            clarifications: Dictionary mapping questions to answers
            
        Returns:
            Updated ProcessedNote with clarifications incorporated
        """
        if note_index >= len(session.processed_notes):
            raise ValueError(f"Invalid note index: {note_index}")
        
        try:
            processed_note = session.processed_notes[note_index]
            
            # Update entities based on clarifications
            updated_entities = []
            for entity in processed_note.entities:
                # Check if this entity was clarified
                entity_updated = False
                
                for question, answer in clarifications.items():
                    # If the question mentions this entity, update it
                    if entity.value in question:
                        # Update confidence and ambiguity based on clarification
                        entity.confidence = 1.0
                        entity.ambiguous = False
                        
                        # Update context with clarification
                        entity.context = f"{entity.context} [Clarified: {answer}]"
                        entity_updated = True
                
                updated_entities.append(entity)
            
            # Update the processed note
            processed_note.entities = updated_entities
            processed_note.requires_clarification = False
            processed_note.clarification_questions = []
            
            # Remove from pending clarifications
            session.pending_clarifications = [
                pc for pc in session.pending_clarifications 
                if pc['note_index'] != note_index
            ]
            
            return processed_note
            
        except Exception as e:
            logger.error(f"Error incorporating clarifications: {e}")
            raise
    
    def confirm_updates(self, session: InteractiveSession, 
                       note_index: int, 
                       confirmed: bool) -> Dict:
        """
        Confirm or reject proposed updates for a note.
        
        If confirmed, returns the updates to be applied. If rejected,
        marks the note as skipped.
        
        Args:
            session: The interactive session
            note_index: Index of the note
            confirmed: Whether updates are confirmed
            
        Returns:
            Dictionary with update information
        """
        if note_index >= len(session.processed_notes):
            raise ValueError(f"Invalid note index: {note_index}")
        
        try:
            processed_note = session.processed_notes[note_index]
            
            if not confirmed:
                return {
                    'confirmed': False,
                    'note_index': note_index,
                    'updates': []
                }
            
            # Generate proposed updates
            proposed_updates = self._generate_proposed_updates(
                processed_note.entities, 
                processed_note.original_text
            )
            
            return {
                'confirmed': True,
                'note_index': note_index,
                'updates': proposed_updates,
                'entities': [e.to_dict() for e in processed_note.entities]
            }
            
        except Exception as e:
            logger.error(f"Error confirming updates: {e}")
            raise
    
    def advance_session(self, session: InteractiveSession):
        """
        Advance the session to the next note.
        
        Args:
            session: The interactive session
        """
        session.current_index += 1
    
    def _detect_missing_context(self, entities: List[Entity], text: str) -> List[str]:
        """
        Detect missing context in a note.
        
        Identifies when a note lacks sufficient information for proper
        knowledge or people updates.
        
        Args:
            entities: List of extracted entities
            text: Original note text
            
        Returns:
            List of questions about missing context
        """
        questions = []
        
        # Check if note is too short
        if len(text.strip()) < 20:
            questions.append("This note seems very brief. Can you provide more details?")
        
        # Check if entities have low confidence
        low_confidence_entities = [e for e in entities if e.confidence < 0.6]
        if low_confidence_entities:
            for entity in low_confidence_entities:
                questions.append(f"Can you clarify what you mean by '{entity.value}'?")
        
        # Check if note has entities but no clear action or insight
        if entities and not any(keyword in text.lower() for keyword in 
                               ['learned', 'discovered', 'discussed', 'met', 'worked', 'found']):
            questions.append("What did you learn or accomplish related to this?")
        
        # Check for vague references
        vague_patterns = [r'\bit\b', r'\bthey\b', r'\bthat\b', r'\bthis\b']
        for pattern in vague_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                questions.append("There are some vague references in this note. Can you be more specific?")
                break
        
        return questions
    
    def _determine_note_type(self, entities: List[Entity]) -> str:
        """
        Determine the primary type of a note based on entities.
        
        Args:
            entities: List of extracted entities
            
        Returns:
            Note type: 'knowledge', 'people', 'time', 'meeting', or 'mixed'
        """
        if not entities:
            return 'mixed'
        
        entity_types = [e.type for e in entities]
        
        # Count entity types
        type_counts = {}
        for entity_type in entity_types:
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        # Determine primary type
        if len(type_counts) == 1:
            return list(type_counts.keys())[0]
        
        # If multiple types, check for meeting indicators
        if 'person' in type_counts and type_counts['person'] > 1:
            return 'meeting'
        
        # Otherwise it's mixed
        return 'mixed'
    
    def process_conversational(self, note_text: str, context: Optional[Dict] = None) -> ConversationResponse:
        """
        Process a note from real-time conversation.
        
        Analyzes the note, detects entities, asks clarifying questions,
        and proposes updates for user confirmation.
        
        Args:
            note_text: The note text from conversation
            context: Optional context from previous conversation turns
            
        Returns:
            ConversationResponse with detected entities and proposed updates
        """
        try:
            # Extract entities with real-time detection
            entities = self.extract_entities(note_text)
            
            # Enhance entity detection with context if available
            if context and 'previous_entities' in context:
                entities = self._enhance_entities_with_context(entities, context['previous_entities'])
            
            # Detect ambiguities and generate clarification questions
            clarification_questions = self._generate_conversational_clarifications(entities, note_text)
            
            # Check for missing context
            missing_context_questions = self._detect_missing_context(entities, note_text)
            clarification_questions.extend(missing_context_questions)
            
            # Propose updates (if no clarifications needed)
            proposed_updates = []
            requires_confirmation = len(clarification_questions) > 0
            
            if not requires_confirmation:
                proposed_updates = self._generate_proposed_updates(entities, note_text)
                requires_confirmation = len(proposed_updates) > 0
            
            return ConversationResponse(
                entities_detected=entities,
                clarification_questions=clarification_questions,
                proposed_updates=proposed_updates,
                requires_confirmation=requires_confirmation
            )
            
        except Exception as e:
            logger.error(f"Error in conversational processing: {e}")
            return ConversationResponse(
                entities_detected=[],
                clarification_questions=[f"Error processing note: {str(e)}"],
                proposed_updates=[],
                requires_confirmation=False
            )
    
    def apply_conversational_updates(self, proposed_updates: List[Dict], 
                                    confirmed: bool = True) -> Dict:
        """
        Apply confirmed updates from conversational capture.
        
        Creates or updates knowledge documents and person profiles based on
        user-confirmed updates from conversation.
        
        Args:
            proposed_updates: List of proposed update dictionaries
            confirmed: Whether updates are confirmed by user
            
        Returns:
            Dictionary with results of applied updates
        """
        if not confirmed:
            return {
                'applied': False,
                'updates': [],
                'message': 'Updates not confirmed by user'
            }
        
        try:
            applied_updates = []
            errors = []
            
            for update in proposed_updates:
                try:
                    action = update.get('action')
                    
                    if action == 'create_knowledge':
                        # Track that knowledge would be created
                        applied_updates.append({
                            'type': 'knowledge_created',
                            'title': update.get('title'),
                            'content': update.get('content')
                        })
                    
                    elif action == 'update_knowledge':
                        # Track that knowledge would be updated
                        applied_updates.append({
                            'type': 'knowledge_updated',
                            'title': update.get('title'),
                            'additional_content': update.get('additional_content')
                        })
                    
                    elif action == 'create_person':
                        # Track that person would be created
                        applied_updates.append({
                            'type': 'person_created',
                            'name': update.get('name'),
                            'context': update.get('context')
                        })
                    
                    elif action == 'update_person':
                        # Track that person would be updated
                        applied_updates.append({
                            'type': 'person_updated',
                            'name': update.get('name'),
                            'additional_context': update.get('additional_context')
                        })
                
                except Exception as e:
                    logger.error(f"Error applying update: {e}")
                    errors.append(f"Failed to apply {update.get('action')}: {str(e)}")
            
            return {
                'applied': True,
                'updates': applied_updates,
                'errors': errors,
                'message': f"Applied {len(applied_updates)} updates"
            }
            
        except Exception as e:
            logger.error(f"Error applying conversational updates: {e}")
            return {
                'applied': False,
                'updates': [],
                'errors': [str(e)],
                'message': f"Error: {str(e)}"
            }
    
    def generate_conversation_summary(self, conversation_history: List[Dict]) -> str:
        """
        Generate a summary of all updates made during a conversation.
        
        Summarizes knowledge created/updated, people created/updated, and
        connections made during the conversational capture session.
        
        Args:
            conversation_history: List of conversation turns with updates
            
        Returns:
            Summary string
        """
        try:
            knowledge_created = []
            knowledge_updated = []
            people_created = []
            people_updated = []
            
            for turn in conversation_history:
                if 'applied_updates' in turn:
                    for update in turn['applied_updates']:
                        update_type = update.get('type')
                        
                        if update_type == 'knowledge_created':
                            knowledge_created.append(update.get('title'))
                        elif update_type == 'knowledge_updated':
                            knowledge_updated.append(update.get('title'))
                        elif update_type == 'person_created':
                            people_created.append(update.get('name'))
                        elif update_type == 'person_updated':
                            people_updated.append(update.get('name'))
            
            # Build summary
            summary_parts = []
            
            if knowledge_created:
                summary_parts.append(f"Created {len(knowledge_created)} knowledge documents: {', '.join(knowledge_created)}")
            
            if knowledge_updated:
                summary_parts.append(f"Updated {len(knowledge_updated)} knowledge documents: {', '.join(knowledge_updated)}")
            
            if people_created:
                summary_parts.append(f"Created {len(people_created)} person profiles: {', '.join(people_created)}")
            
            if people_updated:
                summary_parts.append(f"Updated {len(people_updated)} person profiles: {', '.join(people_updated)}")
            
            if not summary_parts:
                return "No updates were made during this conversation."
            
            return "Conversation Summary: " + ". ".join(summary_parts) + "."
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _enhance_entities_with_context(self, entities: List[Entity], 
                                      previous_entities: List[Entity]) -> List[Entity]:
        """
        Enhance entity detection using context from previous conversation turns.
        
        Args:
            entities: Currently detected entities
            previous_entities: Entities from previous turns
            
        Returns:
            Enhanced list of entities
        """
        # Increase confidence for entities that appeared before
        for entity in entities:
            for prev_entity in previous_entities:
                if entity.value.lower() == prev_entity.value.lower() and entity.type == prev_entity.type:
                    # Boost confidence for repeated mentions
                    entity.confidence = min(1.0, entity.confidence + 0.2)
                    entity.ambiguous = False
                    break
        
        return entities
    
    def _generate_conversational_clarifications(self, entities: List[Entity], 
                                               text: str) -> List[str]:
        """
        Generate clarification questions suitable for conversational flow.
        
        Uses more natural language than batch processing clarifications.
        
        Args:
            entities: List of extracted entities
            text: Original note text
            
        Returns:
            List of clarification questions
        """
        questions = []
        
        for entity in entities:
            if entity.ambiguous:
                if entity.type == 'person':
                    questions.append(f"I found multiple people named '{entity.value}'. Which one are you referring to?")
                elif entity.type == 'knowledge':
                    questions.append(f"Is '{entity.value}' a new topic, or is it related to something you've mentioned before?")
            
            if entity.confidence < 0.6:
                questions.append(f"Can you tell me more about '{entity.value}'?")
        
        return questions
    
    def process_meeting_notes(self, meeting_data: Dict) -> MeetingProcessingResult:
        """
        Process meeting notes with attendees and topics.
        
        Extracts knowledge topics, updates person profiles, and creates
        connections between attendees, topics, and related knowledge.
        
        Args:
            meeting_data: Dictionary containing:
                - attendees: List of attendee names
                - topics: List of topics discussed
                - notes: Meeting notes text
                - date: Meeting date
                
        Returns:
            MeetingProcessingResult with all updates
        """
        try:
            meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            attendees = meeting_data.get('attendees', [])
            topics = meeting_data.get('topics', [])
            notes = meeting_data.get('notes', '')
            
            # Extract additional entities from notes
            entities = self.extract_entities(notes)
            
            # Track what would be created/updated
            result = MeetingProcessingResult(
                meeting_id=meeting_id,
                attendees=attendees,
                topics=topics,
                knowledge_created=[],
                knowledge_updated=[],
                people_updated=[],
                connections_created=[],
                summary=""
            )
            
            # Process topics as knowledge
            for topic in topics:
                if self._is_new_knowledge(topic):
                    result.knowledge_created.append(topic)
                else:
                    result.knowledge_updated.append(topic)
            
            # Process attendees as people
            for attendee in attendees:
                result.people_updated.append(attendee)
            
            # Create connections
            for attendee in attendees:
                for topic in topics:
                    result.connections_created.append({
                        'type': 'person_to_knowledge',
                        'source': attendee,
                        'target': topic,
                        'context': f"Discussed in meeting {meeting_id}"
                    })
            
            # Generate summary
            result.summary = f"Processed meeting with {len(attendees)} attendees and {len(topics)} topics"
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing meeting notes: {e}")
            return MeetingProcessingResult(
                meeting_id="error",
                attendees=[],
                topics=[],
                knowledge_created=[],
                knowledge_updated=[],
                people_updated=[],
                connections_created=[],
                summary=f"Error: {str(e)}"
            )
    
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract entities (knowledge topics, people, time references) from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of Entity objects
        """
        entities = []
        
        # Extract wikilinks (explicit knowledge references)
        for match in self.WIKILINK_PATTERN.finditer(text):
            target = match.group(1).strip()
            context = self._extract_context(text, match.start(), match.end())
            
            # Determine if it's a person or knowledge
            entity_type = 'person' if self._looks_like_person(target) else 'knowledge'
            
            entities.append(Entity(
                type=entity_type,
                value=target,
                context=context,
                confidence=1.0,  # Explicit wikilinks have high confidence
                ambiguous=False
            ))
        
        # Extract person mentions
        for match in self.PERSON_MENTION_PATTERN.finditer(text):
            # Get the captured group that's not None
            person_name = next((g for g in match.groups() if g is not None), None)
            if person_name:
                context = self._extract_context(text, match.start(), match.end())
                
                entities.append(Entity(
                    type='person',
                    value=person_name,
                    context=context,
                    confidence=0.8,  # Inferred mentions have lower confidence
                    ambiguous=self._is_ambiguous_person(person_name)
                ))
        
        # Extract knowledge topics (implicit)
        knowledge_topics = self._extract_knowledge_topics(text)
        for topic, confidence in knowledge_topics:
            context = self._extract_context_for_topic(text, topic)
            
            entities.append(Entity(
                type='knowledge',
                value=topic,
                context=context,
                confidence=confidence,
                ambiguous=confidence < 0.7
            ))
        
        # Extract time references
        for match in self.TIME_PATTERN.finditer(text):
            duration = match.group(1)
            unit = match.group(2)
            context = self._extract_context(text, match.start(), match.end())
            
            entities.append(Entity(
                type='time',
                value=f"{duration} {unit}",
                context=context,
                confidence=1.0,
                ambiguous=False
            ))
        
        return entities
    
    def _split_notes(self, content: str) -> List[str]:
        """
        Split content into individual notes.
        
        Notes are separated by:
        - Double blank lines
        - Markdown headers (## or ###)
        - Horizontal rules (---)
        
        Args:
            content: Full content string
            
        Returns:
            List of individual note strings
        """
        # Remove the header if present
        if content.startswith('# Notes Inbox'):
            content = re.sub(r'^# Notes Inbox\s*\n+', '', content)
        
        # Split by double blank lines
        notes = re.split(r'\n\s*\n\s*\n', content)
        
        # Also split by headers
        all_notes = []
        for note in notes:
            # Split by headers
            header_split = re.split(r'\n(#{2,3}\s+.+)\n', note)
            all_notes.extend([n.strip() for n in header_split if n.strip()])
        
        return [n for n in all_notes if n and not n.startswith('#')]
    
    def _extract_context(self, text: str, start: int, end: int, context_chars: int = 50) -> str:
        """
        Extract surrounding context for a match.
        
        Args:
            text: Full text
            start: Start position of match
            end: End position of match
            context_chars: Characters to include on each side
            
        Returns:
            Context string
        """
        context_start = max(0, start - context_chars)
        context_end = min(len(text), end + context_chars)
        
        context = text[context_start:context_end].strip()
        return context
    
    def _extract_context_for_topic(self, text: str, topic: str, context_chars: int = 50) -> str:
        """
        Extract context for a topic mention.
        
        Args:
            text: Full text
            topic: Topic to find
            context_chars: Characters to include on each side
            
        Returns:
            Context string
        """
        pos = text.lower().find(topic.lower())
        if pos == -1:
            return ""
        
        return self._extract_context(text, pos, pos + len(topic), context_chars)
    
    def _extract_knowledge_topics(self, text: str) -> List[Tuple[str, float]]:
        """
        Extract implicit knowledge topics from text.
        
        Uses keyword matching and capitalization patterns to identify topics.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (topic, confidence) tuples
        """
        topics = []
        
        # Look for capitalized phrases (potential topics)
        capitalized_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b')
        for match in capitalized_pattern.finditer(text):
            topic = match.group(1)
            
            # Skip common words
            if topic.lower() in ['the', 'a', 'an', 'i', 'you', 'we', 'they']:
                continue
            
            # Check if it's near a knowledge keyword
            context = self._extract_context(text, match.start(), match.end(), 100)
            confidence = 0.5
            
            for keyword in self.KNOWLEDGE_KEYWORDS:
                if keyword in context.lower():
                    confidence = 0.8
                    break
            
            topics.append((topic, confidence))
        
        return topics
    
    def _looks_like_person(self, text: str) -> bool:
        """
        Determine if text looks like a person name.
        
        Args:
            text: Text to check
            
        Returns:
            True if it looks like a person name
        """
        # Check if it's in the People directory - use consolidated knowledgebase
        people_dir = self.base_dir / 'knowledgebase' / '-common' / 'People'
        if people_dir.exists():
            person_file = people_dir / f"{text}.md"
            if person_file.exists():
                return True
        
        # Check if it's a capitalized name pattern (including all caps)
        # Matches: "John", "John Smith", "AAA", "ABC DEF"
        name_pattern = re.compile(r'^[A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*$')
        return bool(name_pattern.match(text))
    
    def _is_ambiguous_person(self, name: str) -> bool:
        """
        Check if a person name is ambiguous (multiple matches possible).
        
        Args:
            name: Person name to check
            
        Returns:
            True if ambiguous
        """
        # Check for multiple matches in People directory - use consolidated knowledgebase
        people_dir = self.base_dir / 'knowledgebase' / '-common' / 'People'
        if not people_dir.exists():
            return False
        
        # Look for similar names
        matches = list(people_dir.glob(f"{name}*.md"))
        return len(matches) > 1
    
    def _is_new_knowledge(self, topic: str) -> bool:
        """
        Check if a knowledge topic is new (doesn't exist yet).
        
        Args:
            topic: Topic to check
            
        Returns:
            True if new
        """
        knowledge_dir = self.base_dir / 'knowledgebase' / '-common' / 'Topics'
        if not knowledge_dir.exists():
            return True
        
        topic_file = knowledge_dir / f"{topic}.md"
        return not topic_file.exists()
    
    def _is_new_person(self, name: str) -> bool:
        """
        Check if a person is new (doesn't exist yet).
        
        Args:
            name: Person name to check
            
        Returns:
            True if new
        """
        people_dir = self.base_dir / 'knowledgebase' / '-common' / 'People'
        if not people_dir.exists():
            return True
        
        person_file = people_dir / f"{name}.md"
        return not person_file.exists()
    
    def _generate_clarification_questions(self, entities: List[Entity], text: str) -> List[str]:
        """
        Generate clarification questions for ambiguous entities.
        
        Args:
            entities: List of extracted entities
            text: Original note text
            
        Returns:
            List of clarification questions
        """
        questions = []
        
        for entity in entities:
            if entity.ambiguous:
                if entity.type == 'person':
                    questions.append(f"Which '{entity.value}' did you mean? (Multiple people found)")
                elif entity.type == 'knowledge':
                    questions.append(f"Is '{entity.value}' a new topic or related to existing knowledge?")
            
            if entity.confidence < 0.7:
                questions.append(f"Can you provide more context about '{entity.value}'?")
        
        # Check for missing context
        if len(entities) == 0:
            questions.append("What is the main topic or person this note is about?")
        
        return questions
    
    def _generate_proposed_updates(self, entities: List[Entity], text: str) -> List[Dict]:
        """
        Generate proposed updates based on entities.
        
        Args:
            entities: List of extracted entities
            text: Original note text
            
        Returns:
            List of proposed update dictionaries
        """
        updates = []
        
        for entity in entities:
            if entity.type == 'knowledge':
                if self._is_new_knowledge(entity.value):
                    updates.append({
                        'action': 'create_knowledge',
                        'title': entity.value,
                        'content': text,
                        'context': entity.context
                    })
                else:
                    updates.append({
                        'action': 'update_knowledge',
                        'title': entity.value,
                        'additional_content': text,
                        'context': entity.context
                    })
            
            elif entity.type == 'person':
                if self._is_new_person(entity.value):
                    updates.append({
                        'action': 'create_person',
                        'name': entity.value,
                        'context': entity.context
                    })
                else:
                    updates.append({
                        'action': 'update_person',
                        'name': entity.value,
                        'additional_context': text,
                        'context': entity.context
                    })
        
        return updates
    
    def _generate_batch_summary(self, result: ProcessingResult) -> str:
        """
        Generate a summary of batch processing results.
        
        Args:
            result: ProcessingResult object
            
        Returns:
            Summary string
        """
        parts = []
        
        parts.append(f"Processed {result.processed_count} notes")
        
        if result.knowledge_created:
            parts.append(f"Created {len(result.knowledge_created)} knowledge documents")
        if result.knowledge_updated:
            parts.append(f"Updated {len(result.knowledge_updated)} knowledge documents")
        if result.people_created:
            parts.append(f"Created {len(result.people_created)} person profiles")
        if result.people_updated:
            parts.append(f"Updated {len(result.people_updated)} person profiles")
        if result.time_entries_created:
            parts.append(f"Created {len(result.time_entries_created)} time entries")
        
        if result.errors:
            parts.append(f"Encountered {len(result.errors)} errors")
        
        return ". ".join(parts) + "."
    
    def _clear_inbox(self, notes_file: Path):
        """
        Clear the notes inbox file (preserve header).
        
        Args:
            notes_file: Path to notes file to clear
        """
        try:
            notes_file.write_text("# Notes Inbox\n\n", encoding='utf-8')
            logger.info(f"Cleared notes inbox: {notes_file}")
        except Exception as e:
            logger.error(f"Error clearing inbox: {e}")
