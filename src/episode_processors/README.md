# Episode processors

This directory contains all possible episode processors. An episode processor may add metadata to an episode, and may also exclude the episode from the podcast it's a part of.

The processors are placed one after another in _pipelines_.

## How to create your own

1. Create a new Python module in this folder, like `example.py`.
2. Import `EpisodeProcessor` from `episode_processors`.
3. Create your episode processor as a class which extends `EpisodeProcessor`.
4. Optionally override and implement `__init__`, call the superclass' constructor and define additional attributes you need. See existing implementations.
5. Optionally override and implement `prepare_batch`, where you download and parse any data you need from external resources, but only if that saves time versus doing it one by one.
6. Override and implement the `accepts` method, return `super().accepts(episode)` and apply any additional restrictions on which episodes you will deal with (using `and`).
7. Override and implement the `populate` method, in which you make whatever changes you want to `episode`, or raise `SkipEpisode` if this episode should not be added to the podcast.
8. Describe the processor's purpose and the additional settings it accepts in
   the class' docstring.

For show processors, the process is pretty much the same. See the existing
processors inside `src/show_processors`.


## How to configure

Each processor has two configurations: a global configuration and a local one.

The global configuration is defined in the `processors` setting, with classname as key and settings as value. If an episode processor and a show processor share their classname, they will share this configuration. You can set what will be bypassed by setting `bypass_show` and `bypass_episode`. For episodes, you can use `start_date` and `end_date` (in format `YYYY-MM-DD`) to specify an interval of episodes the processor will accept.

The local configuration overrides the global one. It is defined in the pipeline configuration, again with the class name being key and local settings being the value. This configuration is only given to the processor at this place in this pipeline, so you may even have the same processor multiple times in the same pipeline, and have different settings for them.

Note that the merging mechanism is very stupid and will simply replace one list with another. As a result, you cannot add additional episodes to bypass in a local configuration; you can only define a new list of episodes to bypass.

### Settings accepted by all processors

* **`bypass_show`**: List of Digas IDs which should be bypassed (that is, not
  touched by this processor). For Show processors, shows with a Digas ID found
  here are bypassed. For Episode processors, episodes which are part of a show
  whose Digas ID is found here, are bypassed. The default is empty.
* **`bypass_episode`**: List of episode URLs (original URLs, not proxy) which should
  be bypassed. Only observed by Episode processors. The default is empty.
* **`start_date`**: Date in format `YYYY-MM-DD`. The first date of episodes which
  should be accepted; episodes published before this date are bypassed. The
  default is the start of time.
* **`end_date`**: Date in format `YYYY-MM-DD`. The last date of episodes which should
  be accepted; episodes published after this date are bypassed. The default is
  the end of time.
  
All processors may accept more settings; please see the documentation inside
each processor's class.
