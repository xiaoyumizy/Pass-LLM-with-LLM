"""Configurable embedding 封装（exam-memory V2 核心层）。

设计对齐 OneFind v1.7：
  - pooling: CLS token（非 mean），确保向量空间兼容
  - normalize: L2，使 dot product = cosine similarity
  - 维度: 1024，与 OneFind zotero/obsidian/folder source 一致

无 LangChain 依赖，CPU-only，静默降级。

配置（环境变量）:
    EXAM_MEMORY_EMBEDDING_PROVIDER   local|api（默认 local）
    EXAM_MEMORY_EMBEDDING_MODEL      BAAI/bge-m3（默认）或本地路径
    EXAM_MEMORY_EMBEDDING_LOCAL_FILES_ONLY  0|1（默认 0）
    EXAM_MEMORY_EMBEDDING_NORMALIZE  0|1（默认 1）

用法:
    from exam_memory.embedding import get_embedder, encode, is_available
    if is_available():
        vec = encode("双指针三数之和")          # (1024,) float32
        vecs = encode(["背包问题", "动态规划"])   # (2, 1024) float32
"""

from __future__ import annotations

import logging
import os
from typing import Union

import numpy as np

logger = logging.getLogger(__name__)

# ── 配置读取 ────────────────────────────────────────────────

EMBEDDING_ENV_PREFIX = "EXAM_MEMORY_EMBEDDING"

_EMBEDDING_DEFAULTS: dict[str, str] = {
    "PROVIDER": "local",
    "MODEL": "BAAI/bge-m3",
    "LOCAL_FILES_ONLY": "0",
    "NORMALIZE": "1",
}


def get_embedding_config() -> dict[str, str]:
    """读取所有 EXAM_MEMORY_EMBEDDING_* 环境变量，返回配置字典。

    未设置时使用默认值。仅包含实际存在的环境变量，方便上层按需读取。
    """
    config: dict[str, str] = {}
    for key, default in _EMBEDDING_DEFAULTS.items():
        env_key = f"{EMBEDDING_ENV_PREFIX}_{key}"
        config[key] = os.environ.get(env_key, default)
    # 透传 API 专用变量（默认空字符串）
    for key in ("API_BASE", "API_KEY", "API_MODEL"):
        env_key = f"{EMBEDDING_ENV_PREFIX}_{key}"
        config[key] = os.environ.get(env_key, "")
    return config


# ── 依赖检测 ────────────────────────────────────────────────

class EmbeddingError(Exception):
    pass


def _check_dependency() -> None:
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        raise EmbeddingError(
            "sentence-transformers 未安装。"
            "请运行: pip install '.[embed]'"
        )


# ── 模型单例 ────────────────────────────────────────────────

_MODEL = None


def get_embedder(model_name: str | None = None):
    """延迟加载 embedding 模型（单例）。CPU-only。

    对齐 OneFind: CLS pooling + L2 normalize。
    验证 model[1].pooling_mode_cls_token == True。

    Args:
        model_name: 模型名称或本地路径。为 None 时从
            EXAM_MEMORY_EMBEDDING_MODEL 读取，默认 BAAI/bge-m3。
    """
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    _check_dependency()
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

    if model_name is None:
        config = get_embedding_config()
        model_name = config["MODEL"]

    from sentence_transformers import SentenceTransformer
    _MODEL = SentenceTransformer(model_name, device="cpu")

    _verify_pooling(_MODEL)
    return _MODEL


def _verify_pooling(model) -> None:
    """验证模型使用 CLS pooling（对齐 OneFind）。"""
    try:
        pooling = model[1]
        if hasattr(pooling, "pooling_mode_cls_token"):
            is_cls = pooling.pooling_mode_cls_token
        elif hasattr(pooling, "pooling_mode_mean_tokens"):
            is_cls = not pooling.pooling_mode_mean_tokens
        else:
            is_cls = True  # 无法检测时假设正确，OneFind 已知配置

        if not is_cls:
            logger.warning(
                "[embedding] 模型 pooling 非 CLS 模式，向量空间可能与 OneFind 不兼容。"
                "当前 pooling_mode_cls_token=False，建议检查模型配置。"
            )
        else:
            logger.info("[embedding] CLS pooling 已确认，向量空间与 OneFind 兼容。")
    except Exception as e:
        logger.debug(f"[embedding] pooling 验证跳过（结构不匹配）: {e}")


def is_available() -> bool:
    """embedding 层是否可用。"""
    try:
        _check_dependency()
        return True
    except EmbeddingError:
        return False


# ── 编码接口 ────────────────────────────────────────────────

def encode_safe(
    text: Union[str, list[str]],
    *,
    normalize: bool | None = None,
) -> np.ndarray | None:
    """编码的安静版本——依赖不可用时返回 None。"""
    try:
        return encode(text, normalize=normalize)
    except Exception:
        return None


# ── API 嵌入提供者 ────────────────────────────────────────────

def encode_api(
    text: Union[str, list[str]],
    *,
    api_base: str | None = None,
    api_key: str | None = None,
    api_model: str | None = None,
    normalize: bool | None = None,
) -> np.ndarray:
    """通过 OpenAI 兼容 embedding API 编码文本。

    Args:
        text: 单条文本或文本列表（API 通常支持批量）。
        api_base: API 端点，None 时从 EXAM_MEMORY_EMBEDDING_API_BASE 读取。
        api_key: API key，None 时从 EXAM_MEMORY_EMBEDDING_API_KEY 读取。
        api_model: 模型名称，None 时从 EXAM_MEMORY_EMBEDDING_API_MODEL 读取。
        normalize: L2 归一化，None 时从 EXAM_MEMORY_EMBEDDING_NORMALIZE 读取。

    Returns:
        float32 numpy 数组。
    """
    try:
        from litellm import embedding
    except ImportError:
        raise EmbeddingError(
            "API embedding 需要 litellm。"
            "请运行: pip install '.[embed-api]'"
        )

    cfg = get_embedding_config()
    base = api_base or cfg.get("API_BASE", "")
    key = api_key or cfg.get("API_KEY", "")
    model = api_model or cfg.get("API_MODEL", "")
    if normalize is None:
        normalize = cfg.get("NORMALIZE", "1") == "1"

    if not base:
        raise EmbeddingError(
            "EXAM_MEMORY_EMBEDDING_API_BASE 未设置，无法使用 API embedding。"
        )
    if not model:
        raise EmbeddingError(
            "EXAM_MEMORY_EMBEDDING_API_MODEL 未设置，无法使用 API embedding。"
        )

    inputs = text if isinstance(text, list) else [text]
    resp = embedding(
        model=model,
        input=inputs,
        api_base=base,
        api_key=key or None,
    )
    vecs = np.array([d["embedding"] for d in resp.data], dtype=np.float32)
    if normalize:
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vecs = vecs / norms
    return vecs if isinstance(text, list) else vecs[0]


# ── 统一编码接口 ──────────────────────────────────────────────

def encode(
    text: Union[str, list[str]],
    *,
    normalize: bool | None = None,
    provider: str | None = None,
) -> np.ndarray:
    """将文本编码为 embedding 向量，自动选择 provider。

    provider 为 None 时从 EXAM_MEMORY_EMBEDDING_PROVIDER 读取：
      - local（默认）：sentence-transformers CPU-only
      - api：OpenAI 兼容 embedding API（litellm）

    Args:
        text: 单条文本或文本列表。
        normalize: L2 归一化。为 None 时从环境变量读取。
        provider: 覆盖环境变量中的 provider 设置。
    """
    if provider is None:
        cfg = get_embedding_config()
        provider = cfg.get("PROVIDER", "local")

    if provider == "api":
        return encode_api(text, normalize=normalize)

    return _encode_local(text, normalize=normalize)


def _encode_local(
    text: Union[str, list[str]],
    normalize: bool | None = None,
) -> np.ndarray:
    """本地 sentence-transformers 编码。"""
    model = get_embedder()
    if normalize is None:
        cfg = get_embedding_config()
        normalize = cfg.get("NORMALIZE", "1") == "1"
    emb = model.encode(
        text,
        normalize_embeddings=normalize,
        show_progress_bar=False,
    )
    return np.asarray(emb, dtype=np.float32)
