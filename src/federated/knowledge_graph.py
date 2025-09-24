"""
Cross-Node Knowledge Graph
Knowledge graph that spans multiple federated nodes for entity relationships.
"""

from typing import Dict, List, Optional, Any, Tuple
import networkx as nx
import json
from datetime import datetime
from collections import defaultdict
import hashlib
import re

class FederatedKnowledgeGraph:
    """Knowledge graph that spans multiple federated nodes"""
    
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self.graph = nx.Graph()
        self.entity_index = {}
        self.relationship_index = {}
        self.node_contributions = defaultdict(set)
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
    
    async def build_cross_node_knowledge_graph(self, entities: List[str]) -> Dict:
        """Build knowledge graph by querying multiple nodes for entity information"""
        
        print(f"🔗 Building knowledge graph for entities: {entities}")
        
        cross_node_graph = {
            'entities': {},
            'relationships': [],
            'sources': set(),
            'graph_stats': {}
        }
        
        for entity in entities:
            # Query all nodes for information about this entity
            entity_results = await self.query_entity_across_nodes(entity)
            
            # Merge entity information from different nodes
            merged_entity = self.merge_entity_information(entity, entity_results)
            cross_node_graph['entities'][entity] = merged_entity
            
            # Extract relationships
            relationships = self.extract_cross_node_relationships(entity_results)
            cross_node_graph['relationships'].extend(relationships)
            
            # Track sources
            for result in entity_results:
                if result['success']:
                    cross_node_graph['sources'].add(result['node_id'])
        
        # Build networkx graph
        self.build_networkx_graph(cross_node_graph)
        
        # Calculate graph statistics
        cross_node_graph['graph_stats'] = self.calculate_graph_statistics()
        
        return cross_node_graph
    
    async def query_entity_across_nodes(self, entity: str) -> Dict:
        """Query information about an entity across all federated nodes"""
        
        # Create entity-centric query
        query = f"Information about {entity} including properties, relationships, and context"
        
        if self.orchestrator:
            node_results = await self.orchestrator.execute_federated_search(
                query, 
                list(self.orchestrator.nodes.values()),
                {'domain': 'knowledge_graph', 'entity_query': True}
            )
            return node_results
        else:
            # Mock results for demonstration
            return {
                'node1': {
                    'success': True,
                    'results': {
                        'documents': [
                            {
                                'content': f'{entity} is a key concept in the domain with important properties.',
                                'metadata': {'domain': 'general', 'type': 'definition'}
                            }
                        ]
                    }
                }
            }
    
    def merge_entity_information(self, entity: str, node_results: Dict) -> Dict:
        """Merge entity information from multiple nodes"""
        
        merged_info = {
            'name': entity,
            'properties': {},
            'descriptions': [],
            'sources': [],
            'confidence': 0.0,
            'node_contributions': {}
        }
        
        property_votes = {}
        descriptions = []
        node_contributions = {}
        
        for node_id, result in node_results.items():
            if result['success']:
                node_contributions[node_id] = {
                    'result_count': len(result['results'].get('documents', [])),
                    'confidence': result.get('confidence', 0.5)
                }
                
                for doc in result['results']['documents']:
                    # Extract entity properties using pattern matching
                    properties = self.extract_entity_properties(doc['content'], entity)
                    descriptions.append(self.extract_entity_description(doc['content'], entity))
                    
                    # Vote on properties
                    for prop, value in properties.items():
                        if prop not in property_votes:
                            property_votes[prop] = {}
                        if value not in property_votes[prop]:
                            property_votes[prop][value] = 0
                        property_votes[prop][value] += 1
        
        # Resolve property conflicts by voting
        for prop, votes in property_votes.items():
            if votes:
                best_value = max(votes.items(), key=lambda x: x[1])
                merged_info['properties'][prop] = {
                    'value': best_value[0],
                    'confidence': best_value[1] / len(node_results),
                    'sources': list(votes.keys())
                }
        
        merged_info['descriptions'] = list(set(descriptions))
        merged_info['sources'] = list(node_results.keys())
        merged_info['confidence'] = len([r for r in node_results.values() if r['success']]) / len(node_results)
        merged_info['node_contributions'] = node_contributions
        
        return merged_info
    
    def extract_entity_properties(self, content: str, entity: str) -> Dict[str, str]:
        """Extract properties of an entity from content"""
        properties = {}
        
        # Simple pattern matching for entity properties
        patterns = {
            'type': rf'{entity}\s+is\s+(?:a|an|the)?\s*([^.]*)',
            'location': rf'{entity}\s+(?:is\s+)?(?:in|at|located\s+in)\s+([^.]*)',
            'purpose': rf'{entity}\s+(?:is\s+)?(?:used\s+for|purpose\s+is)\s+([^.]*)',
            'status': rf'{entity}\s+(?:is\s+)?(?:active|inactive|pending|completed)',
            'value': rf'{entity}\s+(?:has\s+)?(?:value|worth|cost)\s+([^.]*)'
        }
        
        for prop_name, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if prop_name == 'status':
                    properties[prop_name] = match.group(0)
                else:
                    properties[prop_name] = match.group(1).strip()
        
        return properties
    
    def extract_entity_description(self, content: str, entity: str) -> str:
        """Extract description of an entity from content"""
        # Find sentences containing the entity
        sentences = content.split('.')
        entity_sentences = [s.strip() for s in sentences if entity.lower() in s.lower()]
        
        if entity_sentences:
            return entity_sentences[0] + '.'
        else:
            return content[:200] + '...' if len(content) > 200 else content
    
    def extract_cross_node_relationships(self, node_results: Dict) -> List[Dict]:
        """Extract relationships from cross-node results"""
        relationships = []
        
        for node_id, result in node_results.items():
            if result['success']:
                for doc in result['results']['documents']:
                    doc_relationships = self.relationship_extractor.extract_relationships(
                        doc['content'], node_id
                    )
                    relationships.extend(doc_relationships)
        
        return relationships
    
    def build_networkx_graph(self, cross_node_graph: Dict):
        """Build NetworkX graph from cross-node information"""
        
        # Add entities as nodes
        for entity_name, entity_info in cross_node_graph['entities'].items():
            self.graph.add_node(
                entity_name,
                **entity_info,
                node_type='entity'
            )
        
        # Add relationships as edges
        for relationship in cross_node_graph['relationships']:
            source = relationship.get('source')
            target = relationship.get('target')
            if source and target:
                self.graph.add_edge(
                    source, target,
                    relationship_type=relationship.get('type', 'related'),
                    confidence=relationship.get('confidence', 0.5),
                    sources=relationship.get('sources', [])
                )
        
        # Update entity index
        for node in self.graph.nodes():
            if self.graph.nodes[node].get('node_type') == 'entity':
                self.entity_index[node] = self.graph.nodes[node]
    
    def calculate_graph_statistics(self) -> Dict:
        """Calculate statistics for the knowledge graph"""
        if not self.graph.nodes():
            return {}
        
        return {
            'total_entities': len([n for n in self.graph.nodes() if self.graph.nodes[n].get('node_type') == 'entity']),
            'total_relationships': self.graph.number_of_edges(),
            'average_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes()) if self.graph.nodes() else 0,
            'connected_components': nx.number_connected_components(self.graph),
            'density': nx.density(self.graph),
            'clustering_coefficient': nx.average_clustering(self.graph)
        }
    
    def find_entity_paths(self, source_entity: str, target_entity: str, max_length: int = 3) -> List[List[str]]:
        """Find paths between entities in the knowledge graph"""
        try:
            paths = list(nx.all_simple_paths(
                self.graph, source_entity, target_entity, cutoff=max_length
            ))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def get_entity_neighbors(self, entity: str, max_depth: int = 2) -> Dict:
        """Get neighbors of an entity up to specified depth"""
        if entity not in self.graph:
            return {}
        
        neighbors = {
            'direct': list(self.graph.neighbors(entity)),
            'extended': []
        }
        
        if max_depth > 1:
            for neighbor in neighbors['direct']:
                extended_neighbors = list(self.graph.neighbors(neighbor))
                neighbors['extended'].extend(extended_neighbors)
        
        return neighbors
    
    def suggest_related_entities(self, entity: str, limit: int = 5) -> List[Dict]:
        """Suggest related entities based on graph structure"""
        if entity not in self.graph:
            return []
        
        # Get direct neighbors with their relationship information
        suggestions = []
        for neighbor in self.graph.neighbors(entity):
            edge_data = self.graph.get_edge_data(entity, neighbor)
            suggestions.append({
                'entity': neighbor,
                'relationship_type': edge_data.get('relationship_type', 'related'),
                'confidence': edge_data.get('confidence', 0.5),
                'sources': edge_data.get('sources', [])
            })
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:limit]

class EntityExtractor:
    """Extract entities from text content"""
    
    def __init__(self):
        self.entity_patterns = {
            'person': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            'organization': r'\b[A-Z][a-z]+\s+(?:Inc|Corp|LLC|Ltd|Company|Organization)\b',
            'location': r'\b(?:in|at|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'date': r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            'number': r'\b\d+(?:\.\d+)?\b'
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text using pattern matching"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            entities[entity_type] = list(set(matches))
        
        return entities

class RelationshipExtractor:
    """Extract relationships between entities"""
    
    def __init__(self):
        self.relationship_patterns = {
            'is_a': r'(\w+)\s+is\s+(?:a|an|the)?\s*(\w+)',
            'has': r'(\w+)\s+has\s+(\w+)',
            'located_in': r'(\w+)\s+(?:is\s+)?(?:in|at|located\s+in)\s+(\w+)',
            'works_for': r'(\w+)\s+(?:works\s+for|employed\s+by)\s+(\w+)',
            'related_to': r'(\w+)\s+(?:is\s+)?(?:related\s+to|connected\s+to)\s+(\w+)'
        }
    
    def extract_relationships(self, text: str, source_node: str) -> List[Dict]:
        """Extract relationships from text"""
        relationships = []
        
        for rel_type, pattern in self.relationship_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                relationships.append({
                    'source': match[0],
                    'target': match[1],
                    'type': rel_type,
                    'confidence': 0.8,  # Simple confidence scoring
                    'sources': [source_node]
                })
        
        return relationships

class KnowledgeGraphAnalyzer:
    """Analyze knowledge graph structure and content"""
    
    def __init__(self, graph: nx.Graph):
        self.graph = graph
    
    def analyze_entity_centrality(self) -> Dict[str, float]:
        """Analyze entity centrality in the graph"""
        centrality_measures = {
            'degree': nx.degree_centrality(self.graph),
            'betweenness': nx.betweenness_centrality(self.graph),
            'closeness': nx.closeness_centrality(self.graph),
            'eigenvector': nx.eigenvector_centrality(self.graph, max_iter=1000)
        }
        
        return centrality_measures
    
    def find_community_structure(self) -> Dict:
        """Find community structure in the knowledge graph"""
        try:
            communities = nx.community.greedy_modularity_communities(self.graph)
            return {
                'communities': list(communities),
                'modularity': nx.community.modularity(self.graph, communities),
                'number_of_communities': len(communities)
            }
        except:
            return {'communities': [], 'modularity': 0, 'number_of_communities': 0}
    
    def identify_key_entities(self, top_k: int = 10) -> List[Dict]:
        """Identify key entities based on centrality measures"""
        centrality = self.analyze_entity_centrality()
        
        # Combine centrality measures
        entity_scores = {}
        for entity in self.graph.nodes():
            if self.graph.nodes[entity].get('node_type') == 'entity':
                score = (
                    centrality['degree'].get(entity, 0) * 0.3 +
                    centrality['betweenness'].get(entity, 0) * 0.3 +
                    centrality['closeness'].get(entity, 0) * 0.2 +
                    centrality['eigenvector'].get(entity, 0) * 0.2
                )
                entity_scores[entity] = score
        
        # Sort and return top entities
        sorted_entities = sorted(entity_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'entity': entity,
                'score': score,
                'centrality_measures': {
                    'degree': centrality['degree'].get(entity, 0),
                    'betweenness': centrality['betweenness'].get(entity, 0),
                    'closeness': centrality['closeness'].get(entity, 0),
                    'eigenvector': centrality['eigenvector'].get(entity, 0)
                }
            }
            for entity, score in sorted_entities[:top_k]
        ]
