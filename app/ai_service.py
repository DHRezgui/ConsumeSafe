"""
AI Service Module - Chatbot, Recommendations & Sentiment Analysis
"""
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Handle all AI operations for ConsumeSafe"""
    
    def __init__(self, products_data: List[Dict[str, Any]]):
        self.products = products_data
        self.conversation_history = []
        self.user_preferences = {}
        
    # ============ CHATBOT FUNCTIONALITY ============
    
    def chat(self, user_message: str) -> str:
        """
        Conversational AI for boycott education
        
        Args:
            user_message: User's message
            
        Returns:
            AI response about boycott alternatives
        """
        self.conversation_history.append({"role": "user", "content": user_message})
        message_lower = user_message.lower()
        
        # First, check if it's a specific product question
        product_match = self._extract_product(user_message)
        if product_match:
            response = self._answer_specific_product(product_match)
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        # Then detect broader intent
        intent = self._detect_intent(user_message)
        
        # Generate response based on intent
        if intent == "why_boycott":
            response = self._answer_why_boycott()
        elif intent == "find_alternative":
            response = self._find_alternative("")
        elif intent == "statistics":
            response = self._get_chat_statistics()
        elif intent == "palestine_support":
            response = self._answer_palestine_support()
        else:
            response = self._generate_general_response(user_message)
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["produits", "products", "boycotter", "boycott", "listes", "list"]):
            return "why_boycott"
        elif any(word in message_lower for word in ["pourquoi", "why", "raison", "reason"]):
            return "why_boycott"
        elif any(word in message_lower for word in ["alternative", "remplacer", "autre", "tunisien", "replace"]):
            return "find_alternative"
        elif any(word in message_lower for word in ["stats", "statistiques", "nombre", "total", "combien"]):
            return "statistics"
        elif any(word in message_lower for word in ["palestine", "enfants", "children", "guerre", "war"]):
            return "palestine_support"
        else:
            return "general"
    
    def _extract_product(self, message: str) -> str:
        """Extract product name from message - SMART VERSION"""
        message_lower = message.lower()
        
        # Normalize message (remove special chars for matching)
        normalized_msg = message_lower.replace("-", " ").replace("'", "")
        
        # Check each product in database
        for product in self.products:
            product_name = product.get('boycott_product', '').lower()
            brand = product.get('brand', '').lower()
            
            # Normalize product names
            normalized_product = product_name.replace("-", " ").replace("'", "")
            normalized_brand = brand.replace("-", " ").replace("'", "")
            
            # Exact match first
            if product_name in message_lower or brand in message_lower:
                return product_name
            
            # Then try normalized match
            if normalized_product in normalized_msg or normalized_brand in normalized_msg:
                return product_name
            
            # Partial match for multi-word brands (at least 2 words)
            product_words = normalized_product.split()
            brand_words = normalized_brand.split()
            
            for word in product_words:
                if len(word) > 3 and word in normalized_msg:
                    return product_name
            
            for word in brand_words:
                if len(word) > 3 and word in normalized_msg:
                    return product_name
        
        return None
    
    def _answer_why_boycott(self) -> str:
        """Explain why boycott is important and list top products"""
        # Get top 5 products
        top_products = self.products[:5] if self.products else []
        products_list = "\n".join([
            f"❌ {p.get('boycott_product')} ({p.get('brand')})"
            for p in top_products
        ])
        
        return f"""**Produits à Boycotter:**

{products_list}

... et {len(self.products) - 5} autres

**Impact:** $10+ milliards de pertes depuis 2023
💡 Demandez: "Coca Cola" ou "Alternative pour [produit]"?"""
    
    def _answer_palestine_support(self) -> str:
        """Answer about Palestine support"""
        total_products = len(self.products)
        return f"""🇵🇸 **ConsumeSafe pour la Palestine:**

✅ {total_products} marques boycottées identifiées
✅ 100+ alternatives tunisiennes
✅ $10+ milliards d'impact global

Votre consommation = votre vote pour la justice! 🇹🇳"""

    def _answer_specific_product(self, product_query: str) -> str:
        """Answer specifically about one product - SHORT AND DIRECT"""
        if not product_query:
            return "Je n'ai pas compris. Quel produit?"
        
        # Find the product
        for product in self.products:
            product_name = product.get('boycott_product', '').lower()
            brand = product.get('brand', '').lower()
            
            if product_name in product_query.lower() or brand in product_query.lower():
                alternative = product.get('tunisian_alternative', 'N/A')
                alt_brand = product.get('alternative_brand', 'N/A')
                reason = product.get('reason', 'Soutien à l\'occupation')
                
                return f"""❌ **À BOYCOTTER**

{product.get('boycott_product')}
Marque: {product.get('brand')}

Raison: {reason}

━━━━━━━━━━━━━━━━━━━━━━━

✅ **ALTERNATIVE TUNISIENNE**

{alternative}
Marque: {alt_brand} 🇹🇳"""
        
        return f"❓ Produit non trouvé"
    
    def _find_alternative(self, product_name: str) -> str:
        """Find alternative for a product"""
        if not product_name:
            return "🤔 Je n'ai pas bien compris le produit. Pouvez-vous être plus spécifique?"
        
        for product in self.products:
            if product_name.lower() in product.get('boycott_product', '').lower():
                alternative = product.get('tunisian_alternative', 'N/A')
                brand = product.get('alternative_brand', 'N/A')
                reason = product.get('reason', '')
                
                return f"""✅ **Alternative trouvée:**

❌ À éviter: **{product.get('boycott_product')}** ({product.get('brand')})
Raison: {reason}

✅ À choisir: **{alternative}** ({brand})
🇹🇳 Cette marque soutient l'économie tunisienne!

En faisant ce choix, vous:
- Soutenez la Palestine indirectement
- Renforcez l'économie tunisienne
- Votez avec votre portefeuille"""
        
        return f"❌ Je n'ai pas trouvé '{product_name}' dans notre base de données. C'est peut-être un produit sûr!"
    
    def _get_chat_statistics(self) -> str:
        """Get statistics for chat"""
        total = len(self.products)
        categories = set(p.get('category', '') for p in self.products)
        brands = set(p.get('brand', '') for p in self.products)
        
        return f"""📊 **Statistiques:**

• **Produits:** {total}
• **Catégories:** {len(categories)}
• **Marques:** {len(brands)}

Demandez un produit spécifique pour plus d'info!"""
    
    def _generate_general_response(self, message: str) -> str:
        """Generate general response"""
        return """🤖 **Comment vous aider?**

• "Coca Cola" → Info produit
• "Statistiques" → Les chiffres
• "Palestine" → Pourquoi
• "Quels produits?" → La liste"""
    
    # ============ RECOMMENDATIONS FUNCTIONALITY ============
    
    def get_recommendations(self, user_history: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations based on user history
        
        Args:
            user_history: List of products user viewed/searched
            limit: Number of recommendations
            
        Returns:
            List of recommended alternatives
        """
        recommendations = []
        viewed_categories = set()
        
        # Get categories from user history
        for product_name in user_history:
            for product in self.products:
                if product_name.lower() in product.get('boycott_product', '').lower():
                    viewed_categories.add(product.get('category', ''))
        
        # Get products from same categories
        for product in self.products:
            if product.get('category', '') in viewed_categories:
                recommendations.append({
                    "product": product.get('boycott_product'),
                    "brand": product.get('brand'),
                    "alternative": product.get('tunisian_alternative'),
                    "category": product.get('category'),
                    "score": self._calculate_relevance_score(product, viewed_categories)
                })
        
        # Sort by relevance score and return top N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]
    
    def _calculate_relevance_score(self, product: Dict, user_categories: set) -> float:
        """Calculate relevance score for recommendation"""
        score = 0.0
        
        # Category match
        if product.get('category') in user_categories:
            score += 0.7
        
        # Alternative availability
        if product.get('tunisian_alternative'):
            score += 0.2
        
        # Popularity (assume products at start are more popular)
        score += 0.1
        
        return score
    
    # ============ SENTIMENT ANALYSIS FUNCTIONALITY ============
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of user feedback
        
        Args:
            text: User feedback text
            
        Returns:
            Sentiment analysis result
        """
        sentiment = self._simple_sentiment(text)
        
        return {
            "text": text,
            "sentiment": sentiment['label'],
            "score": sentiment['score'],
            "category": self._categorize_feedback(text),
            "actionable": sentiment['label'] in ['negative', 'neutral'],
            "suggestion": self._generate_suggestion(sentiment['label'], text)
        }
    
    def _simple_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple sentiment analysis"""
        text_lower = text.lower()
        
        positive_words = ['excellent', 'bon', 'merveilleux', 'fantastic', 'love', 'adore', 'parfait']
        negative_words = ['mauvais', 'nul', 'terrible', 'hate', 'awful', 'problème', 'bug', 'erreur']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {"label": "positive", "score": 0.8 + (positive_count * 0.1)}
        elif negative_count > positive_count:
            return {"label": "negative", "score": 0.8 + (negative_count * 0.1)}
        else:
            return {"label": "neutral", "score": 0.5}
    
    def _categorize_feedback(self, text: str) -> str:
        """Categorize feedback type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['interface', 'design', 'couleur', 'button']):
            return "UI/UX"
        elif any(word in text_lower for word in ['vitesse', 'lent', 'fast', 'performance']):
            return "Performance"
        elif any(word in text_lower for word in ['produit', 'données', 'data', 'alternative']):
            return "Content"
        elif any(word in text_lower for word in ['bug', 'erreur', 'error', 'crash']):
            return "Bug"
        else:
            return "General"
    
    def _generate_suggestion(self, sentiment: str, text: str) -> str:
        """Generate actionable suggestion"""
        category = self._categorize_feedback(text)
        
        if sentiment == "negative":
            return f"❌ Feedback négatif détecté en {category}. À investiguer en priorité."
        elif sentiment == "neutral":
            return f"ℹ️ Suggestion d'amélioration en {category}. À examiner."
        else:
            return f"✅ Feedback positif! Utilisateur satisfait avec {category}."


def create_ai_service(products_data: List[Dict[str, Any]]) -> AIService:
    """Factory function to create AI service"""
    return AIService(products_data)
