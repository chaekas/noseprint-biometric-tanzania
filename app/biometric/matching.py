import numpy as np


def best_animal_match(query_embedding, rows):
    """Aggregate image-level cosine similarities into one score per animal."""
    best_by_animal = {}
    query = np.asarray(query_embedding, dtype=np.float32)
    query /= max(float(np.linalg.norm(query)), 1e-12)
    for animal_id, animal_code, stored_vector in rows:
        candidate = np.asarray(stored_vector, dtype=np.float32)
        score = float(np.dot(query, candidate) / max(float(np.linalg.norm(candidate)), 1e-12))
        previous = best_by_animal.get(animal_id)
        if previous is None or score > previous["similarity"]:
            best_by_animal[animal_id] = {
                "animal_id": animal_id,
                "animal_code": animal_code,
                "similarity": score,
            }
    return max(best_by_animal.values(), key=lambda item: item["similarity"], default=None)
