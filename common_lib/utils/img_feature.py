import hashlib
from os.path import join
from timeit import default_timer as timer
from typing import Optional, Iterator

import numpy as np
from model_embedding_msgspec import embedding_pb2

from common_lib.models.img_feature import (
    ModelFeature,
    ModelFeatureList,
    FeatureListForGroup,
    FeatureHashWithObjectKey,
    FeatureSet,
    FeatureColorWeight,
)
from common_lib.models.intra_similarity import ModelIndexFeature


def extract_major_version(version: str) -> Optional[str]:
    if version is None:
        return "5"
    major_version = version.split(".")[0]
    return major_version


def get_object_key(major_version: str, feature_id: str, product_id) -> str:
    key = f"{major_version}/{feature_id}/{product_id}.proto"
    return key


def get_chunked_keys(
    chunks: Iterator[list[FeatureListForGroup]],
) -> list[list[FeatureHashWithObjectKey]]:
    chunked_list = []
    for _, chunk in enumerate(chunks):
        chunked_feature_lists = []
        for feature_list in chunk:
            major_version = extract_major_version(feature_list.model_version)
            object_key = get_object_key(
                major_version, feature_list.feature_id, feature_list.product_id
            )
            chunked_feature_lists.append(
                FeatureHashWithObjectKey(
                    feat_hash=feature_list.feat_hash,
                    object_key=object_key,
                )
            )
        chunked_list.append(chunked_feature_lists)
    return chunked_list


def get_feat_hash(data: ModelFeatureList):
    return hashlib.md5(
        f"{data.s3_image_url}+"
        f"{data.top:.6f}+"
        f"{data.left:.6f}+"
        f"{data.width:.6f}+"
        f"{data.height:.6f}".encode("utf-8")
    ).hexdigest()


def serialize(feature: ModelFeature) -> bytes:
    pb_obj = embedding_pb2.EmbeddingObject(
        detectionId=0,
        feature_with_color=feature.feature_with_color,
        feature_without_color=feature.feature_without_color,
        feature_with_color_more=feature.feature_with_color_more,
    )
    serialized = pb_obj.SerializeToString()
    return serialized


def deserialize(feature_byte: bytes) -> ModelFeature:
    pb_obj = embedding_pb2.EmbeddingObject()
    pb_obj.ParseFromString(feature_byte)

    return ModelFeature(
        feature_with_color=list(pb_obj.feature_with_color),
        feature_without_color=list(pb_obj.feature_without_color),
        feature_with_color_more=list(pb_obj.feature_with_color_more),
    )


def load_cached_feature_list(
    feature_set: FeatureSet,
) -> tuple[list, list]:
    cached_feature_lists, cached_features = [], []
    filenames = [
        join(feature_set.file_dir, filename)
        for filename in feature_set.file_names.split(",")
    ]
    for filename in filenames:
        try:
            npzfile = np.load(filename, allow_pickle=True)
            cached_feature_lists.extend(list(npzfile["feature_lists"]))
            cached_features.extend(list(npzfile["features"]))
        except Exception as e:  # noqa
            pass

    return cached_feature_lists, cached_features


def get_download_list_from_cached_feature(
    download_list: list[FeatureListForGroup],
    cached_feature_lists: list,
    cached_features: list,
) -> tuple[dict, list]:
    feature_dict = {
        feature_list.feat_hash: feature_list for feature_list in download_list
    }
    cached_feature_dict = {
        feature_list.feat_hash: feature
        for feature_list, feature in zip(cached_feature_lists, cached_features)
    }
    feat_hash_set = set(feature_dict)
    cached_feat_hash_set = set(cached_feature_dict)
    new_feat_hash_set = feat_hash_set.difference(cached_feat_hash_set)
    new_download_list = [feature_dict[feat_hash] for feat_hash in new_feat_hash_set]
    return cached_feature_dict, new_download_list


def get_cached_feature(
    time_measures: dict,
    feature_set: FeatureSet,
    download_list: list[FeatureListForGroup],
) -> tuple[dict, list]:
    if not feature_set:
        return {}, download_list

    tic_load = timer()
    cached_feature_lists, cached_features = load_cached_feature_list(
        feature_set=feature_set
    )
    time_measures["load_cached_feature_list"] += timer() - tic_load

    tic_append = timer()
    cached_feature_dict, new_download_list = get_download_list_from_cached_feature(
        download_list=download_list,
        cached_feature_lists=cached_feature_lists,
        cached_features=cached_features,
    )
    time_measures["new_download_list"] += timer() - tic_append

    return cached_feature_dict, new_download_list


class ModelFeatureSelector:
    def __init__(self, model_feature: ModelFeature):
        self.features = {
            FeatureColorWeight.LOW: model_feature.feature_without_color,
            FeatureColorWeight.MEDIUM: model_feature.feature_with_color,
            FeatureColorWeight.HIGH: model_feature.feature_with_color_more,
        }

    def get_model_feature(self, feature_color_weight: str) -> np.array:
        return np.array(self.features[feature_color_weight], dtype="float32")


def parse_binary_feature(feature: ModelFeature, feature_color_weight: str):
    model_feature_selector = ModelFeatureSelector(feature)
    features = model_feature_selector.get_model_feature(feature_color_weight)
    return ModelIndexFeature(features=features)
