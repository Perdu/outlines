from functools import singledispatch

from outlines.fsm.guide import RegexGuide
from outlines.generate.api import (
    SequenceGenerator,
    SequenceGeneratorAdapter,
    VisionSequenceGeneratorAdapter,
)
from outlines.models import (
    MLXLM,
    VLLM,
    LlamaCpp,
    OpenAI,
    Transformers,
    TransformersVision,
)
from outlines.samplers import Sampler, multinomial


@singledispatch
def regex(model, regex_str: str, sampler: Sampler = multinomial()):
    """Generate structured text in the language of a regular expression.

    Parameters
    ----------
    model:
        An instance of `Transformer` that represents a model from the
        `transformers` library.
    regex_str:
        The regular expression that the output must follow.
    sampler:
        The sampling algorithm to use to generate token ids from the logits
        distribution.

    Returns
    -------
    A `SequenceGenerator` instance that generates text constrained by the
    regular expression.

    """
    fsm = RegexGuide(regex_str, model.tokenizer)

    device = model.device
    generator = SequenceGenerator(fsm, model, sampler, device)

    return generator


@regex.register(MLXLM)
@regex.register(Transformers)
@regex.register(LlamaCpp)
def regex_unified(
    model,
    regex_str: str,
    sampler: Sampler = multinomial(),
):
    from outlines.processors import RegexLogitsProcessor

    logits_processor = RegexLogitsProcessor(regex_str, tokenizer=model.tokenizer)
    return SequenceGeneratorAdapter(model, logits_processor, sampler)


@regex.register(TransformersVision)
def regex_vision(
    model,
    regex_str: str,
    sampler: Sampler = multinomial(),
):
    from outlines.processors import RegexLogitsProcessor

    logits_processor = RegexLogitsProcessor(regex_str, tokenizer=model.tokenizer)
    return VisionSequenceGeneratorAdapter(model, logits_processor, sampler)


@regex.register(VLLM)
def regex_vllm(
    model: VLLM,
    regex_str: str,
    sampler: Sampler = multinomial(),
):
    from outlines.integrations.vllm import RegexLogitsProcessor

    logits_processor = RegexLogitsProcessor(regex_str, model.model)
    return SequenceGeneratorAdapter(model, logits_processor, sampler)


@regex.register(OpenAI)
def regex_openai(
    model: OpenAI,
    regex_str: str,
    sampler: Sampler = multinomial(),
):
    raise NotImplementedError(
        "Cannot use regex-structured generation with an OpenAI model"
        + "due to the limitations of the OpenAI API."
    )
