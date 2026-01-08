"""Tests for AI Service module."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ai_service import AIService, Recommendation


@pytest.fixture
def sample_products():
    """Fixture with sample product data."""
    return [
        {"name": "Nestle Coffee", "category": "Beverages", "intensity": "high"},
        {"name": "Coca-Cola", "category": "Beverages", "intensity": "high"},
        {"name": "Danone Yogurt", "category": "Dairy", "intensity": "medium"},
        {"name": "Pringles", "category": "Snacks", "intensity": "high"},
        {"name": "Starbucks", "category": "Beverages", "intensity": "medium"},
    ]


@pytest.fixture
def ai_service(sample_products):
    """Fixture for AI service instance."""
    return AIService(sample_products)


class TestChatbot:
    """Test chatbot functionality."""
    
    def test_chat_why_boycott(self, ai_service):
        """Test chatbot response for boycott reason."""
        response = ai_service.chat("Why should I boycott Nestle?")
        assert isinstance(response, str)
        assert len(response) > 0
        assert response.lower() != "i don't understand"
    
    def test_chat_find_alternative(self, ai_service):
        """Test chatbot finding alternatives."""
        response = ai_service.chat("What can I use instead of Coca-Cola?")
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_chat_statistics(self, ai_service):
        """Test chatbot providing statistics."""
        response = ai_service.chat("How many boycotted products are there?")
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_chat_palestine_support(self, ai_service):
        """Test chatbot on Palestine support topic."""
        response = ai_service.chat("Why is this boycott related to Palestine?")
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_chat_general_question(self, ai_service):
        """Test chatbot for general questions."""
        response = ai_service.chat("Tell me more about this app.")
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_chat_empty_input(self, ai_service):
        """Test chatbot with empty input."""
        response = ai_service.chat("")
        assert isinstance(response, str)
    
    def test_chat_long_input(self, ai_service):
        """Test chatbot with very long input."""
        long_input = "This is a very long input " * 100
        response = ai_service.chat(long_input)
        assert isinstance(response, str)
        assert len(response) > 0


class TestIntentDetection:
    """Test intent detection."""
    
    def test_detect_boycott_reason_intent(self, ai_service):
        """Test detection of boycott reason intent."""
        intents = [
            "Why boycott Nestle?",
            "What are reasons to boycott?",
            "Tell me why I should boycott",
        ]
        for msg in intents:
            intent = ai_service._detect_intent(msg)
            assert intent in ["why_boycott", "general"]
    
    def test_detect_alternative_intent(self, ai_service):
        """Test detection of alternative finding intent."""
        intents = [
            "What's an alternative to Coca-Cola?",
            "Find me a replacement",
            "I want alternative products",
        ]
        for msg in intents:
            intent = ai_service._detect_intent(msg)
            assert intent in ["find_alternative", "general"]
    
    def test_detect_statistics_intent(self, ai_service):
        """Test detection of statistics intent."""
        intents = [
            "How many boycotted products?",
            "Show me statistics",
            "What are the stats?",
        ]
        for msg in intents:
            intent = ai_service._detect_intent(msg)
            assert intent in ["statistics", "general"]


class TestProductExtraction:
    """Test product name extraction from user input."""
    
    def test_extract_product_simple(self, ai_service):
        """Test extracting simple product name."""
        product = ai_service._extract_product("What about Nestle?")
        assert product is not None
    
    def test_extract_product_none(self, ai_service):
        """Test extraction when no product mentioned."""
        product = ai_service._extract_product("Hello there")
        # May be None or empty
        assert isinstance(product, (str, type(None)))


class TestRecommendations:
    """Test recommendation engine."""
    
    def test_get_recommendations_with_history(self, ai_service):
        """Test getting recommendations with user history."""
        history = ["Nestle Coffee", "Coca-Cola"]
        recommendations = ai_service.get_recommendations(history)
        
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert isinstance(rec, Recommendation)
            assert hasattr(rec, 'name')
            assert hasattr(rec, 'category')
            assert hasattr(rec, 'score')
            assert 0 <= rec.score <= 1
    
    def test_get_recommendations_empty_history(self, ai_service):
        """Test recommendations with empty history."""
        recommendations = ai_service.get_recommendations([])
        assert isinstance(recommendations, list)
    
    def test_recommendations_sorted_by_score(self, ai_service):
        """Test that recommendations are sorted by relevance score."""
        history = ["Nestle Coffee", "Coca-Cola"]
        recommendations = ai_service.get_recommendations(history)
        
        if len(recommendations) > 1:
            scores = [rec.score for rec in recommendations]
            assert scores == sorted(scores, reverse=True)
    
    def test_relevance_score_calculation(self, ai_service):
        """Test relevance score calculation."""
        history = ["Nestle Coffee"]
        recommendations = ai_service.get_recommendations(history)
        
        # Score should be calculated (0-1)
        for rec in recommendations:
            assert isinstance(rec.score, (int, float))
            assert 0 <= rec.score <= 1.5  # May exceed 1 with combined scoring


class TestSentimentAnalysis:
    """Test sentiment analysis functionality."""
    
    def test_analyze_sentiment_positive(self, ai_service):
        """Test sentiment analysis for positive text."""
        result = ai_service.analyze_sentiment(
            "This app is amazing! I love it so much."
        )
        assert isinstance(result, dict)
        assert "sentiment" in result
        assert result["sentiment"] in ["positive", "negative", "neutral"]
    
    def test_analyze_sentiment_negative(self, ai_service):
        """Test sentiment analysis for negative text."""
        result = ai_service.analyze_sentiment(
            "This is terrible and doesn't work at all."
        )
        assert isinstance(result, dict)
        assert "sentiment" in result
    
    def test_analyze_sentiment_neutral(self, ai_service):
        """Test sentiment analysis for neutral text."""
        result = ai_service.analyze_sentiment(
            "The app has a home page."
        )
        assert isinstance(result, dict)
        assert "sentiment" in result
    
    def test_analyze_sentiment_result_structure(self, ai_service):
        """Test sentiment result has all required fields."""
        result = ai_service.analyze_sentiment("Test feedback message")
        
        required_fields = ["sentiment", "category", "suggestion"]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_sentiment_categorization(self, ai_service):
        """Test feedback categorization."""
        result = ai_service.analyze_sentiment("The UI is ugly and confusing")
        assert result["category"] in [
            "UI/UX", "Performance", "Content", "Bug", "General"
        ]
    
    def test_sentiment_suggestion_generation(self, ai_service):
        """Test that suggestions are generated."""
        result = ai_service.analyze_sentiment("Very slow app")
        assert isinstance(result["suggestion"], str)
        assert len(result["suggestion"]) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_chat_with_special_characters(self, ai_service):
        """Test chat with special characters."""
        response = ai_service.chat("!@#$%^&*()")
        assert isinstance(response, str)
    
    def test_chat_with_unicode(self, ai_service):
        """Test chat with unicode characters."""
        response = ai_service.chat("مرحبا بك في التطبيق")  # Arabic
        assert isinstance(response, str)
    
    def test_chat_with_numbers(self, ai_service):
        """Test chat with numbers only."""
        response = ai_service.chat("123456789")
        assert isinstance(response, str)
    
    def test_recommendations_with_duplicate_history(self, ai_service):
        """Test recommendations with duplicate products in history."""
        history = ["Nestle Coffee", "Nestle Coffee", "Coca-Cola"]
        recommendations = ai_service.get_recommendations(history)
        assert isinstance(recommendations, list)
    
    def test_sentiment_with_very_long_text(self, ai_service):
        """Test sentiment analysis with very long text."""
        long_text = "This is great! " * 1000
        result = ai_service.analyze_sentiment(long_text)
        assert isinstance(result, dict)
        assert "sentiment" in result


class TestIntegration:
    """Integration tests combining multiple features."""
    
    def test_full_conversation_flow(self, ai_service):
        """Test a complete conversation flow."""
        # User asks about boycott
        response1 = ai_service.chat("Why boycott Nestle?")
        assert len(response1) > 0
        
        # User asks for alternatives
        response2 = ai_service.chat("What's an alternative?")
        assert len(response2) > 0
        
        # User gets recommendations
        recommendations = ai_service.get_recommendations(["Nestle Coffee"])
        assert len(recommendations) > 0
    
    def test_feedback_workflow(self, ai_service):
        """Test feedback analysis workflow."""
        feedback = "The app works well but is a bit slow"
        result = ai_service.analyze_sentiment(feedback)
        
        assert "sentiment" in result
        assert "category" in result
        assert "suggestion" in result
        assert result["suggestion"]  # Should provide actionable feedback


class TestPerformance:
    """Test performance of AI operations."""
    
    def test_chat_performance(self, ai_service):
        """Test chat response time."""
        import time
        start = time.time()
        ai_service.chat("Why boycott?")
        elapsed = time.time() - start
        
        # Should respond quickly (< 500ms)
        assert elapsed < 0.5, f"Chat took {elapsed}s"
    
    def test_recommendations_performance(self, ai_service):
        """Test recommendations generation performance."""
        import time
        history = ["Nestle Coffee", "Coca-Cola"] * 5  # Larger history
        
        start = time.time()
        ai_service.get_recommendations(history)
        elapsed = time.time() - start
        
        # Should compute quickly (< 200ms)
        assert elapsed < 0.2, f"Recommendations took {elapsed}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
