"""
Advanced Query Processing Module
Handles query understanding, expansion, and intent classification
"""

import spacy
from transformers import pipeline
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self):
        """Initialize query processor with NLP models"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        try:
            self.spell_checker = pipeline(
                "text2text-generation", 
                model="oliverguhr/spelling-correction-english-base"
            )
        except Exception as e:
            logger.warning(f"Spell checker model not available: {e}")
            self.spell_checker = None
        
        try:
            self.ner = pipeline("ner", aggregation_strategy="simple")
        except Exception as e:
            logger.warning(f"NER model not available: {e}")
            self.ner = None
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Comprehensive query processing"""
        processed = {
            'original': query,
            'corrected': self.correct_spelling(query),
            'entities': self.extract_entities(query),
            'intent': self.classify_intent(query),
            'expanded': self.expand_query(query),
            'keywords': self.extract_keywords(query),
            'complexity': self.assess_complexity(query)
        }
        return processed
    
    def correct_spelling(self, query: str) -> str:
        """Spell correction for user queries"""
        if not self.spell_checker:
            return query
        
        try:
            result = self.spell_checker(query, max_length=64)
            return result[0]['generated_text']
        except Exception as e:
            logger.warning(f"Spell correction failed: {e}")
            return query
    
    def extract_entities(self, query: str) -> List[Dict[str, Any]]:
        """Named Entity Recognition"""
        if not self.ner:
            return []
        
        try:
            entities = self.ner(query)
            return [
                {
                    'text': ent['word'], 
                    'type': ent['entity'], 
                    'score': ent['score'],
                    'start': ent['start'],
                    'end': ent['end']
                } 
                for ent in entities
            ]
        except Exception as e:
            logger.warning(f"NER failed: {e}")
            return []
    
    def classify_intent(self, query: str) -> str:
        """Classify query intent using rule-based approach"""
        if not self.nlp:
            return "general_inquiry"
        
        doc = self.nlp(query)
        
        # Question words
        question_words = {'what', 'how', 'why', 'when', 'where', 'who', 'which'}
        if any(token.text.lower() in question_words for token in doc):
            return "factual_question"
        
        # Comparison indicators
        comparison_words = {'compare', 'difference', 'versus', 'vs', 'better', 'worse'}
        if any(token.lemma_.lower() in comparison_words for token in doc):
            return "comparison"
        
        # Summarization indicators
        summary_words = {'summarize', 'summary', 'overview', 'brief', 'outline'}
        if any(token.lemma_.lower() in summary_words for token in doc):
            return "summarization"
        
        # Analysis indicators
        analysis_words = {'analyze', 'analysis', 'explain', 'describe', 'discuss'}
        if any(token.lemma_.lower() in analysis_words for token in doc):
            return "analysis"
        
        # Definition indicators
        definition_words = {'define', 'definition', 'meaning', 'what is'}
        if any(token.lemma_.lower() in definition_words for token in doc):
            return "definition"
        
        return "general_inquiry"
    
    def expand_query(self, query: str) -> List[str]:
        """Query expansion using synonyms and related terms"""
        if not self.nlp:
            return [query]
        
        doc = self.nlp(query)
        expanded_terms = []
        
        for token in doc:
            if token.pos_ in ['NOUN', 'ADJ'] and not token.is_stop:
                synonyms = self.get_synonyms(token.text)
                expanded_terms.extend(synonyms[:2])  # Limit to 2 synonyms per term
        
        expanded_queries = [query]
        if expanded_terms:
            expanded_query = query + " " + " ".join(expanded_terms[:3])
            expanded_queries.append(expanded_query)
        
        return expanded_queries
    
    def get_synonyms(self, word: str) -> List[str]:
        """Get synonyms for query expansion"""
        synonym_map = {
            'price': ['cost', 'fee', 'charge', 'rate'],
            'benefit': ['advantage', 'pro', 'upside', 'merit'],
            'problem': ['issue', 'challenge', 'difficulty', 'trouble'],
            'solution': ['answer', 'fix', 'resolution', 'remedy'],
            'company': ['organization', 'business', 'firm', 'corporation'],
            'customer': ['client', 'user', 'buyer', 'consumer'],
            'product': ['item', 'goods', 'service', 'offering'],
            'technology': ['tech', 'innovation', 'system', 'platform'],
            'data': ['information', 'facts', 'statistics', 'metrics'],
            'performance': ['efficiency', 'effectiveness', 'results', 'output']
        }
        return synonym_map.get(word.lower(), [])
    
    def extract_keywords(self, query: str) -> List[Dict[str, Any]]:
        """Extract key terms from query with importance scoring"""
        if not self.nlp:
            return []
        
        doc = self.nlp(query)
        keywords = []
        
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                token.is_alpha and 
                len(token.text) > 2):
                
                if token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB']:
                    importance = self.calculate_importance(token)
                    keywords.append({
                        'text': token.lemma_.lower(),
                        'original': token.text,
                        'pos': token.pos_,
                        'importance': importance
                    })
        
        return sorted(keywords, key=lambda x: x['importance'], reverse=True)[:5]
    
    def calculate_importance(self, token) -> float:
        """Calculate importance score for keywords"""
        pos_weights = {
            'PROPN': 1.0,  # Proper nouns (most important)
            'NOUN': 0.8,   # Nouns
            'VERB': 0.7,   # Verbs
            'ADJ': 0.6,    # Adjectives
            'ADV': 0.4     # Adverbs
        }
        
        base_score = pos_weights.get(token.pos_, 0.3)
        
        # Boost score for longer words (likely more specific)
        length_bonus = min(len(token.text) / 10, 0.2)
        
        # Boost score for capitalized words (likely proper nouns)
        case_bonus = 0.1 if token.text[0].isupper() else 0
        
        return base_score + length_bonus + case_bonus
    
    def assess_complexity(self, query: str) -> Dict[str, Any]:
        """Assess query complexity"""
        if not self.nlp:
            return {'level': 'medium', 'score': 0.5}
        
        doc = self.nlp(query)
        
        # Factors that increase complexity
        complexity_factors = {
            'length': len(query.split()) / 20,  # Normalize by expected length
            'entities': len(self.extract_entities(query)) / 5,
            'conjunctions': sum(1 for token in doc if token.text.lower() in ['and', 'or', 'but', 'however']),
            'questions': sum(1 for token in doc if token.text == '?'),
            'negations': sum(1 for token in doc if token.lemma_ in ['not', 'no', 'never', 'none'])
        }
        
        complexity_score = sum(complexity_factors.values()) / len(complexity_factors)
        
        if complexity_score < 0.3:
            level = 'simple'
        elif complexity_score < 0.7:
            level = 'medium'
        else:
            level = 'complex'
        
        return {
            'level': level,
            'score': complexity_score,
            'factors': complexity_factors
        }
    
    def get_query_suggestions(self, query: str) -> List[str]:
        """Generate query suggestions for better results"""
        suggestions = []
        
        # Add question variations
        if not query.endswith('?'):
            suggestions.append(query + '?')
        
        # Add "what is" variations for definitions
        if not query.lower().startswith(('what is', 'what are')):
            suggestions.append(f"What is {query.lower()}")
        
        # Add "how to" variations for instructions
        if not query.lower().startswith(('how to', 'how do')):
            suggestions.append(f"How to {query.lower()}")
        
        return suggestions[:3]  # Limit to 3 suggestions
