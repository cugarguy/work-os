"""
Time Intelligence Engine for WorkOS

This module provides time tracking, analysis, and estimation capabilities.
It tracks work duration, analyzes patterns, and provides intelligent estimates
based on historical data.
"""

import json
import uuid
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Distraction:
    """Represents a distraction event during work"""
    type: str
    duration_minutes: int
    description: str
    timestamp: str


@dataclass
class TimeEntry:
    """Represents a single work time entry"""
    id: str
    start_time: str
    end_time: Optional[str]
    duration_minutes: Optional[int]
    work_description: str
    work_type: str
    knowledge_refs: List[str]
    people_refs: List[str]
    distractions: List[Dict[str, Any]]
    completion_percentage: Optional[int]
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class EstimateResult:
    """Represents a time estimate with supporting data"""
    mean_minutes: float
    variance: float
    std_dev: float
    min_estimate: float
    max_estimate: float
    confidence_range: Tuple[float, float]
    similar_work_count: int
    similar_work_ids: List[str]
    explanation: str


@dataclass
class EstimationAccuracy:
    """Represents estimation accuracy analysis"""
    total_estimates: int
    accurate_estimates: int
    overestimates: int
    underestimates: int
    average_error_percentage: float
    common_deviation_patterns: List[Dict[str, Any]]


@dataclass
class WorkChunk:
    """Represents a chunk of work in a breakdown"""
    id: str
    description: str
    estimated_minutes: float
    work_type: str
    knowledge_refs: List[str]
    dependencies: List[str]


@dataclass
class WorkBreakdown:
    """Represents a complete work breakdown"""
    original_work: str
    estimated_total: float
    chunks: List[WorkChunk]
    breakdown_id: str
    created_at: str
    completed_chunks: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "original_work": self.original_work,
            "estimated_total": self.estimated_total,
            "chunks": [
                {
                    "id": chunk.id,
                    "description": chunk.description,
                    "estimated_minutes": chunk.estimated_minutes,
                    "work_type": chunk.work_type,
                    "knowledge_refs": chunk.knowledge_refs,
                    "dependencies": chunk.dependencies
                }
                for chunk in self.chunks
            ],
            "breakdown_id": self.breakdown_id,
            "created_at": self.created_at,
            "completed_chunks": self.completed_chunks
        }


class TimeIntelligence:
    """
    Time Intelligence Engine for tracking work time and providing estimates.
    
    This class manages time entries, calculates durations, records distractions,
    and stores all time data in JSON format.
    """
    
    def __init__(self, base_dir: Path):
        """
        Initialize the Time Intelligence Engine.
        
        Args:
            base_dir: Base directory for the WorkOS system
        """
        self.base_dir = Path(base_dir)
        self.system_dir = self.base_dir / ".system"
        self.time_file = self.system_dir / "time_analytics.json"
        
        # Ensure system directory exists
        self.system_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize time data file if it doesn't exist
        if not self.time_file.exists():
            self._save_time_data({"entries": [], "version": "1.0"})
    
    def _load_time_data(self) -> Dict[str, Any]:
        """Load time data from JSON file"""
        try:
            with open(self.time_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"entries": [], "version": "1.0"}
    
    def _save_time_data(self, data: Dict[str, Any]) -> None:
        """Save time data to JSON file"""
        with open(self.time_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def start_work(
        self,
        description: str,
        work_type: str = "general",
        knowledge_refs: Optional[List[str]] = None,
        people_refs: Optional[List[str]] = None
    ) -> str:
        """
        Start tracking work time.
        
        Args:
            description: Description of the work being performed
            work_type: Type/category of work (e.g., "technical", "writing", "meeting")
            knowledge_refs: List of related knowledge document names
            people_refs: List of related people names
            
        Returns:
            Unique identifier for this work entry
        """
        # Generate unique ID
        work_id = f"time_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        # Create time entry
        entry = TimeEntry(
            id=work_id,
            start_time=datetime.now(timezone.utc).isoformat(),
            end_time=None,
            duration_minutes=None,
            work_description=description,
            work_type=work_type,
            knowledge_refs=knowledge_refs or [],
            people_refs=people_refs or [],
            distractions=[],
            completion_percentage=None,
            notes=""
        )
        
        # Load existing data
        data = self._load_time_data()
        
        # Add new entry
        data["entries"].append(entry.to_dict())
        
        # Save updated data
        self._save_time_data(data)
        
        return work_id
    
    def end_work(
        self,
        work_id: str,
        completion_notes: str = "",
        completion_percentage: Optional[int] = None
    ) -> Optional[TimeEntry]:
        """
        End work tracking and calculate duration.
        
        Args:
            work_id: Unique identifier of the work entry
            completion_notes: Notes about work completion
            completion_percentage: Percentage of work completed (0-100)
            
        Returns:
            Updated TimeEntry object, or None if work_id not found
        """
        # Load existing data
        data = self._load_time_data()
        
        # Find the entry
        entry_dict = None
        for entry in data["entries"]:
            if entry["id"] == work_id:
                entry_dict = entry
                break
        
        if not entry_dict:
            return None
        
        # Update end time and calculate duration
        end_time = datetime.now(timezone.utc)
        start_time = datetime.fromisoformat(entry_dict["start_time"])
        
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        
        entry_dict["end_time"] = end_time.isoformat()
        entry_dict["duration_minutes"] = duration_minutes
        entry_dict["notes"] = completion_notes
        
        if completion_percentage is not None:
            entry_dict["completion_percentage"] = completion_percentage
        
        # Save updated data
        self._save_time_data(data)
        
        # Return as TimeEntry object
        return TimeEntry(**entry_dict)
    
    def record_distraction(
        self,
        work_id: str,
        distraction_type: str,
        duration_minutes: int,
        description: str = ""
    ) -> bool:
        """
        Record a distraction event during work.
        
        Args:
            work_id: Unique identifier of the work entry
            distraction_type: Type of distraction (e.g., "meeting", "interruption", "email")
            duration_minutes: Duration of the distraction in minutes
            description: Optional description of the distraction
            
        Returns:
            True if distraction was recorded, False if work_id not found
        """
        # Load existing data
        data = self._load_time_data()
        
        # Find the entry
        entry_dict = None
        for entry in data["entries"]:
            if entry["id"] == work_id:
                entry_dict = entry
                break
        
        if not entry_dict:
            return False
        
        # Create distraction record
        distraction = {
            "type": distraction_type,
            "duration_minutes": duration_minutes,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add to entry's distractions
        entry_dict["distractions"].append(distraction)
        
        # Save updated data
        self._save_time_data(data)
        
        return True
    
    def get_time_entry(self, work_id: str) -> Optional[TimeEntry]:
        """
        Retrieve a specific time entry.
        
        Args:
            work_id: Unique identifier of the work entry
            
        Returns:
            TimeEntry object, or None if not found
        """
        data = self._load_time_data()
        
        for entry_dict in data["entries"]:
            if entry_dict["id"] == work_id:
                # Filter to only TimeEntry fields (ignore extra metadata like breakdown_id)
                time_entry_fields = {
                    "id", "start_time", "end_time", "duration_minutes",
                    "work_description", "work_type", "knowledge_refs",
                    "people_refs", "distractions", "completion_percentage", "notes"
                }
                filtered_dict = {k: v for k, v in entry_dict.items() if k in time_entry_fields}
                return TimeEntry(**filtered_dict)
        
        return None
    
    def get_all_entries(self) -> List[TimeEntry]:
        """
        Retrieve all time entries.
        
        Returns:
            List of all TimeEntry objects
        """
        data = self._load_time_data()
        time_entry_fields = {
            "id", "start_time", "end_time", "duration_minutes",
            "work_description", "work_type", "knowledge_refs",
            "people_refs", "distractions", "completion_percentage", "notes"
        }
        return [
            TimeEntry(**{k: v for k, v in entry.items() if k in time_entry_fields})
            for entry in data["entries"]
        ]
    
    def get_entries_by_work_type(self, work_type: str) -> List[TimeEntry]:
        """
        Retrieve time entries filtered by work type.
        
        Args:
            work_type: Type of work to filter by
            
        Returns:
            List of matching TimeEntry objects
        """
        data = self._load_time_data()
        time_entry_fields = {
            "id", "start_time", "end_time", "duration_minutes",
            "work_description", "work_type", "knowledge_refs",
            "people_refs", "distractions", "completion_percentage", "notes"
        }
        return [
            TimeEntry(**{k: v for k, v in entry.items() if k in time_entry_fields})
            for entry in data["entries"]
            if entry["work_type"] == work_type
        ]
    
    def get_entries_by_knowledge(self, knowledge_ref: str) -> List[TimeEntry]:
        """
        Retrieve time entries linked to a specific knowledge document.
        
        Args:
            knowledge_ref: Name of the knowledge document
            
        Returns:
            List of matching TimeEntry objects
        """
        data = self._load_time_data()
        time_entry_fields = {
            "id", "start_time", "end_time", "duration_minutes",
            "work_description", "work_type", "knowledge_refs",
            "people_refs", "distractions", "completion_percentage", "notes"
        }
        return [
            TimeEntry(**{k: v for k, v in entry.items() if k in time_entry_fields})
            for entry in data["entries"]
            if knowledge_ref in entry["knowledge_refs"]
        ]
    
    def get_entries_by_person(self, person_ref: str) -> List[TimeEntry]:
        """
        Retrieve time entries linked to a specific person.
        
        Args:
            person_ref: Name of the person
            
        Returns:
            List of matching TimeEntry objects
        """
        data = self._load_time_data()
        time_entry_fields = {
            "id", "start_time", "end_time", "duration_minutes",
            "work_description", "work_type", "knowledge_refs",
            "people_refs", "distractions", "completion_percentage", "notes"
        }
        return [
            TimeEntry(**{k: v for k, v in entry.items() if k in time_entry_fields})
            for entry in data["entries"]
            if person_ref in entry["people_refs"]
        ]
    
    def find_similar_work(
        self,
        work_description: str,
        work_type: str,
        knowledge_refs: Optional[List[str]] = None
    ) -> List[TimeEntry]:
        """
        Identify similar historical work based on type and knowledge connections.
        
        This implements the similar work identification algorithm by matching:
        1. Work type (exact match)
        2. Knowledge references (any overlap)
        
        Args:
            work_description: Description of the new work
            work_type: Type of work
            knowledge_refs: List of related knowledge document names
            
        Returns:
            List of similar TimeEntry objects with completed durations
        """
        knowledge_refs = knowledge_refs or []
        data = self._load_time_data()
        similar_entries = []
        time_entry_fields = {
            "id", "start_time", "end_time", "duration_minutes",
            "work_description", "work_type", "knowledge_refs",
            "people_refs", "distractions", "completion_percentage", "notes"
        }
        
        for entry_dict in data["entries"]:
            # Only consider completed entries with duration
            if entry_dict.get("duration_minutes") is None:
                continue
            
            # Match by work type
            if entry_dict["work_type"] != work_type:
                continue
            
            # If knowledge refs provided, check for overlap
            if knowledge_refs:
                entry_knowledge = set(entry_dict.get("knowledge_refs", []))
                query_knowledge = set(knowledge_refs)
                
                # Must have at least one knowledge reference in common
                if not entry_knowledge.intersection(query_knowledge):
                    continue
            
            filtered_dict = {k: v for k, v in entry_dict.items() if k in time_entry_fields}
            similar_entries.append(TimeEntry(**filtered_dict))
        
        return similar_entries
    
    def calculate_statistics(self, entries: List[TimeEntry]) -> Tuple[float, float]:
        """
        Calculate average duration and variance for a set of time entries.
        
        Args:
            entries: List of TimeEntry objects with completed durations
            
        Returns:
            Tuple of (mean_minutes, variance)
        """
        if not entries:
            return (0.0, 0.0)
        
        # Extract durations (filter out None values)
        durations = [
            entry.duration_minutes
            for entry in entries
            if entry.duration_minutes is not None
        ]
        
        if not durations:
            return (0.0, 0.0)
        
        # Calculate mean
        mean = sum(durations) / len(durations)
        
        # Calculate variance
        if len(durations) == 1:
            variance = 0.0
        else:
            variance = sum((d - mean) ** 2 for d in durations) / len(durations)
        
        return (mean, variance)
    
    def generate_estimate(
        self,
        work_description: str,
        work_type: str,
        knowledge_refs: Optional[List[str]] = None
    ) -> Optional[EstimateResult]:
        """
        Generate a time estimate based on historical patterns.
        
        Provides a time range using mean ± standard deviation from similar work.
        
        Args:
            work_description: Description of the work to estimate
            work_type: Type of work
            knowledge_refs: List of related knowledge document names
            
        Returns:
            EstimateResult with time range and explanation, or None if no similar work found
        """
        # Find similar work
        similar_work = self.find_similar_work(work_description, work_type, knowledge_refs)
        
        if not similar_work:
            return None
        
        # Calculate statistics
        mean, variance = self.calculate_statistics(similar_work)
        std_dev = math.sqrt(variance)
        
        # Generate estimate range (mean ± std_dev)
        min_estimate = max(0, mean - std_dev)
        max_estimate = mean + std_dev
        confidence_range = (min_estimate, max_estimate)
        
        # Build explanation
        similar_work_ids = [entry.id for entry in similar_work]
        explanation = self._build_estimate_explanation(
            similar_work, mean, std_dev, work_type, knowledge_refs
        )
        
        return EstimateResult(
            mean_minutes=mean,
            variance=variance,
            std_dev=std_dev,
            min_estimate=min_estimate,
            max_estimate=max_estimate,
            confidence_range=confidence_range,
            similar_work_count=len(similar_work),
            similar_work_ids=similar_work_ids,
            explanation=explanation
        )
    
    def _build_estimate_explanation(
        self,
        similar_work: List[TimeEntry],
        mean: float,
        std_dev: float,
        work_type: str,
        knowledge_refs: Optional[List[str]]
    ) -> str:
        """
        Build a human-readable explanation of the estimate.
        
        Args:
            similar_work: List of similar TimeEntry objects
            mean: Average duration
            std_dev: Standard deviation
            work_type: Type of work
            knowledge_refs: Knowledge references
            
        Returns:
            Explanation string
        """
        explanation_parts = []
        
        # Base explanation
        explanation_parts.append(
            f"Based on {len(similar_work)} similar {work_type} work items"
        )
        
        # Knowledge context
        if knowledge_refs:
            knowledge_str = ", ".join(knowledge_refs)
            explanation_parts.append(f"related to: {knowledge_str}")
        
        # Statistical summary
        explanation_parts.append(
            f"Average duration: {mean:.1f} minutes (±{std_dev:.1f} minutes)"
        )
        
        # Reference specific work items
        if len(similar_work) <= 3:
            work_refs = [
                f"'{entry.work_description}' ({entry.duration_minutes} min)"
                for entry in similar_work
            ]
            explanation_parts.append(f"Historical work: {', '.join(work_refs)}")
        else:
            # Show a sample
            sample = similar_work[:3]
            work_refs = [
                f"'{entry.work_description}' ({entry.duration_minutes} min)"
                for entry in sample
            ]
            explanation_parts.append(
                f"Sample work: {', '.join(work_refs)} (and {len(similar_work) - 3} more)"
            )
        
        return ". ".join(explanation_parts) + "."
    
    def analyze_estimation_accuracy(
        self,
        tolerance_percentage: float = 20.0
    ) -> EstimationAccuracy:
        """
        Analyze estimation accuracy by comparing estimates to actual durations.
        
        This identifies patterns in estimation accuracy and common deviations.
        For this analysis, we look at completed work and compare what the estimate
        would have been (based on prior similar work) to the actual duration.
        
        Args:
            tolerance_percentage: Percentage tolerance for "accurate" estimates (default 20%)
            
        Returns:
            EstimationAccuracy object with analysis results
        """
        data = self._load_time_data()
        completed_entries = [
            TimeEntry(**entry)
            for entry in data["entries"]
            if entry.get("duration_minutes") is not None
        ]
        
        if len(completed_entries) < 2:
            # Need at least 2 entries to analyze (one for history, one to estimate)
            return EstimationAccuracy(
                total_estimates=0,
                accurate_estimates=0,
                overestimates=0,
                underestimates=0,
                average_error_percentage=0.0,
                common_deviation_patterns=[]
            )
        
        total_estimates = 0
        accurate_estimates = 0
        overestimates = 0
        underestimates = 0
        error_percentages = []
        deviation_patterns = []
        
        # For each completed entry, see what the estimate would have been
        # based on prior work (simulate historical estimation)
        for i, entry in enumerate(completed_entries):
            # Use only prior entries as "history"
            prior_entries = completed_entries[:i]
            
            if not prior_entries:
                continue
            
            # Find similar work from prior entries
            similar_work = [
                e for e in prior_entries
                if e.work_type == entry.work_type
            ]
            
            if not similar_work:
                continue
            
            # Calculate what the estimate would have been
            mean, variance = self.calculate_statistics(similar_work)
            
            if mean == 0:
                continue
            
            # Compare to actual duration
            actual = entry.duration_minutes
            estimated = mean
            
            error_percentage = abs(actual - estimated) / actual * 100
            error_percentages.append(error_percentage)
            
            total_estimates += 1
            
            # Categorize the estimate
            if error_percentage <= tolerance_percentage:
                accurate_estimates += 1
            elif estimated > actual:
                overestimates += 1
                deviation_patterns.append({
                    "type": "overestimate",
                    "work_type": entry.work_type,
                    "estimated": estimated,
                    "actual": actual,
                    "error_percentage": error_percentage
                })
            else:
                underestimates += 1
                deviation_patterns.append({
                    "type": "underestimate",
                    "work_type": entry.work_type,
                    "estimated": estimated,
                    "actual": actual,
                    "error_percentage": error_percentage
                })
        
        # Calculate average error
        avg_error = sum(error_percentages) / len(error_percentages) if error_percentages else 0.0
        
        # Identify common patterns (group by work type)
        common_patterns = self._identify_common_patterns(deviation_patterns)
        
        return EstimationAccuracy(
            total_estimates=total_estimates,
            accurate_estimates=accurate_estimates,
            overestimates=overestimates,
            underestimates=underestimates,
            average_error_percentage=avg_error,
            common_deviation_patterns=common_patterns
        )
    
    def _identify_common_patterns(
        self,
        deviation_patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify common deviation patterns by work type.
        
        Args:
            deviation_patterns: List of deviation records
            
        Returns:
            List of common patterns with aggregated statistics
        """
        if not deviation_patterns:
            return []
        
        # Group by work type and deviation type
        patterns_by_key = {}
        
        for pattern in deviation_patterns:
            key = (pattern["work_type"], pattern["type"])
            
            if key not in patterns_by_key:
                patterns_by_key[key] = {
                    "work_type": pattern["work_type"],
                    "deviation_type": pattern["type"],
                    "count": 0,
                    "total_error": 0.0
                }
            
            patterns_by_key[key]["count"] += 1
            patterns_by_key[key]["total_error"] += pattern["error_percentage"]
        
        # Calculate averages and format results
        common_patterns = []
        for key, data in patterns_by_key.items():
            if data["count"] >= 2:  # Only include patterns that occur multiple times
                common_patterns.append({
                    "work_type": data["work_type"],
                    "deviation_type": data["deviation_type"],
                    "occurrence_count": data["count"],
                    "average_error_percentage": data["total_error"] / data["count"]
                })
        
        # Sort by occurrence count (most common first)
        common_patterns.sort(key=lambda x: x["occurrence_count"], reverse=True)
        
        return common_patterns
    
    def analyze_complexity(self, work_description: str) -> Dict[str, Any]:
        """
        Analyze work description for complexity indicators.
        
        Complexity indicators include:
        - Length of description (longer = more complex)
        - Multiple verbs/actions (indicates multiple steps)
        - Conjunctions like "and", "then", "also" (indicates multiple parts)
        - Technical terms or domain-specific language
        - Words indicating scope like "complete", "full", "entire"
        
        Args:
            work_description: Description of the work to analyze
            
        Returns:
            Dictionary with complexity analysis results
        """
        description_lower = work_description.lower()
        
        # Complexity indicators
        complexity_score = 0
        indicators = []
        
        # Length indicator (>100 chars suggests complexity)
        if len(work_description) > 100:
            complexity_score += 2
            indicators.append("Long description suggests multiple components")
        elif len(work_description) > 50:
            complexity_score += 1
            indicators.append("Moderate description length")
        
        # Multiple action verbs
        action_verbs = [
            "implement", "create", "build", "design", "develop", "write",
            "test", "deploy", "configure", "setup", "integrate", "refactor",
            "update", "modify", "add", "remove", "fix", "debug"
        ]
        verb_count = sum(1 for verb in action_verbs if verb in description_lower)
        if verb_count >= 3:
            complexity_score += 2
            indicators.append(f"Multiple action verbs ({verb_count}) suggest multiple tasks")
        elif verb_count >= 2:
            complexity_score += 1
            indicators.append(f"Multiple actions ({verb_count}) detected")
        
        # Conjunctions indicating multiple parts
        conjunctions = ["and", "then", "also", "plus", "along with", "as well as"]
        conjunction_count = sum(1 for conj in conjunctions if conj in description_lower)
        if conjunction_count >= 2:
            complexity_score += 2
            indicators.append(f"Multiple conjunctions ({conjunction_count}) suggest compound work")
        elif conjunction_count >= 1:
            complexity_score += 1
            indicators.append("Conjunctions suggest multiple components")
        
        # Scope indicators
        scope_words = ["complete", "full", "entire", "comprehensive", "end-to-end", "all"]
        scope_count = sum(1 for word in scope_words if word in description_lower)
        if scope_count >= 2:
            complexity_score += 2
            indicators.append("Broad scope indicators detected")
        elif scope_count >= 1:
            complexity_score += 1
            indicators.append("Scope indicator suggests larger work item")
        
        # Determine complexity level
        if complexity_score >= 5:
            complexity_level = "high"
            recommendation = "Strong candidate for breakdown into smaller chunks"
        elif complexity_score >= 3:
            complexity_level = "medium"
            recommendation = "Consider breaking down into 2-3 chunks"
        else:
            complexity_level = "low"
            recommendation = "Appears to be a single, focused work item"
        
        return {
            "complexity_score": complexity_score,
            "complexity_level": complexity_level,
            "indicators": indicators,
            "recommendation": recommendation
        }
    
    def suggest_breakdown(
        self,
        work_description: str,
        work_type: str,
        knowledge_refs: Optional[List[str]] = None
    ) -> Optional[WorkBreakdown]:
        """
        Suggest a logical breakdown of work into smaller chunks.
        
        This analyzes the work description and suggests breakdown points based on:
        1. Complexity analysis
        2. Work type patterns
        3. Common work phases (design, implement, test, document)
        
        Args:
            work_description: Description of the work to break down
            work_type: Type of work
            knowledge_refs: List of related knowledge document names
            
        Returns:
            WorkBreakdown object with suggested chunks, or None if breakdown not recommended
        """
        knowledge_refs = knowledge_refs or []
        
        # Analyze complexity
        complexity = self.analyze_complexity(work_description)
        
        # Only suggest breakdown for medium or high complexity
        if complexity["complexity_level"] == "low":
            return None
        
        # Generate breakdown based on work type
        chunks = self._generate_chunks_by_type(
            work_description, work_type, knowledge_refs, complexity
        )
        
        if not chunks:
            return None
        
        # Calculate total estimate
        total_estimate = sum(chunk.estimated_minutes for chunk in chunks)
        
        # Create breakdown
        breakdown_id = f"breakdown_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        return WorkBreakdown(
            original_work=work_description,
            estimated_total=total_estimate,
            chunks=chunks,
            breakdown_id=breakdown_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            completed_chunks=[]
        )
    
    def _generate_chunks_by_type(
        self,
        work_description: str,
        work_type: str,
        knowledge_refs: List[str],
        complexity: Dict[str, Any]
    ) -> List[WorkChunk]:
        """
        Generate work chunks based on work type and complexity.
        
        Args:
            work_description: Description of the work
            work_type: Type of work
            knowledge_refs: Knowledge references
            complexity: Complexity analysis results
            
        Returns:
            List of WorkChunk objects
        """
        chunks = []
        description_lower = work_description.lower()
        
        # Common patterns for technical work
        if work_type == "technical":
            # Design phase
            if any(word in description_lower for word in ["design", "architecture", "plan", "spec"]):
                chunks.append(WorkChunk(
                    id="chunk_1",
                    description=f"Design and plan: {work_description}",
                    estimated_minutes=self._estimate_chunk("design", work_type, knowledge_refs),
                    work_type=work_type,
                    knowledge_refs=knowledge_refs,
                    dependencies=[]
                ))
            
            # Implementation phase
            if any(word in description_lower for word in ["implement", "build", "create", "develop", "code"]):
                chunks.append(WorkChunk(
                    id=f"chunk_{len(chunks) + 1}",
                    description=f"Implement core functionality: {work_description}",
                    estimated_minutes=self._estimate_chunk("implement", work_type, knowledge_refs),
                    work_type=work_type,
                    knowledge_refs=knowledge_refs,
                    dependencies=[chunks[-1].id] if chunks else []
                ))
            
            # Testing phase
            if any(word in description_lower for word in ["test", "verify", "validate"]) or complexity["complexity_level"] == "high":
                chunks.append(WorkChunk(
                    id=f"chunk_{len(chunks) + 1}",
                    description=f"Test and validate: {work_description}",
                    estimated_minutes=self._estimate_chunk("test", work_type, knowledge_refs),
                    work_type=work_type,
                    knowledge_refs=knowledge_refs,
                    dependencies=[chunks[-1].id] if chunks else []
                ))
            
            # Documentation phase
            if any(word in description_lower for word in ["document", "doc", "write"]) or complexity["complexity_level"] == "high":
                chunks.append(WorkChunk(
                    id=f"chunk_{len(chunks) + 1}",
                    description=f"Document: {work_description}",
                    estimated_minutes=self._estimate_chunk("document", work_type, knowledge_refs),
                    work_type="writing",
                    knowledge_refs=knowledge_refs,
                    dependencies=[chunks[-1].id] if chunks else []
                ))
        
        # Writing work patterns
        elif work_type == "writing":
            # Research/outline phase
            chunks.append(WorkChunk(
                id="chunk_1",
                description=f"Research and outline: {work_description}",
                estimated_minutes=self._estimate_chunk("research", work_type, knowledge_refs),
                work_type=work_type,
                knowledge_refs=knowledge_refs,
                dependencies=[]
            ))
            
            # Draft phase
            chunks.append(WorkChunk(
                id="chunk_2",
                description=f"Write first draft: {work_description}",
                estimated_minutes=self._estimate_chunk("draft", work_type, knowledge_refs),
                work_type=work_type,
                knowledge_refs=knowledge_refs,
                dependencies=["chunk_1"]
            ))
            
            # Review/edit phase
            chunks.append(WorkChunk(
                id="chunk_3",
                description=f"Review and edit: {work_description}",
                estimated_minutes=self._estimate_chunk("edit", work_type, knowledge_refs),
                work_type=work_type,
                knowledge_refs=knowledge_refs,
                dependencies=["chunk_2"]
            ))
        
        # Meeting work patterns
        elif work_type == "meeting":
            # Preparation
            chunks.append(WorkChunk(
                id="chunk_1",
                description=f"Prepare for: {work_description}",
                estimated_minutes=self._estimate_chunk("prepare", work_type, knowledge_refs),
                work_type=work_type,
                knowledge_refs=knowledge_refs,
                dependencies=[]
            ))
            
            # Meeting itself
            chunks.append(WorkChunk(
                id="chunk_2",
                description=f"Attend: {work_description}",
                estimated_minutes=self._estimate_chunk("attend", work_type, knowledge_refs),
                work_type=work_type,
                knowledge_refs=knowledge_refs,
                dependencies=["chunk_1"]
            ))
            
            # Follow-up
            chunks.append(WorkChunk(
                id="chunk_3",
                description=f"Follow-up actions: {work_description}",
                estimated_minutes=self._estimate_chunk("followup", work_type, knowledge_refs),
                work_type=work_type,
                knowledge_refs=knowledge_refs,
                dependencies=["chunk_2"]
            ))
        
        # Generic breakdown for other work types
        else:
            # If no specific pattern, break into phases based on complexity
            if complexity["complexity_level"] == "high":
                phase_count = 4
            else:
                phase_count = 2
            
            for i in range(phase_count):
                chunks.append(WorkChunk(
                    id=f"chunk_{i + 1}",
                    description=f"Phase {i + 1}: {work_description}",
                    estimated_minutes=self._estimate_chunk("generic", work_type, knowledge_refs),
                    work_type=work_type,
                    knowledge_refs=knowledge_refs,
                    dependencies=[f"chunk_{i}"] if i > 0 else []
                ))
        
        return chunks
    
    def _estimate_chunk(
        self,
        chunk_type: str,
        work_type: str,
        knowledge_refs: List[str]
    ) -> float:
        """
        Estimate time for a specific chunk type.
        
        Uses historical data if available, otherwise uses heuristics.
        
        Args:
            chunk_type: Type of chunk (e.g., "design", "implement", "test")
            work_type: Overall work type
            knowledge_refs: Knowledge references
            
        Returns:
            Estimated minutes for the chunk
        """
        # Try to find similar work
        similar_work = self.find_similar_work(chunk_type, work_type, knowledge_refs)
        
        if similar_work:
            mean, _ = self.calculate_statistics(similar_work)
            if mean > 0:
                return mean
        
        # Fallback to heuristics based on chunk type
        heuristics = {
            "design": 60,
            "implement": 120,
            "test": 60,
            "document": 30,
            "research": 45,
            "draft": 90,
            "edit": 30,
            "prepare": 20,
            "attend": 60,
            "followup": 30,
            "generic": 60
        }
        
        return heuristics.get(chunk_type, 60)
    
    def accept_breakdown(self, breakdown: WorkBreakdown) -> List[str]:
        """
        Accept a work breakdown and create time tracking entries for each chunk.
        
        Args:
            breakdown: WorkBreakdown object to accept
            
        Returns:
            List of work IDs for the created time entries
        """
        # Load existing data
        data = self._load_time_data()
        
        # Store the breakdown
        if "breakdowns" not in data:
            data["breakdowns"] = []
        
        data["breakdowns"].append(breakdown.to_dict())
        
        # Create time entries for each chunk (in "planned" state)
        work_ids = []
        for chunk in breakdown.chunks:
            entry = TimeEntry(
                id=f"time_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
                start_time=None,  # Not started yet
                end_time=None,
                duration_minutes=None,
                work_description=chunk.description,
                work_type=chunk.work_type,
                knowledge_refs=chunk.knowledge_refs,
                people_refs=[],
                distractions=[],
                completion_percentage=None,
                notes=f"Part of breakdown: {breakdown.breakdown_id}"
            )
            
            # Add metadata linking to breakdown
            entry_dict = entry.to_dict()
            entry_dict["breakdown_id"] = breakdown.breakdown_id
            entry_dict["chunk_id"] = chunk.id
            entry_dict["estimated_minutes"] = chunk.estimated_minutes
            
            data["entries"].append(entry_dict)
            work_ids.append(entry.id)
        
        # Save updated data
        self._save_time_data(data)
        
        return work_ids
    
    def get_breakdown_progress(self, breakdown_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress information for a work breakdown.
        
        Args:
            breakdown_id: ID of the breakdown
            
        Returns:
            Dictionary with progress information, or None if not found
        """
        data = self._load_time_data()
        
        # Find the breakdown
        breakdown_dict = None
        for bd in data.get("breakdowns", []):
            if bd["breakdown_id"] == breakdown_id:
                breakdown_dict = bd
                break
        
        if not breakdown_dict:
            return None
        
        # Find all entries for this breakdown
        breakdown_entries = [
            entry for entry in data["entries"]
            if entry.get("breakdown_id") == breakdown_id
        ]
        
        # Calculate progress
        total_chunks = len(breakdown_dict["chunks"])
        completed_chunks = sum(
            1 for entry in breakdown_entries
            if entry.get("duration_minutes") is not None
        )
        
        # Calculate actual vs estimated time
        total_estimated = breakdown_dict["estimated_total"]
        total_actual = sum(
            entry.get("duration_minutes", 0)
            for entry in breakdown_entries
            if entry.get("duration_minutes") is not None
        )
        
        return {
            "breakdown_id": breakdown_id,
            "original_work": breakdown_dict["original_work"],
            "total_chunks": total_chunks,
            "completed_chunks": completed_chunks,
            "progress_percentage": (completed_chunks / total_chunks * 100) if total_chunks > 0 else 0,
            "estimated_total_minutes": total_estimated,
            "actual_total_minutes": total_actual,
            "remaining_estimated_minutes": max(0, total_estimated - total_actual),
            "variance_minutes": total_actual - total_estimated if completed_chunks == total_chunks else None
        }
    
    def aggregate_breakdown_results(self, breakdown_id: str) -> Optional[Dict[str, Any]]:
        """
        Aggregate actual time for completed breakdown chunks and compare to estimates.
        
        Args:
            breakdown_id: ID of the breakdown
            
        Returns:
            Dictionary with aggregated results and comparison, or None if not found
        """
        data = self._load_time_data()
        
        # Find the breakdown
        breakdown_dict = None
        for bd in data.get("breakdowns", []):
            if bd["breakdown_id"] == breakdown_id:
                breakdown_dict = bd
                break
        
        if not breakdown_dict:
            return None
        
        # Find all entries for this breakdown
        breakdown_entries = [
            entry for entry in data["entries"]
            if entry.get("breakdown_id") == breakdown_id
        ]
        
        # Aggregate by chunk
        chunk_results = []
        for chunk in breakdown_dict["chunks"]:
            chunk_entry = next(
                (e for e in breakdown_entries if e.get("chunk_id") == chunk["id"]),
                None
            )
            
            if chunk_entry:
                actual_minutes = chunk_entry.get("duration_minutes")
                estimated_minutes = chunk["estimated_minutes"]
                
                chunk_results.append({
                    "chunk_id": chunk["id"],
                    "description": chunk["description"],
                    "estimated_minutes": estimated_minutes,
                    "actual_minutes": actual_minutes,
                    "variance_minutes": (actual_minutes - estimated_minutes) if actual_minutes else None,
                    "variance_percentage": (
                        ((actual_minutes - estimated_minutes) / estimated_minutes * 100)
                        if actual_minutes and estimated_minutes > 0
                        else None
                    ),
                    "completed": actual_minutes is not None
                })
        
        # Calculate totals
        total_estimated = sum(chunk["estimated_minutes"] for chunk in breakdown_dict["chunks"])
        total_actual = sum(
            r["actual_minutes"] for r in chunk_results
            if r["actual_minutes"] is not None
        )
        completed_count = sum(1 for r in chunk_results if r["completed"])
        
        return {
            "breakdown_id": breakdown_id,
            "original_work": breakdown_dict["original_work"],
            "total_chunks": len(breakdown_dict["chunks"]),
            "completed_chunks": completed_count,
            "chunk_results": chunk_results,
            "total_estimated_minutes": total_estimated,
            "total_actual_minutes": total_actual,
            "total_variance_minutes": total_actual - total_estimated,
            "total_variance_percentage": (
                ((total_actual - total_estimated) / total_estimated * 100)
                if total_estimated > 0
                else 0
            ),
            "all_chunks_completed": completed_count == len(breakdown_dict["chunks"])
        }

    def analyze_distraction_patterns(
        self,
        days: Optional[int] = None,
        work_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Identify distraction patterns by time of day, day of week, and work type.
        
        This analyzes all recorded distractions to find patterns in when and how
        distractions occur, helping users understand their most productive times
        and most disruptive distraction types.
        
        Args:
            days: Number of days to analyze (None = all time)
            work_type: Filter by specific work type (None = all types)
            
        Returns:
            Dictionary with pattern analysis including:
            - by_time_of_day: Distraction counts by hour
            - by_day_of_week: Distraction counts by day (0=Monday, 6=Sunday)
            - by_work_type: Distraction counts by work type
            - by_distraction_type: Counts by distraction type
            - most_disruptive_hour: Hour with most distractions
            - most_disruptive_day: Day with most distractions
            - most_common_distraction_type: Most frequent distraction type
        """
        data = self._load_time_data()
        
        # Filter entries by date range if specified
        entries = data["entries"]
        if days is not None:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            entries = [
                entry for entry in entries
                if entry.get("start_time") and
                datetime.fromisoformat(entry["start_time"]) >= cutoff_date
            ]
        
        # Filter by work type if specified
        if work_type is not None:
            entries = [
                entry for entry in entries
                if entry.get("work_type") == work_type
            ]
        
        # Initialize pattern tracking
        by_time_of_day = {hour: 0 for hour in range(24)}
        by_day_of_week = {day: 0 for day in range(7)}
        by_work_type_dict = {}
        by_distraction_type = {}
        
        total_distractions = 0
        
        # Analyze each entry's distractions
        for entry in entries:
            entry_work_type = entry.get("work_type", "unknown")
            
            for distraction in entry.get("distractions", []):
                total_distractions += 1
                
                # Parse distraction timestamp
                timestamp_str = distraction.get("timestamp")
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    
                    # Track by hour of day
                    hour = timestamp.hour
                    by_time_of_day[hour] += 1
                    
                    # Track by day of week (0=Monday, 6=Sunday)
                    day_of_week = timestamp.weekday()
                    by_day_of_week[day_of_week] += 1
                
                # Track by work type
                if entry_work_type not in by_work_type_dict:
                    by_work_type_dict[entry_work_type] = 0
                by_work_type_dict[entry_work_type] += 1
                
                # Track by distraction type
                distraction_type = distraction.get("type", "unknown")
                if distraction_type not in by_distraction_type:
                    by_distraction_type[distraction_type] = 0
                by_distraction_type[distraction_type] += 1
        
        # Find most disruptive patterns
        most_disruptive_hour = max(by_time_of_day.items(), key=lambda x: x[1])[0] if total_distractions > 0 else None
        most_disruptive_day = max(by_day_of_week.items(), key=lambda x: x[1])[0] if total_distractions > 0 else None
        most_common_distraction_type = (
            max(by_distraction_type.items(), key=lambda x: x[1])[0]
            if by_distraction_type else None
        )
        
        # Day names for readability
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        return {
            "total_distractions": total_distractions,
            "by_time_of_day": by_time_of_day,
            "by_day_of_week": by_day_of_week,
            "by_work_type": by_work_type_dict,
            "by_distraction_type": by_distraction_type,
            "most_disruptive_hour": most_disruptive_hour,
            "most_disruptive_day": most_disruptive_day,
            "most_disruptive_day_name": day_names[most_disruptive_day] if most_disruptive_day is not None else None,
            "most_common_distraction_type": most_common_distraction_type
        }
    
    def calculate_distraction_impact(
        self,
        work_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate the impact of distractions on work duration.
        
        This compares work duration with and without distractions to quantify
        the overhead that distractions add to work completion time.
        
        Args:
            work_type: Filter by specific work type (None = all types)
            
        Returns:
            Dictionary with impact analysis including:
            - average_duration_with_distractions: Average work duration when distractions occurred
            - average_duration_without_distractions: Average work duration with no distractions
            - average_distraction_overhead_minutes: Additional time due to distractions
            - average_distraction_overhead_percentage: Percentage overhead
            - total_distraction_time: Sum of all distraction durations
            - entries_with_distractions: Count of entries with distractions
            - entries_without_distractions: Count of entries without distractions
        """
        data = self._load_time_data()
        
        # Filter completed entries
        entries = [
            entry for entry in data["entries"]
            if entry.get("duration_minutes") is not None
        ]
        
        # Filter by work type if specified
        if work_type is not None:
            entries = [
                entry for entry in entries
                if entry.get("work_type") == work_type
            ]
        
        # Separate entries with and without distractions
        with_distractions = []
        without_distractions = []
        total_distraction_time = 0
        
        for entry in entries:
            distractions = entry.get("distractions", [])
            
            if distractions:
                with_distractions.append(entry)
                # Sum distraction durations
                for distraction in distractions:
                    total_distraction_time += distraction.get("duration_minutes", 0)
            else:
                without_distractions.append(entry)
        
        # Calculate averages
        avg_with_distractions = (
            sum(e["duration_minutes"] for e in with_distractions) / len(with_distractions)
            if with_distractions else 0.0
        )
        
        avg_without_distractions = (
            sum(e["duration_minutes"] for e in without_distractions) / len(without_distractions)
            if without_distractions else 0.0
        )
        
        # Calculate overhead
        overhead_minutes = avg_with_distractions - avg_without_distractions
        overhead_percentage = (
            (overhead_minutes / avg_without_distractions * 100)
            if avg_without_distractions > 0 else 0.0
        )
        
        return {
            "average_duration_with_distractions": avg_with_distractions,
            "average_duration_without_distractions": avg_without_distractions,
            "average_distraction_overhead_minutes": overhead_minutes,
            "average_distraction_overhead_percentage": overhead_percentage,
            "total_distraction_time": total_distraction_time,
            "entries_with_distractions": len(with_distractions),
            "entries_without_distractions": len(without_distractions)
        }
    
    def generate_estimate_with_distraction_overhead(
        self,
        work_description: str,
        work_type: str,
        knowledge_refs: Optional[List[str]] = None
    ) -> Optional[EstimateResult]:
        """
        Generate a time estimate that factors in typical distraction overhead for the work type.
        
        This enhances the base estimate by adding expected distraction overhead based on
        historical patterns for the work type.
        
        Args:
            work_description: Description of the work to estimate
            work_type: Type of work
            knowledge_refs: List of related knowledge document names
            
        Returns:
            EstimateResult with distraction overhead factored in, or None if no similar work found
        """
        # Get base estimate
        base_estimate = self.generate_estimate(work_description, work_type, knowledge_refs)
        
        if base_estimate is None:
            return None
        
        # Calculate distraction impact for this work type
        impact = self.calculate_distraction_impact(work_type=work_type)
        
        # If we have distraction data, factor it into the estimate
        if impact["entries_with_distractions"] > 0:
            overhead_percentage = impact["average_distraction_overhead_percentage"]
            
            # Apply overhead to base estimate
            adjusted_mean = base_estimate.mean_minutes * (1 + overhead_percentage / 100)
            adjusted_min = base_estimate.min_estimate * (1 + overhead_percentage / 100)
            adjusted_max = base_estimate.max_estimate * (1 + overhead_percentage / 100)
            
            # Update explanation
            adjusted_explanation = (
                base_estimate.explanation +
                f" Adjusted for typical distraction overhead: +{overhead_percentage:.1f}% "
                f"({impact['average_distraction_overhead_minutes']:.1f} minutes) "
                f"based on {impact['entries_with_distractions']} historical work items with distractions."
            )
            
            return EstimateResult(
                mean_minutes=adjusted_mean,
                variance=base_estimate.variance,
                std_dev=base_estimate.std_dev,
                min_estimate=adjusted_min,
                max_estimate=adjusted_max,
                confidence_range=(adjusted_min, adjusted_max),
                similar_work_count=base_estimate.similar_work_count,
                similar_work_ids=base_estimate.similar_work_ids,
                explanation=adjusted_explanation
            )
        else:
            # No distraction data, return base estimate
            return base_estimate
    
    # Knowledge-Time Integration Methods
    
    def link_time_to_knowledge(
        self,
        work_id: str,
        knowledge_refs: List[str]
    ) -> bool:
        """
        Link a time entry to knowledge documents.
        
        Creates connections between time data and knowledge documents by updating
        the time entry's knowledge_refs field.
        
        Args:
            work_id: Unique identifier of the work entry
            knowledge_refs: List of knowledge document names to link
            
        Returns:
            True if link created successfully, False if work_id not found
        """
        data = self._load_time_data()
        
        # Find the entry
        entry_dict = None
        for entry in data["entries"]:
            if entry["id"] == work_id:
                entry_dict = entry
                break
        
        if not entry_dict:
            return False
        
        # Update knowledge references (merge with existing)
        existing_refs = set(entry_dict.get("knowledge_refs", []))
        new_refs = set(knowledge_refs)
        entry_dict["knowledge_refs"] = list(existing_refs.union(new_refs))
        
        # Save updated data
        self._save_time_data(data)
        
        return True
    
    def get_knowledge_time_investment(self, knowledge_ref: str) -> Dict[str, Any]:
        """
        Get total time invested in a specific knowledge area.
        
        Calculates the total time spent on work related to a knowledge document,
        including number of work items and average duration.
        
        Args:
            knowledge_ref: Name of the knowledge document
            
        Returns:
            Dictionary with time investment statistics:
            - total_minutes: Total time invested
            - work_item_count: Number of work items
            - average_duration: Average time per work item
            - work_items: List of work item summaries
        """
        entries = self.get_entries_by_knowledge(knowledge_ref)
        
        # Filter to completed entries only
        completed_entries = [e for e in entries if e.duration_minutes is not None]
        
        if not completed_entries:
            return {
                "knowledge_ref": knowledge_ref,
                "total_minutes": 0,
                "work_item_count": 0,
                "average_duration": 0.0,
                "work_items": []
            }
        
        # Calculate statistics
        total_minutes = sum(e.duration_minutes for e in completed_entries)
        work_item_count = len(completed_entries)
        average_duration = total_minutes / work_item_count
        
        # Build work item summaries
        work_items = [
            {
                "id": entry.id,
                "description": entry.work_description,
                "duration_minutes": entry.duration_minutes,
                "work_type": entry.work_type,
                "start_time": entry.start_time
            }
            for entry in completed_entries
        ]
        
        return {
            "knowledge_ref": knowledge_ref,
            "total_minutes": total_minutes,
            "work_item_count": work_item_count,
            "average_duration": average_duration,
            "work_items": work_items
        }
    
    def rank_expertise_by_time(self, min_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Rank knowledge areas by time investment to identify expertise.
        
        Analyzes all time entries to determine which knowledge areas have the most
        time invested, indicating areas of expertise or focus.
        
        Args:
            min_minutes: Minimum time threshold to include a knowledge area (default 60)
            
        Returns:
            List of knowledge areas ranked by time investment, each containing:
            - knowledge_ref: Name of the knowledge area
            - total_minutes: Total time invested
            - work_item_count: Number of work items
            - rank: Ranking position (1 = most time)
        """
        data = self._load_time_data()
        
        # Aggregate time by knowledge reference
        knowledge_time: Dict[str, Dict[str, Any]] = {}
        
        for entry in data["entries"]:
            # Only count completed entries
            if entry.get("duration_minutes") is None:
                continue
            
            duration = entry["duration_minutes"]
            
            # Process each knowledge reference
            for knowledge_ref in entry.get("knowledge_refs", []):
                if knowledge_ref not in knowledge_time:
                    knowledge_time[knowledge_ref] = {
                        "knowledge_ref": knowledge_ref,
                        "total_minutes": 0,
                        "work_item_count": 0
                    }
                
                knowledge_time[knowledge_ref]["total_minutes"] += duration
                knowledge_time[knowledge_ref]["work_item_count"] += 1
        
        # Filter by minimum time threshold
        filtered_areas = [
            area for area in knowledge_time.values()
            if area["total_minutes"] >= min_minutes
        ]
        
        # Sort by total time (descending)
        filtered_areas.sort(key=lambda x: x["total_minutes"], reverse=True)
        
        # Add rank
        for i, area in enumerate(filtered_areas, start=1):
            area["rank"] = i
        
        return filtered_areas
    
    def get_time_trends_by_knowledge(
        self,
        knowledge_ref: Optional[str] = None,
        days: int = 90,
        group_by: str = "week"
    ) -> Dict[str, Any]:
        """
        Group time by knowledge area and show trends over time.
        
        Analyzes time entries to show how time investment in knowledge areas
        changes over time, helping identify learning patterns and focus shifts.
        
        Args:
            knowledge_ref: Specific knowledge area to analyze (None = all areas)
            days: Number of days to analyze (default 90)
            group_by: Grouping period - "day", "week", or "month" (default "week")
            
        Returns:
            Dictionary with trend analysis:
            - knowledge_ref: Knowledge area (or "all")
            - period_data: List of time periods with minutes invested
            - total_minutes: Total time across all periods
            - trend_direction: "increasing", "decreasing", or "stable"
        """
        data = self._load_time_data()
        
        # Calculate cutoff date
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Filter entries by date and knowledge reference
        filtered_entries = []
        for entry in data["entries"]:
            # Only completed entries
            if entry.get("duration_minutes") is None:
                continue
            
            # Check date
            if entry.get("start_time"):
                start_time = datetime.fromisoformat(entry["start_time"])
                if start_time < cutoff_date:
                    continue
            
            # Check knowledge reference
            if knowledge_ref is not None:
                if knowledge_ref not in entry.get("knowledge_refs", []):
                    continue
            
            filtered_entries.append(entry)
        
        # Group by time period
        period_data: Dict[str, int] = {}
        
        for entry in filtered_entries:
            start_time = datetime.fromisoformat(entry["start_time"])
            
            # Determine period key
            if group_by == "day":
                period_key = start_time.strftime("%Y-%m-%d")
            elif group_by == "week":
                # ISO week format
                period_key = start_time.strftime("%Y-W%W")
            elif group_by == "month":
                period_key = start_time.strftime("%Y-%m")
            else:
                period_key = start_time.strftime("%Y-W%W")  # Default to week
            
            # Aggregate time
            if period_key not in period_data:
                period_data[period_key] = 0
            period_data[period_key] += entry["duration_minutes"]
        
        # Sort periods chronologically
        sorted_periods = sorted(period_data.items())
        
        # Calculate trend direction
        trend_direction = "stable"
        if len(sorted_periods) >= 2:
            # Compare first half to second half
            midpoint = len(sorted_periods) // 2
            first_half_avg = sum(v for _, v in sorted_periods[:midpoint]) / midpoint if midpoint > 0 else 0
            second_half_avg = sum(v for _, v in sorted_periods[midpoint:]) / (len(sorted_periods) - midpoint) if (len(sorted_periods) - midpoint) > 0 else 0
            
            # Determine trend (>20% change)
            if second_half_avg > first_half_avg * 1.2:
                trend_direction = "increasing"
            elif second_half_avg < first_half_avg * 0.8:
                trend_direction = "decreasing"
        
        # Build result
        total_minutes = sum(period_data.values())
        
        return {
            "knowledge_ref": knowledge_ref or "all",
            "period_data": [
                {"period": period, "minutes": minutes}
                for period, minutes in sorted_periods
            ],
            "total_minutes": total_minutes,
            "trend_direction": trend_direction,
            "days_analyzed": days,
            "group_by": group_by
        }
    
    def generate_experience_adjusted_estimate(
        self,
        work_description: str,
        work_type: str,
        knowledge_refs: Optional[List[str]] = None
    ) -> Optional[EstimateResult]:
        """
        Generate an estimate that considers the user's experience level in related knowledge areas.
        
        Adjusts estimates based on how much time the user has invested in the relevant
        knowledge areas. More experience typically leads to faster completion times.
        
        Args:
            work_description: Description of the work to estimate
            work_type: Type of work
            knowledge_refs: List of related knowledge document names
            
        Returns:
            EstimateResult with experience adjustment, or None if no similar work found
        """
        knowledge_refs = knowledge_refs or []
        
        # Get base estimate
        base_estimate = self.generate_estimate(work_description, work_type, knowledge_refs)
        
        if base_estimate is None:
            return None
        
        # If no knowledge references, return base estimate
        if not knowledge_refs:
            return base_estimate
        
        # Calculate experience level for each knowledge area
        total_experience_minutes = 0
        experience_areas = []
        
        for knowledge_ref in knowledge_refs:
            investment = self.get_knowledge_time_investment(knowledge_ref)
            total_experience_minutes += investment["total_minutes"]
            experience_areas.append({
                "knowledge_ref": knowledge_ref,
                "minutes": investment["total_minutes"],
                "work_items": investment["work_item_count"]
            })
        
        # Determine experience level and adjustment factor
        # Experience levels:
        # - Novice (0-120 min): 1.2x multiplier (20% slower)
        # - Intermediate (120-480 min): 1.0x multiplier (baseline)
        # - Experienced (480-1200 min): 0.85x multiplier (15% faster)
        # - Expert (1200+ min): 0.7x multiplier (30% faster)
        
        if total_experience_minutes < 120:
            experience_level = "novice"
            adjustment_factor = 1.2
        elif total_experience_minutes < 480:
            experience_level = "intermediate"
            adjustment_factor = 1.0
        elif total_experience_minutes < 1200:
            experience_level = "experienced"
            adjustment_factor = 0.85
        else:
            experience_level = "expert"
            adjustment_factor = 0.7
        
        # Apply adjustment
        adjusted_mean = base_estimate.mean_minutes * adjustment_factor
        adjusted_min = base_estimate.min_estimate * adjustment_factor
        adjusted_max = base_estimate.max_estimate * adjustment_factor
        
        # Build explanation
        experience_summary = ", ".join([
            f"{area['knowledge_ref']} ({area['minutes']} min, {area['work_items']} items)"
            for area in experience_areas
        ])
        
        adjusted_explanation = (
            base_estimate.explanation +
            f" Experience adjustment: {experience_level} level "
            f"({total_experience_minutes} total minutes across {len(knowledge_refs)} knowledge areas). "
            f"Estimate adjusted by {adjustment_factor}x. "
            f"Experience breakdown: {experience_summary}."
        )
        
        return EstimateResult(
            mean_minutes=adjusted_mean,
            variance=base_estimate.variance,
            std_dev=base_estimate.std_dev,
            min_estimate=adjusted_min,
            max_estimate=adjusted_max,
            confidence_range=(adjusted_min, adjusted_max),
            similar_work_count=base_estimate.similar_work_count,
            similar_work_ids=base_estimate.similar_work_ids,
            explanation=adjusted_explanation
        )
    
    # People-Time Integration Methods
    
    def link_time_to_people(
        self,
        work_id: str,
        people_refs: List[str]
    ) -> bool:
        """
        Link a time entry to people.
        
        Creates connections between time data and person profiles by updating
        the time entry's people_refs field.
        
        Args:
            work_id: Unique identifier of the work entry
            people_refs: List of person names to link
            
        Returns:
            True if link created successfully, False if work_id not found
        """
        data = self._load_time_data()
        
        # Find the entry
        entry_dict = None
        for entry in data["entries"]:
            if entry["id"] == work_id:
                entry_dict = entry
                break
        
        if not entry_dict:
            return False
        
        # Update people references (merge with existing)
        existing_refs = set(entry_dict.get("people_refs", []))
        new_refs = set(people_refs)
        entry_dict["people_refs"] = list(existing_refs.union(new_refs))
        
        # Save updated data
        self._save_time_data(data)
        
        return True
    
    def get_person_collaboration_time(self, person_ref: str) -> Dict[str, Any]:
        """
        Get total time spent on work involving a specific person.
        
        Calculates the total time spent on work related to a person,
        including number of work items and average duration.
        
        Args:
            person_ref: Name of the person
            
        Returns:
            Dictionary with collaboration time statistics:
            - person_ref: Name of the person
            - total_minutes: Total time spent on work involving this person
            - work_item_count: Number of work items
            - average_duration: Average time per work item
            - work_items: List of work item summaries
        """
        entries = self.get_entries_by_person(person_ref)
        
        # Filter to completed entries only
        completed_entries = [e for e in entries if e.duration_minutes is not None]
        
        if not completed_entries:
            return {
                "person_ref": person_ref,
                "total_minutes": 0,
                "work_item_count": 0,
                "average_duration": 0.0,
                "work_items": []
            }
        
        # Calculate statistics
        total_minutes = sum(e.duration_minutes for e in completed_entries)
        work_item_count = len(completed_entries)
        average_duration = total_minutes / work_item_count
        
        # Build work item summaries
        work_items = [
            {
                "id": entry.id,
                "description": entry.work_description,
                "duration_minutes": entry.duration_minutes,
                "work_type": entry.work_type,
                "start_time": entry.start_time
            }
            for entry in completed_entries
        ]
        
        return {
            "person_ref": person_ref,
            "total_minutes": total_minutes,
            "work_item_count": work_item_count,
            "average_duration": average_duration,
            "work_items": work_items
        }
    
    def identify_collaboration_patterns(
        self,
        days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Identify frequent collaborators and time patterns.
        
        Analyzes time entries to find which people are collaborated with most
        frequently and what patterns exist in collaboration timing.
        
        Args:
            days: Number of days to analyze (None = all time)
            
        Returns:
            Dictionary with collaboration pattern analysis:
            - frequent_collaborators: List of people ranked by collaboration time
            - collaboration_by_work_type: Breakdown of collaboration by work type
            - total_collaboration_time: Total time spent on collaborative work
            - solo_work_time: Total time spent on solo work
            - collaboration_percentage: Percentage of time spent collaborating
        """
        data = self._load_time_data()
        
        # Filter entries by date range if specified
        entries = data["entries"]
        if days is not None:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            entries = [
                entry for entry in entries
                if entry.get("start_time") and
                datetime.fromisoformat(entry["start_time"]) >= cutoff_date
            ]
        
        # Only consider completed entries
        entries = [e for e in entries if e.get("duration_minutes") is not None]
        
        # Track collaboration data
        person_time: Dict[str, Dict[str, Any]] = {}
        work_type_collaboration: Dict[str, int] = {}
        total_collaboration_time = 0
        total_solo_time = 0
        
        for entry in entries:
            duration = entry["duration_minutes"]
            people_refs = entry.get("people_refs", [])
            work_type = entry.get("work_type", "unknown")
            
            if people_refs:
                # This is collaborative work
                total_collaboration_time += duration
                
                # Track time by person
                for person_ref in people_refs:
                    if person_ref not in person_time:
                        person_time[person_ref] = {
                            "person_ref": person_ref,
                            "total_minutes": 0,
                            "work_item_count": 0
                        }
                    
                    person_time[person_ref]["total_minutes"] += duration
                    person_time[person_ref]["work_item_count"] += 1
                
                # Track by work type
                if work_type not in work_type_collaboration:
                    work_type_collaboration[work_type] = 0
                work_type_collaboration[work_type] += duration
            else:
                # This is solo work
                total_solo_time += duration
        
        # Rank collaborators by time
        frequent_collaborators = sorted(
            person_time.values(),
            key=lambda x: x["total_minutes"],
            reverse=True
        )
        
        # Add rank
        for i, collaborator in enumerate(frequent_collaborators, start=1):
            collaborator["rank"] = i
        
        # Calculate collaboration percentage
        total_time = total_collaboration_time + total_solo_time
        collaboration_percentage = (
            (total_collaboration_time / total_time * 100)
            if total_time > 0 else 0.0
        )
        
        return {
            "frequent_collaborators": frequent_collaborators,
            "collaboration_by_work_type": work_type_collaboration,
            "total_collaboration_time": total_collaboration_time,
            "solo_work_time": total_solo_time,
            "collaboration_percentage": collaboration_percentage,
            "days_analyzed": days
        }
    
    def generate_collaboration_adjusted_estimate(
        self,
        work_description: str,
        work_type: str,
        people_refs: Optional[List[str]] = None,
        knowledge_refs: Optional[List[str]] = None
    ) -> Optional[EstimateResult]:
        """
        Generate an estimate that factors in historical collaboration time with specific people.
        
        Adjusts estimates based on past work involving the same people, as collaborative
        work often has different time characteristics than solo work.
        
        Args:
            work_description: Description of the work to estimate
            work_type: Type of work
            people_refs: List of people involved in the work
            knowledge_refs: List of related knowledge document names
            
        Returns:
            EstimateResult with collaboration adjustment, or None if no similar work found
        """
        people_refs = people_refs or []
        
        # Get base estimate
        base_estimate = self.generate_estimate(work_description, work_type, knowledge_refs)
        
        if base_estimate is None:
            return None
        
        # If no people references, return base estimate
        if not people_refs:
            return base_estimate
        
        # Find similar work involving the same people
        data = self._load_time_data()
        similar_collaborative_work = []
        
        for entry_dict in data["entries"]:
            # Only completed entries
            if entry_dict.get("duration_minutes") is None:
                continue
            
            # Match by work type
            if entry_dict["work_type"] != work_type:
                continue
            
            # Check if any of the people are involved
            entry_people = set(entry_dict.get("people_refs", []))
            query_people = set(people_refs)
            
            if entry_people.intersection(query_people):
                time_entry_fields = {
                    "id", "start_time", "end_time", "duration_minutes",
                    "work_description", "work_type", "knowledge_refs",
                    "people_refs", "distractions", "completion_percentage", "notes"
                }
                filtered_dict = {k: v for k, v in entry_dict.items() if k in time_entry_fields}
                similar_collaborative_work.append(TimeEntry(**filtered_dict))
        
        # If we have collaborative work history, use it to adjust the estimate
        if similar_collaborative_work:
            # Calculate statistics for collaborative work
            collab_mean, collab_variance = self.calculate_statistics(similar_collaborative_work)
            
            # Compare to base estimate
            if collab_mean > 0:
                # Use collaborative work statistics
                collab_std_dev = math.sqrt(collab_variance)
                adjusted_mean = collab_mean
                adjusted_min = max(0, collab_mean - collab_std_dev)
                adjusted_max = collab_mean + collab_std_dev
                
                # Build explanation
                people_str = ", ".join(people_refs)
                adjusted_explanation = (
                    f"Based on {len(similar_collaborative_work)} similar {work_type} work items "
                    f"involving {people_str}. "
                    f"Average collaborative duration: {collab_mean:.1f} minutes (±{collab_std_dev:.1f} minutes). "
                    f"Collaborative work with these people typically takes "
                    f"{((collab_mean - base_estimate.mean_minutes) / base_estimate.mean_minutes * 100):.1f}% "
                    f"{'more' if collab_mean > base_estimate.mean_minutes else 'less'} time than solo work."
                )
                
                return EstimateResult(
                    mean_minutes=adjusted_mean,
                    variance=collab_variance,
                    std_dev=collab_std_dev,
                    min_estimate=adjusted_min,
                    max_estimate=adjusted_max,
                    confidence_range=(adjusted_min, adjusted_max),
                    similar_work_count=len(similar_collaborative_work),
                    similar_work_ids=[e.id for e in similar_collaborative_work],
                    explanation=adjusted_explanation
                )
        
        # No collaborative work history, return base estimate
        return base_estimate
    
    def categorize_work_type_by_collaboration(
        self,
        work_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Distinguish between solo work and collaborative work in time analysis.
        
        Categorizes work entries as solo or collaborative based on whether
        people references are present, and provides statistics for each category.
        
        Args:
            work_id: Optional specific work entry to categorize (None = analyze all)
            
        Returns:
            Dictionary with categorization results:
            - If work_id provided: category ("solo" or "collaborative") and details
            - If work_id None: statistics for all work (solo vs collaborative breakdown)
        """
        data = self._load_time_data()
        
        if work_id is not None:
            # Categorize a specific work entry
            entry_dict = None
            for entry in data["entries"]:
                if entry["id"] == work_id:
                    entry_dict = entry
                    break
            
            if not entry_dict:
                return {"error": "Work entry not found"}
            
            people_refs = entry_dict.get("people_refs", [])
            
            if people_refs:
                return {
                    "work_id": work_id,
                    "category": "collaborative",
                    "people_involved": people_refs,
                    "people_count": len(people_refs)
                }
            else:
                return {
                    "work_id": work_id,
                    "category": "solo",
                    "people_involved": [],
                    "people_count": 0
                }
        else:
            # Analyze all work entries
            solo_entries = []
            collaborative_entries = []
            
            for entry in data["entries"]:
                # Only completed entries
                if entry.get("duration_minutes") is None:
                    continue
                
                people_refs = entry.get("people_refs", [])
                
                if people_refs:
                    collaborative_entries.append(entry)
                else:
                    solo_entries.append(entry)
            
            # Calculate statistics
            solo_time = sum(e["duration_minutes"] for e in solo_entries)
            collaborative_time = sum(e["duration_minutes"] for e in collaborative_entries)
            total_time = solo_time + collaborative_time
            
            solo_count = len(solo_entries)
            collaborative_count = len(collaborative_entries)
            total_count = solo_count + collaborative_count
            
            # Calculate averages
            solo_avg = solo_time / solo_count if solo_count > 0 else 0.0
            collaborative_avg = collaborative_time / collaborative_count if collaborative_count > 0 else 0.0
            
            # Breakdown by work type
            solo_by_type: Dict[str, int] = {}
            collaborative_by_type: Dict[str, int] = {}
            
            for entry in solo_entries:
                work_type = entry.get("work_type", "unknown")
                solo_by_type[work_type] = solo_by_type.get(work_type, 0) + entry["duration_minutes"]
            
            for entry in collaborative_entries:
                work_type = entry.get("work_type", "unknown")
                collaborative_by_type[work_type] = collaborative_by_type.get(work_type, 0) + entry["duration_minutes"]
            
            return {
                "solo_work": {
                    "total_minutes": solo_time,
                    "work_item_count": solo_count,
                    "average_duration": solo_avg,
                    "percentage_of_total_time": (solo_time / total_time * 100) if total_time > 0 else 0.0,
                    "by_work_type": solo_by_type
                },
                "collaborative_work": {
                    "total_minutes": collaborative_time,
                    "work_item_count": collaborative_count,
                    "average_duration": collaborative_avg,
                    "percentage_of_total_time": (collaborative_time / total_time * 100) if total_time > 0 else 0.0,
                    "by_work_type": collaborative_by_type
                },
                "total_work": {
                    "total_minutes": total_time,
                    "work_item_count": total_count
                }
            }
