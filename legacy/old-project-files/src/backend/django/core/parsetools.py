# coding: utf-8
"""
Parsing tools for parliamentary data.
This module provides utilities for parsing and normalizing parliamentary text and data.
"""

import re
import unicodedata
from typing import Optional

def normalizeName(name: str) -> str:
    """
    Normalize a politician's name for consistent comparison.
    
    Args:
        name: The name to normalize
        
    Returns:
        Normalized name string
    """
    if not name:
        return ""
    
    # Convert to lowercase and strip whitespace
    name = name.lower().strip()
    
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name)
    
    # Remove common titles and prefixes
    titles = ['hon.', 'honourable', 'mr.', 'mr', 'mrs.', 'mrs', 'ms.', 'ms', 'dr.', 'dr']
    for title in titles:
        if name.startswith(title + ' '):
            name = name[len(title):].strip()
    
    # Remove common suffixes
    suffixes = ['mp', 'm.p.', 'pc', 'p.c.', 'qc', 'q.c.']
    for suffix in suffixes:
        if name.endswith(' ' + suffix):
            name = name[:-len(suffix)].strip()
    
    return name

def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    
    Args:
        text: The text to convert
        
    Returns:
        URL-friendly slug string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFD', text)
    
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r'[^a-z0-9\-]', '', text)
    
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    
    # Remove leading and trailing hyphens
    text = text.strip('-')
    
    return text

def extractRidingName(text: str) -> Optional[str]:
    """
    Extract riding name from text.
    
    Args:
        text: Text that may contain a riding name
        
    Returns:
        Extracted riding name or None
    """
    if not text:
        return None
    
    # Common riding patterns
    patterns = [
        r'riding of ([^,]+)',
        r'constituency of ([^,]+)',
        r'([^,]+) riding',
        r'([^,]+) constituency'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def cleanText(text: str) -> str:
    """
    Clean parliamentary text by removing common artifacts.
    
    Args:
        text: Raw parliamentary text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common parliamentary artifacts
    text = re.sub(r'\[.*?\]', '', text)  # Remove square brackets
    text = re.sub(r'\(.*?\)', '', text)  # Remove parentheses
    
    # Clean up punctuation
    text = re.sub(r'\.+', '.', text)  # Multiple periods to single
    text = re.sub(r',+', ',', text)   # Multiple commas to single
    
    return text.strip()

def extractPartyName(text: str) -> Optional[str]:
    """
    Extract party name from text.
    
    Args:
        text: Text that may contain a party name
        
    Returns:
        Extracted party name or None
    """
    if not text:
        return None
    
    # Common party patterns
    patterns = [
        r'liberal party',
        r'conservative party',
        r'new democratic party',
        r'ndp',
        r'bloc québécois',
        r'green party',
        r'peoples party',
        r'independent'
    ]
    
    text_lower = text.lower()
    for pattern in patterns:
        if pattern in text_lower:
            return pattern.title()
    
    return None