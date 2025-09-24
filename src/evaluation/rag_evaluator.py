"""
RAG evaluation framework using RAGAS and custom metrics.
"""

import time
import logging
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import json

logger = logging.getLogger(__name__)

try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        answer_correctness,
        answer_similarity
    )
    RAGAS_AVAILABLE = True
except ImportError:
    logger.warning("RAGAS not available. Install with: pip install ragas")
    RAGAS_AVAILABLE = False


class RAGEvaluator:
    """Comprehensive RAG system evaluation."""
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        use_ragas: bool = True
    ):
        """
        Initialize RAG evaluator.
        
        Args:
            embedding_model: Model for semantic similarity calculations
            use_ragas: Whether to use RAGAS metrics
        """
        self.embedding_model_name = embedding_model
        self.use_ragas = use_ragas and RAGAS_AVAILABLE
        
        # Initialize embedding model for custom metrics
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            self.embedding_model = None
        
        # Initialize RAGAS metrics if available
        if self.use_ragas:
            self.ragas_metrics = [
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
                answer_correctness,
                answer_similarity
            ]
        else:
            self.ragas_metrics = []
        
        logger.info(f"RAG Evaluator initialized with RAGAS: {self.use_ragas}")
    
    def evaluate_rag_system(
        self,
        test_questions: List[str],
        ground_truths: List[str],
        rag_system,
        contexts: Optional[List[List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate RAG system with comprehensive metrics.
        
        Args:
            test_questions: List of test questions
            ground_truths: List of ground truth answers
            rag_system: RAG system to evaluate
            contexts: Optional list of contexts for each question
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info(f"Starting evaluation of {len(test_questions)} questions")
        
        # Generate RAG responses
        rag_responses = []
        for question in test_questions:
            try:
                response = rag_system.generate_answer(question)
                rag_responses.append({
                    "question": question,
                    "answer": response["answer"],
                    "sources": response.get("sources", []),
                    "confidence": response.get("confidence", 0.0),
                    "processing_time": response.get("total_time", 0.0)
                })
            except Exception as e:
                logger.error(f"Error generating response for question: {e}")
                rag_responses.append({
                    "question": question,
                    "answer": "Error generating response",
                    "sources": [],
                    "confidence": 0.0,
                    "processing_time": 0.0
                })
        
        # Calculate custom metrics
        custom_metrics = self._calculate_custom_metrics(
            test_questions, ground_truths, rag_responses
        )
        
        # Calculate RAGAS metrics if available
        ragas_results = {}
        if self.use_ragas and contexts:
            try:
                ragas_results = self._calculate_ragas_metrics(
                    test_questions, ground_truths, rag_responses, contexts
                )
            except Exception as e:
                logger.error(f"Error calculating RAGAS metrics: {e}")
                ragas_results = {}
        
        # Compile results
        results = {
            "custom_metrics": custom_metrics,
            "ragas_metrics": ragas_results,
            "individual_results": rag_responses,
            "summary": self._create_summary(custom_metrics, ragas_results)
        }
        
        logger.info("Evaluation completed successfully")
        return results
    
    def _calculate_custom_metrics(
        self,
        questions: List[str],
        ground_truths: List[str],
        rag_responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate custom evaluation metrics."""
        metrics = {}
        
        # Semantic similarity
        if self.embedding_model:
            try:
                similarities = []
                for response, ground_truth in zip(rag_responses, ground_truths):
                    similarity = self._calculate_semantic_similarity(
                        response["answer"], ground_truth
                    )
                    similarities.append(similarity)
                
                metrics["semantic_similarity"] = {
                    "mean": np.mean(similarities),
                    "std": np.std(similarities),
                    "scores": similarities
                }
            except Exception as e:
                logger.error(f"Error calculating semantic similarity: {e}")
                metrics["semantic_similarity"] = {"mean": 0.0, "std": 0.0, "scores": []}
        
        # Answer length metrics
        answer_lengths = [len(response["answer"]) for response in rag_responses]
        metrics["answer_length"] = {
            "mean": np.mean(answer_lengths),
            "std": np.std(answer_lengths),
            "min": np.min(answer_lengths),
            "max": np.max(answer_lengths)
        }
        
        # Confidence metrics
        confidences = [response["confidence"] for response in rag_responses]
        metrics["confidence"] = {
            "mean": np.mean(confidences),
            "std": np.std(confidences),
            "min": np.min(confidences),
            "max": np.max(confidences)
        }
        
        # Processing time metrics
        processing_times = [response["processing_time"] for response in rag_responses]
        metrics["processing_time"] = {
            "mean": np.mean(processing_times),
            "std": np.std(processing_times),
            "min": np.min(processing_times),
            "max": np.max(processing_times)
        }
        
        # Source metrics
        source_counts = [len(response["sources"]) for response in rag_responses]
        metrics["source_count"] = {
            "mean": np.mean(source_counts),
            "std": np.std(source_counts),
            "min": np.min(source_counts),
            "max": np.max(source_counts)
        }
        
        # Exact match accuracy
        exact_matches = []
        for response, ground_truth in zip(rag_responses, ground_truths):
            exact_match = response["answer"].strip().lower() == ground_truth.strip().lower()
            exact_matches.append(exact_match)
        
        metrics["exact_match_accuracy"] = {
            "score": np.mean(exact_matches),
            "count": sum(exact_matches),
            "total": len(exact_matches)
        }
        
        # Keyword overlap
        keyword_overlaps = []
        for response, ground_truth in zip(rag_responses, ground_truths):
            overlap = self._calculate_keyword_overlap(
                response["answer"], ground_truth
            )
            keyword_overlaps.append(overlap)
        
        metrics["keyword_overlap"] = {
            "mean": np.mean(keyword_overlaps),
            "std": np.std(keyword_overlaps),
            "scores": keyword_overlaps
        }
        
        return metrics
    
    def _calculate_ragas_metrics(
        self,
        questions: List[str],
        ground_truths: List[str],
        rag_responses: List[Dict[str, Any]],
        contexts: List[List[str]]
    ) -> Dict[str, Any]:
        """Calculate RAGAS metrics."""
        try:
            # Prepare data for RAGAS
            dataset_data = []
            for i, (question, ground_truth, response, context) in enumerate(
                zip(questions, ground_truths, rag_responses, contexts)
            ):
                dataset_data.append({
                    "question": question,
                    "answer": response["answer"],
                    "contexts": context,
                    "ground_truth": ground_truth
                })
            
            # Create dataset
            from datasets import Dataset
            dataset = Dataset.from_list(dataset_data)
            
            # Evaluate with RAGAS
            result = evaluate(
                dataset,
                metrics=self.ragas_metrics
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in RAGAS evaluation: {e}")
            return {}
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if not self.embedding_model:
            return 0.0
        
        try:
            embeddings = self.embedding_model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    def _calculate_keyword_overlap(self, text1: str, text2: str) -> float:
        """Calculate keyword overlap between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _create_summary(self, custom_metrics: Dict, ragas_metrics: Dict) -> Dict[str, Any]:
        """Create evaluation summary."""
        summary = {
            "overall_score": 0.0,
            "key_metrics": {},
            "recommendations": []
        }
        
        # Calculate overall score
        scores = []
        
        if "semantic_similarity" in custom_metrics:
            scores.append(custom_metrics["semantic_similarity"]["mean"])
        
        if "exact_match_accuracy" in custom_metrics:
            scores.append(custom_metrics["exact_match_accuracy"]["score"])
        
        if "keyword_overlap" in custom_metrics:
            scores.append(custom_metrics["keyword_overlap"]["mean"])
        
        if scores:
            summary["overall_score"] = np.mean(scores)
        
        # Key metrics
        summary["key_metrics"] = {
            "semantic_similarity": custom_metrics.get("semantic_similarity", {}).get("mean", 0.0),
            "exact_match_accuracy": custom_metrics.get("exact_match_accuracy", {}).get("score", 0.0),
            "average_confidence": custom_metrics.get("confidence", {}).get("mean", 0.0),
            "average_processing_time": custom_metrics.get("processing_time", {}).get("mean", 0.0)
        }
        
        # Generate recommendations
        if summary["key_metrics"]["semantic_similarity"] < 0.7:
            summary["recommendations"].append("Consider improving retrieval quality or prompt engineering")
        
        if summary["key_metrics"]["average_confidence"] < 0.5:
            summary["recommendations"].append("Review model parameters and training data quality")
        
        if summary["key_metrics"]["average_processing_time"] > 5.0:
            summary["recommendations"].append("Consider optimizing model performance or using faster models")
        
        return summary
    
    def create_evaluation_report(
        self,
        results: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """Create a comprehensive evaluation report."""
        report = []
        
        # Header
        report.append("# RAG System Evaluation Report")
        report.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        summary = results.get("summary", {})
        report.append("## Summary")
        report.append(f"Overall Score: {summary.get('overall_score', 0.0):.3f}")
        report.append("")
        
        # Key Metrics
        key_metrics = summary.get("key_metrics", {})
        report.append("## Key Metrics")
        for metric, value in key_metrics.items():
            report.append(f"- **{metric}**: {value:.3f}")
        report.append("")
        
        # Custom Metrics
        custom_metrics = results.get("custom_metrics", {})
        report.append("## Detailed Metrics")
        
        for metric_name, metric_data in custom_metrics.items():
            report.append(f"### {metric_name.replace('_', ' ').title()}")
            if isinstance(metric_data, dict):
                for key, value in metric_data.items():
                    if isinstance(value, (int, float)):
                        report.append(f"- **{key}**: {value:.3f}")
                    else:
                        report.append(f"- **{key}**: {value}")
            else:
                report.append(f"Value: {metric_data}")
            report.append("")
        
        # RAGAS Metrics
        if results.get("ragas_metrics"):
            report.append("## RAGAS Metrics")
            ragas_metrics = results["ragas_metrics"]
            for metric_name, value in ragas_metrics.items():
                report.append(f"- **{metric_name}**: {value:.3f}")
            report.append("")
        
        # Recommendations
        recommendations = summary.get("recommendations", [])
        if recommendations:
            report.append("## Recommendations")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        # Individual Results
        individual_results = results.get("individual_results", [])
        if individual_results:
            report.append("## Individual Results")
            for i, result in enumerate(individual_results, 1):
                report.append(f"### Question {i}")
                report.append(f"**Question**: {result['question']}")
                report.append(f"**Answer**: {result['answer']}")
                report.append(f"**Confidence**: {result['confidence']:.3f}")
                report.append(f"**Processing Time**: {result['processing_time']:.3f}s")
                report.append(f"**Sources**: {len(result['sources'])}")
                report.append("")
        
        report_text = "\n".join(report)
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"Evaluation report saved to {output_path}")
        
        return report_text
    
    def evaluate_retrieval_quality(
        self,
        questions: List[str],
        expected_contexts: List[List[str]],
        rag_system
    ) -> Dict[str, Any]:
        """Evaluate retrieval quality specifically."""
        retrieval_metrics = {
            "precision_scores": [],
            "recall_scores": [],
            "f1_scores": []
        }
        
        for question, expected_context in zip(questions, expected_contexts):
            try:
                # Get retrieved documents
                query_embedding = rag_system.embedding_generator.generate_embeddings(question)
                retrieved_docs = rag_system.hybrid_retriever.hybrid_search(
                    query=question,
                    query_embedding=query_embedding,
                    k=len(expected_context)
                )
                
                retrieved_texts = [doc.get("document", "") for doc in retrieved_docs]
                
                # Calculate precision and recall
                precision, recall, f1 = self._calculate_retrieval_metrics(
                    retrieved_texts, expected_context
                )
                
                retrieval_metrics["precision_scores"].append(precision)
                retrieval_metrics["recall_scores"].append(recall)
                retrieval_metrics["f1_scores"].append(f1)
                
            except Exception as e:
                logger.error(f"Error evaluating retrieval for question: {e}")
                retrieval_metrics["precision_scores"].append(0.0)
                retrieval_metrics["recall_scores"].append(0.0)
                retrieval_metrics["f1_scores"].append(0.0)
        
        # Calculate averages
        retrieval_metrics["average_precision"] = np.mean(retrieval_metrics["precision_scores"])
        retrieval_metrics["average_recall"] = np.mean(retrieval_metrics["recall_scores"])
        retrieval_metrics["average_f1"] = np.mean(retrieval_metrics["f1_scores"])
        
        return retrieval_metrics
    
    def _calculate_retrieval_metrics(
        self,
        retrieved_texts: List[str],
        expected_contexts: List[str]
    ) -> Tuple[float, float, float]:
        """Calculate precision, recall, and F1 for retrieval."""
        if not retrieved_texts or not expected_contexts:
            return 0.0, 0.0, 0.0
        
        # Simple keyword-based matching
        retrieved_words = set()
        for text in retrieved_texts:
            retrieved_words.update(text.lower().split())
        
        expected_words = set()
        for context in expected_contexts:
            expected_words.update(context.lower().split())
        
        if not retrieved_words or not expected_words:
            return 0.0, 0.0, 0.0
        
        intersection = retrieved_words.intersection(expected_words)
        
        precision = len(intersection) / len(retrieved_words) if retrieved_words else 0.0
        recall = len(intersection) / len(expected_words) if expected_words else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return precision, recall, f1

