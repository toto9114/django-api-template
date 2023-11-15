from dataclasses import dataclass, field

import numpy as np

# product_id / distances
ModelIntraSimilarityItem = tuple[str, float]

# product_id / ModelIntraSimilarityByColorWeight
ModelIntraSimilarity = list[tuple[str, list[ModelIntraSimilarityItem]]]


@dataclass
class ModelIndexFeature:
    product_ids: list[str] = field(default_factory=list)
    features: np.ndarray = None
