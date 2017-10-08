
import itertools


def P(*fns):
	"Creates a pipeline of functions."
	return reduce(lambda fn1, fn2: fn2(fn1), fns)

def apply(fn):
	"Takes a function and returns a map function over an iterable with the provided function."
	return lambda it: itertools.imap(fn, it)

def exclude(fn):
	"Takes a function and returns a filter function over an iterable that removes elements that make the provided function return True."
	return lambda it: itertools.ifilterfalse(fn, it)

def exclude_None(it):
	"Shorthand for removing None objects from the iterable."
	return exclude(lambda i: i is None)(it)

def keep(fn):
	"Same as exclude, but instead returns the elements that match True."
	return lambda it: itertools.ifilter(fn, it)

def aggregate(fn, init=None):
	"Receives a function and returns a reduce function over an iterable."
	def agg(it):
		if init is not None:
			return reduce(fn, it, init)
		return reduce(fn, it)
	return agg

"""
The code below is right out of the sample code from itertools documentation page.
"""
def unique(key=None):
	"""Optionally takes a key function and returns a filter function that removes already seen 
	elements in the iterable. If key is a function (takes one element, returns an immutable object),
	it is used to determine the uniqueness of each item. If key is None or default, default uniqueness criteria
	is used (Python implementation specific).
	"""
	def _uniq(iterable):
		"List unique elements, preserving order. Remember all elements ever seen."
		# unique_everseen('AAAABBBCCDAABBB') --> A B C D
		# unique_everseen('ABBCcAD', str.lower) --> A B C D
		seen = set()
		seen_add = seen.add
		if key is None:
			for element in itertools.ifilterfalse(seen.__contains__, iterable):
				seen_add(element)
				yield element
		else:
			for element in iterable:
				k = key(element)
				if k not in seen:
					seen_add(k)
					yield element
	return _uniq


def project(*attrs):
	"""Takes a list of strings and returns a map function that returns a tuple 
	for each object where the tuple's objects are the attributes of the input objects
	that match the inut strings."""
	return apply(lambda i: (i.__getattribute__(a) for a in attrs))

def kproject(*attrs):
	"Same as project, but instead of a tuple, it returns a dictionary."
	return apply(lambda i: {at: i.__getattribute__(at) for at in attrs})

def splat(fnORcls):
	"""Takes a function name (or class) and returns a map function where each item in the iterable
	is a tuple. That tuple is then passed as positional arguments for the provided function (or class)."""
	return apply(lambda i: fnORcls(*i))

def ksplat(fnORcls):
	"Same as splat, but with dicts instead of tuples."
	return apply(lambda i: fnORcls(**i))	

def puts(it):
	"Prints the items on the iterator and passes them through. Mainly useful for debugging."
	for i in it:
		print i
		yield i

def materialize(it):
	"Will create a list out of the iterator, therefore loading all of it into memory, and then return that list."
	return [i for i in it]

def drain(it):
	"Consumes all of an iterable and then returns an empty list. Similar to materialize, but discards all elements."
	for i in it:
		pass
	return []