#!/usr/bin/env python3
"""
Database models and initialization for PolyRun project management
"""

import sqlite3
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import hashlib

class ProjectDatabase:
    def __init__(self, db_path: str = "database/polyrun.db"):
        """Initialize the project database"""
        self.db_path = db_path
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database schema
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    author TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_public BOOLEAN DEFAULT FALSE,
                    file_path TEXT NOT NULL,
                    language_count INTEGER DEFAULT 0,
                    tags TEXT, -- JSON array of tags
                    metadata TEXT -- JSON metadata
                )
            ''')
            
            # Project versions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_versions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    changes_description TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            
            # Shared links table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shared_links (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    share_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    access_count INTEGER DEFAULT 0,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            
            # Tags table for easier searching
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    usage_count INTEGER DEFAULT 0
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_public ON projects (is_public)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_author ON projects (author)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_created ON projects (created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shared_links_token ON shared_links (share_token)')
            
            conn.commit()
    
    def save_project(self, name: str, description: str, author: str, 
                     file_content: str, tags: List[str] = None, 
                     is_public: bool = False, metadata: Dict = None) -> str:
        """
        Save a new project to the database
        
        Returns:
            project_id: Unique project identifier
        """
        project_id = str(uuid.uuid4())
        file_path = f"projects/{project_id}.mix"
        
        # Ensure projects directory exists
        os.makedirs("projects", exist_ok=True)
        
        # Save .mix file
        full_file_path = file_path
        with open(full_file_path, 'w') as f:
            f.write(file_content)
        
        # Count languages in the file
        language_count = self._count_languages(file_content)
        
        # Prepare data
        tags_json = json.dumps(tags or [])
        metadata_json = json.dumps(metadata or {})
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert project
            cursor.execute('''
                INSERT INTO projects 
                (id, name, description, author, file_path, language_count, tags, metadata, is_public)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (project_id, name, description, author, file_path, 
                  language_count, tags_json, metadata_json, is_public))
            
            # Update tag usage counts
            if tags:
                for tag in tags:
                    cursor.execute('''
                        INSERT INTO tags (name, usage_count) 
                        VALUES (?, 1)
                        ON CONFLICT(name) DO UPDATE SET usage_count = usage_count + 1
                    ''', (tag,))
            
            conn.commit()
        
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a project by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
            row = cursor.fetchone()
            
            if row:
                project = dict(row)
                project['tags'] = json.loads(project['tags'] or '[]')
                project['metadata'] = json.loads(project['metadata'] or '{}')
                
                # Read file content
                try:
                    with open(project['file_path'], 'r') as f:
                        project['content'] = f.read()
                except FileNotFoundError:
                    project['content'] = "# File not found"
                
                return project
        
        return None
    
    def list_projects(self, author: str = None, is_public: bool = None, 
                     limit: int = 50, offset: int = 0) -> List[Dict]:
        """List projects with optional filtering"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = 'SELECT * FROM projects WHERE 1=1'
            params = []
            
            if author:
                query += ' AND author = ?'
                params.append(author)
            
            if is_public is not None:
                query += ' AND is_public = ?'
                params.append(is_public)
            
            query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            projects = []
            
            for row in cursor.fetchall():
                project = dict(row)
                project['tags'] = json.loads(project['tags'] or '[]')
                project['metadata'] = json.loads(project['metadata'] or '{}')
                projects.append(project)
            
            return projects
    
    def update_project(self, project_id: str, **updates) -> bool:
        """Update a project"""
        if not updates:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build update query
            set_clauses = []
            params = []
            
            for key, value in updates.items():
                if key in ['name', 'description', 'author', 'is_public']:
                    set_clauses.append(f'{key} = ?')
                    params.append(value)
                elif key == 'tags':
                    set_clauses.append('tags = ?')
                    params.append(json.dumps(value))
                elif key == 'metadata':
                    set_clauses.append('metadata = ?')
                    params.append(json.dumps(value))
                elif key == 'content':
                    # Update file content
                    project = self.get_project(project_id)
                    if project:
                        with open(project['file_path'], 'w') as f:
                            f.write(value)
                        # Update language count
                        set_clauses.append('language_count = ?')
                        params.append(self._count_languages(value))
            
            if set_clauses:
                set_clauses.append('updated_at = CURRENT_TIMESTAMP')
                query = f'UPDATE projects SET {", ".join(set_clauses)} WHERE id = ?'
                params.append(project_id)
                
                cursor.execute(query, params)
                conn.commit()
                
                return cursor.rowcount > 0
        
        return False
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and its file"""
        project = self.get_project(project_id)
        if not project:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete from database
            cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            cursor.execute('DELETE FROM project_versions WHERE project_id = ?', (project_id,))
            cursor.execute('DELETE FROM shared_links WHERE project_id = ?', (project_id,))
            
            conn.commit()
            
            # Delete file
            try:
                os.remove(project['file_path'])
            except FileNotFoundError:
                pass
            
            return True
    
    def create_share_link(self, project_id: str, expires_at: str = None) -> str:
        """Create a shareable link for a project"""
        share_token = hashlib.sha256(f"{project_id}{datetime.now()}".encode()).hexdigest()[:16]
        link_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO shared_links (id, project_id, share_token, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (link_id, project_id, share_token, expires_at))
            
            conn.commit()
        
        return share_token
    
    def get_project_by_share_token(self, share_token: str) -> Optional[Dict]:
        """Get a project by its share token"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if share link is valid
            cursor.execute('''
                SELECT sl.*, p.* FROM shared_links sl
                JOIN projects p ON sl.project_id = p.id
                WHERE sl.share_token = ? AND sl.is_active = TRUE
                AND (sl.expires_at IS NULL OR sl.expires_at > CURRENT_TIMESTAMP)
            ''', (share_token,))
            
            row = cursor.fetchone()
            if row:
                # Update access count
                cursor.execute('''
                    UPDATE shared_links SET access_count = access_count + 1
                    WHERE share_token = ?
                ''', (share_token,))
                conn.commit()
                
                project = dict(row)
                project['tags'] = json.loads(project['tags'] or '[]')
                project['metadata'] = json.loads(project['metadata'] or '{}')
                
                # Read file content
                try:
                    with open(project['file_path'], 'r') as f:
                        project['content'] = f.read()
                except FileNotFoundError:
                    project['content'] = "# File not found"
                
                return project
        
        return None
    
    def search_projects(self, query: str, is_public: bool = True) -> List[Dict]:
        """Search projects by name, description, or tags"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            search_query = '''
                SELECT * FROM projects 
                WHERE is_public = ? AND (
                    name LIKE ? OR 
                    description LIKE ? OR 
                    tags LIKE ?
                )
                ORDER BY created_at DESC
                LIMIT 100
            '''
            
            search_term = f'%{query}%'
            cursor.execute(search_query, (is_public, search_term, search_term, search_term))
            
            projects = []
            for row in cursor.fetchall():
                project = dict(row)
                project['tags'] = json.loads(project['tags'] or '[]')
                project['metadata'] = json.loads(project['metadata'] or '{}')
                projects.append(project)
            
            return projects
    
    def get_popular_tags(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Get most popular tags"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, usage_count FROM tags 
                ORDER BY usage_count DESC 
                LIMIT ?
            ''', (limit,))
            
            return cursor.fetchall()
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total projects
            cursor.execute('SELECT COUNT(*) FROM projects')
            stats['total_projects'] = cursor.fetchone()[0]
            
            # Public projects
            cursor.execute('SELECT COUNT(*) FROM projects WHERE is_public = TRUE')
            stats['public_projects'] = cursor.fetchone()[0]
            
            # Total shares
            cursor.execute('SELECT COUNT(*) FROM shared_links WHERE is_active = TRUE')
            stats['active_shares'] = cursor.fetchone()[0]
            
            # Most popular languages
            cursor.execute('''
                SELECT language_count, COUNT(*) as count 
                FROM projects 
                GROUP BY language_count 
                ORDER BY count DESC
            ''')
            stats['language_distribution'] = dict(cursor.fetchall())
            
            return stats
    
    def _count_languages(self, content: str) -> int:
        """Count the number of #lang: directives in content"""
        return content.count('#lang:')

# Test the database
if __name__ == "__main__":
    # Initialize database
    db = ProjectDatabase()
    
    # Test saving a project
    sample_content = '''#lang: python
#export: message
message = "Hello from Python!"
print(message)

#lang: javascript
#import: message
console.log("JS received:", message);
'''
    
    project_id = db.save_project(
        name="Test Data Passing",
        description="A simple example of data passing between Python and JavaScript",
        author="test_user",
        file_content=sample_content,
        tags=["python", "javascript", "data-passing", "tutorial"],
        is_public=True,
        metadata={"difficulty": "beginner", "estimated_time": "5 minutes"}
    )
    
    print(f"✅ Created project: {project_id}")
    
    # Test retrieving the project
    project = db.get_project(project_id)
    print(f"✅ Retrieved project: {project['name']}")
    
    # Test creating a share link
    share_token = db.create_share_link(project_id)
    print(f"✅ Created share link: {share_token}")
    
    # Test accessing via share link
    shared_project = db.get_project_by_share_token(share_token)
    print(f"✅ Accessed via share: {shared_project['name']}")
    
    # Test listing projects
    projects = db.list_projects(is_public=True)
    print(f"✅ Found {len(projects)} public projects")
    
    # Test stats
    stats = db.get_stats()
    print(f"✅ Database stats: {stats}")
    
    print("\n🎉 Database tests completed successfully!")
