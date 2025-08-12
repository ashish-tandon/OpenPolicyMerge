import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from sqlalchemy import text
from .database import get_session
import uuid

logger = logging.getLogger(__name__)

class SearchEngine:
    """Full-text search engine for documents and data"""
    
    def __init__(self):
        self.default_limit = 50
        self.max_limit = 100
    
    async def search_documents(self, query: str, filters: Optional[Dict] = None, 
                              limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """
        Search documents using full-text search
        
        Args:
            query: Search query string
            filters: Optional filters (document_type, category, etc.)
            limit: Maximum number of results
            offset: Pagination offset
        
        Returns:
            Search results with metadata
        """
        start_time = datetime.now()
        
        try:
            # Validate and set limits
            limit = min(limit or self.default_limit, self.max_limit)
            
            # Build search query
            search_query = self._build_search_query(query, filters, limit, offset)
            
            # Execute search
            results = await self._execute_search(search_query)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Process and rank results
            processed_results = self._process_results(results, query)
            
            # Log search query for analytics
            await self._log_search_query(query, filters, len(processed_results), execution_time)
            
            return {
                "query": query,
                "results": processed_results,
                "total_count": len(processed_results),
                "limit": limit,
                "offset": offset,
                "execution_time_ms": int(execution_time),
                "filters_applied": filters or {},
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "query": query,
                "results": [],
                "error": str(e),
                "execution_time_ms": int(execution_time),
                "status": "error"
            }
    
    async def index_document(self, document_id: str, document_type: str, 
                           title: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """
        Index a document for search
        
        Args:
            document_id: Unique document identifier
            document_type: Type of document (policy, bill, representative, etc.)
            title: Document title
            content: Document content for full-text search
            metadata: Additional document metadata
        
        Returns:
            True if indexing successful, False otherwise
        """
        try:
            # Generate search vector (simplified - in production would use proper FTS)
            search_vector = self._generate_search_vector(title, content)
            
            # Calculate relevance score (simplified scoring)
            relevance_score = self._calculate_relevance_score(title, content, metadata)
            
            # Store in search index
            await self._store_document_index(
                document_id, document_type, title, content, 
                search_vector, relevance_score, metadata
            )
            
            logger.info(f"Document {document_id} indexed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Document indexing failed: {e}")
            return False
    
    async def get_search_suggestions(self, partial_query: str, 
                                   suggestion_type: str = "autocomplete") -> List[str]:
        """
        Get search suggestions based on partial query
        
        Args:
            partial_query: Partial search query
            suggestion_type: Type of suggestions (autocomplete, related, popular)
        
        Returns:
            List of suggestion strings
        """
        try:
            suggestions = await self._fetch_suggestions(partial_query, suggestion_type)
            return suggestions[:10]  # Limit to 10 suggestions
            
        except Exception as e:
            logger.error(f"Failed to fetch suggestions: {e}")
            return []
    
    def _build_search_query(self, query: str, filters: Optional[Dict], 
                           limit: int, offset: int) -> str:
        """Build SQL search query with filters"""
        base_query = """
            SELECT id, document_id, document_type, title, content, 
                   metadata, relevance_score, created_at
            FROM search.search_indices
            WHERE search_vector @@ plainto_tsquery('english', :query)
        """
        
        # Add filters
        if filters:
            if filters.get('document_type'):
                base_query += " AND document_type = :doc_type"
            if filters.get('category'):
                base_query += " AND metadata->>'category' = :category"
            if filters.get('date_from'):
                base_query += " AND created_at >= :date_from"
            if filters.get('date_to'):
                base_query += " AND created_at <= :date_to"
        
        # Add ordering and pagination
        base_query += """
            ORDER BY relevance_score DESC, created_at DESC
            LIMIT :limit OFFSET :offset
        """
        
        return base_query
    
    async def _execute_search(self, search_query: str) -> List[Dict]:
        """Execute search query against database"""
        try:
            session = get_session()
            result = session.execute(text(search_query))
            return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Search execution failed: {e}")
            return []
    
    def _process_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Process and rank search results"""
        processed = []
        
        for result in results:
            # Calculate query relevance score
            query_relevance = self._calculate_query_relevance(result, query)
            
            # Combine with stored relevance score
            final_score = (result.get('relevance_score', 0) + query_relevance) / 2
            
            processed_result = {
                "id": result.get("id"),
                "document_id": result.get("document_id"),
                "document_type": result.get("document_type"),
                "title": result.get("title"),
                "content_preview": self._generate_content_preview(result.get("content"), query),
                "metadata": result.get("metadata"),
                "relevance_score": final_score,
                "created_at": result.get("created_at").isoformat() if result.get("created_at") else None
            }
            
            processed.append(processed_result)
        
        # Sort by final relevance score
        processed.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return processed
    
    def _generate_search_vector(self, title: str, content: str) -> str:
        """Generate search vector for full-text search"""
        # Simplified vector generation - in production would use proper FTS
        combined_text = f"{title} {content}"
        return combined_text.lower()
    
    def _calculate_relevance_score(self, title: str, content: str, 
                                 metadata: Optional[Dict]) -> float:
        """Calculate document relevance score"""
        score = 0.0
        
        # Title relevance (higher weight)
        if title:
            score += len(title.split()) * 2
        
        # Content relevance
        if content:
            score += len(content.split()) * 0.5
        
        # Metadata relevance
        if metadata:
            if metadata.get('priority') == 'high':
                score += 100
            if metadata.get('verified'):
                score += 50
        
        return min(score, 1000)  # Cap at 1000
    
    def _calculate_query_relevance(self, result: Dict, query: str) -> float:
        """Calculate how well a result matches the query"""
        query_terms = query.lower().split()
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()
        
        score = 0.0
        
        for term in query_terms:
            if term in title:
                score += 10  # Title matches get higher weight
            if term in content:
                score += 1   # Content matches get lower weight
        
        return score
    
    def _generate_content_preview(self, content: str, query: str, 
                                max_length: int = 200) -> str:
        """Generate content preview highlighting query terms"""
        if not content:
            return ""
        
        # Find query terms in content
        query_terms = query.lower().split()
        content_lower = content.lower()
        
        # Find the best position to start preview
        best_position = 0
        best_score = 0
        
        for term in query_terms:
            pos = content_lower.find(term)
            if pos != -1:
                # Score based on position (earlier is better)
                score = len(content) - pos
                if score > best_score:
                    best_score = score
                    best_position = pos
        
        # Generate preview around best position
        start = max(0, best_position - max_length // 2)
        end = min(len(content), start + max_length)
        
        preview = content[start:end]
        
        # Add ellipsis if truncated
        if start > 0:
            preview = "..." + preview
        if end < len(content):
            preview = preview + "..."
        
        return preview
    
    async def _store_document_index(self, document_id: str, document_type: str,
                                  title: str, content: str, search_vector: str,
                                  relevance_score: float, metadata: Optional[Dict]):
        """Store document in search index"""
        try:
            session = get_session()
            
            # Check if document already exists
            existing = session.execute(
                text("SELECT id FROM search.search_indices WHERE document_id = :doc_id"),
                {"doc_id": document_id}
            ).fetchone()
            
            if existing:
                # Update existing
                session.execute(
                    text("""
                        UPDATE search.search_indices 
                        SET title = :title, content = :content, search_vector = :search_vector,
                            relevance_score = :relevance_score, metadata = :metadata,
                            updated_at = NOW(), indexed_at = NOW()
                        WHERE document_id = :document_id
                    """),
                    {
                        "title": title,
                        "content": content,
                        "search_vector": search_vector,
                        "relevance_score": relevance_score,
                        "metadata": json.dumps(metadata) if metadata else None,
                        "document_id": document_id
                    }
                )
            else:
                # Insert new
                session.execute(
                    text("""
                        INSERT INTO search.search_indices 
                        (id, document_id, document_type, title, content, search_vector,
                         relevance_score, metadata, created_at, indexed_at)
                        VALUES (:id, :document_id, :document_type, :title, :content,
                                :search_vector, :relevance_score, :metadata, NOW(), NOW())
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "document_id": document_id,
                        "document_type": document_type,
                        "title": title,
                        "content": content,
                        "search_vector": search_vector,
                        "relevance_score": relevance_score,
                        "metadata": json.dumps(metadata) if metadata else None
                    }
                )
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Failed to store document index: {e}")
            raise
    
    async def _log_search_query(self, query: str, filters: Optional[Dict], 
                               results_count: int, execution_time: float):
        """Log search query for analytics"""
        try:
            session = get_session()
            
            session.execute(
                text("""
                    INSERT INTO search.search_queries 
                    (id, query_text, filters, results_count, execution_time_ms, created_at)
                    VALUES (:id, :query_text, :filters, :results_count, :execution_time, NOW())
                """),
                {
                    "id": str(uuid.uuid4()),
                    "query_text": query,
                    "filters": json.dumps(filters) if filters else None,
                    "results_count": results_count,
                    "execution_time": int(execution_time)
                }
            )
            
            session.commit()
            
        except Exception as e:
            logger.warning(f"Failed to log search query: {e}")
    
    async def _fetch_suggestions(self, partial_query: str, suggestion_type: str) -> List[str]:
        """Fetch search suggestions from database"""
        try:
            session = get_session()
            
            if suggestion_type == "autocomplete":
                # Get autocomplete suggestions
                result = session.execute(
                    text("""
                        SELECT suggestion_text 
                        FROM search.search_suggestions 
                        WHERE suggestion_text ILIKE :partial_query 
                        AND suggestion_type = 'autocomplete'
                        ORDER BY frequency DESC, last_used DESC
                        LIMIT 10
                    """),
                    {"partial_query": f"{partial_query}%"}
                )
            elif suggestion_type == "popular":
                # Get popular suggestions
                result = session.execute(
                    text("""
                        SELECT suggestion_text 
                        FROM search.search_suggestions 
                        WHERE suggestion_type = 'popular'
                        ORDER BY frequency DESC
                        LIMIT 10
                    """)
                )
            else:
                # Get related suggestions
                result = session.execute(
                    text("""
                        SELECT suggestion_text 
                        FROM search.search_suggestions 
                        WHERE suggestion_type = 'related'
                        ORDER BY frequency DESC
                        LIMIT 10
                    """)
                )
            
            return [row[0] for row in result.fetchall()]
            
        except Exception as e:
            logger.error(f"Failed to fetch suggestions: {e}")
            return []
