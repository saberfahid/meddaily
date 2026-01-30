"""
Topic Ingestion Module
Parses medical topics from text files and populates the database
"""

import re
from typing import List, Dict, Tuple
from database import MedicalDatabase


class TopicIngestion:
    """Handles parsing and importing medical topics into the database"""
    
    def __init__(self, db: MedicalDatabase):
        self.db = db
        self.subject_mapping = {
            'Internal Medicine': 'Internal_Medicine_Curriculum',
            'Surgery': 'PART 1: GENERAL SURGICAL PRINCIPLES',
            'Pediatrics': '🩺 PART 2: GROWTH & DEVELOPMENT',
            'Gynecology': '🤰 PART 1: OBSTETRICS'
        }
    
    def parse_topics_file(self, file_path: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Parse the topics file and organize by subject
        Returns: {subject_name: [{'topic': '', 'subtopic': ''}, ...]}
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        topics_by_subject = {
            'Internal Medicine': [],
            'Surgery': [],
            'Pediatrics': [],
            'Gynecology': []
        }
        
        current_subject = None
        
        # Split content into lines
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('##') or line.startswith('---'):
                continue
            
            # Detect subject changes
            if 'Internal_Medicine_Curriculum' in line or 'Internal Medicine' in line:
                current_subject = 'Internal Medicine'
                continue
            elif 'PART 1: GENERAL SURGICAL PRINCIPLES' in line or line.startswith('PART 1:'):
                current_subject = 'Surgery'
                continue
            elif '🩺 PART 2: GROWTH & DEVELOPMENT' in line or (line.startswith('🩺 PART') and 'Pediatrics' not in line):
                current_subject = 'Pediatrics'
                continue
            elif '🤰 PART 1: OBSTETRICS' in line or (line.startswith('🤰 PART') or line.startswith('👶 PART')):
                current_subject = 'Gynecology'
                continue
            
            # Check for section headers (system categories)
            if line.startswith('##') or line.startswith('❤️') or line.startswith('🫁') or \
               line.startswith('🧠') or line.startswith('🩸') or line.startswith('🦴') or \
               line.startswith('🌀') or line.startswith('🫀') or line.startswith('💊') or \
               line.startswith('🧬') or line.startswith('🧓') or line.startswith('⚠️') or \
               line.startswith('🔬') or line.startswith('📊') or line.startswith('🌡️') or \
               line.startswith('🍼') or line.startswith('🏥') or line.startswith('🦠') or \
               line.startswith('🔪') or line.startswith('⚖️') or line.startswith('PART'):
                # This is a section header, skip
                continue
            
            # Parse topic line: format is "Day | Topic | Subtopic | Status"
            # Example: "1 | Heart Failure | Acute Heart Failure | Pending"
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    # Skip day number (first part)
                    topic = parts[1]
                    subtopic = parts[2]
                    
                    # Only add if we have a current subject
                    if current_subject and topic and subtopic:
                        topics_by_subject[current_subject].append({
                            'topic': topic,
                            'subtopic': subtopic
                        })
        
        return topics_by_subject
    
    def import_topics_to_database(self, topics_by_subject: Dict[str, List[Dict[str, str]]]):
        """Import parsed topics into the database"""
        
        for subject_name, topics in topics_by_subject.items():
            if not topics:
                continue
            
            print(f"\nImporting {len(topics)} topics for {subject_name}...")
            
            # Add or get subject
            subject_id = self.db.add_subject(subject_name)
            
            # Add topics
            imported_count = 0
            for topic_data in topics:
                topic_id = self.db.add_topic(
                    subject_id=subject_id,
                    topic_name=topic_data['topic'],
                    subtopic_name=topic_data['subtopic'],
                    cycle_number=1
                )
                if topic_id:
                    imported_count += 1
            
            print(f"Successfully imported {imported_count} topics for {subject_name}")
    
    def import_from_file(self, file_path: str):
        """Main method to parse and import topics from file"""
        print(f"Parsing topics from: {file_path}")
        topics_by_subject = self.parse_topics_file(file_path)
        
        # Print summary
        print("\n=== Parsing Summary ===")
        for subject, topics in topics_by_subject.items():
            print(f"{subject}: {len(topics)} topics")
        
        # Import to database
        print("\n=== Importing to Database ===")
        self.import_topics_to_database(topics_by_subject)
        
        # Print final statistics
        print("\n=== Database Statistics ===")
        stats = self.db.get_statistics()
        print(f"Total Subjects: {stats['total_subjects']}")
        print(f"Total Topics: {stats['total_topics']}")
        print("\nTopics by Subject:")
        for subject, count in stats['topics_by_subject'].items():
            print(f"  {subject}: {count}")


def main():
    """Main function to run topic ingestion"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python topic_ingestion.py <topics_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Initialize database
    db = MedicalDatabase()
    
    # Create ingestion instance and import
    ingestion = TopicIngestion(db)
    ingestion.import_from_file(file_path)
    
    print("\n✅ Topic ingestion completed successfully!")


if __name__ == "__main__":
    main()
