"""
Insyte AI - Q&A Generator
Automatically generates relevant questions and answers from document content.
"""

import re
from typing import List, Dict, Tuple


class QAGenerator:
    """Generate questions and answers from document text."""
    
    def __init__(self):
        """Initialize the Q&A generator."""
        self.min_answer_length = 100  # Minimum characters for an answer
        self.max_answer_length = 500  # Maximum characters for an answer
    
    def generate_qa_pairs(self, text: str, filename: str, max_pairs: int = 10) -> List[Dict[str, str]]:
        """
        Generate Q&A pairs from document text.
        
        Args:
            text: Document content
            filename: Source filename
            max_pairs: Maximum number of Q&A pairs to generate
            
        Returns:
            List of dictionaries with 'question' and 'answer' keys
        """
        qa_pairs = []
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return qa_pairs
        
        # Extract document metadata questions
        qa_pairs.extend(self._generate_metadata_questions(text, filename))
        
        # Generate topic-based questions
        qa_pairs.extend(self._generate_topic_questions(text, sentences))
        
        # Generate definition questions
        qa_pairs.extend(self._generate_definition_questions(text, sentences))
        
        # Generate method/process questions
        qa_pairs.extend(self._generate_method_questions(text, sentences))
        
        # Limit to max_pairs
        return qa_pairs[:max_pairs]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        return sentences
    
    def _generate_metadata_questions(self, text: str, filename: str) -> List[Dict[str, str]]:
        """Generate questions about the document itself."""
        qa_pairs = []
        
        # Extract title from first line or filename
        first_line = text.split('\n')[0][:100].strip()
        
        # Question 1: What is this document about?
        intro = self._extract_introduction(text)
        if intro:
            qa_pairs.append({
                'question': f"What is this document about?",
                'answer': intro,
                'source': filename
            })
        
        # Question 2: Document title/name
        if len(first_line) > 10:
            qa_pairs.append({
                'question': f"What is the title or main topic?",
                'answer': first_line,
                'source': filename
            })
        
        return qa_pairs
    
    def _generate_topic_questions(self, text: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Generate questions about main topics."""
        qa_pairs = []
        
        # Look for topic indicators
        topic_keywords = ['about', 'focuses on', 'discusses', 'covers', 'examines', 'explores']
        
        for sentence in sentences[:20]:  # Check first 20 sentences
            for keyword in topic_keywords:
                if keyword in sentence.lower():
                    # Extract the topic
                    answer = self._extract_context(sentences, sentence)
                    if len(answer) >= self.min_answer_length:
                        qa_pairs.append({
                            'question': "What are the main topics covered?",
                            'answer': answer,
                            'source': 'document'
                        })
                        return qa_pairs  # One topic question is enough
        
        return qa_pairs
    
    def _generate_definition_questions(self, text: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Generate 'What is X?' style questions."""
        qa_pairs = []
        
        # Look for definitions
        definition_patterns = [
            r'(\w+(?:\s+\w+){0,3})\s+is\s+(?:a|an|the)\s+(.{20,200})',
            r'(\w+(?:\s+\w+){0,3})\s+refers to\s+(.{20,200})',
            r'(\w+(?:\s+\w+){0,3})\s+means\s+(.{20,200})'
        ]
        
        for sentence in sentences[:30]:
            for pattern in definition_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()
                    
                    # Skip if term is too common or short
                    if len(term) < 5 or term.lower() in ['this', 'that', 'these', 'those', 'it']:
                        continue
                    
                    answer = self._extract_context(sentences, sentence)
                    if len(answer) >= self.min_answer_length:
                        qa_pairs.append({
                            'question': f"What is {term}?",
                            'answer': answer,
                            'source': 'document'
                        })
                        
                        if len(qa_pairs) >= 3:  # Max 3 definition questions
                            return qa_pairs
        
        return qa_pairs
    
    def _generate_method_questions(self, text: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Generate 'How does X work?' style questions."""
        qa_pairs = []
        
        # Look for process descriptions
        method_keywords = ['how', 'process', 'method', 'approach', 'technique', 'system', 'works']
        
        for sentence in sentences[:30]:
            if any(keyword in sentence.lower() for keyword in method_keywords):
                answer = self._extract_context(sentences, sentence, context_size=3)
                if len(answer) >= self.min_answer_length:
                    # Create a generic "how" question
                    qa_pairs.append({
                        'question': "How does the system/process work?",
                        'answer': answer,
                        'source': 'document'
                    })
                    return qa_pairs  # One method question is enough
        
        return qa_pairs
    
    def _extract_introduction(self, text: str) -> str:
        """Extract introduction/abstract from document."""
        # Look for abstract section
        abstract_match = re.search(r'abstract[:\s]+(.{100,800})', text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            return abstract_match.group(1).strip()[:self.max_answer_length]
        
        # Look for introduction
        intro_match = re.search(r'introduction[:\s]+(.{100,800})', text, re.IGNORECASE | re.DOTALL)
        if intro_match:
            return intro_match.group(1).strip()[:self.max_answer_length]
        
        # Use first few paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
        if paragraphs:
            intro = ' '.join(paragraphs[:2])
            return intro[:self.max_answer_length]
        
        return ""
    
    def _extract_context(self, sentences: List[str], target_sentence: str, context_size: int = 2) -> str:
        """Extract surrounding context for a sentence."""
        try:
            idx = sentences.index(target_sentence)
            start = max(0, idx - context_size)
            end = min(len(sentences), idx + context_size + 1)
            context = ' '.join(sentences[start:end])
            return context[:self.max_answer_length]
        except ValueError:
            return target_sentence[:self.max_answer_length]
    
    def extract_key_facts(self, text: str, max_facts: int = 5) -> List[str]:
        """Extract key facts or statements from text."""
        facts = []
        sentences = self._split_into_sentences(text)
        
        # Look for sentences with key indicators
        fact_indicators = ['important', 'key', 'critical', 'essential', 'main', 
                          'significant', 'notable', 'primary', 'major']
        
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in fact_indicators):
                if len(sentence) > 30:
                    facts.append(sentence.strip())
            
            if len(facts) >= max_facts:
                break
        
        # If no facts found, use first few meaningful sentences
        if not facts:
            facts = [s for s in sentences[:max_facts] if len(s) > 50]
        
        return facts[:max_facts]
