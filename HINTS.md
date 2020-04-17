# Hint configuration

Hints are an integral part of this bot. Here, you can see an example hint definition:

```
    {
        "points": 5,
        "text": "Congratulations! You have level 2 now!",
        "group_message": null,
        "even_contestant": false,
        "even_position": null
    },
```

There isn't any limit in the amount of hints you can define: simply copy this structure as many times as needed.

## What does each key means?

**(All of the keys are mandatory and they must be present in the hint definition, otherwise you will receive an error message)**

### points
This key specifies the minimum amount of points that a contestant needs to have for
receiving that hint. In our example, an eligible contestant needs to have 5 or more points (7,8,10, whatever) for receiving that hint.

* Allowed datatypes: ``null`` or any number (``integer``)

### text
This key specifies the message that will be sent to the contestant's chat, privately.

You can use [Telegram's markdown](https://sourceforge.net/p/telegram/wiki/markdown_syntax/) here

* Allowed datatypes: ``null`` or any string

### group_message
This key specifies the message that will be sent to the group/channel that is holding the leaderboards.
Useful for letting know other contestants that someone else have reached a certain milestone.

You can use [Telegram's markdown](https://sourceforge.net/p/telegram/wiki/markdown_syntax/) here

* Allowed datatypes: ``null`` or any string

### even_contestant
This key specifies if the hint will be issued to contestants that have an even or odd ``Contestant ID``. This is based in the order you followed
for joining the contestants.

* Allowed datatypes: ``null``, ``true`` or ``false``
    * ``true``: Contestants that are **even** trigger this hint
    * ``false``: Contestants that are **odd** trigger this hint
    * ``null``: The joining order is completely ignored.

### even_position
This key specifies if the hint will be issued to contestants in an even or odd position **after the points have been issued**

If a contestant is in the 4th position and, after issuing the points, reaches 3rd position, the position of the contestant is **odd**, not even.

* Allowed datatypes: ``null``, ``true`` or ``false``
    * ``true``: Contestants that are in an **even** position trigger this hint.
    * ``false``: Contestants that are in an **odd** position trigger this hint.
    * ``null``: The position of the contestant is ignored.

## What happens when the "random" key is set to "true"?

The ``points`` key is completely ignored, so you can set it to ``0`` or ``null``
if you have ``"random": true``. The other conditions **will still take place**

Note that the key **is still mandatory**. This is, for example, a bad hint definition:

```
"random": false,
    "hints": [{
        "text": "The ",
        "group_message": null,
        "even_contestant": true,
        "even_position": null
    },
    (...)
```

# Examples

Each hint is triggered once for each contestant. That means that the above hint will 

If a hint was already triggered, it won't be triggered twice for that contestant, as explained in the README.md (**Tips** section)

Let's see some examples to understand how everything works better.

In the hint definition above, the following will happen:
* One message will be sent:
    * To the contestant privately: ``Congratulations! You have level 2 now!``
* When?:
    * A contestant has **5 points or more**
    * Joined the Scavenger in an **odd position** (**odd** ``contestant ID``)

### Let's see more definitions:

```
    "random": false,
    "hints": [{
    (...)
    {
        "points": 5,
        "text": "Congratulations! You have level 2 now!",
        "group_message": "{0} is on level 2 right now!",
        "even_contestant": null,
        "even_position": null
    },
    (...)
```
* Two messages will be sent:
    * To the contestant privately: ``Congratulations! You have level 2 now!``
    * To the leaderboard's group: ``The Painter is on level 2 right now!`` (``{0}`` is replaced with
    the contestant's alias)
* When?:
    * Contestants has **5 points or more**

```
    "random": false,
    "hints": [{
    (...)
    {
        "points": 7,
        "text": null,
        "group_message": "One contestant participating in the north area has now 7 points",
        "even_contestant": true,
        "even_position": true
    },
    (...)
```
* One message will be sent:
    * To the leaderboard's group: ``One contestant participating in the north area has now 7 points``
* When?:
    * Contestants has **7 points or more**
    * Joined the Scavenger in an **even position** (**even** ``contestant ID``)
    * It's current position in the leaderboards is an **even number**

# Other considerations

* You can't set the ``text`` and ``group_message`` keys to ``null`` at the same time: that makes no sense

* Every time the ``!prom`` or ``.p`` command is issued and points are added or substracted, the bot will check if some of the hint definitions
meet the new conditions that the contestant has, and will run them.

* Hints will never be repeated to one contestant. For example:
    * A contestant has 9 points. In a challenge he earns 5 points, so he has 14 points now.
    * A hint is configured to be sent everytime a contestant gets > 10 points, so the contestant gets it.
    * Later, you penalise that contestant and remove 7 points. He has 7 points now
    * In another challenge, the contestant gets 4 points, so he has 11 points.
    * The contestant **won't receive the previous hint**

* However, hints apply **always** to all contestants. For example:
    * A hint definition says that one message is going to be sent to the contestant privately and another one to the group
    * Only for contestants in an even position that have >= 10 points
    * One contestant receives that hint.
    * Another contestant that meets the same criteria later **will receive the same hint again**
