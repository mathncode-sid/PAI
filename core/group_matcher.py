import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances
from core.database import db

def match_study_groups():
    """
    Extracts student topic scores, clusters them via K-Means, 
    and pairs students with maximum Euclidean distance (complementary skills).
    """
    # 1. Extract user performance matrices from Neo4j
    query = """
    MATCH (s:Student)-[r:LOGGED_SESSION]->(t:Topic)
    RETURN s.id AS student_id, t.id AS topic_id, r.difficulty_score AS score
    """
    records = db.execute_query(query)
    
    if not records:
        return {"error": "No study log data available to form groups."}
        
    # 2. Structure data into a Pandas DataFrame
    df = pd.DataFrame([dict(record) for record in records])
    
    # Pivot to create a matrix of Student (rows) x Topics (columns)
    # Fill missing topics with a default neutral score of 5
    matrix = df.pivot(index='student_id', columns='topic_id', values='score').fillna(5)
    
    # 3. Apply K-Means Clustering
    # Enforce 'auto' for n_init to avoid warnings and speed up convergence
    n_clusters = 2 if len(matrix) >= 2 else 1
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    matrix['cluster'] = kmeans.fit_predict(matrix.values)
    
    # 4. Pair Complementary Students (Opposites Attract)
    features = matrix.drop(columns=['cluster'])
    distances = euclidean_distances(features)
    
    paired = set()
    pairs = []
    student_ids = list(features.index)
    
    for i, student_a in enumerate(student_ids):
        if student_a in paired:
            continue
            
        max_dist = -1
        best_match = None
        
        # Find the student furthest away in the feature space who isn't paired
        for j, student_b in enumerate(student_ids):
            if i != j and student_b not in paired:
                if distances[i][j] > max_dist:
                    max_dist = distances[i][j]
                    best_match = student_b
                    
        if best_match:
            pairs.append((student_a, best_match))
            paired.add(student_a)
            paired.add(best_match)
        else:
            pairs.append((student_a, "No match available (Odd number of students)"))
            
    return {
        "clusters": matrix['cluster'].to_dict(),
        "complementary_pairs": pairs
    }

#  Local Testing Block 
if __name__ == "__main__":
    result = match_study_groups()
    
    print("\n SMART STUDY GROUP MATCHER")
    print("\nClusters Assigned:")
    for student, cluster in result.get('clusters', {}).items():
        print(f" -> {student} is in Cluster {cluster}")
        
    print("\nComplementary Pairs Created:")
    for pair in result.get('complementary_pairs', []):
        print(f" -> {pair[0]} matched with {pair[1]}")
        
    db.close()