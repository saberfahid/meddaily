"""
Database module for Medical Education App
Handles SQLite database initialization and operations
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


class MedicalDatabase:
    """Manages all database operations for the medical education app"""
    
    def __init__(self, db_path: str = "medical_education.db"):
        self.db_path = db_path
        self.initialize_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def initialize_database(self):
        """Create all necessary tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create subjects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create topics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                topic_name TEXT NOT NULL,
                subtopic_name TEXT,
                cycle_number INTEGER DEFAULT 1,
                used BOOLEAN DEFAULT 0,
                last_used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects(id),
                UNIQUE(subject_id, topic_name, subtopic_name)
            )
        """)
        
        # Create cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                case_text TEXT NOT NULL,
                mcqs TEXT NOT NULL,
                answers TEXT NOT NULL,
                mnemonic TEXT NOT NULL,
                video_url TEXT,
                video_path TEXT,
                youtube_id TEXT,
                telegram_message_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        """)
        
        # Create workflow state table to track daily rotation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                current_subject_id INTEGER,
                last_run_date DATE,
                total_runs INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create AI generated topics log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_topic_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                topics_generated TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_topics_subject_used 
            ON topics(subject_id, used, cycle_number)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cases_topic 
            ON cases(topic_id)
        """)
        
        conn.commit()
        conn.close()
    
    def add_subject(self, name: str) -> int:
        """Add a new subject and return its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
            subject_id = cursor.lastrowid
            conn.commit()
            return subject_id
        except sqlite3.IntegrityError:
            # Subject already exists, get its ID
            cursor.execute("SELECT id FROM subjects WHERE name = ?", (name,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def get_subject_id(self, name: str) -> Optional[int]:
        """Get subject ID by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def add_topic(self, subject_id: int, topic_name: str, subtopic_name: str = None, 
                  cycle_number: int = 1) -> Optional[int]:
        """Add a new topic and return its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO topics (subject_id, topic_name, subtopic_name, cycle_number)
                VALUES (?, ?, ?, ?)
            """, (subject_id, topic_name, subtopic_name, cycle_number))
            topic_id = cursor.lastrowid
            conn.commit()
            return topic_id
        except sqlite3.IntegrityError:
            # Topic already exists for this cycle
            return None
        finally:
            conn.close()
    
    def get_next_unused_topic(self, subject_id: int) -> Optional[Dict[str, Any]]:
        """Get the next unused topic for a subject"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current cycle number for this subject
        cursor.execute("""
            SELECT MAX(cycle_number) FROM topics WHERE subject_id = ?
        """, (subject_id,))
        result = cursor.fetchone()
        current_cycle = result[0] if result[0] else 1
        
        # Try to find unused topic in current cycle
        cursor.execute("""
            SELECT id, topic_name, subtopic_name, cycle_number
            FROM topics
            WHERE subject_id = ? AND cycle_number = ? AND used = 0
            ORDER BY id
            LIMIT 1
        """, (subject_id, current_cycle))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'topic_name': result[1],
                'subtopic_name': result[2],
                'cycle_number': result[3]
            }
        return None
    
    def mark_topic_as_used(self, topic_id: int):
        """Mark a topic as used"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE topics 
            SET used = 1, last_used_at = ?
            WHERE id = ?
        """, (datetime.now(), topic_id))
        conn.commit()
        conn.close()
    
    def check_and_start_new_cycle(self, subject_id: int) -> bool:
        """
        Check if all topics in current cycle are used.
        If yes, create new cycle with all topics marked as unused.
        Returns True if new cycle was started.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current cycle
        cursor.execute("""
            SELECT MAX(cycle_number) FROM topics WHERE subject_id = ?
        """, (subject_id,))
        result = cursor.fetchone()
        current_cycle = result[0] if result[0] else 1
        
        # Check if all topics in current cycle are used
        cursor.execute("""
            SELECT COUNT(*) FROM topics 
            WHERE subject_id = ? AND cycle_number = ? AND used = 0
        """, (subject_id, current_cycle))
        unused_count = cursor.fetchone()[0]
        
        if unused_count == 0:
            # All topics used, start new cycle
            new_cycle = current_cycle + 1
            
            # Get all topics from cycle 1 (original topics)
            cursor.execute("""
                SELECT topic_name, subtopic_name FROM topics
                WHERE subject_id = ? AND cycle_number = 1
            """, (subject_id,))
            original_topics = cursor.fetchall()
            
            # Reset all topics for this subject to unused and increment cycle
            cursor.execute("""
                UPDATE topics 
                SET used = 0, cycle_number = ?
                WHERE subject_id = ?
            """, (new_cycle, subject_id))
            
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def add_case(self, topic_id: int, case_text: str, mcqs: str, answers: str, 
                 mnemonic: str, video_path: str = None, video_url: str = None,
                 youtube_id: str = None, telegram_message_id: str = None) -> int:
        """Add a new case and return its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO cases (topic_id, case_text, mcqs, answers, mnemonic, 
                             video_path, video_url, youtube_id, telegram_message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (topic_id, case_text, mcqs, answers, mnemonic, video_path, 
              video_url, youtube_id, telegram_message_id))
        
        case_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return case_id
    
    def update_case_video_info(self, case_id: int, video_url: str = None, 
                               youtube_id: str = None, telegram_message_id: str = None):
        """Update video information for a case"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if video_url:
            updates.append("video_url = ?")
            params.append(video_url)
        if youtube_id:
            updates.append("youtube_id = ?")
            params.append(youtube_id)
        if telegram_message_id:
            updates.append("telegram_message_id = ?")
            params.append(telegram_message_id)
        
        if updates:
            params.append(case_id)
            query = f"UPDATE cases SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    def get_next_subject_for_rotation(self) -> Optional[int]:
        """Get the next subject ID for daily rotation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all subjects
        cursor.execute("SELECT id FROM subjects ORDER BY id")
        subjects = [row[0] for row in cursor.fetchall()]
        
        if not subjects:
            conn.close()
            return None
        
        # Get current workflow state
        cursor.execute("SELECT current_subject_id FROM workflow_state WHERE id = 1")
        result = cursor.fetchone()
        
        if result and result[0]:
            current_subject_id = result[0]
            # Find next subject in rotation
            try:
                current_index = subjects.index(current_subject_id)
                next_index = (current_index + 1) % len(subjects)
                next_subject_id = subjects[next_index]
            except ValueError:
                next_subject_id = subjects[0]
        else:
            # First run, start with first subject
            next_subject_id = subjects[0]
        
        conn.close()
        return next_subject_id
    
    def update_workflow_state(self, subject_id: int):
        """Update workflow state after processing"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO workflow_state (id, current_subject_id, last_run_date, total_runs)
            VALUES (1, ?, DATE('now'), 1)
            ON CONFLICT(id) DO UPDATE SET
                current_subject_id = excluded.current_subject_id,
                last_run_date = excluded.last_run_date,
                total_runs = total_runs + 1,
                updated_at = CURRENT_TIMESTAMP
        """, (subject_id,))
        
        conn.commit()
        conn.close()
    
    def get_topic_count_by_subject(self, subject_id: int) -> int:
        """Get count of topics for a subject in cycle 1"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM topics 
            WHERE subject_id = ? AND cycle_number = 1
        """, (subject_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def log_ai_topic_generation(self, subject_id: int, topics: List[Dict[str, str]]):
        """Log AI-generated topics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ai_topic_log (subject_id, topics_generated)
            VALUES (?, ?)
        """, (subject_id, json.dumps(topics)))
        conn.commit()
        conn.close()
    
    def get_all_subjects(self) -> List[Dict[str, Any]]:
        """Get all subjects"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM subjects ORDER BY id")
        subjects = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        conn.close()
        return subjects
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total subjects
        cursor.execute("SELECT COUNT(*) FROM subjects")
        stats['total_subjects'] = cursor.fetchone()[0]
        
        # Total topics (cycle 1 only)
        cursor.execute("SELECT COUNT(*) FROM topics WHERE cycle_number = 1")
        stats['total_topics'] = cursor.fetchone()[0]
        
        # Total cases generated
        cursor.execute("SELECT COUNT(*) FROM cases")
        stats['total_cases'] = cursor.fetchone()[0]
        
        # Topics by subject
        cursor.execute("""
            SELECT s.name, COUNT(t.id) as count
            FROM subjects s
            LEFT JOIN topics t ON s.id = t.subject_id AND t.cycle_number = 1
            GROUP BY s.id, s.name
        """)
        stats['topics_by_subject'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Workflow state
        cursor.execute("SELECT current_subject_id, last_run_date, total_runs FROM workflow_state WHERE id = 1")
        result = cursor.fetchone()
        if result:
            stats['workflow'] = {
                'current_subject_id': result[0],
                'last_run_date': result[1],
                'total_runs': result[2]
            }
        else:
            stats['workflow'] = None
        
        conn.close()
        return stats


if __name__ == "__main__":
    # Initialize database and print statistics
    db = MedicalDatabase()
    print("Database initialized successfully!")
    print("\nDatabase Statistics:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
