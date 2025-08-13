"""
Search Service API - Complete Implementation
FastAPI application for document indexing and search functionality.
"""

from fastapi import FastAPI, Depends, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
import uuid
from datetime import datetime

from .models import SearchIndex, SearchQuery, SearchSuggestion
from .database import get_session as get_db_session
from .search_engine import SearchEngine
from .service_client import ServiceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Search Service API",
    description="OpenPolicy Platform - Document Search and Indexing Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
search_engine = SearchEngine()
service_client = ServiceClient()

# Pydantic models for API requests/responses
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DocumentIndexRequest(BaseModel):
    document_type: str = Field(..., description="Type of document")
    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[List[str]] = Field(None, description="Document tags")
    category: Optional[str] = Field(None, description="Document category")
    language: str = Field("en", description="Document language")
    priority: int = Field(1, description="Search priority (1-10)")

class DocumentIndexResponse(BaseModel):
    id: str
    document_type: str
    document_id: str
    title: str
    content: str
    metadata: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    category: Optional[str]
    language: str
    priority: int
    indexed_at: datetime
    search_vector: str

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    document_types: Optional[List[str]] = Field(None, description="Filter by document types")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    language: Optional[str] = Field(None, description="Filter by language")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    sort_by: str = Field("relevance", description="Sort by: relevance, date, title")
    sort_order: str = Field("desc", description="Sort order: asc, desc")

class SearchResult(BaseModel):
    document_id: str
    document_type: str
    title: str
    content_preview: str
    metadata: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    category: Optional[str]
    language: str
    relevance_score: float
    indexed_at: datetime
    url: Optional[str]

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResult]
    suggestions: List[str]
    search_time_ms: float
    facets: Dict[str, Any]

class SearchSuggestionRequest(BaseModel):
    query: str = Field(..., description="Partial search query")
    limit: int = Field(10, ge=1, le=50, description="Maximum suggestions to return")

class SearchSuggestionResponse(BaseModel):
    suggestions: List[str]
    query: str
    total_found: int

class BulkIndexRequest(BaseModel):
    documents: List[DocumentIndexRequest] = Field(..., description="Documents to index")

class BulkIndexResponse(BaseModel):
    total_documents: int
    successful_indexes: int
    failed_indexes: int
    results: List[Dict[str, Any]]

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, description="Document title")
    content: Optional[str] = Field(None, description="Document content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[List[str]] = Field(None, description="Document tags")
    category: Optional[str] = Field(None, description="Document category")
    priority: Optional[int] = Field(None, description="Search priority")

class IndexStatsResponse(BaseModel):
    total_documents: int
    documents_by_type: Dict[str, int]
    documents_by_category: Dict[str, int]
    documents_by_language: Dict[str, int]
    total_size_bytes: int
    last_indexed: Optional[datetime]
    index_health: str

# Dependency functions
async def get_current_user():
    """Get current authenticated user (placeholder for now)."""
    # TODO: Implement actual JWT validation
    return {"id": "test-user", "username": "testuser", "role": "admin"}

def get_db_session():
    """Get database session."""
    return next(get_db_session())

# Health and readiness endpoints
@app.get("/healthz", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db = get_db_session()
        db.execute("SELECT 1")
        
        # Check search engine
        engine_health = search_engine.health_check()
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "search-service",
            "version": "1.0.0",
            "database": "connected",
            "search_engine": engine_health
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/readyz", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Check database connection
        db = get_db_session()
        db.execute("SELECT 1")
        
        # Check if search engine is ready
        if not search_engine.is_ready():
            raise HTTPException(status_code=503, detail="Search engine not ready")
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "service": "search-service"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

# Document indexing endpoints
@app.post("/index", response_model=DocumentIndexResponse, status_code=201, tags=["Document Indexing"])
async def index_document(
    request: DocumentIndexRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Index a single document."""
    try:
        # Check if document already exists
        existing = db_session.query(SearchIndex).filter(
            SearchIndex.document_id == request.document_id,
            SearchIndex.document_type == request.document_type
        ).first()
        
        if existing:
            # Update existing document
            existing.title = request.title
            existing.content = request.content
            existing.metadata = request.metadata or {}
            existing.tags = request.tags or []
            existing.category = request.category
            existing.language = request.language
            existing.priority = request.priority
            existing.updated_at = datetime.now()
            
            # Update search vector
            search_vector = search_engine.generate_search_vector(
                request.title, request.content, request.tags or []
            )
            existing.search_vector = search_vector
            
            db_session.commit()
            db_session.refresh(existing)
            
            logger.info(f"Document updated: {existing.id}")
        else:
            # Create new document
            search_vector = search_engine.generate_search_vector(
                request.title, request.content, request.tags or []
            )
            
            document = SearchIndex(
                id=str(uuid.uuid4()),
                document_type=request.document_type,
                document_id=request.document_id,
                title=request.title,
                content=request.content,
                metadata=request.metadata or {},
                tags=request.tags or [],
                category=request.category,
                language=request.language,
                priority=request.priority,
                search_vector=search_vector,
                indexed_at=datetime.now(),
                updated_at=datetime.now(),
                indexed_by=current_user["id"]
            )
            
            db_session.add(document)
            db_session.commit()
            db_session.refresh(document)
            
            logger.info(f"Document indexed: {document.id}")
        
        # Record metrics
        await service_client.record_metric(
            "search_documents_indexed_total", 1,
            {"document_type": request.document_type, "category": request.category}
        )
        
        return DocumentIndexResponse(
            id=document.id if 'document' in locals() else existing.id,
            document_type=request.document_type,
            document_id=request.document_id,
            title=request.title,
            content=request.content,
            metadata=request.metadata,
            tags=request.tags,
            category=request.category,
            language=request.language,
            priority=request.priority,
            indexed_at=datetime.now(),
            search_vector=search_vector
        )
        
    except Exception as e:
        logger.error(f"Failed to index document: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to index document")

@app.post("/index/bulk", response_model=BulkIndexResponse, tags=["Document Indexing"])
async def bulk_index_documents(
    request: BulkIndexRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Index multiple documents in bulk."""
    try:
        results = []
        successful_indexes = 0
        failed_indexes = 0
        
        for doc_request in request.documents:
            try:
                # Check if document already exists
                existing = db_session.query(SearchIndex).filter(
                    SearchIndex.document_id == doc_request.document_id,
                    SearchIndex.document_type == doc_request.document_type
                ).first()
                
                if existing:
                    # Update existing document
                    existing.title = doc_request.title
                    existing.content = doc_request.content
                    existing.metadata = doc_request.metadata or {}
                    existing.tags = doc_request.tags or []
                    existing.category = doc_request.category
                    existing.language = doc_request.language
                    existing.priority = doc_request.priority
                    existing.updated_at = datetime.now()
                    
                    # Update search vector
                    search_vector = search_engine.generate_search_vector(
                        doc_request.title, doc_request.content, doc_request.tags or []
                    )
                    existing.search_vector = search_vector
                    
                    results.append({
                        "document_id": doc_request.document_id,
                        "status": "updated",
                        "id": existing.id
                    })
                    
                else:
                    # Create new document
                    search_vector = search_engine.generate_search_vector(
                        doc_request.title, doc_request.content, doc_request.tags or []
                    )
                    
                    document = SearchIndex(
                        id=str(uuid.uuid4()),
                        document_type=doc_request.document_type,
                        document_id=doc_request.document_id,
                        title=doc_request.title,
                        content=doc_request.content,
                        metadata=doc_request.metadata or {},
                        tags=doc_request.tags or [],
                        category=doc_request.category,
                        language=doc_request.language,
                        priority=doc_request.priority,
                        search_vector=search_vector,
                        indexed_at=datetime.now(),
                        updated_at=datetime.now(),
                        indexed_by=current_user["id"]
                    )
                    
                    db_session.add(document)
                    
                    results.append({
                        "document_id": doc_request.document_id,
                        "status": "created",
                        "id": document.id
                    })
                
                successful_indexes += 1
                
            except Exception as e:
                logger.error(f"Failed to index document {doc_request.document_id}: {e}")
                results.append({
                    "document_id": doc_request.document_id,
                    "status": "failed",
                    "error": str(e)
                })
                failed_indexes += 1
        
        db_session.commit()
        
        # Record metrics
        await service_client.record_metric(
            "search_bulk_indexes_total", 1,
            {"total_documents": len(request.documents), "successful": successful_indexes}
        )
        
        return BulkIndexResponse(
            total_documents=len(request.documents),
            successful_indexes=successful_indexes,
            failed_indexes=failed_indexes,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Failed to bulk index documents: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to bulk index documents")

@app.put("/index/{document_id}", response_model=DocumentIndexResponse, tags=["Document Indexing"])
async def update_document(
    document_id: str = Path(..., description="Document ID"),
    document_type: str = Query(..., description="Document type"),
    request: DocumentUpdateRequest = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Update an existing indexed document."""
    try:
        document = db_session.query(SearchIndex).filter(
            SearchIndex.document_id == document_id,
            SearchIndex.document_type == document_type
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update fields if provided
        if request.title is not None:
            document.title = request.title
        if request.content is not None:
            document.content = request.content
        if request.metadata is not None:
            document.metadata = request.metadata
        if request.tags is not None:
            document.tags = request.tags
        if request.category is not None:
            document.category = request.category
        if request.priority is not None:
            document.priority = request.priority
        
        document.updated_at = datetime.now()
        document.updated_by = current_user["id"]
        
        # Update search vector
        search_vector = search_engine.generate_search_vector(
            document.title, document.content, document.tags or []
        )
        document.search_vector = search_vector
        
        db_session.commit()
        db_session.refresh(document)
        
        logger.info(f"Document updated: {document.id}")
        
        return DocumentIndexResponse(
            id=document.id,
            document_type=document.document_type,
            document_id=document.document_id,
            title=document.title,
            content=document.content,
            metadata=document.metadata,
            tags=document.tags,
            category=document.category,
            language=document.language,
            priority=document.priority,
            indexed_at=document.indexed_at,
            search_vector=document.search_vector
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update document {document_id}: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update document")

@app.delete("/index/{document_id}", status_code=204, tags=["Document Indexing"])
async def delete_document(
    document_id: str = Path(..., description="Document ID"),
    document_type: str = Query(..., description="Document type"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Delete an indexed document."""
    try:
        document = db_session.query(SearchIndex).filter(
            SearchIndex.document_id == document_id,
            SearchIndex.document_type == document_type
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        db_session.delete(document)
        db_session.commit()
        
        logger.info(f"Document deleted: {document_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete document")

# Search endpoints
@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_documents(
    request: SearchRequest,
    db_session: Session = Depends(get_db_session)
):
    """Search for documents."""
    try:
        start_time = datetime.now()
        
        # Perform search
        search_results = search_engine.search_documents(
            query=request.query,
            document_types=request.document_types,
            categories=request.categories,
            tags=request.tags,
            language=request.language,
            limit=request.limit,
            offset=request.offset,
            sort_by=request.sort_by,
            sort_order=request.sort_order,
            db_session=db_session
        )
        
        # Get search suggestions
        suggestions = search_engine.get_search_suggestions(
            request.query, limit=5, db_session=db_session
        )
        
        # Calculate facets
        facets = search_engine.calculate_search_facets(
            search_results["results"], db_session
        )
        
        # Record search query
        search_query = SearchQuery(
            id=str(uuid.uuid4()),
            query=request.query,
            filters=request.dict(),
            results_count=len(search_results["results"]),
            total_results=search_results["total"],
            search_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            searched_at=datetime.now()
        )
        
        db_session.add(search_query)
        db_session.commit()
        
        # Record metrics
        await service_client.record_metric(
            "search_queries_total", 1,
            {"query_length": len(request.query), "results_count": len(search_results["results"])}
        )
        
        # Convert results to response format
        results = []
        for doc in search_results["results"]:
            results.append(SearchResult(
                document_id=doc["document_id"],
                document_type=doc["document_type"],
                title=doc["title"],
                content_preview=doc["content_preview"],
                metadata=doc.get("metadata"),
                tags=doc.get("tags"),
                category=doc.get("category"),
                language=doc.get("language", "en"),
                relevance_score=doc["relevance_score"],
                indexed_at=doc["indexed_at"],
                url=doc.get("url")
            ))
        
        search_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return SearchResponse(
            query=request.query,
            total_results=search_results["total"],
            results=results,
            suggestions=[s["suggestion"] for s in suggestions],
            search_time_ms=search_time_ms,
            facets=facets
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.get("/suggest", response_model=SearchSuggestionResponse, tags=["Search"])
async def get_search_suggestions(
    query: str = Query(..., description="Partial search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum suggestions to return"),
    db_session: Session = Depends(get_db_session)
):
    """Get search suggestions for autocomplete."""
    try:
        suggestions = search_engine.get_search_suggestions(
            query, limit, db_session
        )
        
        return SearchSuggestionResponse(
            suggestions=[s["suggestion"] for s in suggestions],
            query=query,
            total_found=len(suggestions)
        )
        
    except Exception as e:
        logger.error(f"Failed to get search suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search suggestions")

@app.get("/documents/{document_id}", response_model=DocumentIndexResponse, tags=["Document Management"])
async def get_document(
    document_id: str = Path(..., description="Document ID"),
    document_type: str = Query(..., description="Document type"),
    db_session: Session = Depends(get_db_session)
):
    """Get a specific indexed document."""
    try:
        document = db_session.query(SearchIndex).filter(
            SearchIndex.document_id == document_id,
            SearchIndex.document_type == document_type
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentIndexResponse(
            id=document.id,
            document_type=document.document_type,
            document_id=document.document_id,
            title=document.title,
            content=document.content,
            metadata=document.metadata,
            tags=document.tags,
            category=document.category,
            language=document.language,
            priority=document.priority,
            indexed_at=document.indexed_at,
            search_vector=document.search_vector
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document")

@app.get("/documents", response_model=List[DocumentIndexResponse], tags=["Document Management"])
async def list_documents(
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by language"),
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of documents to return"),
    db_session: Session = Depends(get_db_session)
):
    """List indexed documents with optional filtering."""
    try:
        query = db_session.query(SearchIndex)
        
        if document_type:
            query = query.filter(SearchIndex.document_type == document_type)
        if category:
            query = query.filter(SearchIndex.category == category)
        if language:
            query = query.filter(SearchIndex.language == language)
        
        documents = query.offset(skip).limit(limit).all()
        
        return [
            DocumentIndexResponse(
                id=doc.id,
                document_type=doc.document_type,
                document_id=doc.document_id,
                title=doc.title,
                content=doc.content,
                metadata=doc.metadata,
                tags=doc.tags,
                category=doc.category,
                language=doc.language,
                priority=doc.priority,
                indexed_at=doc.indexed_at,
                search_vector=doc.search_vector
            )
            for doc in documents
        ]
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")

# Statistics and analytics endpoints
@app.get("/stats", response_model=IndexStatsResponse, tags=["Analytics"])
async def get_index_statistics(
    db_session: Session = Depends(get_db_session)
):
    """Get search index statistics."""
    try:
        total_documents = db_session.query(SearchIndex).count()
        
        # Documents by type
        docs_by_type = db_session.query(
            SearchIndex.document_type,
            db_session.query(SearchIndex).filter(
                SearchIndex.document_type == SearchIndex.document_type
            ).count().label('count')
        ).distinct().all()
        
        documents_by_type = {row.document_type: row.count for row in docs_by_type}
        
        # Documents by category
        docs_by_category = db_session.query(
            SearchIndex.category,
            db_session.query(SearchIndex).filter(
                SearchIndex.category == SearchIndex.category
            ).count().label('count')
        ).filter(SearchIndex.category.isnot(None)).distinct().all()
        
        documents_by_category = {row.category: row.count for row in docs_by_category}
        
        # Documents by language
        docs_by_language = db_session.query(
            SearchIndex.language,
            db_session.query(SearchIndex).filter(
                SearchIndex.language == SearchIndex.language
            ).count().label('count')
        ).distinct().all()
        
        documents_by_language = {row.language: row.count for row in docs_by_language}
        
        # Total size estimation
        total_size_bytes = sum(
            len(str(doc.content)) + len(str(doc.metadata)) + len(str(doc.tags))
            for doc in db_session.query(SearchIndex).all()
        )
        
        # Last indexed document
        last_indexed = db_session.query(SearchIndex).order_by(
            SearchIndex.indexed_at.desc()
        ).first()
        
        last_indexed_time = last_indexed.indexed_at if last_indexed else None
        
        # Index health
        index_health = "healthy"
        if total_documents == 0:
            index_health = "empty"
        elif last_indexed_time and (datetime.now() - last_indexed_time).days > 7:
            index_health = "stale"
        
        return IndexStatsResponse(
            total_documents=total_documents,
            documents_by_type=documents_by_type,
            documents_by_category=documents_by_category,
            documents_by_language=documents_by_language,
            total_size_bytes=total_size_bytes,
            last_indexed=last_indexed_time,
            index_health=index_health
        )
        
    except Exception as e:
        logger.error(f"Failed to get index statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get index statistics")

@app.get("/search/history", tags=["Analytics"])
async def get_search_history(
    limit: int = Query(100, ge=1, le=1000, description="Maximum queries to return"),
    db_session: Session = Depends(get_db_session)
):
    """Get recent search query history."""
    try:
        queries = db_session.query(SearchQuery).order_by(
            SearchQuery.searched_at.desc()
        ).limit(limit).all()
        
        return {
            "queries": [
                {
                    "id": query.id,
                    "query": query.query,
                    "filters": query.filters,
                    "results_count": query.results_count,
                    "total_results": query.total_results,
                    "search_time_ms": query.search_time_ms,
                    "searched_at": query.searched_at.isoformat()
                }
                for query in queries
            ],
            "total_queries": len(queries)
        }
        
    except Exception as e:
        logger.error(f"Failed to get search history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search history")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
