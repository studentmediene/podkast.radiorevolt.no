import warnings
from itertools import filterfalse

from typing import List, Mapping, Dict, Sequence, Set, Union, cast
import requests

import episode_processors
import show_processors
from episode_processors import EpisodeProcessor
from show_processors import ShowProcessor

ShowPipelines = Mapping[str, Sequence[ShowProcessor]]
EpisodePipelines = Mapping[str, Sequence[EpisodeProcessor]]

Pipeline = Union[Sequence[ShowProcessor], Sequence[EpisodeProcessor]]
InternalPipeline = Union[List[ShowProcessor], List[EpisodeProcessor]]
InternalPipelines = Union[Dict[str, List[ShowProcessor]],
                          Dict[str, List[EpisodeProcessor]]]


def create_show_pipelines(
        requests_session: requests.Session,
        settings: dict,
        get_global
) -> ShowPipelines:
    """
    Return a dictionary of show pipelines, all initialized.

    This may raise an error if there is something wrong with the pipeline
    configuration.

    Args:
        requests_session: Object processors can use to make requests.
        settings: The application settings, used to look up pipeline and
            processor configurations.
        get_global: Function which returns the data source with the given key.

    Returns:
        Dictionary with pipeline name as key, list of initialized processors
        as value.
    """
    pipelines = init_all_pipelines(
        requests_session,
        settings,
        get_global,
        "show",
        show_processors
    )
    validate_pipelines(pipelines, {"web", "all_feed", "image_processing"})
    return cast(ShowPipelines, pipelines)


def create_episode_pipelines(
        requests_session: requests.Session,
        settings: dict,
        get_global
) -> EpisodePipelines:
    """
    Return a dictionary of episode pipelines, all initialized.

    This may raise an error if there is something wrong with the pipeline
    configuration.

    Args:
        requests_session: Object processors can use to make requests.
        settings: The application settings, used to look up pipeline and
            processor configurations.
        get_global: Function which returns the data source with the given key.

    Returns:
        Dictionary with pipeline name as key, list of initialized processors
        as value.
    """
    pipelines = init_all_pipelines(
        requests_session,
        settings,
        get_global,
        "episode",
        episode_processors
    )
    validate_pipelines(pipelines, {"web", "spotify"})
    return cast(EpisodePipelines, pipelines)


def validate_pipelines(
        pipelines: InternalPipelines,
        expected_pipelines: Set[str]
) -> None:
    """
    Ensure there are no missing pipelines, and warn about pipelines with a name
    that indicates they should be expected, yet they are not.

    By starting a pipeline name with an underscore, you indicate that the
    pipeline is for internal use only and not one to be used directly by our
    code here (instead, its purpose is to be included in other pipelines).

    Args:
        pipelines: Configured pipelines.
        expected_pipelines: Set of pipeline names to assert are found in
            pipelines.

    Returns:
        Nothing.

    Raises:
        ValueError: When an expected pipeline was not found.

    Warnings:
        UserWarning: When a pipeline's name starts with a letter, yet it is not
            an expected pipeline. Perhaps it's a misspelling.
    """
    existing_pipelines = list(pipelines.keys())
    for pipeline in existing_pipelines:
        if pipeline[0] != "_" and pipeline not in expected_pipelines:
            warnings.warn("Pipeline named {} was not expected. Pipelines meant "
                          "to be used by other pipelines should start with an "
                          "underscore. Or maybe it was misspelled? Expected "
                          "pipelines: {}"
                          .format(pipeline, expected_pipelines))
    missing_pipelines = list(set(expected_pipelines) - set(existing_pipelines))
    if missing_pipelines:
        raise ValueError("The following pipelines were expected, but not "
                         "found: {}".format(missing_pipelines))


def init_all_pipelines(
        requests_session: requests.Session,
        settings: dict,
        get_global,
        pipeline_type: str,
        package
) -> InternalPipelines:
    """
    Initialize all pipelines of the given pipeline_type.

    Args:
        requests_session: Object processors can use to make HTTP requests.
        settings: Application settings used to find and configure pipelines and
            processors.
        get_global: Function which returns a data source when given its key.
        pipeline_type: Type of pipeline. Either "show" or "episode".
        package: Object whose attributes are classes available as processors
            for this type of pipeline.

    Returns:
        Dictionary where pipeline name is key, and a list of initialized
        processors is the value.
    """
    all_pipelines = dict()
    for pipeline in settings['pipelines'][pipeline_type]:
        if pipeline not in all_pipelines:
            init_pipeline_into(
                all_pipelines,
                requests_session,
                settings,
                get_global,
                pipeline_type,
                package,
                pipeline
            )
    return all_pipelines


def init_pipeline_into(
        pipeline_dict: InternalPipelines,
        requests_session: requests.Session,
        settings: dict,
        get_global,
        pipeline_type: str,
        package,
        pipeline: str,
        pipeline_hier: List[str]=None
) -> None:
    """
    Initialize the given pipeline, inserting it to the given pipeline_dict.

    This function implements inserting other pipelines into this pipeline, with
    checks in place to guard against endless recursion.

    Args:
        pipeline_dict: Dictionary of pipelines already configured, and in which
            this pipeline should be added when done initializing.
        requests_session: Object used by processors to make HTTP requests.
        settings: Application settings used to look up pipeline and processor
            configurations.
        get_global: Function which returns the data source with the given key.
        pipeline_type: Type of pipeline. Can be either "show" or "episode".
        package: Object where available processor classes can be retrieved as
            attributes.
        pipeline: Name of pipeline to initialize and insert into pipeline_dict.
        pipeline_hier: List of pipelines we are in the process of initializing
            at this moment. Used to ensure we don't try to initialize a
            pipeline which we are already initializing, a symptom of a cyclic
            dependency.

    Returns:
        Nothing, pipeline_dict is manipulated in place.
    """
    def hier2str(l):
        return " -> ".join(l)

    # Do some housekeeping to ensure we don't go into endless recursion
    if pipeline_hier is None:
        pipeline_hier = [pipeline]
    else:
        if pipeline in pipeline_hier:
            raise RuntimeError("Cyclic pipeline dependency detected! {}"
                               .format(hier2str(pipeline_hier + [pipeline])))
        else:
            # Create copy
            pipeline_hier = pipeline_hier[:]
            # and add ourselves
            pipeline_hier.append(pipeline)

    # Does there exist a pipeline with this name? Try fetching config
    try:
        pipeline_conf = settings['pipelines'][pipeline_type][pipeline]
    except KeyError as e:
        raise ValueError(
            "Found no pipeline named {}.{}! (pipeline hierarchy: {})"
                .format(
                pipeline_type,
                pipeline,
                hier2str(pipeline_hier)
            )
        ) from e

    initialized_processors = []  # type: InternalPipeline
    for entry in pipeline_conf:
        handle_pipeline_entry(
            entry,
            initialized_processors,
            pipeline_dict,
            requests_session,
            settings,
            get_global,
            pipeline_type,
            package,
            pipeline,
            pipeline_hier
        )
    # Save this pipeline
    pipeline_dict[pipeline] = initialized_processors


def handle_pipeline_entry(
        entry: Union[str, dict],
        initialized_processors: InternalPipeline,
        pipeline_dict: InternalPipelines,
        requests_session: requests.Session,
        settings: dict,
        get_global,
        pipeline_type: str,
        package,
        pipeline: str,
        pipeline_hier: List[str]
) -> None:
    """
    Handle this entry in a pipeline's configuration.

    This may either be a new processor to instantiate, or a reference to
    another pipeline, in which case the other pipeline is created if it's not
    already, and then inserted into this pipeline.

    Args:
        entry: This entry in the pipeline's configuration.
        initialized_processors: This pipeline's processors. New processors
            are added to this list by this function.
        pipeline_dict: Dictionary of configured pipelines. New pipelines
            created as a result of references to other pipelines are added here
            in place.
        requests_session: Object used by processors to make HTTP requests.
        settings: Application settings used to look up processor configurations,
            and pipeline configurations for recursive calls.
        get_global: Function used by processors to obtain instances of data
            sources.
        pipeline_type: Type of pipeline. Can be either "show" or "episode".
        package: Object whose attributes are classes available to instantiate.
        pipeline: Name of pipeline we're handling an entry of.
        pipeline_hier: List of pipelines we are already initializing.

    Returns:
        Nothing, initialized_processors and pipeline_dict are modified in place.
    """
    # Each entry in a pipeline is a dictionary with a single key: value pair
    # The key is the class to use, the value is the configuration (dict).
    # However, if there is nothing to configure, the entry may be just the
    # class name, which then makes the entry a string.
    # The entry may also be a reference to another pipeline, which should
    # then be embedded here.
    if isinstance(entry, dict):
        class_name, local_processor_conf = next(iter(entry.items()))
    elif isinstance(entry, str):
        # Just a string, which means no local configuration
        first_char = entry[0]
        if first_char == "_" or first_char.islower():
            # This is a reference to another pipeline, insert it here
            if entry not in pipeline_dict:
                init_pipeline_into(
                    pipeline_dict,
                    requests_session,
                    settings,
                    get_global,
                    pipeline_type,
                    package,
                    entry,
                    pipeline_hier
                )
            initialized_processors.extend(pipeline_dict[entry])
            return
        else:
            # First letter is uppercase, so it's a class name
            class_name = entry
            local_processor_conf = {}
    else:
        raise RuntimeError(
            "Did not understand the entry {!r} in pipeline {}.{}. Entry "
            "must be either a dictionary with a single item, or a string."
                .format(entry, pipeline_type, pipeline)
        )

    initialized_processors.append(create_processor(
        requests_session,
        settings,
        get_global,
        pipeline_type,
        package,
        pipeline,
        class_name,
        local_processor_conf
    ))


def create_processor(
        requests_session: requests.Session,
        settings: dict,
        get_global,
        pipeline_type: str,
        package,
        pipeline: str,
        class_name: str,
        local_processor_conf: dict
) -> Union[ShowProcessor, EpisodeProcessor]:
    """
    Create instance of the given processor, initialized with its configuration.

    Args:
        requests_session: Object this processor can use to make requests.
        settings: Application settings, used to look up this processor's
            global configuration.
        get_global: Function this processor can use to gain access to data
            sources by calling it with the data source's key.
        pipeline_type: Type of pipeline, can be either "show" or "episode".
        package: Object from which we can obtain an instance of the class named
            in class_name.
        pipeline: Name of pipeline this processor is configured for. Used to
            give some context to exceptions.
        class_name: Name of class to instantiate as a processor.
        local_processor_conf: Local configuration specific for this instance of
            the processor.

    Returns:
        Instance of the processor named in the class_name parameter.

    Raises:
        RuntimeError: When the class_name is not found as an attribute of
            package.
    """
    # Create configuration for this processor, starting with empty dict,
    # overwriting with global processor config and finally config for this
    # appearance in a pipeline specifically
    processor_conf = dict()
    glb_processor_conf = settings['processors'].get(class_name, dict())
    # Ensure we can specify both episodes and shows to bypass for
    # processors which are both show and episode processors
    glb_processor_conf['bypass'] = glb_processor_conf.get(
        'bypass_' + pipeline_type,
        []
    )
    processor_conf.update(glb_processor_conf)
    processor_conf.update(local_processor_conf)

    # Find the constructor
    processor_func = getattr(package, class_name, None)
    if processor_func is None:
        available_classes = get_available_classes(package)
        raise RuntimeError(
            "The class {class_} in pipeline {type}.{pipeline} was not found. "
            "Available classes: {classes}"
                .format(
                class_=class_name,
                pipeline=pipeline,
                type=pipeline_type,
                classes=available_classes
            )
        )
    # Use it
    return processor_func(
        processor_conf,
        processor_conf['bypass'],
        requests_session,
        get_global
    )


def get_available_classes(package) -> List[str]:
    """
    Create list of classes available to the pipeline configuration.

    Args:
        package: Object with the classes available as attributes.

    Returns:
        List of class names which can be used in pipelines of this type.
    """
    classes = dir(package)
    classes = filterfalse(lambda c: c.startswith("_"), classes)
    classes = filterfalse(lambda c: c in ('ShowProcessor', 'EpisodeProcessor'),
                          classes)
    classes = filter(lambda c: c[0].isupper(), classes)
    return list(classes)
