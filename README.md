# pipeline

Ever tried Elixir? Wish you could use the pipe operator everywhere? (of course you have!)
Then this small project will help you around creating pipelines for all you data-processing needs!

Pipeline is oriented toward processing streams of objects rather than individual objects,
therefore the majority of the functions in it take an iterator and return another iterator.

It is a wrapper around itertools. I have changed the names of common operations (eg map -> apply, filter -> keep/exclude) so there is no risk of accidentally replacing a builtin function.

## installation

Clone repo and run ```python setup.py install``` or ```pip install .```

# usage

For a runnable piece of code that uses most of the capabilities of the package, please consult
the *_test.py file, namely the last few lines. Here it is below, slightly modified:
```python
from pipeline import pipeline as pp
p = pp.P(
	range(10) + [None, None] + range(10), 			#initial iterator
	pp.exclude_None, 								#exclude items which are None
	pp.keep(lambda i: i%2 == 0),					#keep even elements
	pp.apply(lambda i: i*2),						#multiply every element by two
	pp.apply(lambda i: (i, i+1, i+2)),				#create a tuple with numbers 
	pp.splat(GenericThing),							#"cast" tuple to object
	pp.unique(lambda gt: gt.to_immutable()),		#remove duplicate objects according to key
	pp.project("thisattr", "thatattr", "otherattr"),#get tuple with selected attributes
	pp.splat(GenericThing),							#"recast" tuple to objects
	pp.materialize,									#"precipitate" the processing of the pipeline, returning a list
)
```

"P" is the main object that creates pipelines. It will return whatever the pipeline returns at the end.
In this sample, it will be a list.

The canonical usage for this is reading from a queue, performing some computations over the messages,
and writing the new data to another queue or database. Something like the below:

```python
import functools

from favouritekafkadriver import KConsumer, KProducer
from pipeline import pipeline as pp

class MessageIn(object):
	...

class MessageOut(object):
	...

kc = KConsumer("127.0.0.1:9092") #assume KConsumer implements an iterator interface
kp = KProducer("127.0.0.1:9092")

p = pp.P(
	kc,
	pp.apply(lambda x: MessageIn.from_json(x.messageBytes)),
	pp.exclude(lambda mi: mi.not_important()),
	pp.apply(lambda mi: mi.to_message_out()), #likely here you would project/splat stuff from MI to MO
	pp.apply(lambda mo: mo.to_json()),
	functools.partial(kp.send, "mytopic"), #func signature is send(topic, messages)
	pp.drain #we drain the stream as the messages arrive. we don't want to materialize, it may be an infinite stream
)

```

This idea of this code is to run indefinitely and pass messages from one queue to another,
while processing them in some way. 


# pros

- the order of execution is clear
- it can handle infinite streams
- it's nifty!

# cons

- it's a "#$%& to debug!
- no idea about performance
- lots of unnamed functions 


# future work
There is one feature I think is lacking which is the ability to invoke some of the functions with a batch of items and not just a single item at a time.