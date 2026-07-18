from core.database import db

def calculate_downstream_impact(topic_id: str):
    """
    Traverses the graph to find all topics that require the missed concept.
    Calculates the cumulative risk score based on the weight of impacted topics.
    """
    # The asterisk in <-[:REQUIRES*]- tells Neo4j to recursively traverse the chain 
    # as far as it goes to catch indirect dependencies.
    query = """
    MATCH (missed:Topic {id: $topic_id})<-[:REQUIRES*]-(dependent:Topic)
    RETURN DISTINCT dependent.id AS id, 
                    dependent.name AS name, 
                    dependent.weight AS weight
    """
    
    # Execute the traversal against AuraDB
    records = db.execute_query(query, topic_id=topic_id)
    
    impacted_topics = []
    total_risk_score = 0.0
    
    for record in records:
        impacted_topics.append({
            "id": record["id"],
            "name": record["name"],
            "weight": record["weight"]
        })
        total_risk_score += record["weight"]
        
    return {
        "missed_topic_id": topic_id,
        "total_dependent_topics": len(impacted_topics),
        "cumulative_risk_score": round(total_risk_score, 2),
        "impacted_chain": impacted_topics
    }

#  Local Testing Block 
if __name__ == "__main__":
    # Test: If a student fails or misses "Vector Spaces" (TOP_VEC), 
    # what is the downstream blast radius?
    result = calculate_downstream_impact("TOP_VEC")
    
    print(f"\n TIME MACHINE: IMPACT ANALYSIS ")
    print(f"Missed Topic: {result['missed_topic_id']}")
    print(f"Total Future Topics at Risk: {result['total_dependent_topics']}")
    print(f"Cumulative Readiness Degradation Score: {result['cumulative_risk_score']}")
    
    print("\nImpacted Topic Chain:")
    for topic in result['impacted_chain']:
        print(f" -> {topic['name']} (Weight: {topic['weight']})")
        
    db.close()