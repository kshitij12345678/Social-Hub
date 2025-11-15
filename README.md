# Social Hub - AI-Powered Recommendation System

A comprehensive social media platform with multiple AI-powered recommendation systems, featuring statistical methods, matrix factorization, two-tower deep learning, and Vision Transformer architectures.

## Table of Contents

- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Recommendation Systems](#recommendation-systems)
- [System Selection](#system-selection)
- [Evaluation Metrics](#evaluation-metrics)

## System Architecture

### Overall System Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   Frontend      │ ──────────────► │   Backend API   │
│   (React + TS)  │                 │   (FastAPI)     │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │ Recommendation  │
                                   │    Engine       │
                                   └─────────────────┘
                                            │
                                            ▼
┌─────────────────┐      Queries    ┌─────────────────┐
│  File Storage   │ ◄──────────────► │   Database      │
│ (Local Files)   │                 │   (SQLite)      │
└─────────────────┘                 └─────────────────┘
```

### Backend Structure

```
Backend Components:
├── FastAPI Application (main.py)
├── Database Layer (SQLite)
├── Authentication (JWT + Google OAuth)
├── File Storage (Local uploads/)
├── Recommendation Engine
└── API Endpoints
```

## Tech Stack

### Frontend
- **Framework:** React with TypeScript
- **Styling:** Tailwind CSS
- **Build Tool:** Vite
- **State Management:** React Hooks

### Backend
- **API Framework:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Authentication:** JWT + Google OAuth + Appwrite
- **File Handling:** Local file storage
- **Validation:** Pydantic models

### Machine Learning
- **Core Libraries:** NumPy, Pandas, Scikit-learn
- **Deep Learning:** TensorFlow
- **Computer Vision:** OpenCV, Pillow
- **NLP:** Basic text processing

## Recommendation Systems

Our platform implements four different recommendation approaches, each designed for different use cases and computational requirements.

### 1. Statistical Hybrid System

This system combines collaborative filtering and content-based filtering using traditional statistical methods. It analyzes user interaction patterns and content similarities to generate recommendations without requiring machine learning training.

The process involves extracting user preferences from historical interactions, finding similar users through cosine similarity, matching content attributes like location and category preferences, and combining both approaches with intelligent diversity algorithms to ensure varied recommendations.

**Architecture:**
```
User Request → User Profiling → Collaborative Filtering
                    ↓               ↓
           Content Analysis → Hybrid Combination
                    ↓               ↓
           Diversity Rules → Final Recommendations
```

**Pros:**
- Fast inference and real-time ready
- No training required
- Interpretable results
- Production-ready implementation
- High success rate

**Cons:**
- No learning capability
- Rule-based approach limitations
- Cold start problems for new users
- Manual parameter tuning required

### 2. Matrix Factorization AI

This system uses Non-negative Matrix Factorization to decompose user-item interaction matrices into latent factors, enabling pure machine learning recommendations. It learns hidden patterns in user behavior and item characteristics automatically.

The process creates a user-item interaction matrix from historical data, applies NMF algorithm to discover latent factors representing user preferences and item features, then generates recommendations by computing similarity scores between learned user and item embeddings.

**Architecture:**
```
User-Item Matrix → NMF Algorithm → Latent Factors
        ↓              ↓              ↓
Interaction Data → Learning Process → User/Item Embeddings
        ↓              ↓              ↓
New User Request → Similarity Calc → AI Recommendations
```

**Pros:**
- Pure machine learning approach
- Learns hidden user behavior patterns
- Automatic feature discovery
- Scalable to large datasets
- High AI confidence scores

**Cons:**
- Requires sufficient training data
- Black box predictions
- Cold start issues
- Need for periodic retraining

### 3. Two-Tower Deep Learning

This system uses separate neural networks for users and content, creating dense embeddings that capture complex patterns. The two-tower architecture can handle multimodal data including text, images, and user behavior.

The process involves training separate neural networks for user features and content features, generating embeddings from each tower, computing similarity between user and content embeddings, and ranking recommendations based on learned representations.

**Without Images Architecture:**
```
User Features → User Tower (NN) → User Embedding
     ↓               ↓                    ↓
Content Features → Content Tower (NN) → Content Embedding
     ↓               ↓                    ↓
Cosine Similarity → Ranking → Final Recommendations
```

**With Images Architecture:**
```
User History → LSTM → User Embedding
     ↓           ↓          ↓
Images → CNN → Visual Embedding
     ↓           ↓          ↓
Text → TF-IDF → Text Embedding
     ↓           ↓          ↓
Multimodal Fusion → Final Embedding → Recommendations
```

**Pros:**
- Deep learning architecture
- Neural embeddings capture complex patterns
- Multimodal capabilities
- Scalable framework
- End-to-end training

**Cons:**
- Requires GPU for training
- Complex architecture and deployment
- Longer inference time
- Need for hyperparameter tuning

### 4. Vision Transformer + LSTM

This represents the most advanced approach, using Vision Transformers for image understanding and LSTM with self-attention for sequential user modeling. It provides state-of-the-art multimodal recommendations by fusing visual and temporal features.

The process involves processing images through Vision Transformer to extract patch-based visual features, using LSTM with self-attention to model user interaction sequences over time, applying cross-modal attention to fuse image and user features, and generating final recommendations through advanced neural networks.

**Architecture:**
```
Travel Images → Vision Transformer → Visual Embeddings
        ↓              ↓                      ↓
    Patch-based → Multi-head Attention → Global Visual Features
        ↓              ↓                      ↓
User Sequences → LSTM + Self-Attention → Temporal Embeddings
        ↓              ↓                      ↓
Cross-Modal Attention → Fusion Network → Final Recommendations
```

**Pros:**
- State-of-the-art AI technology
- Advanced image understanding
- Temporal user modeling
- Multimodal fusion capabilities
- Maximum personalization potential

**Cons:**
- Extremely high computational requirements
- Very slow training process
- Requires large labeled datasets
- Complex deployment infrastructure
- High operational costs

## System Selection

For our social media platform focusing on travel content, we have chosen the **Vision Transformer + LSTM** as our advanced recommendation engine.

### Why Vision Transformer + LSTM

The Vision Transformer + LSTM system represents the most advanced and sophisticated approach for travel content recommendations. This cutting-edge system is specifically designed to handle the visual-rich nature of travel social media platforms where images are the primary content type.

For travel content, visual understanding is crucial as users make decisions based on the aesthetic appeal and visual similarity of destinations. The Vision Transformer excels at understanding complex visual patterns in travel images, from architectural styles to natural landscapes, while the LSTM component captures temporal user preferences and seasonal travel patterns.

This system provides maximum personalization by learning both what users visually prefer and how their preferences evolve over time. The multimodal fusion capability allows the system to understand the relationship between visual content, textual descriptions, and user behavior patterns, resulting in highly accurate and contextually relevant travel recommendations.

While this approach requires significant computational resources and infrastructure investment, it provides unmatched recommendation quality and user engagement for a travel-focused platform where visual content drives user decisions.

## Evaluation Metrics

The following metrics can be used to evaluate and compare recommendation system performance:

### Accuracy Metrics
- **Precision:** Percentage of recommended items that are relevant
- **Recall:** Percentage of relevant items that are recommended  
- **F1-Score:** Harmonic mean of precision and recall

### Diversity and Coverage Metrics
- **Diversity Score:** Measure of variety in recommendation categories

### System Performance Metrics
- **Response Time:** Latency from request to recommendation delivery